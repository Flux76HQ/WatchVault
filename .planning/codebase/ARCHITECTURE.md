<!-- refreshed: 2026-07-21 -->
# Architecture

**Analysis Date:** 2026-07-21

## System Overview

```text
┌───────────────────────────────────────────────────────────────────────────┐
│ Browser / installable React PWA                                           │
│ `frontend/src/main.tsx` → `frontend/src/App.tsx` → pages/components       │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   │ same-origin HTTP
                                   ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ nginx edge and static host                                                │
│ `deploy/nginx.conf`                                                       │
├───────────────────────┬────────────────────────┬──────────────────────────┤
│ `/api/*`              │ `/mcp`                 │ static/PWA fallback      │
│ Gunicorn + Flask      │ Flask JSON-RPC bridge  │ `/app/web`               │
│ `backend/wsgi.py`     │ `backend/server.py`    │ `frontend/dist/` build   │
└───────────┬───────────┴────────────┬───────────┴──────────────────────────┘
            │                        │
            ▼                        ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ Application and background processing                                    │
│ Blueprints `backend/app/api/`; auth `backend/app/auth/`;                  │
│ ingest `backend/app/ingest/`; plugins `backend/app/plugins/`;             │
│ queue worker `backend/worker.py`                                          │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   │ psycopg pool / SQL transactions
                                   ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ PostgreSQL 17: identity, catalog, watch events, jobs, aggregates, sync     │
│ `backend/app/db.py`; `backend/migrations/*.sql`                           │
└───────────────────────────────────────────────────────────────────────────┘
```

WatchVault is a self-hosted modular monolith packaged as one application container plus PostgreSQL. The application container runs nginx, three Gunicorn API workers, a standalone MCP process, and a queue worker under Supervisor (`Dockerfile`, `deploy/supervisord.conf`, `docker-compose.yml`). The React PWA, Flask API, MCP bridge, background worker, provider adapters, and metadata plugins share one PostgreSQL model (`frontend/src/`, `backend/app/`, `backend/server.py`, `backend/worker.py`, `backend/migrations/`).

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| React bootstrap | Installs the router, error boundary, global app context, and styles | `frontend/src/main.tsx` |
| Route shell | Gates unauthenticated users and maps browser routes to pages | `frontend/src/App.tsx` |
| App context | Owns session bootstrap, profiles, preferences, profile scope, permissions, theme, and toasts | `frontend/src/lib/app.tsx` |
| API client | Provides same-origin `/api` requests, cookie credentials, query serialization, and normalized errors | `frontend/src/lib/api.ts` |
| Page layer | Fetches API view models and composes feature UI | `frontend/src/pages/` |
| Shared UI layer | Provides layout, controls, charts, icons, grids, and feature widgets | `frontend/src/components/` |
| Flask application factory | Creates the API app, registers blueprints, configures JSON serialization, and installs error handlers | `backend/app/__init__.py` |
| API blueprints | Own HTTP routing, permission checks, household scoping, request validation, and response shaping | `backend/app/api/` |
| Authentication | Implements WebAuthn, sessions, API tokens, OAuth bridge routes, and permission decorators | `backend/app/auth/routes.py`, `backend/app/auth/sessions.py` |
| Ingestion domain | Converts provider data and live playback into deduplicated central watch records | `backend/app/ingest/` |
| Provider registry | Maps provider adapter IDs to `SourceAdapter` implementations | `backend/app/ingest/adapters/__init__.py` |
| Catalog domain | Merges title/person metadata, provenance, genres, cast, crew, episodes, and duplicates | `backend/app/catalog.py` |
| Plugin runtime | Discovers manifest-based plugins and dispatches metadata capabilities | `backend/app/plugins/runtime.py`, `plugins/` |
| Background worker | Claims queued jobs, schedules connection syncs, enriches metadata, and expires live sessions | `backend/worker.py` |
| MCP bridge | Exposes authenticated JSON-RPC `search` and `stats` tools over `/mcp` | `backend/server.py` |
| Persistence gateway | Provides a process-local connection pool and transactional SQL helpers | `backend/app/db.py` |
| Schema management | Applies ordered, checksum-guarded, forward-only SQL migrations before startup | `backend/app/migrations_runner.py`, `backend/migrations/` |
| Edge/process layer | Serves the PWA, proxies API/MCP traffic, and supervises application processes | `deploy/nginx.conf`, `deploy/supervisord.conf`, `deploy/entrypoint.sh` |

## Pattern Overview

**Overall:** Single-container modular monolith with a React SPA/PWA, Flask blueprint API, PostgreSQL-backed job queue, and adapter/plugin extension points (`Dockerfile`, `frontend/src/`, `backend/app/`, `backend/worker.py`).

**Key Characteristics:**
- Keep deployment cohesive: nginx, API, MCP, and worker run as separate processes but ship from one image (`Dockerfile`, `deploy/supervisord.conf`).
- Keep HTTP modules thin enough to delegate reusable write workflows into domain modules; blueprints remain the transport boundary (`backend/app/api/`, `backend/app/ingest/`, `backend/app/catalog.py`).
- Normalize all provider input to `NormalizedEvent` before persistence, regardless of file import, API sync, or live scrobble source (`backend/app/ingest/models.py`, `backend/app/ingest/normalize.py`, `backend/app/ingest/scrobble.py`).
- Extend source ingestion through registered `SourceAdapter` classes and metadata through manifest-discovered plugins (`backend/app/ingest/adapters/base.py`, `backend/app/ingest/adapters/__init__.py`, `backend/app/plugins/runtime.py`).
- Treat PostgreSQL as the system of record, transaction manager, queue, aggregate engine, and revision source (`backend/app/db.py`, `backend/migrations/0004_plugins_jobs_audit.sql`, `backend/migrations/0005_aggregates.sql`, `backend/app/api/sync.py`).
- Scope user-facing reads and writes to the authenticated household/profile (`backend/app/api/_common.py`, `backend/app/auth/sessions.py`).

## Layers

**Edge and Process Layer:**
- Purpose: Start migrations, supervise processes, serve static assets, and route external traffic.
- Location: `Dockerfile`, `deploy/entrypoint.sh`, `deploy/supervisord.conf`, `deploy/nginx.conf`
- Contains: Multi-stage image build, boot sequencing, Supervisor programs, nginx upstreams, upload limits, and SPA fallback.
- Depends on: Built assets from `frontend/dist/` and executable entry points in `backend/`.
- Used by: Browser/PWA clients, MCP clients, Docker Compose, and the GHCR image pipeline in `.github/workflows/docker.yml`.

**Frontend Presentation Layer:**
- Purpose: Render authenticated household watch data and collect user actions.
- Location: `frontend/src/pages/`, `frontend/src/components/`, `frontend/src/styles/`
- Contains: Route pages, shared visual components, charts, layout editing, responsive shell, and CSS tokens.
- Depends on: State/data helpers in `frontend/src/lib/` and routes declared in `frontend/src/App.tsx`.
- Used by: The browser entry point `frontend/src/main.tsx`.

**Frontend State and Transport Layer:**
- Purpose: Centralize session state, profile scope, preferences, localization, formatting, and HTTP access.
- Location: `frontend/src/lib/`
- Contains: `AppProvider`, `api`, `useFetch`, WebAuthn helpers, i18n, branding, and formatting.
- Depends on: Browser APIs, React context/hooks, and `/api` endpoints.
- Used by: Pages and components under `frontend/src/pages/` and `frontend/src/components/`.

**HTTP and Authentication Layer:**
- Purpose: Expose JSON endpoints, validate input, enforce permissions, scope data, and shape response view models.
- Location: `backend/app/api/`, `backend/app/auth/`
- Contains: Flask blueprints, WebAuthn routes, JWT/API-token resolution, decorators, and shared API helpers.
- Depends on: Domain modules in `backend/app/`, transaction helpers in `backend/app/db.py`, and configuration in `backend/app/config.py`.
- Used by: Gunicorn via `backend/wsgi.py` and the PWA through `frontend/src/lib/api.ts`.

**Domain and Application Layer:**
- Purpose: Implement ingestion, normalization, deduplication, title progress, metadata composition, tags, network attribution, and manual watch operations.
- Location: `backend/app/ingest/`, `backend/app/catalog.py`, `backend/app/networks.py`, `backend/app/genres.py`
- Contains: Provider-neutral dataclasses, transaction-aware workflows, catalog merge rules, and aggregate/progress maintenance.
- Depends on: SQL transactions from `backend/app/db.py`, provider adapters in `backend/app/ingest/adapters/`, and plugin enrichment in `backend/app/plugins/`.
- Used by: API routes in `backend/app/api/`, jobs in `backend/worker.py`, and live scrobbling in `backend/app/ingest/scrobble.py`.

**Integration Extension Layer:**
- Purpose: Isolate provider-specific import/API behavior and external metadata capabilities.
- Location: `backend/app/ingest/adapters/`, `backend/app/plugins/`, `plugins/tmdb/`
- Contains: `SourceAdapter`, adapter registry/implementations, plugin discovery, plugin manifests, and enrichment orchestration.
- Depends on: `NormalizedEvent` in `backend/app/ingest/models.py`, shared catalog helpers in `backend/app/catalog.py`, and plugin code under `plugins/`.
- Used by: Ingestion routes in `backend/app/api/ingest.py` and jobs in `backend/worker.py`.

**Persistence Layer:**
- Purpose: Own pooled connections, transaction boundaries, schema evolution, relational constraints, aggregate functions, and revision tracking.
- Location: `backend/app/db.py`, `backend/app/migrations_runner.py`, `backend/migrations/`
- Contains: psycopg helpers and ordered SQL migrations.
- Depends on: PostgreSQL configuration from `backend/app/config.py`.
- Used by: All backend processes, including `backend/wsgi.py`, `backend/worker.py`, and `backend/server.py`.

## Data Flow

### Primary Browser Request Path

1. React mounts `BrowserRouter`, `AppProvider`, and `App` (`frontend/src/main.tsx:10`).
2. `AppProvider` calls `/api/auth/status`, then loads preferences and profiles after a user resolves (`frontend/src/lib/app.tsx:111`, `frontend/src/lib/app.tsx:160`, `frontend/src/lib/app.tsx:168`).
3. `App` selects the login view or an authenticated route under `Layout` (`frontend/src/App.tsx:27`).
4. A page calls the same-origin fetch wrapper, commonly through `useFetch`; the dashboard requests scoped stats (`frontend/src/pages/Dashboard.tsx:34`, `frontend/src/lib/api.ts:32`, `frontend/src/lib/useFetch.ts:12`).
5. nginx proxies `/api/*` to Gunicorn (`deploy/nginx.conf:25`), and the factory-registered blueprint resolves the route (`backend/app/__init__.py:30`, `backend/app/__init__.py:38`).
6. Auth decorators resolve a JWT cookie, bearer JWT, or API token and attach the user to Flask request state (`backend/app/auth/sessions.py:98`, `backend/app/auth/sessions.py:116`, `backend/app/auth/sessions.py:126`).
7. The route scopes IDs to the household/profile, runs parameterized SQL through the pool, and returns JSON (`backend/app/api/_common.py:15`, `backend/app/api/_common.py:24`, `backend/app/db.py:42`).
8. `api.handle` converts non-2xx responses to `ApiError`; `useFetch` updates page loading/data/error state (`frontend/src/lib/api.ts:12`, `frontend/src/lib/useFetch.ts:12`).

### File Import and Normalization

1. `/api/ingest/import` validates permission, provider, target household user, and upload (`backend/app/api/ingest.py:64`).
2. The registered provider adapter parses bytes into `NormalizedEvent` records (`backend/app/api/ingest.py:81`, `backend/app/ingest/adapters/base.py:22`, `backend/app/ingest/models.py:9`).
3. `ingest_events` opens one transaction and resolves or creates central titles and episodes (`backend/app/ingest/normalize.py:108`, `backend/app/ingest/normalize.py:14`, `backend/app/ingest/normalize.py:54`).
4. `_ingest_events` inserts deduplicated `watch_events`, recomputes affected daily aggregates and title progress, and queues enrichment for new titles (`backend/app/ingest/normalize.py:192`, `backend/app/ingest/normalize.py:227`, `backend/app/ingest/normalize.py:246`, `backend/app/ingest/normalize.py:253`, `backend/app/ingest/normalize.py:258`).
5. The route records an audit event and returns the import summary (`backend/app/api/ingest.py:92`).

### Scheduled Provider Sync

1. The worker periodically selects enabled API connections and inserts deduplicated `sync_connection` jobs (`backend/worker.py:122`, `backend/worker.py:170`).
2. A worker claims one pending job with `FOR UPDATE SKIP LOCKED`, allowing multiple workers to coordinate through PostgreSQL (`backend/worker.py:22`).
3. `_run_sync` resolves the connection and adapter, refreshes adapter configuration if needed, and fetches provider history/cursor (`backend/worker.py:78`, `backend/app/ingest/adapters/base.py:25`).
4. Events are grouped through `scrobble_account_map`, then each profile group enters the same normalized ingestion path (`backend/app/ingest/normalize.py:125`, `backend/app/ingest/normalize.py:149`).
5. The worker prunes deselected libraries, updates the connection cursor/status, and marks or retries the job (`backend/worker.py:108`, `backend/worker.py:117`, `backend/worker.py:193`).

### Live Scrobble Path

1. Plex or generic/Home Assistant payloads enter `/api/scrobble/*` and are parsed into `ScrobbleEvent` (`backend/app/api/scrobble.py:68`, `backend/app/api/scrobble.py:90`, `backend/app/ingest/scrobble.py:99`).
2. Stateful handling maps platform and source account, updates `scrobble_sessions`, and determines whether the watch threshold is met (`backend/app/ingest/scrobble.py:259`, `backend/app/ingest/scrobble.py:313`, `backend/app/ingest/scrobble.py:326`).
3. A completed session is converted to `NormalizedEvent` and committed through `ingest_events` on the caller-owned cursor to preserve one transaction and avoid self-deadlock (`backend/app/ingest/scrobble.py:369`).
4. The worker expires stale sessions every minute and commits qualifying durationless sessions (`backend/worker.py:180`, `backend/app/ingest/scrobble.py`).

### Metadata Enrichment

1. New titles enqueue `enrich_title` jobs during normalized ingestion (`backend/app/ingest/normalize.py:258`).
2. The worker dispatches the job to `enrich_title` (`backend/worker.py:56`).
3. The plugin runtime discovers `plugins/*/manifest.json`, resolves enabled capability providers, and dynamically loads `plugin.py` (`backend/app/plugins/runtime.py:28`, `backend/app/plugins/runtime.py:59`, `backend/app/plugins/runtime.py:95`).
4. Enrichment searches/fetches external metadata, deduplicates titles by provider identity, and applies fill-empty/additive merge rules with provenance (`backend/app/plugins/enrich.py:129`, `backend/app/catalog.py:117`, `backend/app/catalog.py:166`).
5. Series episodes, daily aggregates, title progress, and network attribution are refreshed after metadata arrives (`backend/app/plugins/enrich.py:208`, `backend/app/plugins/enrich.py:213`, `backend/app/plugins/enrich.py:224`).

### Offline Revision Sync

1. An authenticated client calls `/api/sync/changes?since=N` (`backend/app/api/sync.py:18`).
2. The endpoint reads changed household users/events/preferences plus shared titles using revision columns and tombstones (`backend/app/api/sync.py:25`).
3. The response includes the `wv_revision_seq` high-water mark for the next incremental pull (`backend/app/api/sync.py:49`).

**State Management:**
- Browser session/profile/preferences/toasts live in React context; page request state lives in local hooks (`frontend/src/lib/app.tsx`, `frontend/src/lib/useFetch.ts`).
- Durable identity, domain, queue, aggregate, live-session, and sync state lives in PostgreSQL (`backend/migrations/0001_identity.sql`, `backend/migrations/0003_domain.sql`, `backend/migrations/0004_plugins_jobs_audit.sql`, `backend/migrations/0005_aggregates.sql`, `backend/migrations/0016_scrobble_sessions.sql`).
- Process-local caches are limited to configuration, connection pools, plugin manifests, and plugin instances (`backend/app/config.py`, `backend/app/db.py`, `backend/app/plugins/runtime.py`).

## Key Abstractions

**Flask Blueprint:**
- Purpose: Partition API transport concerns by feature.
- Examples: `backend/app/api/stats.py`, `backend/app/api/search.py`, `backend/app/api/ingest.py`, `backend/app/auth/routes.py`
- Pattern: Define `bp`, decorate routes, apply `require_auth`/`require_perm`, and register the module in `create_app()` (`backend/app/__init__.py`).

**NormalizedEvent:**
- Purpose: Represent one provider-neutral watch event before central persistence.
- Examples: `backend/app/ingest/models.py`, `backend/app/ingest/normalize.py`, `backend/app/ingest/scrobble.py`
- Pattern: Adapters/parsers populate a dataclass; only normalization resolves catalog entities and inserts deduplicated events.

**SourceAdapter:**
- Purpose: Isolate file/API source behavior behind one provider contract.
- Examples: `backend/app/ingest/adapters/base.py`, `backend/app/ingest/adapters/netflix.py`, `backend/app/ingest/adapters/plex.py`, `backend/app/ingest/adapters/trakt.py`
- Pattern: Subclass `SourceAdapter`, implement supported operations, and register one instance in `backend/app/ingest/adapters/__init__.py`.

**Plugin Manifest and Capability Provider:**
- Purpose: Add metadata services without coupling enrichment orchestration to a concrete SDK.
- Examples: `plugins/tmdb/manifest.json`, `plugins/tmdb/plugin.py`, `backend/app/plugins/runtime.py`
- Pattern: Discover `manifest.json`, load sibling `plugin.py`, instantiate `Plugin(settings, secrets)`, and dispatch by declared capability.

**Transactional Connection:**
- Purpose: Make commit-on-success and rollback-on-error the default persistence boundary.
- Examples: `backend/app/db.py`, `backend/app/ingest/normalize.py`, `backend/app/catalog.py`
- Pattern: Use `with connection() as conn, conn.cursor() as cur`; pass `cur` into multi-step domain operations that must share locks and atomicity.

**PostgreSQL Job Queue:**
- Purpose: Decouple slow synchronization/enrichment from request handling.
- Examples: `backend/worker.py`, `backend/migrations/0004_plugins_jobs_audit.sql`
- Pattern: Insert JSON payloads into `background_jobs`, claim with row locks and `SKIP LOCKED`, then mark done, retry, or error.

**AppProvider and useFetch:**
- Purpose: Separate durable global UI state from page-scoped remote request state.
- Examples: `frontend/src/lib/app.tsx`, `frontend/src/lib/useFetch.ts`, `frontend/src/pages/Dashboard.tsx`
- Pattern: Put auth/profile/preferences in context; keep endpoint-specific data in `useFetch` within pages.

## Entry Points

**Container Bootstrap:**
- Location: `deploy/entrypoint.sh`
- Triggers: Docker image startup from `Dockerfile`.
- Responsibilities: Run `backend/migrate.py` before serving traffic, then exec Supervisor.

**Production Web API:**
- Location: `backend/wsgi.py`
- Triggers: Gunicorn command in `deploy/supervisord.conf`.
- Responsibilities: Construct the Flask application through `backend/app/__init__.py:create_app`.

**Background Worker:**
- Location: `backend/worker.py`
- Triggers: Supervisor process in `deploy/supervisord.conf`.
- Responsibilities: Schedule, claim, execute, retry, and complete database-backed jobs; expire stale scrobbles.

**MCP Server:**
- Location: `backend/server.py`
- Triggers: Supervisor process or direct `python backend/server.py --http`.
- Responsibilities: Serve JSON-RPC initialize/tool operations and health over `/mcp`/`/`.

**Frontend:**
- Location: `frontend/src/main.tsx`
- Triggers: Browser loading `frontend/index.html`.
- Responsibilities: Mount the React PWA and install global providers.

**Migration CLI:**
- Location: `backend/migrate.py`
- Triggers: `deploy/entrypoint.sh` or direct Python execution.
- Responsibilities: Delegate to checksum-guarded migration execution in `backend/app/migrations_runner.py`.

**Home Assistant Blueprint:**
- Location: `homeassistant/watchvault_realtime.yaml`
- Triggers: Home Assistant media-player state changes and 30-second ticks.
- Responsibilities: Push generic scrobble events to `backend/app/api/scrobble.py`.

## Architectural Constraints

- **Threading/process model:** Gunicorn runs three API worker processes; MCP uses Flask threaded mode; the queue worker is a single polling loop but its `SKIP LOCKED` claim permits multiple worker processes (`deploy/supervisord.conf`, `backend/server.py:212`, `backend/worker.py:22`).
- **Global state:** Configuration and the psycopg pool are process-local singletons; plugin manifests/instances are mutable process-local caches (`backend/app/config.py:51`, `backend/app/db.py:12`, `backend/app/plugins/runtime.py:24`).
- **Transactions:** Pass a caller-owned cursor for nested write flows; do not open a second pooled connection while holding an uncommitted first-seen title lock (`backend/app/ingest/normalize.py:108`, `backend/app/ingest/scrobble.py:369`).
- **Database concurrency:** Queue consumers must preserve `FOR UPDATE SKIP LOCKED`; pool capacity is ten connections per process (`backend/worker.py:22`, `backend/app/db.py:15`).
- **Schema evolution:** Add forward-only numbered SQL files and never edit an applied migration because checksums are enforced (`backend/app/migrations_runner.py`, `backend/migrations/`).
- **Household isolation:** Resolve profile filters only from the authenticated household IDs; never trust arbitrary client-supplied user IDs (`backend/app/api/_common.py`, `backend/app/api/ingest.py:52`).
- **Catalog identity:** Preserve normalized keys, provider IDs, and dedup hashes; all ingestion sources must use central resolution and dedup (`backend/app/ingest/normalize.py`, `backend/app/util.py`, `backend/app/catalog.py`).
- **Manual overrides:** Metadata merge logic must retain manually pinned title kind, title, and poster choices (`backend/app/catalog.py`, `backend/app/api/titles_edit.py`).
- **Frontend origin:** Production assumes same-origin `/api` and `/mcp`; development reproduces that contract through Vite proxies (`frontend/src/lib/api.ts`, `frontend/vite.config.ts`, `deploy/nginx.conf`).
- **Circular imports:** Delayed imports in `backend/worker.py`, `backend/app/plugins/enrich.py`, and package exports in `backend/app/ingest/__init__.py` are part of dependency-cycle control; avoid moving worker-only imports to module scope without checking cycles.

## Anti-Patterns

### Fat Blueprint Modules

**What happens:** Large route modules such as `backend/app/api/ingest.py`, `backend/app/api/stats.py`, and `backend/app/api/search.py` combine transport validation, SQL, response mapping, and some domain decisions.
**Why it's wrong:** Adding more write orchestration directly to these files increases coupling, duplicates transaction/scoping rules, and makes reusable flows unavailable to `backend/worker.py` or `backend/server.py`.
**Do this instead:** Keep route-specific parsing/serialization in `backend/app/api/`, but place reusable writes and calculations in focused modules following `backend/app/ingest/normalize.py`, `backend/app/catalog.py`, and `backend/app/networks.py`.

### Duplicated MCP Authentication

**What happens:** `backend/server.py` independently implements API-token lookup and permission loading that overlaps `backend/app/auth/sessions.py`.
**Why it's wrong:** Token prefix parsing, hashing, last-used behavior, and permission semantics can diverge between `/api` and `/mcp`.
**Do this instead:** Reuse or extract a request-independent API-token resolver from `backend/app/auth/sessions.py` when changing authentication, while retaining the standalone Flask app boundary in `backend/server.py`.

### Bypassing the Normalized Ingestion Spine

**What happens:** A direct `watch_events` insert outside `backend/app/ingest/normalize.py` would skip title/episode resolution, deduplication, aggregate recomputation, progress updates, and enrichment queueing.
**Why it's wrong:** Search, dashboard totals, title progress, and cross-source identity would disagree with raw event rows defined by `backend/migrations/0003_domain.sql`.
**Do this instead:** Convert source data to `NormalizedEvent` and call `ingest_events`, as file imports and scrobbling do in `backend/app/api/ingest.py` and `backend/app/ingest/scrobble.py`.

## Error Handling

**Strategy:** Convert expected transport failures to structured JSON/status codes, roll back transactional failures, retry asynchronous jobs up to `max_attempts`, and log unexpected API/worker exceptions (`backend/app/__init__.py`, `backend/app/db.py`, `backend/worker.py`).

**Patterns:**
- Flask HTTP exceptions become `{error, message}` responses; unhandled errors are logged with method/path and hide details in production (`backend/app/__init__.py:56`).
- Permission decorators return explicit 401/403 JSON before invoking route logic (`backend/app/auth/sessions.py:116`, `backend/app/auth/sessions.py:126`).
- `connection()` commits on success and rolls back/re-raises on failure (`backend/app/db.py:29`).
- Parse/validation failures that are expected client input errors are caught near the route and returned as 400 responses (`backend/app/api/ingest.py:81`).
- Background jobs record `last_error`, retry after 60 seconds, and become `error` after `max_attempts` (`backend/worker.py:46`).
- The worker's outer loop catches all exceptions so one failed poll cannot terminate processing (`backend/worker.py:161`).
- Frontend HTTP failures become `ApiError`; `useFetch` exposes error/retry while silent refresh preserves existing data (`frontend/src/lib/api.ts`, `frontend/src/lib/useFetch.ts`).

## Cross-Cutting Concerns

**Logging:** Flask uses standard `logging` configured from `LOG_LEVEL`; worker/startup paths write process-prefixed stdout/stderr consumed by Supervisor/nginx (`backend/app/__init__.py`, `backend/app/config.py`, `backend/worker.py`, `deploy/supervisord.conf`).

**Validation:** Validation is explicit at route and adapter boundaries; WebAuthn uses its library-specific verification, upload size is capped at 64 MB in Flask and nginx, and relational integrity lives in SQL constraints (`backend/app/auth/routes.py`, `backend/app/api/ingest.py`, `backend/app/__init__.py:36`, `deploy/nginx.conf:14`, `backend/migrations/`).

**Authentication:** PWA sessions use HttpOnly JWT cookies backed by revocable session rows; API/MCP integrations use salted-hashed personal tokens; routes enforce RBAC permission keys (`backend/app/auth/sessions.py`, `backend/app/auth/routes.py`, `backend/server.py`, `backend/migrations/0002_rbac_prefs.sql`).

**Authorization/tenancy:** Household and profile scoping is resolved server-side from the authenticated user (`backend/app/api/_common.py`, `backend/app/auth/sessions.py`).

**Observability:** Health endpoints expose API/database and MCP liveness, while job status and audit data persist in PostgreSQL (`backend/app/api/meta.py`, `backend/server.py:207`, `backend/migrations/0004_plugins_jobs_audit.sql`).

**Internationalization:** UI strings are language modules under `frontend/src/locales/`; metadata overviews/biographies are merged per language in `backend/app/catalog.py`.

**Offline/PWA behavior:** Vite PWA supplies the service worker, app-shell fallback, network-first stats/search caching, and poster caching; revision sync supports a future/native incremental client (`frontend/vite.config.ts`, `backend/app/api/sync.py`).

---

*Architecture analysis: 2026-07-21*
