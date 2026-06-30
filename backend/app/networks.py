"""Re-attribute Trakt watch events to the actual streaming service.

Trakt's history never says *which* service a watch came from. TMDB does expose a
series' ``networks`` (the broadcaster/streamer it airs on, e.g. Netflix, Prime
Video, HBO Max, Apple TV+). We map that network to one of the household's
configured providers and move the Trakt-sourced ``watch_events`` onto it — so
the title page *and* every aggregate/statistic count those hours under the real
service instead of "Trakt".

Rules:
  * Only Trakt-sourced events are touched; Plex/Jellyfin/Netflix already *are*
    the service/library they came from.
  * A network that isn't in the catalogue — and movies, which have no network —
    fall back to the generic ``Other`` provider (localized "Overig" in the UI).
  * ``dedup_hash`` is intentionally left untouched: it was computed with the
    Trakt provider id, so a later Trakt sync recomputes the same hash and hits
    ``ON CONFLICT (dedup_hash) DO NOTHING`` — the event is never re-created.
  * Aggregates (``watch_daily_agg``) are keyed on ``provider_id``, so after the
    move we recompute both the old (Trakt) and new provider over the affected
    days via ``wv_recompute_agg_days``.
"""
from __future__ import annotations

from .db import connection

# Normalized TMDB network name -> provider key in our catalogue. Resolution
# still checks the provider exists in the DB, so removed providers (e.g. nlziet)
# simply fall through to the generic provider.
_NETWORK_ALIASES = {
    "netflix": "netflix",
    "hbo": "hbomax",
    "hbo max": "hbomax",
    "max": "hbomax",
    "amazon": "prime",
    "amazon prime": "prime",
    "amazon prime video": "prime",
    "prime video": "prime",
    "prime": "prime",
    "disney+": "disney",
    "disney plus": "disney",
    "disney": "disney",
    "skyshowtime": "skyshowtime",
    "videoland": "videoland",
    "nlziet": "nlziet",
    "apple tv+": "appletv",
    "apple tv plus": "appletv",
    "apple tv": "appletv",
}


def _norm(name: str | None) -> str:
    return " ".join((name or "").strip().lower().split())


def resolve_network_provider(cur, networks: list[dict]):
    """Return ``(provider_id, provider_key)`` for the first network that maps to
    a provider present in the catalogue, else the generic provider."""
    for n in networks or []:
        key = _NETWORK_ALIASES.get(_norm(n.get("name")))
        if not key:
            continue
        cur.execute("SELECT id, key FROM providers WHERE key = %s", (key,))
        row = cur.fetchone()
        if row:
            return str(row["id"]), row["key"]
    cur.execute("SELECT id, key FROM providers WHERE key = 'generic'")
    row = cur.fetchone()
    return str(row["id"]), row["key"]


def reattribute_title_trakt_events(title_id: str) -> dict:
    """Move a title's Trakt-sourced watch events onto the provider matching its
    TMDB network (or the generic provider), recomputing aggregates for both the
    old and new provider over the affected days.

    Returns a status dict with the number of events ``moved`` and ``collapsed``
    (tombstoned because the same watch already exists on the target provider)."""
    with connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, metadata FROM titles WHERE id = %s", (title_id,))
        title = cur.fetchone()
        if not title:
            return {"status": "no_title"}

        cur.execute("SELECT id FROM providers WHERE key = 'trakt'")
        trakt = cur.fetchone()
        if not trakt:
            return {"status": "no_trakt_provider"}
        trakt_id = str(trakt["id"])

        networks = (title["metadata"] or {}).get("networks") or []
        target_id, target_key = resolve_network_provider(cur, networks)
        if target_id == trakt_id:
            return {"status": "noop"}

        cur.execute(
            "SELECT id, user_id, watched_date, episode_id "
            "FROM watch_events "
            "WHERE title_id = %s AND provider_id = %s AND deleted_at IS NULL",
            (title_id, trakt_id))
        rows = cur.fetchall()
        if not rows:
            return {"status": "ok", "moved": 0, "collapsed": 0, "provider": target_key}

        affected: dict[str, set] = {}
        for r in rows:
            affected.setdefault(str(r["user_id"]), set()).add(r["watched_date"])

        moved = collapsed = 0
        for r in rows:
            # Collapse (tombstone) the Trakt event when the same watch already
            # exists on the target provider, to avoid double counting.
            cur.execute(
                "SELECT 1 FROM watch_events "
                "WHERE user_id = %s AND title_id = %s AND provider_id = %s "
                "  AND watched_date = %s AND deleted_at IS NULL "
                "  AND episode_id IS NOT DISTINCT FROM %s AND id <> %s LIMIT 1",
                (str(r["user_id"]), title_id, target_id, r["watched_date"],
                 r["episode_id"], r["id"]))
            if cur.fetchone():
                cur.execute("UPDATE watch_events SET deleted_at = now() WHERE id = %s",
                            (r["id"],))
                collapsed += 1
                continue
            cur.execute("UPDATE watch_events SET provider_id = %s WHERE id = %s",
                        (target_id, r["id"]))
            moved += 1

        for uid, dates in affected.items():
            dl = list(dates)
            cur.execute("SELECT wv_recompute_agg_days(%s, %s, %s)", (uid, trakt_id, dl))
            cur.execute("SELECT wv_recompute_agg_days(%s, %s, %s)", (uid, target_id, dl))

    return {"status": "ok", "moved": moved, "collapsed": collapsed,
            "provider": target_key}


def reattribute_all_trakt() -> dict:
    """Backfill: re-attribute every enriched title that still has Trakt events.

    Used as a one-time job on deploy so existing history is moved off "Trakt"
    onto the real services without waiting for each title to be re-enriched."""
    with connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT DISTINCT we.title_id FROM watch_events we "
            "JOIN providers p ON p.id = we.provider_id "
            "JOIN titles t ON t.id = we.title_id "
            "WHERE p.key = 'trakt' AND we.deleted_at IS NULL "
            "  AND t.enriched_at IS NOT NULL")
        title_ids = [str(r["title_id"]) for r in cur.fetchall()]

    titles = moved = collapsed = 0
    for tid in title_ids:
        res = reattribute_title_trakt_events(tid)
        if res.get("status") == "ok":
            titles += 1
            moved += res.get("moved", 0)
            collapsed += res.get("collapsed", 0)
    return {"status": "ok", "titles": titles, "moved": moved, "collapsed": collapsed}
