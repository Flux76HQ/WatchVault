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


def refresh_calendar(conn: dict, today: dt.date | None = None) -> dict:
    """Fetch the calendar window for a ``source_connections`` row (joined with its
    provider's ``adapter``) and store it. Records the outcome on the connection and
    re-raises a failure so callers can surface it."""
    adapter = get_adapter(conn["adapter"])
    start, end = window(today)
    try:
        items = adapter.fetch_calendar(conn["config"] or {}, start, end)
        with connection() as c, c.cursor() as cur:
            n = store_calendar(cur, conn["household_id"], conn["id"], items)
            cur.execute(
                "UPDATE source_connections SET last_status = %s, last_sync_at = now() WHERE id = %s",
                (f"ok: {n} ready to watch", conn["id"]))
    except Exception as exc:  # noqa: BLE001 — record, then let the caller report it
        with connection() as c, c.cursor() as cur:
            cur.execute(
                "UPDATE source_connections SET last_status = %s, last_sync_at = now() WHERE id = %s",
                (f"error: {exc}", conn["id"]))
        raise
    return {"calendar": n, "inserted": 0, "duplicates": 0}
