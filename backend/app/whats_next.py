"""The dashboard "What's next" block.

Every series that carries at least one tag of the household is followed: for each
we look up the next episode nobody in scope has watched and say where it stands.

* ``ready``    -- Sonarr already downloaded it (``calendar_items``).
* ``aired``    -- it has aired but is not known to be downloaded; ``behind`` counts
                  the further aired episodes waiting behind it.
* ``upcoming`` -- it airs later (or has no date yet); Sonarr's next airing refines it.
* ``caught_up``-- everything known is watched; shown only while Sonarr knows a
                  future airing, otherwise the series is left out.
* ``pending``  -- the catalog has no episodes for it yet (TMDB enrichment has not
                  run); Sonarr's date and poster stand in.

``build_whats_next`` is pure (plain dicts in, plain dicts out) so the rules are
testable without a database; the ``fetch_*`` functions are thin queries.
"""
from __future__ import annotations

import datetime as dt

from .continue_watching import fetch_watched
from .db import query_all

LIMIT = 48

# Most urgent first: something to watch right now, then what is waiting, then what
# is still to come, and series the catalog knows nothing about last.
_RANK = {"ready": 0, "aired": 1, "upcoming": 2, "caught_up": 2, "pending": 3}
_FAR = dt.date.max.toordinal()


def _iso(value) -> str | None:
    return value.isoformat() if value else None


def _next_airing_date(row: dict) -> dt.date | None:
    na = row.get("next_airing")
    return na.date() if na else None


def _item(row: dict, state: str, poster, **fields) -> dict:
    base = {
        "key": f"w:{row['title_id']}", "title_id": str(row["title_id"]), "title": row["title"],
        "year": row.get("year"), "kind": "series",
        "poster": poster(row.get("poster_path")) or row.get("sonarr_poster"),
        "tags": [{"id": str(t["id"]), "name": t["name"], "color": t.get("color")}
                 for t in row.get("tags") or []],
        "state": state, "season": None, "episode": None, "episode_id": None, "episode_name": None,
        "air_date": None, "air_at": None, "available_at": None, "behind": 0,
        "runtime_minutes": None,
    }
    base.update(fields)
    base["air_date"] = _iso(base["air_date"])
    base["air_at"] = _iso(base["air_at"])
    base["available_at"] = _iso(base["available_at"])
    return base


def _sort_key(item: dict):
    state = item["state"]
    if state == "ready":
        # newest download first
        when = dt.datetime.fromisoformat(item["available_at"]).timestamp()
        order = -when
    elif state == "aired":
        order = -dt.date.fromisoformat(item["air_date"]).toordinal() if item["air_date"] else 0
    elif state in ("upcoming", "caught_up"):
        order = (dt.date.fromisoformat(item["air_date"]).toordinal() if item["air_date"] else _FAR)
    else:
        order = 0
    return (_RANK[state], order, item["title"].lower(), item["title_id"])


def build_whats_next(series: list[dict], episodes: list[dict], watched: dict[str, set],
                     ready: list[dict], *, today: dt.date, tag: str | None = None,
                     poster=lambda p: p, limit: int = LIMIT) -> dict:
    """The block's payload: ``{"tags": [...], "items": [...]}``.

    ``series`` rows: ``title_id, title, year, tmdb_id, poster_path, tags[{id,name,color}],
    next_airing, sonarr_poster``. ``episodes``: ``episode_id, title_id, season, episode, name,
    air_date, runtime_minutes`` (any order; season 0 / specials are ignored).
    ``watched``: title_id -> {(season, episode)}, "anyone in scope watched it" counts.
    ``ready``: calendar rows ``tmdb_id, season, episode, available_at``.
    The tag counts are taken before the ``tag`` filter so the chips stay put."""
    by_title: dict[str, list[dict]] = {}
    for e in episodes:
        if (e.get("season") or 0) > 0:
            by_title.setdefault(str(e["title_id"]), []).append(e)
    ready_at: dict[tuple, dt.datetime] = {}
    for r in ready:
        key = (r.get("tmdb_id"), r.get("season"), r.get("episode"))
        if r.get("available_at") and (key not in ready_at or r["available_at"] > ready_at[key]):
            ready_at[key] = r["available_at"]

    built: list[tuple[tuple, dict]] = []
    for row in series:
        tid = str(row["title_id"])
        if not row.get("tags"):
            continue
        eps = sorted(by_title.get(tid, []), key=lambda e: (e["season"], e["episode"]))
        seen = watched.get(tid, set())
        na_date = _next_airing_date(row)
        if not eps:
            if row.get("next_airing") is None:
                item = _item(row, "pending", poster)
            else:
                item = _item(row, "pending", poster, air_date=na_date, air_at=row["next_airing"])
        else:
            todo = [e for e in eps if (e["season"], e["episode"]) not in seen]
            if not todo:
                if na_date is None or na_date < today:
                    continue
                item = _item(row, "caught_up", poster, air_date=na_date, air_at=row["next_airing"])
            else:
                first = todo[0]
                fields = {"season": first["season"], "episode": first["episode"],
                          "episode_id": first.get("episode_id"), "episode_name": first.get("name"),
                          "runtime_minutes": first.get("runtime_minutes"),
                          "air_date": first.get("air_date")}
                aired = sum(1 for e in todo if e.get("air_date") and e["air_date"] <= today)
                got = ready_at.get((row.get("tmdb_id"), first["season"], first["episode"]))
                if got is not None:
                    item = _item(row, "ready", poster, available_at=got,
                                 behind=max(0, aired - 1), **fields)
                elif first.get("air_date") and first["air_date"] <= today:
                    item = _item(row, "aired", poster, behind=max(0, aired - 1), **fields)
                else:
                    if first.get("air_date") is None and na_date is not None:
                        fields["air_date"] = na_date
                    if fields["air_date"] is not None and fields["air_date"] == na_date:
                        fields["air_at"] = row["next_airing"]
                    item = _item(row, "upcoming", poster, **fields)
        built.append((_sort_key(item), item))

    built.sort(key=lambda p: p[0])
    items = [i for _, i in built]

    counts: dict[str, dict] = {}
    for i in items:
        for t in i["tags"]:
            entry = counts.setdefault(t["id"], {**t, "count": 0})
            entry["count"] += 1
    tags = sorted(counts.values(), key=lambda t: t["name"].lower())

    if tag:
        items = [i for i in items if any(t["id"] == tag for t in i["tags"])]
    return {"tags": tags, "items": items[:limit]}


def fetch_series(household_id: str) -> list[dict]:
    """Series carrying at least one tag of this household, with those tags and what
    the household's enabled Sonarr connections say about them."""
    return query_all(
        "SELECT t.id AS title_id, t.title, t.year, t.tmdb_id, t.poster_path, "
        "  (SELECT jsonb_agg(jsonb_build_object('id', g.id::text, 'name', g.name, 'color', g.color) "
        "                    ORDER BY lower(g.name)) "
        "   FROM title_tags tt JOIN tags g ON g.id = tt.tag_id "
        "   WHERE tt.title_id = t.id AND g.household_id = %s) AS tags, "
        "  a.next_airing, a.poster_url AS sonarr_poster "
        "FROM titles t "
        "LEFT JOIN LATERAL ("
        "  SELECT s.next_airing, s.poster_url FROM arr_series s "
        "  JOIN source_connections sc ON sc.id = s.connection_id "
        "  WHERE s.household_id = %s AND sc.enabled "
        "    AND (s.tmdb_id = t.tmdb_id "
        "         OR (s.normalized_key = t.normalized_key AND (t.tmdb_id IS NULL OR s.tmdb_id IS NULL))) "
        "  ORDER BY (s.tmdb_id = t.tmdb_id) DESC NULLS LAST, s.next_airing NULLS LAST LIMIT 1) a ON true "
        "WHERE t.kind = 'series' AND EXISTS ("
        "  SELECT 1 FROM title_tags tt JOIN tags g ON g.id = tt.tag_id "
        "  WHERE tt.title_id = t.id AND g.household_id = %s)",
        (household_id, household_id, household_id))


def fetch_episodes(title_ids: list[str]) -> list[dict]:
    if not title_ids:
        return []
    return query_all(
        "SELECT id::text AS episode_id, title_id::text AS title_id, season, episode, name, air_date, "
        "  runtime_minutes "
        "FROM title_episodes WHERE title_id = ANY(%s::uuid[]) AND season > 0",
        (title_ids,))


def fetch_ready(household_id: str, tmdb_ids: list[int]) -> list[dict]:
    """Downloaded Sonarr episodes (the last 30 days of calendar) of the given series."""
    if not tmdb_ids:
        return []
    return query_all(
        "SELECT c.tmdb_id, c.season, c.episode, c.available_at FROM calendar_items c "
        "JOIN source_connections sc ON sc.id = c.connection_id "
        "WHERE c.household_id = %s AND c.kind = 'series' AND sc.enabled "
        "  AND c.tmdb_id = ANY(%s::int[])",
        (household_id, tmdb_ids))


def whats_next(household_id: str, user_ids: list[str], poster=lambda p: p,
               tag: str | None = None, today: dt.date | None = None) -> dict:
    today = today or dt.datetime.now(dt.timezone.utc).date()
    series = fetch_series(household_id)
    title_ids = [str(r["title_id"]) for r in series]
    episodes = fetch_episodes(title_ids)
    ready = fetch_ready(household_id, sorted({r["tmdb_id"] for r in series if r["tmdb_id"]}))
    return build_whats_next(series, episodes, fetch_watched(user_ids, title_ids), ready,
                            today=today, tag=tag, poster=poster)
