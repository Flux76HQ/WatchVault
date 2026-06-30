"""Tests for the manual "add a cinema film" flow — no database or network.

Covers the two pure pieces of the feature: the TMDB search-result mapper and the
``get_or_create_movie_by_tmdb`` catalog helper (driven by a fake cursor so the
branch logic is verified without a live Postgres)."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.api.ingest import _map_movie_search_result  # noqa: E402
from app.catalog import get_or_create_movie_by_tmdb  # noqa: E402


def test_map_movie_search_result_full():
    out = _map_movie_search_result({
        "id": 693134, "title": "Dune: Part Two",
        "release_date": "2024-02-27", "poster_path": "/p.jpg",
        "overview": "On Arrakis.",
    })
    assert out == {
        "tmdb_id": 693134, "title": "Dune: Part Two", "year": 2024,
        "release_date": "2024-02-27",
        "poster": "https://image.tmdb.org/t/p/w342/p.jpg",
        "overview": "On Arrakis.",
    }


def test_map_movie_search_result_handles_missing_fields():
    out = _map_movie_search_result({"id": 5, "name": "Old Film", "release_date": ""})
    assert out["tmdb_id"] == 5
    assert out["title"] == "Old Film"   # falls back to `name`
    assert out["year"] is None
    assert out["release_date"] is None
    assert out["poster"] is None
    assert out["overview"] is None


def test_map_movie_search_result_skips_idless():
    assert _map_movie_search_result({"title": "No Id"}) is None


class FakeCursor:
    """Minimal cursor recording executes and replaying canned fetchone rows."""
    def __init__(self, rows):
        self._rows = list(rows)
        self.executed = []

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def fetchone(self):
        return self._rows.pop(0) if self._rows else None


def test_get_or_create_reuses_existing():
    cur = FakeCursor([{"id": "abc-123"}])
    tid = get_or_create_movie_by_tmdb(cur, 693134, "Dune: Part Two", 2024)
    assert tid == "abc-123"
    # Only the SELECT ran — no INSERT when the movie already exists.
    assert len(cur.executed) == 1
    assert "SELECT" in cur.executed[0][0]


def test_get_or_create_inserts_when_absent():
    cur = FakeCursor([None, {"id": "new-id"}])
    tid = get_or_create_movie_by_tmdb(cur, 693134, "Dune: Part Two", 2024)
    assert tid == "new-id"
    assert len(cur.executed) == 2
    insert_sql, params = cur.executed[1]
    assert "INSERT INTO titles" in insert_sql
    assert params[0] == "Dune: Part Two"   # title
    assert params[1] == 2024               # year
    assert params[2] == 693134             # tmdb_id


def test_get_or_create_normalized_key_fallback():
    cur = FakeCursor([None, {"id": "x"}])
    get_or_create_movie_by_tmdb(cur, 42, "", None)
    _, params = cur.executed[1]
    assert params[0] == "TMDB 42"          # placeholder title
    assert params[3] == "tmdb:42"          # normalized_key fallback
