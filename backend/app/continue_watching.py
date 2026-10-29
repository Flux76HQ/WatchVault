"""The dashboard "Continue watching" block.

Two kinds of item, nothing else:

* **partial** — something a household member started and stopped part-way. This
  comes from the live scrobble sessions (Plex webhooks, Home Assistant, Apple TV):
  ``position_seconds`` / ``progress_percent`` that never reached the commit
  threshold. A session that is playing *right now* belongs to "Now playing", not
  here.
* **ready** — an episode or film that Sonarr/Radarr already downloaded recently
  (``calendar_items``) and nobody in scope has watched yet. Several waiting
  episodes of one series collapse into one card for its earliest unwatched episode.

``build_continue`` is pure (plain dicts in, plain dicts out) so the rules are
testable without a database; the ``fetch_*`` functions are thin queries.
"""
from __future__ import annotations

from .db import query_all, query_one
from .ingest.calendar import DEFAULT_DAYS, MAX_DAYS
from .ingest.scrobble import DEFAULT_THRESHOLD

MIN_PROGRESS = 2.0   # below this a "partial" is an accidental start, not a break
PARTIAL_DAYS = 60    # an abandoned start older than this is not "continue" any more
LIMIT = 24

_SOURCE_NAMES = {"sonarr": "Sonarr", "radarr": "Radarr", "plex": "Plex",
                 "homeassistant": "Home Assistant", "appletv": "Apple TV"}


def clamp_days(value) -> int:
    """The requested "ready to watch" period as a whole number of days in 0..MAX_DAYS;
    anything missing or unparseable falls back to the default."""
    try:
        return max(0, min(MAX_DAYS, int(value)))
    except (TypeError, ValueError):
        return DEFAULT_DAYS


def _threshold() -> float:
    row = query_one("SELECT data->>'scrobble_commit_threshold' AS t FROM app_settings WHERE id = 1")
    try:
        return float(row["t"]) if row and row["t"] is not None else DEFAULT_THRESHOLD
    except (TypeError, ValueError):
        return DEFAULT_THRESHOLD


def fetch_partials(household_id: str, user_ids: list[str]) -> list[dict]:
    """Stopped/paused, uncommitted playback below the commit threshold, minus anything
    that was watched to the end afterwards."""
    if not user_ids:
        return []
    return query_all(
        "SELECT s.id, s.user_id, s.source, s.kind, s.raw_title, s.season, s.episode, "
        "  s.episode_name, s.progress_percent, s.duration_seconds, s.updated_at, "
        "  s.title_id, t.title AS t_title, t.poster_path, t.runtime_minutes, "
        "  p.key AS provider_key, p.name AS provider_name, p.color AS provider_color, "
        "  u.display_name AS profile_name "
        "FROM scrobble_sessions s "
        "LEFT JOIN titles t ON t.id = s.title_id "
        "LEFT JOIN providers p ON p.id = s.provider_id "
        "LEFT JOIN users u ON u.id = s.user_id "
        "WHERE s.household_id = %s AND s.user_id = ANY(%s::uuid[]) "
        "  AND s.committed_at IS NULL AND s.state <> 'playing' "
        "  AND s.progress_percent >= %s AND s.progress_percent < %s "
        "  AND s.updated_at > now() - make_interval(days => %s) "
        "  AND NOT EXISTS ("
        "    SELECT 1 FROM watch_events we "
        "    WHERE we.user_id = s.user_id AND we.title_id = s.title_id AND we.deleted_at IS NULL "
        "      AND we.watched_at >= s.started_at "
        "      AND (s.kind = 'movie' OR (COALESCE(we.season, 0) = COALESCE(s.season, 0) "
        "                                AND we.episode IS NOT DISTINCT FROM s.episode))) "
        "ORDER BY s.updated_at DESC LIMIT 100",
        (household_id, [str(i) for i in user_ids], MIN_PROGRESS, _threshold(), PARTIAL_DAYS))


def fetch_ready(household_id: str, days: int = DEFAULT_DAYS) -> list[dict]:
    """Calendar items that arrived since the start (UTC) of the day ``days`` days ago
    -- so 0 means "today only" -- joined to the catalog title they match."""
    return query_all(
        "SELECT DISTINCT ON (c.id) c.id, c.source, c.kind, c.external_key, c.title, c.year, "
        "  c.season, c.episode, c.episode_name, c.tmdb_id, c.poster_url, c.runtime_minutes, "
        "  c.available_at, t.id AS title_id, t.title AS t_title, t.poster_path "
        "FROM calendar_items c "
        "LEFT JOIN titles t ON t.tmdb_id = c.tmdb_id AND c.tmdb_id IS NOT NULL "
        "  AND t.kind = CASE c.kind WHEN 'movie' THEN 'movie' ELSE 'series' END "
        "WHERE c.household_id = %s "
        "  AND c.available_at >= (date_trunc('day', now() AT TIME ZONE 'UTC') "
        "                         - make_interval(days => %s)) AT TIME ZONE 'UTC' "
        "ORDER BY c.id, t.id",
        (household_id, clamp_days(days)))


def fetch_watched(user_ids: list[str], title_ids: list[str]) -> dict[str, set]:
    """title_id -> {(season, episode)} the scoped profiles have watched; a movie
    watch is recorded as ``(0, None)``."""
    if not user_ids or not title_ids:
        return {}
    rows = query_all(
        "SELECT title_id::text AS title_id, COALESCE(season, 0) AS season, episode "
        "FROM watch_events WHERE user_id = ANY(%s::uuid[]) AND title_id = ANY(%s::uuid[]) "
        "  AND deleted_at IS NULL GROUP BY title_id, COALESCE(season, 0), episode",
        ([str(i) for i in user_ids], title_ids))
    out: dict[str, set] = {}
    for r in rows:
        out.setdefault(r["title_id"], set()).add((r["season"], r["episode"]))
    return out


def _provider(key, name, color=None) -> dict | None:
    if not key:
        return None
    return {"key": key, "name": name or _SOURCE_NAMES.get(key, key.title()), "color": color}


def _partial_item(r: dict, poster) -> dict:
    progress = float(r["progress_percent"] or 0)
    duration = r.get("duration_seconds") or ((r.get("runtime_minutes") or 0) * 60) or None
    remaining = max(0, round(duration * (100 - progress) / 100 / 60)) if duration else None
    key = r.get("provider_key") or r["source"]
    return {
        "key": f"p:{r['id']}", "origin": "partial", "source": r["source"],
        "kind": "series" if r["kind"] == "series" else "movie",
        "title_id": str(r["title_id"]) if r.get("title_id") else None,
        "title": r.get("t_title") or r["raw_title"], "poster": poster(r.get("poster_path")),
        "season": r.get("season"), "episode": r.get("episode"), "episode_name": r.get("episode_name"),
        "progress": round(progress, 1), "remaining_minutes": remaining, "more": 0,
        "at": r["updated_at"].isoformat(),
        "provider": _provider(key, r.get("provider_name"), r.get("provider_color")),
        "profile": r.get("profile_name"),
    }


def _ready_item(rows: list[dict], poster) -> dict:
    """One card for a group of waiting calendar rows (an episode group or one film)."""
    first = min(rows, key=lambda r: (r.get("season") or 0, r.get("episode") or 0))
    newest = max(r["available_at"] for r in rows)
    runtime = first.get("runtime_minutes")
    return {
        "key": f"c:{first['source']}:{first['external_key']}", "origin": "ready",
        "source": first["source"], "kind": "series" if first["kind"] == "series" else "movie",
        "title_id": str(first["title_id"]) if first.get("title_id") else None,
        "title": first.get("t_title") or first["title"],
        "poster": poster(first.get("poster_path")) or first.get("poster_url"),
        "season": first.get("season"), "episode": first.get("episode"),
        "episode_name": first.get("episode_name"),
        "progress": None, "remaining_minutes": runtime, "more": len(rows) - 1,
        "at": newest.isoformat(), "provider": _provider(first["source"], None), "profile": None,
    }


def build_continue(partials: list[dict], ready: list[dict], watched: dict[str, set],
                   poster=lambda p: p, limit: int = LIMIT) -> list[dict]:
    """Merge partial playback and ready-to-watch calendar items into the block's list."""
    # Partials: newest first, one per (profile, title, episode).
    items: list[dict] = []
    seen, claimed = set(), set()
    for r in sorted(partials, key=lambda r: r["updated_at"], reverse=True):
        ident = (str(r["user_id"]), str(r.get("title_id") or r["raw_title"]).lower(),
                 r.get("season") or 0, r.get("episode"))
        if ident in seen:
            continue
        seen.add(ident)
        items.append(_partial_item(r, poster))
        if r.get("title_id"):
            claimed.add((str(r["title_id"]), r.get("season") or 0, r.get("episode")))

    # Ready: drop what is watched or already shown as a partial, then group by series.
    groups: dict[tuple, list[dict]] = {}
    for r in ready:
        tid = str(r["title_id"]) if r.get("title_id") else None
        ep = (r.get("season") or 0, r.get("episode")) if r["kind"] == "series" else (0, None)
        if tid:
            seen_by_scope = watched.get(tid, set())
            if (ep in seen_by_scope) if r["kind"] == "series" else bool(seen_by_scope):
                continue
            if (tid, *ep) in claimed:
                continue
        gkey = ("series", tid or r.get("tmdb_id") or r["title"].lower()) if r["kind"] == "series" \
            else ("movie", r["external_key"], r["source"])
        groups.setdefault(gkey, []).append(r)
    cards = [_ready_item(rows, poster) for rows in groups.values()]
    cards.sort(key=lambda c: c["at"], reverse=True)
    return (items + cards)[:limit]


def continue_items(household_id: str, user_ids: list[str], poster=lambda p: p,
                   days: int = DEFAULT_DAYS) -> list[dict]:
    partials = fetch_partials(household_id, user_ids)
    ready = fetch_ready(household_id, days)
    title_ids = sorted({str(r["title_id"]) for r in ready if r.get("title_id")})
    return build_continue(partials, ready, fetch_watched(user_ids, title_ids), poster)
