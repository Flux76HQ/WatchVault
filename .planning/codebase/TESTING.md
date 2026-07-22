# Testing Patterns

**Analysis Date:** 2026-07-21

## Test Framework

**Runner:**
- pytest `>=8.0`, declared in `backend/requirements-dev.txt`.
- Config: Not detected; there is no `pytest.ini`, `pyproject.toml`, `setup.cfg`, or `tox.ini`.
- Observed baseline: `153 passed` for `backend/tests/` on 2026-07-21.
- Frontend test runner: Not detected. `frontend/package.json` contains development, build, and preview scripts only.

**Assertion Library:**
- Native Python `assert` statements plus `pytest.raises`, as used in `backend/tests/test_stats.py` and `backend/tests/test_adapters.py`.
- Flask's test client supplies response/status/JSON assertions in `backend/tests/test_profiles.py` and `backend/tests/test_scrobble.py`.

**Run Commands:**
```bash
python -m pytest backend/tests                    # Run all backend tests
python -m pytest backend/tests/test_scrobble.py -v # Run one behavior area verbosely
# Watch mode: not configured
# Coverage command: not configured
```

Install both runtime and test dependencies before running the suite:

```bash
python -m pip install -r backend/requirements.txt -r backend/requirements-dev.txt
```

The frontend's available static quality gate is:

```bash
cd frontend
npm install
npm run build   # Type-check with tsc -b, then bundle with Vite
```

## Test File Organization

**Location:**
- Keep Python tests in the separate `backend/tests/` package rather than co-locating them with implementation modules.
- `backend/tests/__init__.py` is empty; test discovery relies on pytest naming.
- Keep reusable static import samples in `sample-data/`; `backend/tests/test_adapters.py` reads `sample-data/netflix-viewing-activity.csv`, `sample-data/hbomax-generic.csv`, and `sample-data/videoland-generic.json`.
- Frontend tests are not present under `frontend/src/` or a separate frontend test directory.

**Naming:**
- Name files `test_<area>.py`, such as `backend/tests/test_networks.py`, `backend/tests/test_progress.py`, and `backend/tests/test_metadata.py`.
- Name test functions `test_<expected_behavior>`, such as `test_range_clause_whitelists_known_ranges` in `backend/tests/test_stats.py`.
- Name local test doubles `FakeCursor`, `_FakeConn`, `_FakeResp`, or behavior-specific variants such as `SmartCursor` in `backend/tests/test_scrobble.py`.
- Prefix non-test builders and helpers with `_`, such as `_load()` in `backend/tests/test_adapters.py`, `_patch()` in `backend/tests/test_networks.py`, and `_new_movie_event()` in `backend/tests/test_scrobble.py`.

**Structure:**
```text
backend/tests/
├── __init__.py
├── test_adapters.py
├── test_add_film.py
├── test_delete_title.py
├── test_metadata.py
├── test_networks.py
├── test_profiles.py
├── test_progress.py
├── test_resolve_title.py
├── test_scrobble.py
├── test_set_kind.py
├── test_stats.py
└── test_title_key.py
```

## Test Structure

**Suite Organization:**
```python
"""Tests for one behavior area — no database or network."""
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.ingest.adapters import get_adapter  # noqa: E402


def test_invalid_configuration_raises():
    with pytest.raises(ValueError):
        get_adapter("trakt_api").fetch_history({"username": "me"}, {})
```

This pattern is used in `backend/tests/test_adapters.py`; files that do not need pytest helpers omit the `pytest` import.

**Patterns:**
- Start each substantial test module with a docstring that states the feature and whether the suite needs a live database/network, as in `backend/tests/test_scrobble.py` and `backend/tests/test_delete_title.py`.
- Bootstrap imports consistently by deriving repository `ROOT`, adding `backend/` to `sys.path`, then importing `app` modules with `# noqa: E402`.
- Group related scenarios with section comments in longer files, especially `backend/tests/test_progress.py` and `backend/tests/test_scrobble.py`.
- Follow arrange-act-assert without dedicated setup methods: build input/fake state, call one public or focused private helper, then assert return values and recorded side effects.
- Verify behavior rather than implementation alone, but inspect SQL shape/parameters when the contract is transaction, deduplication, attribution, or merge behavior.
- No suite-level teardown is normally required because tests avoid live services and construct fresh local doubles per test.

## Mocking

**Framework:** pytest's built-in `monkeypatch` fixture plus handwritten fakes; no standalone mocking package is declared.

**Patterns:**
```python
def test_plex_library_filter(monkeypatch):
    from app.ingest.adapters import plex
    xml = b'<MediaContainer><Video type="movie" title="Kept"/></MediaContainer>'
    monkeypatch.setattr(
        plex.requests,
        "get",
        lambda *args, **kwargs: _FakeResp(content=xml),
    )

    events, _ = plex.PlexAdapter().fetch_history(
        {"base_url": "http://x", "token": "t"},
        {},
    )
    assert [event.clean_title for event in events] == ["Kept"]
```

The network replacement pattern appears throughout `backend/tests/test_adapters.py` and `backend/tests/test_metadata.py`.

For transaction-heavy code, provide a cursor that records SQL and replays rows:

```python
class FakeCursor:
    def __init__(self, rows):
        self._rows = list(rows)
        self.executed = []

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def fetchone(self):
        return self._rows.pop(0) if self._rows else None
```

Variants of this pattern are used in `backend/tests/test_add_film.py`, `backend/tests/test_progress.py`, and `backend/tests/test_resolve_title.py`.

**What to Mock:**
- Patch HTTP at the imported module boundary (`plex.requests.get`, `trakt.requests.get`) so adapter parsing and request construction remain real; see `backend/tests/test_adapters.py`.
- Patch the symbol used by the code under test, such as `networks.connection` in `backend/tests/test_networks.py` or `manual.connection` in `backend/tests/test_delete_title.py`.
- Use fake cursor/connection context managers to verify SQL ordering, parameters, commit-path decisions, deduplication, and transaction reuse without PostgreSQL.
- Patch auth/session resolution and query helpers for DB-free endpoint checks, as in `backend/tests/test_scrobble.py`.

**What NOT to Mock:**
- Do not mock pure normalization and decision helpers; call them directly with representative values, following `backend/tests/test_title_key.py`, `backend/tests/test_stats.py`, and the parser sections of `backend/tests/test_scrobble.py`.
- Do not mock bundled sample file bytes when the adapter's file parsing is under test; read from `sample-data/` through `_load()` in `backend/tests/test_adapters.py`.
- Do not replace Flask routing for lightweight boundary checks; create the real app with `create_app().test_client()` and avoid authenticated DB paths unless dependencies are patched.

## Fixtures and Factories

**Test Data:**
```python
def _plex_movie(event="media.play", offset=300_000, duration=600_000):
    return {
        "event": event,
        "Account": {"title": "Dad"},
        "Metadata": {
            "type": "movie",
            "title": "Dune: Part Two",
            "duration": duration,
            "viewOffset": offset,
        },
    }
```

Use small local builders like `_plex_movie()` and `_new_movie_event()` in `backend/tests/test_scrobble.py` when many tests vary a few fields.

**Location:**
- There is no `conftest.py` and no shared pytest fixture package.
- Keep behavior-specific builders and fake classes in the test module that owns them.
- Keep cross-adapter export samples in `sample-data/`; do not embed large real-world exports in test code.
- Use constants near the top of a module for stable domain identifiers/timestamps, as in `backend/tests/test_networks.py` and `backend/tests/test_progress.py`.

## Coverage

**Requirements:** None enforced. No coverage threshold, `.coveragerc`, pytest-cov dependency, or coverage script is present in `backend/requirements-dev.txt` or `frontend/package.json`.

**View Coverage:**
```bash
# Not configured. Add pytest-cov before using:
# python -m pytest backend/tests --cov=backend/app --cov=plugins --cov-report=term-missing
```

Do not treat the commented command as currently available; `pytest-cov` is not declared in `backend/requirements-dev.txt`.

## Test Types

**Unit Tests:**
- This is the dominant test type. Pure parsing, title normalization, metadata mapping, status decisions, provider attribution, and API serialization are tested directly in `backend/tests/test_adapters.py`, `backend/tests/test_title_key.py`, `backend/tests/test_metadata.py`, `backend/tests/test_progress.py`, and `backend/tests/test_stats.py`.
- SQL-aware unit tests exercise catalog and ingest branches against fake cursors in `backend/tests/test_add_film.py`, `backend/tests/test_delete_title.py`, `backend/tests/test_resolve_title.py`, and `backend/tests/test_set_kind.py`.

**Integration Tests:**
- Lightweight Flask boundary tests instantiate the real application and test client for unauthenticated responses or patched dependencies in `backend/tests/test_profiles.py` and `backend/tests/test_scrobble.py`.
- No test connects to a live PostgreSQL instance or external provider. Multi-statement flows are integration-like but remain in-memory through fake cursor/connection implementations.

**E2E Tests:**
- Not used. No Playwright, Cypress, Selenium, browser test directory, or frontend component test framework is present.

**Frontend Tests:**
- Not used. `frontend/package.json` declares no test script or test dependency.
- TypeScript strict compilation through `npm run build` is the only frontend code validation currently configured.

**CI Automation:**
- `.github/workflows/docker.yml` builds and publishes the Docker image but does not run pytest explicitly.
- The Docker build executes `npm run build` through `Dockerfile`, so frontend type/build failures can block image creation; backend tests are not part of that image build.

## Common Patterns

**Async Testing:**
```python
# Not applicable: the current pytest suite and Flask application paths are synchronous.
```

HTTP-provider tests use synchronous fake `requests` responses in `backend/tests/test_adapters.py`; React asynchronous behavior has no automated tests.

**Error Testing:**
```python
def test_trakt_fetch_title_history_requires_token():
    with pytest.raises(ValueError):
        TraktAdapter().fetch_title_history(
            {"client_id": "c"},
            {"kind": "series", "tmdb_id": 1, "external_ids": {}},
        )
```

Use `pytest.raises(..., match="...")` when the message is part of the user-facing contract, as in `backend/tests/test_adapters.py`. For API guards, assert status codes and optionally parsed JSON:

```python
client = create_app().test_client()
response = client.post("/api/scrobble/generic", json={"title": "X", "event": "play"})
assert response.status_code == 401
```

This boundary pattern appears in `backend/tests/test_scrobble.py` and `backend/tests/test_profiles.py`.

**Regression Testing:**
- Document the original failure mode in a comment or module docstring, then pin the behavioral contract. Examples include Decimal JSON serialization in `backend/tests/test_stats.py`, transaction self-deadlock prevention in `backend/tests/test_scrobble.py`, and cross-kind title reconciliation in `backend/tests/test_resolve_title.py`.
- Assert both the returned result and the forbidden side effect when preventing a regression, such as “no second connection,” “no duplicate insert,” or “no merge call.”

---

*Testing analysis: 2026-07-21*
