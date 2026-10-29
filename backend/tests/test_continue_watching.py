"""Sonarr/Radarr calendar + "Continue watching" tests — no database or network.

The adapters are driven with a faked ``requests.get``; the merge rules of
``build_continue`` (partial playback + ready-to-watch calendar items) run on plain
dicts; the calendar store is checked with a recording fake cursor."""
import datetime as dt
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.continue_watching import build_continue, clamp_days  # noqa: E402
from app.ingest.adapters import get_adapter, arr  # noqa: E402
from app.ingest.calendar import DEFAULT_DAYS, MAX_DAYS, store_calendar, window  # noqa: E402

UTC = dt.timezone.utc


# ── Sonarr / Radarr normalisation ───────────────────────────────────────────

def _episode(**over):
    raw = {
        "id": 11, "seasonNumber": 2, "episodeNumber": 5, "title": "The Reckoning",
        "airDateUtc": "2026-10-20T01:00:00Z", "hasFile": True,
        "episodeFile": {"dateAdded": "2026-10-21T08:30:00Z"}, "runtime": 52,
        "series": {"title": "Severance", "year": 2022, "tmdbId": 95396, "tvdbId": 371980,
                   "imdbId": "tt11280740",
                   "images": [{"coverType": "fanart", "remoteUrl": "https://x/fan.jpg"},
                              {"coverType": "poster", "remoteUrl": "https://x/poster.jpg",
                               "url": "/MediaCover/1/poster.jpg"}]},
    }
    raw.update(over)
    return raw


def test_sonarr_item_maps_an_episode_with_a_file():
    item = arr.sonarr_item(_episode())
    assert item["source"] == "sonarr" and item["kind"] == "series"
    assert item["external_key"] == "e:11"
    assert (item["title"], item["season"], item["episode"]) == ("Severance", 2, 5)
    assert item["episode_name"] == "The Reckoning"
    assert item["tmdb_id"] == 95396 and item["tvdb_id"] == 371980
    assert item["poster_url"] == "https://x/poster.jpg"        # remote copy, not the relative url
    assert item["available_at"] == dt.datetime(2026, 10, 21, 8, 30, tzinfo=UTC)
    assert item["air_date"] == dt.date(2026, 10, 20)


def test_sonarr_item_skips_episodes_without_a_file_or_a_series():
    assert arr.sonarr_item(_episode(hasFile=False)) is None
    assert arr.sonarr_item(_episode(series={})) is None


def test_sonarr_item_falls_back_to_the_air_date_and_ignores_zero_ids():
    raw = _episode(episodeFile={})
    raw["series"]["tmdbId"] = 0
    item = arr.sonarr_item(raw)
    assert item["available_at"] == dt.datetime(2026, 10, 20, 1, 0, tzinfo=UTC)
    assert item["tmdb_id"] is None


def test_radarr_item_maps_a_movie_with_a_file():
    item = arr.radarr_item({
        "id": 7, "title": "Arrival", "year": 2016, "tmdbId": 329865, "imdbId": "tt2543164",
        "hasFile": True, "movieFile": {"dateAdded": "2026-10-25T19:00:00Z"}, "runtime": 116,
        "digitalRelease": "2026-10-10T00:00:00Z",
        "images": [{"coverType": "poster", "remoteUrl": "https://x/arrival.jpg"}],
    })
    assert item["source"] == "radarr" and item["kind"] == "movie"
    assert item["external_key"] == "m:7" and item["season"] is None
    assert item["tmdb_id"] == 329865 and item["poster_url"] == "https://x/arrival.jpg"
    assert item["available_at"] == dt.datetime(2026, 10, 25, 19, 0, tzinfo=UTC)
    assert arr.radarr_item({"id": 8, "title": "No file", "hasFile": False}) is None


# ── fetch_calendar over a faked HTTP layer ──────────────────────────────────

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
START, END = dt.date(2026, 10, 14), dt.date(2026, 10, 29)


def test_sonarr_fetch_calendar_sends_the_key_and_dedupes(monkeypatch):
    calls = _fake_get(monkeypatch, FakeResponse([_episode(), _episode(), _episode(id=12, hasFile=False)]))
    items = get_adapter("sonarr_api").fetch_calendar(CONFIG, START, END)
    assert [i["external_key"] for i in items] == ["e:11"]
    call = calls[0]
    assert call["url"] == "http://sonarr:8989/api/v3/calendar"
    assert call["headers"]["X-Api-Key"] == "k3y"
    assert call["params"]["start"] == "2026-10-14" and call["params"]["end"] == "2026-10-29"
    assert call["params"]["includeSeries"] == "true" and call["params"]["includeEpisodeFile"] == "true"


def test_radarr_fetch_calendar_does_not_ask_for_series(monkeypatch):
    calls = _fake_get(monkeypatch, FakeResponse([]))
    assert get_adapter("radarr_api").fetch_calendar(CONFIG, START, END) == []
    assert "includeSeries" not in calls[0]["params"]


def test_fetch_calendar_reports_a_rejected_key_and_a_bad_response(monkeypatch):
    _fake_get(monkeypatch, FakeResponse({}, status=401))
    with pytest.raises(ValueError, match="rejected the API key"):
        get_adapter("sonarr_api").fetch_calendar(CONFIG, START, END)
    _fake_get(monkeypatch, FakeResponse({"error": "x"}))
    with pytest.raises(ValueError, match="unexpected calendar response"):
        get_adapter("sonarr_api").fetch_calendar(CONFIG, START, END)
    with pytest.raises(ValueError, match="requires base_url and api_key"):
        get_adapter("radarr_api").fetch_calendar({}, START, END)


def test_calendar_adapters_are_marked_and_history_adapters_are_not():
    assert get_adapter("sonarr_api").produces == "calendar"
    assert get_adapter("radarr_api").produces == "calendar"
    assert get_adapter("plex_api").produces == "history"
    with pytest.raises(NotImplementedError):
        get_adapter("sonarr_api").fetch_history({}, {})


# ── the calendar window and its store ───────────────────────────────────────

def test_window_covers_the_longest_selectable_period_up_to_tomorrow():
    start, end = window(dt.date(2026, 10, 28))
    assert MAX_DAYS == 30
    assert start == dt.date(2026, 9, 28)
    assert end == dt.date(2026, 10, 29)


def test_clamp_days_keeps_the_setting_in_range_and_defaults_garbage():
    assert [clamp_days(v) for v in (0, 1, 14, 30, 31, 999, -5, "7", 7.9)] == [0, 1, 14, 30, 30, 30, 0, 7, 7]
    assert clamp_days(None) == DEFAULT_DAYS == 14
    assert clamp_days("abc") == DEFAULT_DAYS
    assert clamp_days("") == DEFAULT_DAYS


class RecordingCursor:
    def __init__(self):
        self.executed = []

    def execute(self, sql, params=None):
        self.executed.append((sql, params))


def test_store_calendar_replaces_the_connections_rows():
    cur = RecordingCursor()
    items = [arr.sonarr_item(_episode()), arr.radarr_item(
        {"id": 7, "title": "Arrival", "hasFile": True, "movieFile": {"dateAdded": "2026-10-25T19:00:00Z"}})]
    assert store_calendar(cur, "hh", "conn", items) == 2
    assert cur.executed[0][0].startswith("DELETE FROM calendar_items") and cur.executed[0][1] == ("conn",)
    inserts = [e for e in cur.executed if e[0].startswith("INSERT INTO calendar_items")]
    assert len(inserts) == 2 and inserts[0][1][:2] == ["hh", "conn"]
    assert "ON CONFLICT (connection_id, external_key) DO NOTHING" in inserts[0][0]
    # Placeholders and values line up: 2 ids + one per column.
    assert inserts[0][0].count("%s") == len(inserts[0][1])


def test_store_calendar_with_no_items_still_clears_old_rows():
    cur = RecordingCursor()
    assert store_calendar(cur, "hh", "conn", []) == 0
    assert len(cur.executed) == 1 and cur.executed[0][0].startswith("DELETE")


# ── merging partial playback and ready items ────────────────────────────────

NOW = dt.datetime(2026, 10, 28, 20, 0, tzinfo=UTC)


def _partial(i, **over):
    row = {"id": f"s{i}", "user_id": "u1", "source": "plex", "kind": "series", "raw_title": "Severance",
           "season": 2, "episode": 3, "episode_name": "Who Is Alive?", "progress_percent": 40,
           "duration_seconds": 3000, "updated_at": NOW - dt.timedelta(hours=i), "title_id": "t-sev",
           "t_title": "Severance", "poster_path": "/sev.jpg", "runtime_minutes": 50,
           "provider_key": "plex", "provider_name": "Plex", "provider_color": "#E5A00D",
           "profile_name": "Helmer"}
    row.update(over)
    return row


def _ready(i, **over):
    row = {"id": f"c{i}", "source": "sonarr", "kind": "series", "external_key": f"e:{i}",
           "title": "Andor", "year": 2022, "season": 2, "episode": i, "episode_name": None,
           "tmdb_id": 83867, "poster_url": "https://x/andor.jpg", "runtime_minutes": 45,
           "available_at": NOW - dt.timedelta(days=1, hours=i), "title_id": None,
           "t_title": None, "poster_path": None}
    row.update(over)
    return row


def test_partial_playback_shows_progress_and_what_is_left():
    [item] = build_continue([_partial(1)], [], {})
    assert item["origin"] == "partial" and item["progress"] == 40.0
    assert item["remaining_minutes"] == 30          # 60% of 3000 s
    assert (item["season"], item["episode"]) == (2, 3)
    assert item["provider"] == {"key": "plex", "name": "Plex", "color": "#E5A00D"}
    assert item["profile"] == "Helmer" and item["title_id"] == "t-sev"


def test_the_latest_partial_of_the_same_episode_wins_per_profile():
    items = build_continue([_partial(3, progress_percent=10), _partial(1, progress_percent=55),
                            _partial(2, user_id="u2", profile_name="Sam")], [], {})
    assert [(i["profile"], i["progress"]) for i in items] == [("Helmer", 55.0), ("Sam", 40.0)]


def test_ready_series_episodes_collapse_into_one_card_for_the_earliest():
    items = build_continue([], [_ready(3), _ready(1), _ready(2)], {})
    assert len(items) == 1
    card = items[0]
    assert card["origin"] == "ready" and (card["season"], card["episode"]) == (2, 1)
    assert card["more"] == 2
    assert card["poster"] == "https://x/andor.jpg"      # not in the catalog: Sonarr's own poster
    assert card["title_id"] is None                       # so no title page to link to
    assert card["provider"]["key"] == "sonarr"


def test_watched_episodes_and_films_are_left_out():
    ready = [_ready(1, title_id="t-and"), _ready(2, title_id="t-and"),
             _ready(9, kind="movie", season=None, episode=None, external_key="m:9", source="radarr",
                    title="Arrival", title_id="t-arr", tmdb_id=329865)]
    watched = {"t-and": {(2, 1)}, "t-arr": {(0, None)}}
    items = build_continue([], ready, watched)
    assert len(items) == 1
    assert (items[0]["season"], items[0]["episode"], items[0]["more"]) == (2, 2, 0)


def test_a_ready_item_already_shown_as_partial_is_not_repeated():
    partial = _partial(1, title_id="t-and", raw_title="Andor", t_title="Andor", season=2, episode=1)
    items = build_continue([partial], [_ready(1, title_id="t-and"), _ready(2, title_id="t-and")], {})
    assert [i["origin"] for i in items] == ["partial", "ready"]
    assert items[1]["episode"] == 2 and items[1]["more"] == 0


def test_partials_come_first_then_ready_newest_first_and_the_list_is_capped():
    movies = [_ready(i, kind="movie", season=None, episode=None, external_key=f"m:{i}", source="radarr",
                     title=f"Film {i}", tmdb_id=1000 + i, available_at=NOW - dt.timedelta(hours=i))
              for i in range(1, 7)]
    items = build_continue([_partial(1)], movies, {}, limit=4)
    assert [i["origin"] for i in items] == ["partial", "ready", "ready", "ready"]
    assert [i["title"] for i in items[1:]] == ["Film 1", "Film 2", "Film 3"]


def test_catalog_title_and_poster_win_over_the_arr_copy():
    ready = _ready(1, title_id="t-and", t_title="Andor", poster_path="/andor.jpg")
    [card] = build_continue([], [ready], {}, poster=lambda p: f"https://img{p}" if p else None)
    assert card["title_id"] == "t-and" and card["poster"] == "https://img/andor.jpg"
