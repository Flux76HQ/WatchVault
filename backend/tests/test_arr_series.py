"""Sonarr running series — adapter, snapshot store, refresh isolation, catalog helper.

No database or network: HTTP is faked, cursors are scripted/recording. The SQL
itself is exercised against a real Postgres by hand (see the PR description)."""
import contextlib
import datetime as dt
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app import catalog  # noqa: E402
from app.api.arr import series_view  # noqa: E402
from app.ingest import calendar as cal  # noqa: E402
from app.ingest.adapters import arr, get_adapter  # noqa: E402

UTC = dt.timezone.utc


def _series(**over):
    raw = {
        "id": 12, "title": "Severance", "year": 2022, "status": "continuing", "monitored": True,
        "tmdbId": 95396, "tvdbId": 371980, "imdbId": "tt11280740", "network": "Apple TV+",
        "images": [{"coverType": "poster", "remoteUrl": "https://x/sev.jpg", "url": "/MediaCover/12/poster.jpg"}],
        "nextAiring": "2026-11-07T02:00:00Z", "previousAiring": "2026-10-31T02:00:00Z",
        "statistics": {"seasonCount": 2, "episodeFileCount": 18, "episodeCount": 19, "totalEpisodeCount": 19},
    }
    raw.update(over)
    return raw


# ── normalisation ───────────────────────────────────────────────────────────

def test_sonarr_series_maps_a_running_series():
    row = arr.sonarr_series(_series())
    assert (row["sonarr_id"], row["title"], row["year"], row["status"]) == (12, "Severance", 2022, "continuing")
    assert (row["tmdb_id"], row["tvdb_id"], row["imdb_id"], row["network"]) == (95396, 371980, "tt11280740", "Apple TV+")
    assert row["normalized_key"] == "severance"
    assert row["poster_url"] == "https://x/sev.jpg"
    assert row["next_airing"] == dt.datetime(2026, 11, 7, 2, 0, tzinfo=UTC)
    assert row["previous_airing"] == dt.datetime(2026, 10, 31, 2, 0, tzinfo=UTC)
    assert (row["season_count"], row["episode_file_count"], row["episode_count"],
            row["total_episode_count"]) == (2, 18, 19, 19)


def test_sonarr_series_only_keeps_running_monitored_series():
    assert arr.sonarr_series(_series(status="ended")) is None
    assert arr.sonarr_series(_series(status="upcoming")) is None
    assert arr.sonarr_series(_series(monitored=False)) is None
    assert arr.sonarr_series(_series(title="  ")) is None
    assert arr.sonarr_series(_series(id=None)) is None


def test_sonarr_series_tolerates_missing_ids_dates_and_zero_counts():
    row = arr.sonarr_series(_series(tmdbId=0, tvdbId=None, nextAiring=None, previousAiring=None,
                                    statistics={"episodeFileCount": 0}))
    assert row["tmdb_id"] is None and row["tvdb_id"] is None
    assert row["next_airing"] is None and row["previous_airing"] is None
    assert row["episode_file_count"] == 0          # zero is a real count, not "unknown"
    assert row["season_count"] is None


def test_sonarr_series_reads_airings_from_statistics_as_a_fallback():
    row = arr.sonarr_series(_series(nextAiring=None, statistics={"nextAiring": "2026-12-01T00:00:00Z"}))
    assert row["next_airing"] == dt.datetime(2026, 12, 1, tzinfo=UTC)


def test_series_year_suffix_is_stripped_from_the_key_like_a_plex_title():
    assert arr.sonarr_series(_series(title="The Office (US)"))["normalized_key"] == "office us"  # same key rule as every other ingest path (leading article dropped)
    assert arr.sonarr_series(_series(title="Show (2023)"))["normalized_key"] == "show"


# ── fetch_series over a faked HTTP layer ────────────────────────────────────

class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload, self.status_code = payload, status

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def _fake_get(monkeypatch, response):
    calls = []

    def get(url, headers=None, params=None, timeout=None):
        calls.append({"url": url, "headers": headers, "params": params})
        return response

    monkeypatch.setattr(arr.requests, "get", get)
    return calls


CONFIG = {"base_url": "http://sonarr:8989/", "api_key": "k3y"}


def test_fetch_series_filters_dedupes_and_sends_the_key(monkeypatch):
    calls = _fake_get(monkeypatch, FakeResponse([_series(), _series(), _series(id=13, status="ended"),
                                                 _series(id=14, title="Andor", tmdbId=83867)]))
    rows = get_adapter("sonarr_api").fetch_series(CONFIG)
    assert [r["sonarr_id"] for r in rows] == [12, 14]
    assert calls[0]["url"] == "http://sonarr:8989/api/v3/series"
    assert calls[0]["headers"]["X-Api-Key"] == "k3y"


def test_fetch_series_reports_a_rejected_key_and_a_bad_response(monkeypatch):
    _fake_get(monkeypatch, FakeResponse([], status=401))
    with pytest.raises(ValueError, match="rejected the API key"):
        get_adapter("sonarr_api").fetch_series(CONFIG)
    _fake_get(monkeypatch, FakeResponse({"message": "nope"}))
    with pytest.raises(ValueError, match="unexpected series response"):
        get_adapter("sonarr_api").fetch_series(CONFIG)


def test_only_sonarr_lists_series():
    assert get_adapter("sonarr_api").lists_series is True
    assert get_adapter("radarr_api").lists_series is False
    with pytest.raises(NotImplementedError):
        get_adapter("radarr_api").fetch_series(CONFIG)


# ── snapshot store ──────────────────────────────────────────────────────────

class RecordingCursor:
    def __init__(self, one=None):
        self.executed, self._one, self.rowcount = [], list(one or []), 0

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def fetchone(self):
        return self._one.pop(0) if self._one else None


def test_store_series_replaces_the_connections_rows():
    cur = RecordingCursor()
    rows = [arr.sonarr_series(_series()), arr.sonarr_series(_series(id=14, title="Andor", tmdbId=83867))]
    assert cal.store_series(cur, "hh", "conn", rows) == 2
    assert cur.executed[0][0].startswith("DELETE FROM arr_series") and cur.executed[0][1] == ("conn",)
    inserts = [e for e in cur.executed if e[0].startswith("INSERT INTO arr_series")]
    assert len(inserts) == 2 and inserts[0][1][:2] == ["hh", "conn"]
    assert inserts[0][0].count("%s") == len(inserts[0][1])


def test_store_series_with_nothing_still_clears_old_rows():
    cur = RecordingCursor()
    assert cal.store_series(cur, "hh", "conn", []) == 0
    assert len(cur.executed) == 1


# ── refresh: the calendar and the series fail independently ─────────────────

class FakeAdapter:
    def __init__(self, calendar=None, series=None, lists_series=True):
        self.lists_series, self._calendar, self._series = lists_series, calendar, series

    def fetch_calendar(self, config, start, end):
        if isinstance(self._calendar, Exception):
            raise self._calendar
        return self._calendar

    def fetch_series(self, config):
        if isinstance(self._series, Exception):
            raise self._series
        return self._series


@pytest.fixture
def refresh(monkeypatch):
    """Run refresh_calendar with a fake adapter and a recording database."""
    log = []

    class Cur(RecordingCursor):
        def execute(self, sql, params=None):
            log.append((sql.split("(")[0].split(" WHERE")[0].strip()[:40], params))

    @contextlib.contextmanager
    def fake_connection():
        class Conn:
            @contextlib.contextmanager
            def cursor(self):
                yield Cur()
        yield Conn()

    monkeypatch.setattr(cal, "connection", fake_connection)

    def run(adapter):
        monkeypatch.setattr(cal, "get_adapter", lambda _id: adapter)
        conn = {"adapter": "x", "config": {}, "household_id": "hh", "id": "conn"}
        return conn, log
    return run


def _status(log):
    return [p[0] for s, p in log if s.startswith("UPDATE source_connections")][-1]


def _statements(log):
    return [s for s, _ in log]


def test_refresh_stores_both_parts_and_reports_both(refresh):
    conn, log = refresh(FakeAdapter(calendar=[{"external_key": "e:1"}], series=[{"sonarr_id": 1}]))
    out = cal.refresh_calendar(conn)
    assert out == {"calendar": 1, "inserted": 0, "duplicates": 0, "series": 1}
    assert _status(log) == "ok: 1 ready to watch, 1 running series"
    assert any(s.startswith("DELETE FROM calendar_items") for s in _statements(log))
    assert any(s.startswith("DELETE FROM arr_series") for s in _statements(log))


def test_a_failing_series_call_does_not_wipe_the_calendar(refresh):
    conn, log = refresh(FakeAdapter(calendar=[{"external_key": "e:1"}], series=ValueError("Sonarr is down")))
    with pytest.raises(ValueError, match="Sonarr is down"):
        cal.refresh_calendar(conn)
    assert any(s.startswith("DELETE FROM calendar_items") for s in _statements(log))   # calendar stored
    assert not any(s.startswith("DELETE FROM arr_series") for s in _statements(log))   # snapshot untouched
    assert _status(log) == "error: series: Sonarr is down"


def test_a_failing_calendar_does_not_stop_the_series(refresh):
    conn, log = refresh(FakeAdapter(calendar=ValueError("calendar broke"), series=[{"sonarr_id": 1}]))
    with pytest.raises(ValueError, match="calendar broke"):
        cal.refresh_calendar(conn)
    assert any(s.startswith("DELETE FROM arr_series") for s in _statements(log))
    assert not any(s.startswith("DELETE FROM calendar_items") for s in _statements(log))
    assert _status(log) == "error: calendar broke"      # the calendar keeps its plain message


def test_both_failing_reports_both_and_raises_the_first(refresh):
    conn, log = refresh(FakeAdapter(calendar=ValueError("a"), series=ValueError("b")))
    with pytest.raises(ValueError, match="^a$"):
        cal.refresh_calendar(conn)
    assert _status(log) == "error: a; series: b"


def test_radarr_only_refreshes_the_calendar(refresh):
    conn, log = refresh(FakeAdapter(calendar=[], lists_series=False))
    assert cal.refresh_calendar(conn) == {"calendar": 0, "inserted": 0, "duplicates": 0}
    assert _status(log) == "ok: 0 ready to watch"
    assert not any("arr_series" in s for s in _statements(log))


# ── catalog helper ──────────────────────────────────────────────────────────

def _cur(*rows):
    return RecordingCursor(one=list(rows))


def test_series_helper_reuses_a_series_with_the_same_tmdb_id():
    cur = _cur({"id": "t1"})
    assert catalog.get_or_create_series_by_tmdb(cur, 95396, "Severance", 2022) == ("t1", False)
    assert len(cur.executed) == 1


def test_series_helper_gives_a_plex_row_without_tmdb_id_its_tmdb_id_instead_of_a_duplicate():
    cur = _cur(None, {"id": "plex-row", "tmdb_id": None})
    assert catalog.get_or_create_series_by_tmdb(cur, 95396, "Severance (2022)", 2022) == ("plex-row", False)
    update = cur.executed[-1]
    assert update[0].startswith("UPDATE titles SET tmdb_id") and update[1] == (95396, "plex-row")
    assert cur.executed[1][1] == ("severance",)       # looked up by the year-less key


def test_series_helper_creates_a_new_series_with_the_title_key():
    cur = _cur(None, None, {"id": "new"})
    assert catalog.get_or_create_series_by_tmdb(cur, 83867, "Andor", 2022) == ("new", True)
    insert = cur.executed[-1]
    assert "INSERT INTO titles" in insert[0] and "ON CONFLICT DO NOTHING" in insert[0]
    assert insert[1] == ("Andor", 2022, 83867, "andor")


def test_series_helper_never_merges_a_remake_with_the_original():
    # Same name, different TMDB id: the new row's key is disambiguated, the old row untouched.
    cur = _cur(None, {"id": "orig", "tmdb_id": 111}, {"id": "remake"})
    assert catalog.get_or_create_series_by_tmdb(cur, 222, "Battlestar Galactica", 2004) == ("remake", True)
    assert cur.executed[-1][1] == ("Battlestar Galactica", 2004, 222, "battlestar galactica 2004")
    assert not any(s.startswith("UPDATE titles") for s, _ in cur.executed)


def test_series_helper_falls_back_to_the_tmdb_id_when_the_year_key_is_taken_too():
    cur = _cur(None, {"id": "orig", "tmdb_id": 111}, None, {"id": "remake"})
    assert catalog.get_or_create_series_by_tmdb(cur, 222, "Show", 2004) == ("remake", True)
    assert cur.executed[-1][1][3] == "show tmdb 222"


def test_series_helper_recovers_from_a_lost_race():
    cur = _cur(None, None, None, {"id": "winner"})       # insert returned nothing; re-select finds it
    assert catalog.get_or_create_series_by_tmdb(cur, 83867, "Andor", 2022) == ("winner", False)


# ── list entry ──────────────────────────────────────────────────────────────

def test_series_view_flags_a_series_without_tmdb_id_as_not_taggable():
    base = {"sonarr_id": 12, "title": "Severance", "year": 2022, "network": "Apple TV+",
            "poster_url": "https://x/sev.jpg", "next_airing": dt.datetime(2026, 11, 7, tzinfo=UTC),
            "tmdb_id": None, "season_count": 2, "episode_file_count": 18, "total_episode_count": 19,
            "title_id": None, "poster_path": None}
    view = series_view(base, [])
    assert view["taggable"] is False and view["title_id"] is None and view["tags"] == []
    assert view["poster"] == "https://x/sev.jpg" and view["next_airing"].startswith("2026-11-07")
    assert (view["episodes_have"], view["episodes_total"]) == (18, 19)


def test_series_view_prefers_the_catalog_poster_and_links_the_title():
    view = series_view({"sonarr_id": 12, "title": "S", "year": None, "network": None,
                        "poster_url": "https://x/arr.jpg", "next_airing": None, "tmdb_id": 95396,
                        "season_count": None, "episode_file_count": None, "total_episode_count": None,
                        "title_id": "t-1", "poster_path": "/sev.jpg"},
                       [{"id": "tag-1", "name": "Follow", "color": "#f0a21a"}])
    assert view["taggable"] is True and view["title_id"] == "t-1"
    assert view["poster"].endswith("/sev.jpg") and "image.tmdb.org" in view["poster"]
    assert view["tags"][0]["name"] == "Follow"
