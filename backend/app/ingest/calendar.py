"""Refresh a Sonarr/Radarr connection's calendar into ``calendar_items``.

Runs from the worker's 15-minute connection schedule and from the manual "Sync"
button. The connection's rows are *replaced* by the window just read, so an item
that was deleted or fell out of the window disappears on the next refresh.
"""
from __future__ import annotations

import datetime as dt

from ..db import connection
from .adapters import get_adapter

# The calendar is always read for the longest period a person can choose to see
# ("Continue watching" setting, 0-30 days); the dashboard narrows it at read time,
# so changing the setting needs no new sync.
MAX_DAYS = 30
DEFAULT_DAYS = 14

_COLUMNS = ("source", "kind", "external_key", "title", "year", "season", "episode",
            "episode_name", "tmdb_id", "tvdb_id", "imdb_id", "poster_url",
            "runtime_minutes", "air_date", "available_at")


def window(today: dt.date | None = None) -> tuple[dt.date, dt.date]:
    """The calendar window to read: the last ``MAX_DAYS`` days up to tomorrow
    (tomorrow, so an episode whose air date is already "tomorrow" in UTC is kept)."""
    today = today or dt.datetime.now(dt.timezone.utc).date()
    return today - dt.timedelta(days=MAX_DAYS), today + dt.timedelta(days=1)


def store_calendar(cur, household_id, connection_id, items: list[dict]) -> int:
    """Replace one connection's calendar rows on a caller-owned cursor."""
    cur.execute("DELETE FROM calendar_items WHERE connection_id = %s", (connection_id,))
    for item in items:
        values = [item.get(c) for c in _COLUMNS]
        cur.execute(
            f"INSERT INTO calendar_items (household_id, connection_id, {', '.join(_COLUMNS)}) "
            f"VALUES (%s, %s, {', '.join(['%s'] * len(_COLUMNS))}) "
            "ON CONFLICT (connection_id, external_key) DO NOTHING",
            [household_id, connection_id, *values])
    return len(items)


_SERIES_COLUMNS = ("sonarr_id", "title", "normalized_key", "year", "status", "monitored",
                   "tmdb_id", "tvdb_id", "imdb_id", "network", "poster_url", "next_airing",
                   "previous_airing", "season_count", "episode_file_count", "episode_count",
                   "total_episode_count")


def store_series(cur, household_id, connection_id, rows: list[dict]) -> int:
    """Replace one connection's running-series snapshot on a caller-owned cursor."""
    cur.execute("DELETE FROM arr_series WHERE connection_id = %s", (connection_id,))
    for row in rows:
        cur.execute(
            f"INSERT INTO arr_series (household_id, connection_id, {', '.join(_SERIES_COLUMNS)}) "
            f"VALUES (%s, %s, {', '.join(['%s'] * len(_SERIES_COLUMNS))}) "
            "ON CONFLICT (connection_id, sonarr_id) DO NOTHING",
            [household_id, connection_id, *[row.get(c) for c in _SERIES_COLUMNS]])
    return len(rows)


def queue_stale_enrichment(cur, household_id) -> int:
    """Re-enrich *tagged* series whose catalog episodes are missing or behind Sonarr.

    TMDB enrichment runs once per title and nothing refreshes it afterwards, so a
    running series would never get its new season or next episode. A tagged series
    qualifies when it has no episodes at all, or when Sonarr knows an upcoming
    airing the catalog has no episode on/after. At most one job per title per day
    (judged by the jobs themselves, whether or not they changed anything)."""
    cur.execute(
        "INSERT INTO background_jobs (kind, payload) "
        "SELECT 'enrich_title', jsonb_build_object('title_id', t.id::text) "
        "FROM titles t "
        "WHERE t.kind = 'series' AND t.tmdb_id IS NOT NULL "
        "  AND EXISTS (SELECT 1 FROM title_tags tt JOIN tags g ON g.id = tt.tag_id "
        "              WHERE tt.title_id = t.id AND g.household_id = %s) "
        "  AND (NOT EXISTS (SELECT 1 FROM title_episodes e WHERE e.title_id = t.id) "
        "       OR EXISTS (SELECT 1 FROM arr_series a "
        "                  WHERE a.household_id = %s AND a.tmdb_id = t.tmdb_id "
        "                    AND a.next_airing >= now() "
        "                    AND NOT EXISTS (SELECT 1 FROM title_episodes e WHERE e.title_id = t.id "
        "                                    AND e.air_date >= (a.next_airing AT TIME ZONE 'UTC')::date))) "
        "  AND NOT EXISTS (SELECT 1 FROM background_jobs j WHERE j.kind = 'enrich_title' "
        "                  AND j.payload->>'title_id' = t.id::text "
        "                  AND j.created_at > now() - interval '1 day')",
        (household_id, household_id))
    return cur.rowcount


def refresh_calendar(conn: dict, today: dt.date | None = None) -> dict:
    """Refresh a ``source_connections`` row (joined with its provider's ``adapter``):
    the ready-to-watch calendar and, for Sonarr, the running series.

    The two parts are independent: each is fetched and stored in its own
    transaction, so a failing series call never wipes the calendar (or vice versa).
    The outcome is recorded on the connection and the first failure is re-raised so
    callers can report it."""
    adapter = get_adapter(conn["adapter"])
    config = conn["config"] or {}
    start, end = window(today)
    counts: dict[str, int] = {}
    errors: list[tuple[str, Exception]] = []

    try:
        items = adapter.fetch_calendar(config, start, end)
        with connection() as c, c.cursor() as cur:
            counts["calendar"] = store_calendar(cur, conn["household_id"], conn["id"], items)
    except Exception as exc:  # noqa: BLE001 — recorded below, re-raised after the other part ran
        errors.append(("calendar", exc))

    if adapter.lists_series:
        try:
            rows = adapter.fetch_series(config)
            with connection() as c, c.cursor() as cur:
                counts["series"] = store_series(cur, conn["household_id"], conn["id"], rows)
                queue_stale_enrichment(cur, conn["household_id"])
        except Exception as exc:  # noqa: BLE001
            errors.append(("series", exc))

    if errors:
        # The calendar keeps the plain "error: <message>" it always had; other parts are named.
        status = "error: " + "; ".join(str(e) if part == "calendar" else f"{part}: {e}"
                                       for part, e in errors)
    else:
        status = f"ok: {counts['calendar']} ready to watch"
        if "series" in counts:
            status += f", {counts['series']} running series"
    with connection() as c, c.cursor() as cur:
        cur.execute("UPDATE source_connections SET last_status = %s, last_sync_at = now() WHERE id = %s",
                    (status, conn["id"]))
    if errors:
        raise errors[0][1]
    out = {"calendar": counts["calendar"], "inserted": 0, "duplicates": 0}
    if "series" in counts:
        out["series"] = counts["series"]
    return out
