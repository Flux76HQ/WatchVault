"""Tests for the Expert-mode "delete a whole title" flow — no live database.

Drives ``delete_title`` with a scripted fake cursor so the delete sequence and
the per-(user, provider) aggregate rebuild are verified without Postgres."""
import datetime as dt
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.ingest import manual  # noqa: E402


class FakeCursor:
    """Cursor that replays canned fetchone/fetchall results in call order and
    records every executed statement for assertions."""
    def __init__(self, fetchone_rows, fetchall_rows):
        self._one = list(fetchone_rows)
        self._all = list(fetchall_rows)
        self.executed = []

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def fetchone(self):
        return self._one.pop(0) if self._one else None

    def fetchall(self):
        return self._all.pop(0) if self._all else []


class _Ctx:
    def __init__(self, val):
        self._val = val

    def __enter__(self):
        return self._val

    def __exit__(self, *a):
        return False


class FakeConn:
    def __init__(self, cur):
        self._cur = cur

    def cursor(self):
        return _Ctx(self._cur)


def _patch(monkeypatch, cur):
    monkeypatch.setattr(manual, "connection", lambda: _Ctx(FakeConn(cur)))


def test_delete_title_missing_returns_no_title(monkeypatch):
    cur = FakeCursor(fetchone_rows=[None], fetchall_rows=[])
    _patch(monkeypatch, cur)
    out = manual.delete_title("nope")
    assert out == {"status": "no_title", "removed_events": 0}
    # Only the existence lookup ran; nothing was deleted.
    assert len(cur.executed) == 1
    assert "SELECT id, title FROM titles" in cur.executed[0][0]


def test_delete_title_removes_events_and_rebuilds_agg(monkeypatch):
    d1, d2 = dt.date(2025, 1, 5), dt.date(2025, 1, 6)
    cur = FakeCursor(
        fetchone_rows=[{"id": "t1", "title": "Dune: Part Two"}],
        fetchall_rows=[
            # affected (user, provider, date) tuples
            [
                {"user_id": "u1", "provider_id": "p1", "watched_date": d1},
                {"user_id": "u1", "provider_id": "p1", "watched_date": d2},
                {"user_id": "u2", "provider_id": "p1", "watched_date": d1},
            ],
            # DELETE ... RETURNING id  -> three rows removed
            [{"id": "e1"}, {"id": "e2"}, {"id": "e3"}],
        ],
    )
    _patch(monkeypatch, cur)

    out = manual.delete_title("t1")
    assert out == {"status": "ok", "title": "Dune: Part Two", "removed_events": 3}

    sqls = [e[0] for e in cur.executed]
    # Watch events are deleted explicitly (title_id is ON DELETE SET NULL).
    assert any("DELETE FROM watch_events WHERE title_id" in s for s in sqls)
    # The catalog row is dropped (episodes/people/genres cascade).
    assert any("DELETE FROM titles WHERE id" in s for s in sqls)
    # Aggregates rebuilt once per distinct (user, provider) pair: (u1,p1)+(u2,p1).
    recompute = [e for e in cur.executed if "wv_recompute_agg_days" in e[0]]
    assert len(recompute) == 2
    pairs = {(e[1][0], e[1][1]) for e in recompute}
    assert pairs == {("u1", "p1"), ("u2", "p1")}
    # u1 watched on both days; that recompute call carries both dates.
    u1 = next(e for e in recompute if e[1][0] == "u1")
    assert set(u1[1][2]) == {d1, d2}
