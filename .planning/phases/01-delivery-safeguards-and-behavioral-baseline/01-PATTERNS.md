# Phase 1: Delivery Safeguards and Behavioral Baseline - Pattern Map

**Mapped:** 2026-07-21
**Files analyzed:** 33 new/modified file targets
**Analogs found:** 25 / 33

## Scope Check

`STATE.md` identifies Phase 1 as the active planning phase. This map covers only DELV-01 through DELV-06: version enforcement, hooks, capability inventory, regression infrastructure, Playwright, and CI. It does not redesign product screens.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `VERSION` | config | transform | `frontend/package.json` | role-match |
| `version-policy.json` | config | transform | — | none |
| `.githooks/pre-commit` | middleware | event-driven | `deploy/entrypoint.sh` | flow-match |
| `scripts/version.mjs` | utility | batch / file-I/O | `backend/app/migrations_runner.py` | role-match |
| `scripts/setup.mjs` | utility | event-driven | `backend/app/migrations_runner.py` | role-match |
| `scripts/ci-changes.mjs` | utility | batch / transform | `backend/app/migrations_runner.py` | role-match |
| `scripts/lib/version-policy.mjs` | utility | transform | `backend/app/migrations_runner.py` | role-match |
| `scripts/tests/version-policy.test.mjs` | test | batch / file-I/O | `backend/tests/test_title_key.py` | role-match |
| `capabilities/schema.json` | config | transform | — | none |
| `capabilities/inventory.json` | model | batch | — | none |
| `docs/CAPABILITIES.md` | config / generated report | batch / file-I/O | — | none |
| `frontend/scripts/capabilities.mjs` | utility | batch / file-I/O | `backend/app/migrations_runner.py` | flow-match |
| `frontend/scripts/capabilities.test.mjs` | test | batch / file-I/O | `backend/tests/test_title_key.py` | role-match |
| `backend/app/version.py` | utility | file-I/O | `backend/app/migrations_runner.py` | flow-match |
| `backend/app/api/meta.py` | controller | request-response | itself | exact |
| `backend/tests/test_meta.py` | test | request-response / file-I/O | `backend/tests/test_profiles.py` | exact |
| `Dockerfile` | config | batch / file-I/O | itself | exact |
| `frontend/package.json` | config | transform | itself | exact |
| `frontend/package-lock.json` | config | transform | itself | exact |
| `frontend/src/test/setup.ts` | config | event-driven | — | none |
| `frontend/src/test/render.tsx` | utility | request-response | `frontend/src/main.tsx` | exact |
| `frontend/src/test/a11y.ts` | utility | transform | — | none |
| `frontend/src/**/*.test.tsx` (representative component tests) | test | event-driven | — | none |
| `frontend/vitest.config.ts` | config | event-driven | `frontend/vite.config.ts` | role-match |
| `frontend/e2e/fixtures/data.ts` | model / fixture | transform | `frontend/src/lib/app.tsx` | role-match |
| `frontend/e2e/fixtures/api.ts` | utility / fixture | request-response / event-driven | `frontend/src/lib/api.ts` | flow-match |
| `frontend/e2e/reference-journey.spec.ts` | test | event-driven / request-response | — | none |
| `frontend/e2e/reference-journey.spec.ts-snapshots/**` | test fixture | file-I/O | `docs/screenshots/{desktop,mobile}/` | role-match |
| `frontend/playwright.config.ts` | config | event-driven | `frontend/vite.config.ts` | role-match |
| `frontend/tsconfig.node.json` | config | transform | itself | exact |
| `.gitignore` | config | transform | itself | exact |
| `.github/workflows/ci.yml` | config | event-driven / batch | `.github/workflows/docker.yml` | role-match |
| `.github/workflows/docker.yml` | config | event-driven / batch | itself | exact |

## Pattern Assignments

### Version policy and repository tooling

**Applies to:** `VERSION`, `version-policy.json`, `.githooks/pre-commit`, `scripts/version.mjs`, `scripts/setup.mjs`, `scripts/ci-changes.mjs`, `scripts/lib/version-policy.mjs`, and `scripts/tests/version-policy.test.mjs`.

**Primary analog:** `backend/app/migrations_runner.py`

**Small pure helper and repository-relative path pattern** (`backend/app/migrations_runner.py:8-16,27-28`):

```python
import hashlib
import pathlib
import sys

MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parent.parent / "migrations"

def _checksum(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
```

Copy the separation of repository path resolution and pure transforms. In the new Node implementation, keep SemVer parsing, path normalization, protected-path classification, comparison, and bump selection in `scripts/lib/version-policy.mjs`; keep Git/process/file adapters in the CLI files.

**Deterministic scan, no-op, and fatal drift pattern** (`backend/app/migrations_runner.py:31-36,47-58`):

```python
files = sorted(MIGRATIONS_DIR.glob("*.sql"))
if not files:
    print("[migrate] no migration files found", flush=True)
    return

for path in files:
    name = path.name
    sql = path.read_text(encoding="utf-8")
    checksum = _checksum(sql)
    if name in applied:
        if applied[name] != checksum:
            raise SystemExit(
                f"[migrate] FATAL: checksum drift on already-applied "
                f"migration {name}. Refusing to start."
            )
        continue
```

Use the same observable shape: sort inputs, explicitly return on a valid no-op, and terminate nonzero on drift. Every version-policy failure must additionally print the exact final remediation command:

```text
node scripts/version.mjs bump
```

**Error handling pattern** (`backend/app/migrations_runner.py:60-73`):

```python
print(f"[migrate] applying {name}", flush=True)
try:
    ...
except Exception as exc:  # noqa: BLE001
    ...
    print(f"[migrate] FAILED on {name}: {exc}", file=sys.stderr, flush=True)
    raise
```

For Node scripts, send diagnostics to stderr, use nonzero exit status, and never build Git commands through shell string concatenation. Use `spawnSync`/`execFileSync` with argument arrays.

**Hook shim analog** (`deploy/entrypoint.sh:1-11`):

```sh
#!/usr/bin/env bash
set -euo pipefail
...
exec supervisord -c /etc/supervisor/conf.d/watchvault.conf
```

The committed hook should be even smaller and POSIX-compatible:

```sh
#!/bin/sh
exec node scripts/version.mjs check --staged
```

Do not copy the Bash-only `set -euo pipefail`; `/bin/sh` plus `exec` is the required portable pattern.

**Pure test organization analog** (`backend/tests/test_title_key.py:1-18,27-45`):

```python
"""Tests for cross-provider title matching — pure functions, no database."""
...
def test_series_paren_year_stripped_matches_yearless():
    assert title_key("Silo (2023)", "series") == title_key("Silo", "series")

def test_movie_paren_year_is_kept():
    assert title_key("Dune (1984)", "movie") != title_key("Dune (2021)", "movie")
```

Mirror this behavior-oriented naming in `node:test`: arrange explicit inputs, assert both accepted and rejected boundaries, and keep temporary Git repositories local to the test file. Cover legacy-base fallback, staged-index accuracy, path separators, manifest drift, patch/minor/major behavior, and second-run no-op behavior.

### Version consumers and backend metadata

**Applies to:** `backend/app/version.py`, `backend/app/api/meta.py`, `backend/tests/test_meta.py`, `Dockerfile`, `frontend/package.json`, and `frontend/package-lock.json`.

**Existing metadata controller** (`backend/app/api/meta.py:1-11,14-28`):

```python
"""Health & public meta endpoints (no auth)."""
from __future__ import annotations

from flask import Blueprint, jsonify

from ..config import get_config
from ..db import query_one

bp = Blueprint("meta", __name__, url_prefix="/api")

VERSION = "1.0.0"
...
return jsonify({"status": "ok" if db_ok else "degraded", "db": db_ok,
                "version": VERSION})
...
return jsonify({"version": VERSION, "rp_id": cfg.RP_ID, "app": cfg.RP_NAME})
```

Preserve the public, unauthenticated response shapes and replace only the hardcoded constant with a package-relative import from `backend/app/version.py`.

**Repository-relative file read analog** (`backend/app/migrations_runner.py:16,47-50`):

```python
MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parent.parent / "migrations"
...
sql = path.read_text(encoding="utf-8")
```

`backend/app/version.py` should resolve `/app/VERSION` in the image and the repository-root `VERSION` in source checkout, read UTF-8 text, strip it, and validate stable `X.Y.Z`. Do not silently retain `1.0.0` as a fallback for the current runtime.

**Backend boundary-test analog** (`backend/tests/test_profiles.py:1-10,49-53`):

```python
"""Profile edit tests ... All DB-free (pure helpers + a no-cookie 401 check)."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.api._common import poster_url  # noqa: E402
...
client = create_app().test_client()
resp = client.post("/api/profiles/some-id/avatar")
assert resp.status_code == 401
```

Use the same `ROOT` bootstrap and real Flask test client. Patch `meta.query_one` for `/api/health` so the test remains DB-free; assert both `/api/health` and `/api/meta/config` expose the canonical file value.

**Manifest synchronization points** (`frontend/package.json:1-10`; `frontend/package-lock.json:1-10`):

```json
{
  "name": "watchvault-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build"
  }
}
```

```json
{
  "name": "watchvault-frontend",
  "version": "1.0.0",
  "lockfileVersion": 3,
  "packages": {
    "": {
      "name": "watchvault-frontend",
      "version": "1.0.0"
    }
  }
}
```

Synchronize all three version locations (`VERSION`, package manifest, lockfile root package) by parsing/writing JSON; do not use `npm version`.

**Image-stage pattern** (`Dockerfile:3-8,20-31`):

```dockerfile
FROM node:20-alpine AS frontend
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
...
WORKDIR /app
COPY backend/ ./backend/
COPY plugins/ ./plugins/
COPY --from=frontend /build/dist /app/web
```

Keep the two-stage layout. Add required `ARG VERSION`, validate it, apply `LABEL org.opencontainers.image.version=$VERSION`, and `COPY VERSION /app/VERSION`. Replace the existing `npm install` with `npm ci`; do not copy the current install command unchanged.

### Capability schema, inventory, generator, and report

**Applies to:** `capabilities/schema.json`, `capabilities/inventory.json`, `docs/CAPABILITIES.md`, `frontend/scripts/capabilities.mjs`, and `frontend/scripts/capabilities.test.mjs`.

There is no existing schema/inventory analog. Use `01-RESEARCH.md` Pattern 4 for the record and schema contract. For implementation shape, copy deterministic scan/drift behavior from `backend/app/migrations_runner.py:31-58`.

**Frontend route catalog** (`frontend/src/App.tsx:19-46`):

```tsx
const { ready, user } = useApp();
...
{!ready ? (
  <div className="center-screen"><Loading /></div>
) : !user ? (
  <Login />
) : (
  <Routes>
    <Route element={<Layout />}>
      <Route index element={<Dashboard />} />
      <Route path="/overviews" element={<Overviews />} />
      <Route path="/search" element={<Search />} />
      ...
      <Route path="*" element={<Dashboard />} />
    </Route>
  </Routes>
)}
```

Discovery must treat loading, unauthenticated login, authenticated layout, index route, explicit paths, and wildcard fallback as distinct candidates.

**Preference/theme/scope catalog** (`frontend/src/lib/app.tsx:34-46,63-80`):

```tsx
export interface Prefs {
  theme: "light" | "dark" | "system";
  accent: string;
  default_profile: string;
  language: string;
  expert?: boolean;
  cinemaAdd?: boolean;
  dashboard_layout?: DashboardLayout;
  unknown_pos?: { month?: number; day?: number };
}
...
scope: string; // 'all' or a user id
...
const DEFAULT_PREFS: Prefs = {
  theme: "system", accent: "#0a84ff", default_profile: "",
  language: "en", expert: false, cinemaAdd: true,
  dashboard_layout: { order: [], hidden: [] }
};
```

**Locale catalog** (`frontend/src/lib/i18n.tsx:13-32`):

```tsx
export type LangCode = "de" | "en" | "es" | "fr" | "it" | "nl";
export const LANGUAGES: Language[] = [
  { code: "de", native: "Deutsch", english: "German", Flag: FlagDE },
  ...
  { code: "nl", native: "Nederlands", english: "Dutch", Flag: FlagNL },
];
const DICTS: Record<LangCode, Dict> = { de, en, es, fr, it, nl };
```

**Permission catalog** (`backend/migrations/0002_rbac_prefs.sql:46-55`):

```sql
INSERT INTO permissions (key, description) VALUES
    ('catalog.read',     'Read watched titles and statistics'),
    ('ingest.write',     'Import files and run provider syncs'),
    ('profiles.manage',  'Manage household members'),
    ('settings.manage',  'Manage global app settings'),
    ('plugins.manage',   'Configure plugins and secrets'),
    ('mcp.use',          'Use the MCP server'),
    ('mcp.tool.search',  'Use the MCP search tool'),
    ('mcp.tool.stats',   'Use the MCP statistics tool');
```

The generator should discover candidates without overwriting human-authored behavior. Validate schema, IDs, source anchors, requirement/phase ownership, duplicate IDs, route/locale/theme/preference coverage, deterministic ordering, final newline, and byte-for-byte report freshness.

### Vitest, Testing Library, and axe infrastructure

**Applies to:** `frontend/vitest.config.ts`, `frontend/src/test/setup.ts`, `frontend/src/test/render.tsx`, `frontend/src/test/a11y.ts`, representative `*.test.tsx`, `frontend/package.json`, `frontend/package-lock.json`, and `frontend/tsconfig.node.json`.

**Configuration style analog** (`frontend/vite.config.ts:1-10,53-79`):

```tsx
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react(), ...],
  server: { ... },
  build: { ... },
});
```

Use two-space indentation, double quotes, semicolons, direct imports, and a default `defineConfig` export. `vitest.config.ts` should use `defineConfig` from `vitest/config`, `react()`, `jsdom`, `setupFiles`, `clearMocks`, and `restoreMocks`.

**Provider composition analog** (`frontend/src/main.tsx:1-19`):

```tsx
import { BrowserRouter } from "react-router-dom";
import { AppProvider } from "./lib/app";
...
<ErrorBoundary>
  <BrowserRouter>
    <AppProvider>
      <App />
    </AppProvider>
  </BrowserRouter>
</ErrorBoundary>
```

`frontend/src/test/render.tsx` should preserve `AppProvider` composition but use a controllable `MemoryRouter` for route tests. Import directly from defining modules; do not add a barrel.

**Application state contracts for fixtures** (`frontend/src/lib/app.tsx:63-77`):

```tsx
interface AppCtx {
  ready: boolean;
  bootstrapped: boolean;
  user: User | null;
  prefs: Prefs;
  profiles: Profile[];
  scope: string;
  ...
  can: (perm: string) => boolean;
}
```

Component tests should cover loading, login, authenticated route composition, theme application, permission-gated actions, and representative mutation feedback. Use semantic Testing Library queries and `userEvent.setup()`, not CSS selectors or direct low-level events.

There is no existing frontend test or axe helper analog. Use the exact Vitest/setup/a11y patterns in `01-RESEARCH.md:459-488` and the pinned package versions in its Standard Stack section.

### Playwright fixtures, journey, and visual snapshots

**Applies to:** `frontend/playwright.config.ts`, `frontend/e2e/fixtures/data.ts`, `frontend/e2e/fixtures/api.ts`, `frontend/e2e/reference-journey.spec.ts`, and snapshot files.

**Client API contract** (`frontend/src/lib/api.ts:12-19,32-61`):

```tsx
async function handle(res: Response): Promise<any> {
  const ct = res.headers.get("content-type") || "";
  const body = ct.includes("application/json") ? await res.json().catch(() => ({})) : await res.text();
  if (!res.ok) {
    const msg = (body && (body.error || body.message)) || res.statusText || "Request failed";
    throw new ApiError(res.status, msg);
  }
  return body;
}

export const api = {
  get: (path, params) =>
    fetch(`/api${path}${qs(params)}`, { credentials: "include" }).then(handle),
  post: (path, body) =>
    fetch(`/api${path}`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    }).then(handle),
};
```

The browser fixture must match this same-origin `/api` boundary, methods, JSON bodies, cookies, and non-2xx semantics. Unknown method/path/body combinations must fail closed.

**Bootstrap calls the fixture must satisfy** (`frontend/src/lib/app.tsx:111-145`):

```tsx
const status = await api.get("/auth/status");
...
const list = await api.get("/profiles");
...
const p = await api.get("/preferences");
...
const saved = await api.put("/preferences", patch);
```

**Reference journey calls**:

`frontend/src/pages/Dashboard.tsx:34-36`:

```tsx
api.get("/stats/summary", { profile: scope })
api.get("/stats/providers", { profile: scope, range })
api.get("/stats/recent", { profile: scope, range: recentRange })
```

`frontend/src/pages/Search.tsx:100-128`:

```tsx
const res = await api.get("/search", { ...params, limit: PAGE, offset: 0 });
setResults(res.results); setTotal(res.total);
```

`frontend/src/pages/TitleDetail.tsx:476-484,513-515,551-556`:

```tsx
const { data: ti } = useFetch<any>(
  () => api.get(`/search/title/${id}`, { profile: scope, lang }), [id, scope, lang]);
...
const canEdit = can("ingest.write");
const targetBody = () => (scope && scope !== "all" ? { user_id: scope } : {});
...
await api.post(`/titles/${id}/watch`, { ...targetBody(), date });
toast(t("title.watchAdded"), "ok");
refresh();
```

Use fixed IDs, dates, locale, timezone, permissions, and image assets. The POST must mutate in-memory history so a subsequent dashboard `/stats/recent` response includes the new record.

**Visual naming analog:** `docs/screenshots/desktop/01-dashboard.png` and `docs/screenshots/mobile/01-dashboard.jpg` already group screenshots by form factor and stable ordered checkpoint names. Playwright snapshots should instead use project-qualified committed baselines generated by Playwright, with four projects and four checkpoints.

There is no existing E2E test analog. Use `01-RESEARCH.md` Pattern 5: install route interception before navigation, pinned Chromium, dark/light desktop/mobile projects, `animations: "disabled"`, CSS scale, fixed time, `maxDiffPixelRatio: 0.001`, axe at each checkpoint, and failure-only artifacts.

### GitHub Actions and publication

**Applies to:** `.github/workflows/ci.yml`, `.github/workflows/docker.yml`, and `scripts/ci-changes.mjs`.

**Workflow structure and permissions analog** (`.github/workflows/docker.yml:1-21`):

```yaml
name: Build & publish Docker image

on:
  push:
    branches: [ "release/**", "main" ]
    tags: [ "v*" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - name: Checkout
        uses: actions/checkout@v4
```

Preserve explicit event declarations, job-local least privilege, and named steps. For PR validation, use read-only permissions and never `pull_request_target`.

**Build metadata and cache analog** (`.github/workflows/docker.yml:33-52`):

```yaml
- name: Extract metadata
  id: meta
  uses: docker/metadata-action@v5
  with:
    images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
    tags: |
      type=ref,event=branch
      type=ref,event=tag
      type=sha
      type=raw,value=latest,enable={{is_default_branch}}

- name: Build and push
  uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ${{ steps.meta.outputs.tags }}
    labels: ${{ steps.meta.outputs.labels }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

Keep metadata and Buildx caching, but make publication downstream of the aggregate gate and pass canonical `VERSION` as the Docker build argument/OCI label input.

`ci.yml` must always trigger for PRs and for pushes to `main`/`v*`; do not use top-level `paths`. Checkout with `fetch-depth: 0`, always run version/inventory validation, compute changed-surface outputs in a repository script, conditionally run backend/frontend/browser jobs for PRs, force all jobs on `main` and tags, and finish with an `if: always()` job whose stable check name is `delivery / gate`.

### Supporting config modifications

**TypeScript config analog** (`frontend/tsconfig.node.json:1-10`):

```json
{
  "compilerOptions": {
    "composite": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true
  },
  "include": ["vite.config.ts"]
}
```

Extend the configuration-file include set only as required for the new Vitest configuration; retain strict bundler resolution.

**Ignore-file analog** (`.gitignore:11-15,28-30`):

```gitignore
# Node / frontend
node_modules/
frontend/dist/
frontend/.vite/
*.local

# Compiled vite config artifacts
frontend/vite.config.js
frontend/vite.config.d.ts
```

Add Playwright reports, traces, and transient test results to this existing Node/generated section. Do not ignore committed screenshot baselines.

## Shared Patterns

### Formatting and imports

- TypeScript/TSX: two spaces, double quotes, semicolons, trailing commas in multiline values.
- Frontend imports are direct relative imports; no path aliases or new barrel files.
- Python: `from __future__ import annotations`, standard library before third party before package-relative imports, four spaces.
- Tests should describe behavior and remain network/DB independent.

### Authentication and authorization

**Source:** `backend/app/auth/sessions.py:116-138`

```python
def require_auth(fn):
    ...
    if not user:
        return jsonify({"error": "unauthorized"}), 401

def require_perm(key: str):
    ...
    if "*" not in perms and key not in perms:
        return jsonify({"error": "forbidden", "needs": key}), 403
```

The backend metadata endpoints remain public. Browser fixtures must return a synthetic user with explicit permissions and must exercise the existing `ingest.write` gate rather than bypassing it.

### Error handling

- CLI/tooling: fail nonzero, write actionable diagnostics to stderr, and include the exact bump remediation.
- Capability validation: collect and print all schema/reference/discovery errors before exiting.
- Browser fixtures: record and abort unknown requests, then assert no unhandled requests during teardown.
- Frontend action tests should assert the existing `ApiError`/toast behavior rather than swallowing failures.

### Determinism

- Normalize Git paths to `/`.
- Sort discovered files and generated inventory rows.
- Use UTF-8 and exactly one final newline for generated text.
- Fix browser time, timezone, locale, viewport, theme, IDs, and payloads.
- Generate authoritative visual baselines only with the pinned Playwright Chromium/container environment.

## No Analog Found

These files introduce capabilities absent from the live codebase. The planner should use the cited `01-RESEARCH.md` patterns rather than inventing a local precedent.

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `version-policy.json` | config | transform | No repository policy/schema file exists |
| `capabilities/schema.json` | config | transform | No JSON Schema exists |
| `capabilities/inventory.json` | model | batch | No machine-readable capability inventory exists |
| `docs/CAPABILITIES.md` | generated report | file-I/O | No deterministic generated report exists |
| `frontend/src/test/setup.ts` | config | event-driven | No frontend test runner exists |
| `frontend/src/test/a11y.ts` | utility | transform | No automated accessibility helper exists |
| `frontend/src/**/*.test.tsx` | test | event-driven | No frontend component tests exist |
| `frontend/e2e/reference-journey.spec.ts` | test | event-driven / request-response | No browser/E2E suite exists |

## Metadata

**Analog search scope:** `.github/workflows`, root build/config files, `deploy`, `backend/app`, `backend/tests`, `backend/migrations`, `frontend/src`, and `frontend` configuration
**Strong source analogs read:** `.github/workflows/docker.yml`, `Dockerfile`, `deploy/entrypoint.sh`, `backend/app/migrations_runner.py`, `backend/app/api/meta.py`, `backend/tests/test_profiles.py`, `backend/tests/test_title_key.py`, `frontend/vite.config.ts`, `frontend/src/main.tsx`, `frontend/src/lib/api.ts`, and catalog sources
**Pattern extraction date:** 2026-07-21
