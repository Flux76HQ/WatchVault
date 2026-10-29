"""The "What's next" block rules -- pure, no database."""
import datetime as dt
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.whats_next import build_whats_next  # noqa: E402

UTC = dt.timezone.utc
TODAY = dt.date(2026, 10, 29)
D = dt.date
TAG_A = {"id": "ta", "name": "Anime", "color": "#f00"}
TAG_B = {"id": "tb", "name": "Binge", "color": None}


def series(tid, title="Show", tags=(TAG_A,), tmdb=100, next_airing=None, **over):
    row = {"title_id": tid, "title": title, "year": 2024, "tmdb_id": tmdb, "poster_path": None,
           "tags": list(tags), "next_airing": next_airing, "sonarr_poster": None}
    row.update(over)
    return row


def ep(tid, s, e, air, name=None):
    return {"title_id": tid, "season": s, "episode": e, "name": name or f"E{e}", "air_date": air,
            "runtime_minutes": 45}


def run(series_rows, episodes=(), watched=None, ready=(), **kw):
    return build_whats_next(list(series_rows), list(episodes), watched or {}, list(ready),
                            today=TODAY, **kw)


def only(result):
    assert len(result["items"]) == 1
    return result["items"][0]


def test_untagged_series_is_ignored():
    assert run([series("a", tags=())], [ep("a", 1, 1, D(2026, 1, 1))])["items"] == []


def test_next_unwatched_episode_is_aired():
    eps = [ep("a", 1, n, D(2026, 10, n)) for n in (1, 2, 3)]
    item = only(run([series("a")], eps, {"a": {(1, 1)}}))
    assert item["state"] == "aired" and (item["season"], item["episode"]) == (1, 2)
    assert item["behind"] == 1                      # episode 3 waits behind it
    assert item["air_date"] == "2026-10-02" and item["kind"] == "series"


def test_anyone_watched_counts_and_season_zero_is_ignored():
    eps = [ep("a", 0, 1, D(2026, 1, 1)), ep("a", 1, 1, D(2026, 10, 1)), ep("a", 1, 2, D(2026, 10, 2))]
    item = only(run([series("a")], eps, {"a": {(1, 1)}}))
    assert (item["season"], item["episode"]) == (1, 2)
    # only the special left unwatched -> nothing to watch, nothing coming
    assert run([series("a")], eps, {"a": {(1, 1), (1, 2)}})["items"] == []


def test_ready_when_sonarr_has_the_file():
    eps = [ep("a", 1, 1, D(2026, 10, 20)), ep("a", 1, 2, D(2026, 10, 21))]
    got = dt.datetime(2026, 10, 25, 9, tzinfo=UTC)
    ready = [{"tmdb_id": 100, "season": 1, "episode": 1, "available_at": got},
             {"tmdb_id": 999, "season": 1, "episode": 1, "available_at": got}]
    item = only(run([series("a")], eps, ready=ready))
    assert item["state"] == "ready" and item["available_at"] == got.isoformat()
    assert item["behind"] == 1
    # a file for another episode does not make this one ready
    other = [{"tmdb_id": 100, "season": 1, "episode": 2, "available_at": got}]
    assert only(run([series("a")], eps, ready=other))["state"] == "aired"


def test_upcoming_future_and_unknown_dates():
    eps = [ep("a", 2, 1, D(2026, 11, 5))]
    na = dt.datetime(2026, 11, 5, 20, tzinfo=UTC)
    item = only(run([series("a", next_airing=na)], eps, {"a": set()}))
    assert item["state"] == "upcoming" and item["air_date"] == "2026-11-05"
    assert item["air_at"] == na.isoformat()
    # today is not "future": an episode airing today counts as aired
    assert only(run([series("a")], [ep("a", 2, 1, TODAY)]))["state"] == "aired"
    # no date on the episode: Sonarr's next airing supplies it
    item = only(run([series("a", next_airing=na)], [ep("a", 2, 1, None)]))
    assert item["state"] == "upcoming" and item["air_date"] == "2026-11-05"
    # no date anywhere: still upcoming, undated
    item = only(run([series("a")], [ep("a", 2, 1, None)]))
    assert item["state"] == "upcoming" and item["air_date"] is None


def test_caught_up_needs_a_future_airing():
    eps = [ep("a", 1, 1, D(2026, 10, 1))]
    seen = {"a": {(1, 1)}}
    assert run([series("a")], eps, seen)["items"] == []
    past = dt.datetime(2026, 10, 1, tzinfo=UTC)
    assert run([series("a", next_airing=past)], eps, seen)["items"] == []
    na = dt.datetime(2026, 11, 3, 20, tzinfo=UTC)
    item = only(run([series("a", next_airing=na)], eps, seen))
    assert item["state"] == "caught_up" and item["air_date"] == "2026-11-03"
    assert item["season"] is None and item["episode"] is None


def test_pending_when_the_catalog_has_no_episodes():
    na = dt.datetime(2026, 11, 3, 20, tzinfo=UTC)
    item = only(run([series("a", next_airing=na, sonarr_poster="https://x/p.jpg")]))
    assert item["state"] == "pending" and item["air_date"] == "2026-11-03"
    assert item["poster"] == "https://x/p.jpg"
    assert only(run([series("a")]))["air_date"] is None
    # only specials -> still pending
    assert only(run([series("a")], [ep("a", 0, 1, D(2026, 1, 1))]))["state"] == "pending"


def test_poster_prefers_the_catalog_one():
    row = series("a", poster_path="/c.jpg", sonarr_poster="https://x/p.jpg")
    assert only(run([row], poster=lambda p: f"img{p}" if p else None))["poster"] == "img/c.jpg"


def test_ordering_across_states():
    got_old, got_new = dt.datetime(2026, 10, 20, tzinfo=UTC), dt.datetime(2026, 10, 25, tzinfo=UTC)
    rows = [series(t, title=t.upper(), tmdb=i) for i, t in enumerate("abcdefg", 1)]
    eps = [ep("a", 1, 1, D(2026, 10, 1)),      # ready (old)
           ep("b", 1, 1, D(2026, 10, 1)),      # ready (new)
           ep("c", 1, 1, D(2026, 10, 10)),     # aired, older
           ep("d", 1, 1, D(2026, 10, 20)),     # aired, newer
           ep("e", 1, 1, D(2026, 12, 1)),      # upcoming, later
           ep("f", 1, 1, D(2026, 11, 1))]      # upcoming, sooner
    ready = [{"tmdb_id": 1, "season": 1, "episode": 1, "available_at": got_old},
             {"tmdb_id": 2, "season": 1, "episode": 1, "available_at": got_new}]
    out = run(rows, eps, ready=ready)           # g: pending
    assert [i["title_id"] for i in out["items"]] == ["b", "a", "d", "c", "f", "e", "g"]


def test_ties_break_on_title_then_id():
    rows = [series("2", title="beta", tmdb=2), series("1", title="Beta", tmdb=1),
            series("3", title="alpha", tmdb=3)]
    eps = [ep(r["title_id"], 1, 1, D(2026, 10, 1)) for r in rows]
    assert [i["title_id"] for i in run(rows, eps)["items"]] == ["3", "1", "2"]


def test_tag_filter_and_stable_counts():
    rows = [series("a", tags=(TAG_A,), tmdb=1), series("b", tags=(TAG_A, TAG_B), tmdb=2),
            series("c", tags=(TAG_B,), tmdb=3)]
    eps = [ep(r["title_id"], 1, 1, D(2026, 10, 1)) for r in rows]
    everything = run(rows, eps)
    assert [(t["id"], t["count"]) for t in everything["tags"]] == [("ta", 2), ("tb", 2)]
    only_a = run(rows, eps, tag="ta")
    assert sorted(i["title_id"] for i in only_a["items"]) == ["a", "b"]
    assert only_a["tags"] == everything["tags"]          # chips do not move when filtering
    assert run(rows, eps, tag="someone-elses")["items"] == []


def test_tag_counts_ignore_series_that_show_nothing():
    rows = [series("a", tags=(TAG_A,)), series("b", tags=(TAG_B,), tmdb=2)]
    eps = [ep("a", 1, 1, D(2026, 10, 1)), ep("b", 1, 1, D(2026, 10, 1))]
    out = run(rows, eps, {"b": {(1, 1)}})               # b is caught up, nothing coming
    assert [t["id"] for t in out["tags"]] == ["ta"]


def test_limit():
    rows = [series(str(i), title=f"s{i:02}", tmdb=i) for i in range(5)]
    eps = [ep(r["title_id"], 1, 1, D(2026, 10, 1)) for r in rows]
    out = run(rows, eps, limit=3)
    assert len(out["items"]) == 3 and out["tags"][0]["count"] == 5


def test_item_shape():
    item = only(run([series("a")], [ep("a", 1, 1, D(2026, 10, 1), name="Pilot")]))
    assert set(item) == {"key", "title_id", "title", "year", "kind", "poster", "tags", "state",
                         "season", "episode", "episode_name", "air_date", "air_at", "available_at",
                         "behind", "runtime_minutes"}
    assert item["key"] == "w:a" and item["episode_name"] == "Pilot" and item["runtime_minutes"] == 45
    assert item["tags"] == [{"id": "ta", "name": "Anime", "color": "#f00"}]
