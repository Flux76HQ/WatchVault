"""Running series from Sonarr: list them, and tag them.

A Sonarr connection keeps a snapshot of the series it reports as running in
``arr_series`` (see ``ingest.calendar``). Tags, however, hang on catalog ``titles``,
and a series nobody has watched is not in the catalog. So tagging a Sonarr series
*adds it to the catalog* (by TMDB id, enrichment queued) and attaches the tag to
that title; from then on it is an ordinary title with the ordinary tag features.
Untagging only removes the tag -- the title stays.
"""
from __future__ import annotations

import json
import uuid

from flask import Blueprint, jsonify

from ..auth.sessions import current_user, require_perm
from ..catalog import enqueue_enrich, get_or_create_series_by_tmdb
from ..db import connection, query_all, query_one
from ._common import poster_url
from .tags import _owned_tag

bp = Blueprint("arr", __name__, url_prefix="/api")


def _household_id() -> str:
    return str(current_user()["household_id"])


def _valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False
    return True


def _sonarr_connection(cur, conn_id: str, household_id: str):
    """The connection row iff it is a Sonarr connection of this household."""
    if not _valid_uuid(conn_id):
        return None
    cur.execute(
        "SELECT sc.id, sc.last_sync_at FROM source_connections sc "
        "JOIN providers p ON p.id = sc.provider_id "
        "WHERE sc.id = %s AND sc.household_id = %s AND p.key = 'sonarr'",
        (conn_id, household_id))
    return cur.fetchone()


def _iso(value) -> str | None:
    return value.isoformat() if value else None


def series_view(row: dict, tags: list[dict]) -> dict:
    """One list entry for the Imports "Running series" panel. ``taggable`` is false
    when this Sonarr gave no TMDB id: without one the series cannot be bound to a
    catalog title, so it is shown but cannot be tagged."""
    return {
        "sonarr_id": row["sonarr_id"], "title": row["title"], "year": row["year"],
        "network": row["network"],
        "poster": poster_url(row.get("poster_path")) or row.get("poster_url"),
        "next_airing": _iso(row["next_airing"]),
        "episodes_have": row["episode_file_count"], "episodes_total": row["total_episode_count"],
        "seasons": row["season_count"], "tmdb_id": row["tmdb_id"],
        "taggable": row["tmdb_id"] is not None,
        "title_id": str(row["title_id"]) if row.get("title_id") else None,
        "tags": tags,
    }


@bp.get("/connections/<conn_id>/series")
@require_perm("catalog.read")
def list_series(conn_id: str):
    hid = _household_id()
    with connection() as conn, conn.cursor() as cur:
        sc = _sonarr_connection(cur, conn_id, hid)
    if not sc:
        return jsonify({"error": "not found"}), 404
    # The catalog title a series maps to: the same TMDB id, or -- for a Plex-created
    # row that has no TMDB id yet -- the same normalized key. A title that carries a
    # *different* TMDB id under the same name is another show and never matches.
    rows = query_all(
        "SELECT a.sonarr_id, a.title, a.year, a.network, a.poster_url, a.next_airing, a.tmdb_id, "
        "  a.season_count, a.episode_file_count, a.total_episode_count, t.id AS title_id, t.poster_path "
        "FROM arr_series a "
        "LEFT JOIN LATERAL ("
        "  SELECT id, poster_path FROM titles "
        "  WHERE kind = 'series' AND (tmdb_id = a.tmdb_id "
        "    OR (normalized_key = a.normalized_key AND (tmdb_id IS NULL OR a.tmdb_id IS NULL))) "
        "  ORDER BY (tmdb_id = a.tmdb_id) DESC NULLS LAST LIMIT 1) t ON true "
        "WHERE a.connection_id = %s ORDER BY a.next_airing NULLS LAST, lower(a.title)",
        (conn_id,))
    title_ids = [str(r["title_id"]) for r in rows if r["title_id"]]
    tags_by_title: dict[str, list[dict]] = {}
    if title_ids:
        for t in query_all(
                "SELECT tt.title_id, tg.id, tg.name, tg.color FROM title_tags tt "
                "JOIN tags tg ON tg.id = tt.tag_id "
                "WHERE tt.title_id = ANY(%s::uuid[]) AND tg.household_id = %s ORDER BY lower(tg.name)",
                (title_ids, hid)):
            tags_by_title.setdefault(str(t["title_id"]), []).append(
                {"id": str(t["id"]), "name": t["name"], "color": t["color"]})
    return jsonify({
        "synced_at": _iso(sc["last_sync_at"]),
        "series": [series_view(r, tags_by_title.get(str(r["title_id"]), []) if r["title_id"] else [])
                   for r in rows],
    })


@bp.post("/connections/<conn_id>/series/<int:sonarr_id>/tags/<tag_id>")
@require_perm("ingest.write")
def tag_series(conn_id: str, sonarr_id: int, tag_id: str):
    hid = _household_id()
    with connection() as conn, conn.cursor() as cur:
        if not _sonarr_connection(cur, conn_id, hid):
            return jsonify({"error": "not found"}), 404
        cur.execute("SELECT * FROM arr_series WHERE connection_id = %s AND sonarr_id = %s",
                    (conn_id, sonarr_id))
        series = cur.fetchone()
        if not series:
            return jsonify({"error": "series not found"}), 404
        if not _valid_uuid(tag_id) or not _owned_tag(cur, tag_id, hid):
            return jsonify({"error": "tag not found"}), 404
        if not series["tmdb_id"]:
            return jsonify({"error": "no_tmdb_id",
                            "message": "Sonarr did not report a TMDB id for this series"}), 422
        title_id, created = get_or_create_series_by_tmdb(
            cur, series["tmdb_id"], series["title"], series["year"])
        if created:
            # Keep what Sonarr knows beyond the TMDB id, for later matching.
            cur.execute(
                "UPDATE titles SET imdb_id = COALESCE(imdb_id, %s), "
                "  external_ids = external_ids || %s::jsonb WHERE id = %s",
                (series["imdb_id"], json.dumps({"tvdb_id": series["tvdb_id"]}), title_id))
        cur.execute("INSERT INTO title_tags (title_id, tag_id) VALUES (%s, %s) "
                    "ON CONFLICT DO NOTHING", (title_id, tag_id))
        enqueue_enrich(cur, title_id)
    return jsonify({"ok": True, "title_id": title_id, "created": created})


@bp.delete("/connections/<conn_id>/series/<int:sonarr_id>/tags/<tag_id>")
@require_perm("ingest.write")
def untag_series(conn_id: str, sonarr_id: int, tag_id: str):
    hid = _household_id()
    with connection() as conn, conn.cursor() as cur:
        if not _sonarr_connection(cur, conn_id, hid):
            return jsonify({"error": "not found"}), 404
        if not _valid_uuid(tag_id) or not _owned_tag(cur, tag_id, hid):
            return jsonify({"error": "tag not found"}), 404
        cur.execute("SELECT tmdb_id FROM arr_series WHERE connection_id = %s AND sonarr_id = %s",
                    (conn_id, sonarr_id))
        series = cur.fetchone()
        if not series:
            return jsonify({"error": "series not found"}), 404
        title_id = None
        if series["tmdb_id"]:
            cur.execute("SELECT id FROM titles WHERE kind = 'series' AND tmdb_id = %s",
                        (series["tmdb_id"],))
            row = cur.fetchone()
            if row:
                title_id = str(row["id"])
                cur.execute("DELETE FROM title_tags WHERE title_id = %s AND tag_id = %s",
                            (title_id, tag_id))
    # No catalog title yet means nothing was ever tagged: a no-op, so it is idempotent.
    return jsonify({"ok": True, "title_id": title_id})
