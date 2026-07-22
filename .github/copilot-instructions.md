<!-- GSD:project-start source:PROJECT.md -->

## Project

**WatchVault**

WatchVault is a self-hosted watch-history platform for media enthusiasts who want to manage personal and household viewing data in one place. It imports and synchronizes activity from media providers, supports live scrobbling and manual history management, enriches a shared media catalog, and presents the result through an installable web application.

This milestone redesigns the full existing interface into a modern, cinematic, premium experience comparable in quality to leading media-tracking products such as TV Time and Trakt, without expanding the product into a social network or recommendation service.

**Core Value:** Self-hosting media enthusiasts can move effortlessly from their dashboard to finding a title, understanding its details, and maintaining accurate personal or household watch history.

### Constraints

- **Existing stack**: Continue with React, TypeScript, Vite, Flask, PostgreSQL, and the current self-hosted deployment architecture — minimize migration risk and preserve proven capabilities
- **Feature preservation**: Every current user-facing capability must remain available and understandable — this is a redesign, not a product reset
- **Backend scope**: Backend changes must directly support existing data in the redesigned UI — no unrelated platform expansion
- **Accessibility**: Keyboard usability, visible focus, semantic structure, and WCAG AA contrast are release requirements — premium quality includes inclusive operation
- **Responsive UX**: The complete interface must support desktop and mobile use — the PWA is the only client
- **Themes**: Use a cinematic dark-first direction while retaining a polished light mode and saved user preferences
- **Versioning**: Runtime, build, deploy, or CI changes require a SemVer project-version bump — default to a patch bump unless scope requires otherwise
- **CI enforcement**: Protected runtime paths must fail CI when changed without a version bump, with an exact remediation message
- **Local enforcement**: Provide an idempotent version-bump helper and fast repository-configured git hooks; keep heavyweight checks in CI
- **Secrets**: Keep `.env` variants ignored, maintain safe `.env.example` placeholders, and never commit production credentials
- **Release discipline**: Publish from `vX.Y.Z` tags through CI with reproducible artifacts and documented stable/latest/beta channel rules
- **Operations**: Keep the README operationally complete for setup, run/stop, health checks, deploy/update, backup/restore, architecture, and data locations
- **Measurability**: Every mandatory process rule must be enforceable through CI or hooks rather than documentation alone

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

## Languages

- Python 3.12 - Flask API, custom MCP server, ingestion adapters, plugin runtime, background worker, and migrations tooling under `backend/`; the production version is fixed by `Dockerfile`.
- TypeScript 5.9.3 (resolved; `^5.5.4` declared) - React PWA source under `frontend/src/`, configured by `frontend/tsconfig.json` and locked in `frontend/package-lock.json`.
- SQL / PL/pgSQL for PostgreSQL 17 - forward-only schema migrations, triggers, aggregates, and seed data in `backend/migrations/`.
- TSX / React JSX - pages and reusable UI in `frontend/src/pages/` and `frontend/src/components/`.
- CSS - design tokens and application styling in `frontend/src/styles/tokens.css` and `frontend/src/styles/app.css`.
- HTML - Vite application shell in `frontend/index.html`.
- YAML - Docker Compose, GitHub Actions, and Home Assistant automation in `docker-compose.yml`, `docker-compose.build.yml`, `.github/workflows/docker.yml`, and `homeassistant/watchvault_realtime.yaml`.
- Bash - container startup and migration orchestration in `deploy/entrypoint.sh`.
- Nginx and Supervisor configuration - reverse proxy and multi-process supervision in `deploy/nginx.conf` and `deploy/supervisord.conf`.

## Runtime

- Python 3.12 on Debian slim runs the Flask API, custom Flask-based MCP server, and background worker in `Dockerfile`.
- Node.js 20 Alpine is build-time only for the PWA in `Dockerfile`; production serves generated static assets through nginx.
- PostgreSQL 17 Alpine is the persistent database service in `docker-compose.yml`.
- Nginx and Supervisor are installed from Debian repositories without pinned package versions in `Dockerfile`.
- npm, version not pinned - frontend scripts and dependencies are declared in `frontend/package.json`.
- Lockfile: present as npm lockfile v3 at `frontend/package-lock.json`.
- pip, version not pinned - Python runtime and test requirements are declared in `backend/requirements.txt` and `backend/requirements-dev.txt`.
- Python lockfile: missing; dependencies use compatible version ranges in `backend/requirements.txt`.

## Frameworks

- Flask `>=3.0,<4` - application factory, HTTP API blueprints, error handling, and custom MCP HTTP service in `backend/app/__init__.py`, `backend/app/api/`, and `backend/server.py`.
- React 18.3.1 - browser UI and component model in `frontend/src/App.tsx`, `frontend/src/pages/`, and `frontend/src/components/`.
- React Router DOM 6.30.4 resolved (`^6.26.2` declared) - client-side navigation in `frontend/src/App.tsx`.
- PostgreSQL 17 with `pgcrypto` - relational system of record, UUID generation, JSONB configuration, triggers, and job queue in `docker-compose.yml` and `backend/migrations/0001_identity.sql`.
- Gunicorn `>=22.0` - production WSGI server with three workers and a 300-second timeout in `backend/requirements.txt` and `deploy/supervisord.conf`.
- Vite PWA / Workbox via `vite-plugin-pwa` 1.3.0 - service worker, install manifest, offline shell, API caching, and TMDB image caching in `frontend/vite.config.ts`.
- pytest `>=8.0` - backend unit tests in `backend/tests/`, declared in `backend/requirements-dev.txt`.
- No frontend test runner or browser E2E framework is declared in `frontend/package.json`.
- Vite 8.1.2 - development server on port 7212 and production frontend bundling in `frontend/vite.config.ts`.
- TypeScript project build (`tsc -b`) - strict type checking before Vite bundling via `frontend/package.json` and `frontend/tsconfig.json`.
- `@vitejs/plugin-react` 6.0.3 - React transformation for Vite in `frontend/vite.config.ts`.
- Docker multi-stage builds - Node frontend compilation followed by Python/nginx runtime assembly in `Dockerfile`.
- Docker Buildx and GitHub Actions - cached multi-platform-capable image build and GHCR publication in `.github/workflows/docker.yml`.

## Key Dependencies

- `psycopg[binary,pool]>=3.2` - PostgreSQL driver and process-local connection pool used by `backend/app/db.py`.
- `PyJWT>=2.9` - HS256 session token issuance and verification in `backend/app/auth/sessions.py`.
- `webauthn>=2.2,<3` - server-side WebAuthn registration and authentication ceremonies in `backend/app/auth/routes.py`.
- `@simplewebauthn/browser` 11.0.0 - browser passkey registration and login in `frontend/src/lib/auth.ts`.
- `requests>=2.32` - TMDB, Plex, Jellyfin, and Trakt HTTP clients in `plugins/tmdb/plugin.py` and `backend/app/ingest/adapters/`.
- React DOM 18.3.1 - browser rendering entry point in `frontend/src/main.tsx`.
- Recharts 2.15.4 resolved (`^2.12.7` declared) - dashboard and overview visualizations in `frontend/src/components/charts.tsx`.
- `gunicorn>=22.0` - API process hosting configured in `deploy/supervisord.conf`.
- `python-dotenv>=1.0` - installed as a runtime dependency in `backend/requirements.txt`; direct imports are not present in `backend/`.
- Nginx - serves `frontend/dist` output and proxies `/api` and `/mcp` in `deploy/nginx.conf`.
- Supervisor - runs Gunicorn, the MCP Flask process, the background worker, and nginx in `deploy/supervisord.conf`.
- Vite Workbox integration - applies `NetworkFirst` caching to statistics/search requests and `CacheFirst` caching to TMDB imagery in `frontend/vite.config.ts`.

## Configuration

- Central backend configuration is loaded from process environment by `backend/app/config.py`; use that module rather than reading environment variables in feature code.
- Runtime variables are `APP_ENV`, `LOG_LEVEL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`, `RP_ID`, `RP_NAME`, `RP_ORIGINS`, `SESSION_SECRET`, `SESSION_TTL_HOURS`, `REGISTRATION_INVITE_CODE`, `TMDB_API_KEY`, and `DATA_DIR` in `backend/app/config.py`.
- Plugin discovery additionally accepts `PLUGINS_DIR` in `backend/app/plugins/runtime.py`.
- Deployment accepts `WEB_PORT` and `DATA_PATH`, passes application configuration through `env_file: .env`, and substitutes database settings in `docker-compose.yml`.
- `.env.example` is present as the deployment template; `docker-compose.yml` expects a local `.env` at runtime, but no `.env` is present in this worktree.
- Vite development proxies `/api` to port 7200 and `/mcp` to port 7211 in `frontend/vite.config.ts`; production uses same-origin nginx routing in `deploy/nginx.conf`.
- `frontend/package.json` defines `dev`, `build`, and `preview`; production build is `tsc -b && vite build`.
- `frontend/tsconfig.json` targets ES2021, uses strict mode, bundler module resolution, React JSX, and no emit.
- `frontend/vite.config.ts` writes to `frontend/dist`, disables source maps, and splits React and chart vendor chunks.
- `Dockerfile` builds frontend assets with Node 20, installs `backend/requirements.txt`, then copies `backend/` and `plugins/` into the Python 3.12 runtime image.
- `deploy/entrypoint.sh` runs checksum-guarded SQL migrations before Supervisor starts any serving processes.
- `.github/workflows/docker.yml` builds on pushes to `main`, `release/**`, version tags, and manual dispatch.

## Platform Requirements

- Docker Engine 24+ with Docker Compose v2 is the documented full-stack path in `README.md`.
- Source-based frontend work requires Node.js 20-compatible tooling because the canonical builder is `node:20-alpine` in `Dockerfile`.
- Source-based backend work requires Python 3.12 and the packages in `backend/requirements.txt`; tests add `backend/requirements-dev.txt`.
- PostgreSQL must support `pgcrypto`, PL/pgSQL triggers, JSONB, `FOR UPDATE SKIP LOCKED`, and generated UUIDs used throughout `backend/migrations/`.
- Passkeys require `localhost` or HTTPS with matching `RP_ID` and `RP_ORIGINS`, as documented in `README.md` and enforced by `backend/app/auth/routes.py`.
- Target is a self-hosted Linux container deployment: one application image plus a PostgreSQL 17 container in `docker-compose.yml`.
- The application image is pulled from GHCR by default (`ghcr.io/helmerznl/watchvault:latest`) in `docker-compose.yml`, or built locally through `docker-compose.build.yml`.
- Only nginx port 7210 is intended for publication; Gunicorn port 7200 and MCP port 7211 stay internal behind `deploy/nginx.conf`.
- Persistent PostgreSQL and application media data are mounted beneath `DATA_PATH` by `docker-compose.yml`.
- A reverse proxy with HTTPS is required for non-localhost passkeys; deployment guidance is in `README.md`.

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

## Naming Patterns

- Use `snake_case.py` for Python modules, such as `backend/app/migrations_runner.py`, `backend/app/ingest/trakt_sync.py`, and `backend/app/api/titles_edit.py`.
- Name Python tests `test_<behavior-area>.py` under `backend/tests/`, for example `backend/tests/test_scrobble.py` and `backend/tests/test_title_key.py`.
- Use PascalCase for React component and page files, such as `frontend/src/components/ErrorBoundary.tsx` and `frontend/src/pages/TitleDetail.tsx`.
- Use camelCase for frontend library files, such as `frontend/src/lib/useFetch.ts` and `frontend/src/lib/lazyEnrich.ts`.
- Use lowercase language codes for locale modules, such as `frontend/src/locales/en.ts` and `frontend/src/locales/nl.ts`.
- Use `snake_case` for Python functions and route handlers: `compose_display_name`, `query_all`, and `create_connection` in `backend/app/api/profiles.py`, `backend/app/db.py`, and `backend/app/api/ingest.py`.
- Prefix non-public Python helpers with `_`, such as `_provider_by_key()` in `backend/app/api/ingest.py` and `_avatars_dir()` in `backend/app/api/profiles.py`.
- Use `camelCase` for TypeScript functions and callbacks: `applyTheme`, `refreshProfiles`, and `savePrefs` in `frontend/src/lib/app.tsx`.
- Name React hooks with the `use` prefix, as in `useApp()` in `frontend/src/lib/app.tsx`, `useT()` in `frontend/src/lib/i18n.tsx`, and `useFetch()` in `frontend/src/lib/useFetch.ts`.
- Name React components and exported visual helpers in PascalCase, as in `Dashboard`, `ErrorState`, and `RangeSeg` in `frontend/src/pages/Dashboard.tsx` and `frontend/src/components/ui.tsx`.
- Use `snake_case` for Python locals that map to domain or database fields, such as `provider_key`, `profile_id`, and `last_seen_at` in `backend/app/api/profiles.py` and `backend/app/api/ingest.py`.
- Use `camelCase` for TypeScript locals and state setters, such as `defaultProfile`, `setToastState`, and `recentRange` in `frontend/src/lib/app.tsx`, `frontend/src/pages/Settings.tsx`, and `frontend/src/pages/Dashboard.tsx`.
- Use leading underscores for intentionally private TypeScript/Python helpers or unused callback parameters, such as `_tmdb_plugin()` in `backend/tests/test_metadata.py` and `_t` in `frontend/src/lib/i18n.tsx`.
- Use `UPPER_SNAKE_CASE` for module constants: `DEFAULT_PREFS` in `backend/app/api/profiles.py`, `LIVE_MIN_WATCH_SECONDS` in `backend/app/ingest/scrobble.py`, and `LANGUAGES`/`DICTS` in `frontend/src/lib/i18n.tsx`.
- Use PascalCase for Python classes and dataclasses: `Config`, `NormalizedEvent`, and `SourceAdapter` in `backend/app/config.py`, `backend/app/ingest/models.py`, and `backend/app/ingest/adapters/base.py`.
- Use PascalCase for TypeScript interfaces and type aliases: `User`, `Prefs`, `DashboardLayout`, and `LangCode` in `frontend/src/lib/app.tsx` and `frontend/src/lib/i18n.tsx`.
- Keep backend-shaped frontend properties in `snake_case` (`display_name`, `household_id`, `is_admin`) in `frontend/src/lib/app.tsx`; these names deliberately mirror JSON returned by `backend/app/api/profiles.py`.
- Use string-literal unions for bounded UI state, as with `Range` in `frontend/src/components/ui.tsx` and `RecentRange`/`BlockId` in `frontend/src/pages/Dashboard.tsx`.

## Code Style

- No dedicated formatter configuration is present; `.prettierrc*`, `pyproject.toml`, `setup.cfg`, and `ruff.toml` are not detected.
- Format Python with four-space indentation, blank lines between top-level definitions, double-quoted strings by default, and manually wrapped calls/imports. Representative files are `backend/app/db.py` and `backend/app/api/ingest.py`.
- Format TypeScript/TSX with two-space indentation, double-quoted strings, semicolons, and trailing commas in multiline literals. Representative files are `frontend/src/lib/app.tsx` and `frontend/src/components/ErrorBoundary.tsx`.
- Keep compact expressions on one line only when they remain readable; multiline JSX props and Python SQL arguments are manually aligned in `frontend/src/components/ui.tsx` and `backend/app/api/profiles.py`.
- Use section-divider comments (`# ── ...` or `// ── ...`) in long domain modules and tests, as in `backend/app/util.py`, `backend/tests/test_scrobble.py`, and `frontend/src/lib/i18n.tsx`.
- No ESLint, Ruff, Flake8, Black, or Prettier runner/configuration is detected in the repository.
- Treat `frontend/tsconfig.json` as the enforced frontend quality gate: `strict`, `isolatedModules`, and `noFallthroughCasesInSwitch` are enabled.
- Do not assume unused symbols fail the build: `noUnusedLocals` and `noUnusedParameters` are explicitly disabled in `frontend/tsconfig.json`.
- Existing source uses targeted suppression comments such as `# noqa: E402` in `backend/tests/test_adapters.py`, `# noqa: BLE001` in `backend/app/api/ingest.py`, and `// eslint-disable-next-line react-hooks/exhaustive-deps` in `frontend/src/lib/useFetch.ts`; add suppressions only beside the intentional exception and explain why.
- Validate frontend changes through the `build` script in `frontend/package.json`, which runs `tsc -b` before Vite.

## Import Organization

- Not detected. `frontend/tsconfig.json` has no `paths` mapping; use explicit relative paths such as `../lib/api` and `../components/ui`.
- Python application code uses package-relative imports inside `backend/app/`, while entry points such as `backend/wsgi.py` import from the top-level `app` package.

## Error Handling

- Return Flask API validation failures as `jsonify({"error": ...}), <status>` close to the guard clause, as in `backend/app/api/ingest.py` and `backend/app/api/profiles.py`.
- Let unexpected exceptions reach the application-level handlers in `backend/app/__init__.py`; these log request context and return a stable JSON error envelope.
- Raise `ValueError` for invalid adapter configuration or parse input, then translate it to an HTTP response at the API boundary. Examples are `backend/app/ingest/adapters/base.py` and `backend/app/api/ingest.py`.
- Use `backend/app/db.py`'s `connection()` context manager for transactional work so success commits and exceptions roll back and re-raise.
- Catch broad exceptions only for explicitly best-effort behavior and annotate the reason with `# noqa: BLE001`, as in `backend/app/api/search.py`, `backend/app/networks.py`, and `backend/app/api/ingest.py`.
- On the frontend, route all API calls through `frontend/src/lib/api.ts`; non-2xx responses become `ApiError` instances carrying the status and server message.
- Use `useFetch()` from `frontend/src/lib/useFetch.ts` for load/error/reload state, and render `ErrorState` from `frontend/src/components/ui.tsx` for page-level failures.
- For user actions, catch errors locally and report them through `toast(..., "err")`, as in `frontend/src/pages/Settings.tsx`. Silent catches are reserved for best-effort refresh, logout, persistence, or recovery paths and include a clarifying comment.
- Keep `frontend/src/components/ErrorBoundary.tsx` around the React tree as the final render-error safety net; log the component stack and offer recovery rather than leaving a blank root.

## Logging

- Configure the Python log level once in `create_app()` in `backend/app/__init__.py`.
- Create module loggers with `logging.getLogger(__name__)`, as in `backend/app/api/ingest.py` and `backend/app/api/search.py`.
- Use `logger.exception()`/`app.logger.exception()` inside exception handlers when a traceback and request/domain context are useful.
- Keep expected 4xx validation responses quiet; `backend/app/__init__.py` logs HTTP exceptions only at 5xx.
- CLI/process entry points may use flushed `print()` for lifecycle output, as in `backend/app/migrations_runner.py` and `backend/worker.py`.
- Frontend business code has no remote logger. Use `console.error` only for uncaught render diagnostics, following `frontend/src/components/ErrorBoundary.tsx`.

## Comments

- Explain domain invariants, regression-sensitive behavior, and non-obvious fallbacks rather than restating syntax. Examples include title matching in `backend/app/util.py`, transactional deadlock guards in `backend/tests/test_scrobble.py`, and PWA recovery behavior in `frontend/src/components/ErrorBoundary.tsx`.
- Put short rationale comments beside best-effort catches, security boundaries, and intentionally unusual state behavior in `backend/app/api/ingest.py` and `frontend/src/lib/useFetch.ts`.
- Use section headers to make long modules navigable, but keep small modules free of decorative commentary.
- Python module, class, and complex helper docstrings are common and use concise prose plus occasional reStructuredText-style literals, as in `backend/app/ingest/adapters/base.py` and `backend/app/ingest/models.py`.
- Public TypeScript APIs generally rely on types and line comments rather than JSDoc. Preserve this pattern in `frontend/src/lib/app.tsx` and `frontend/src/components/ui.tsx`.

## Function Design

## Module Design

- Use `%s` placeholders and pass parameters separately; examples are `backend/app/db.py` and `backend/app/api/profiles.py`.
- Use `connection()` plus a cursor for multi-statement transactions, and `query_one`, `query_all`, or `execute` for isolated operations from `backend/app/db.py`.
- Preserve `dict_row` assumptions: production and fake cursors return mapping-like rows throughout `backend/app/` and `backend/tests/`.
- Keep application-wide auth, preferences, profiles, scope, permissions, and toasts in `AppProvider` at `frontend/src/lib/app.tsx`.
- Keep page-local interaction state in `useState`, server reads in `useFetch`, and reusable presentation in `frontend/src/components/`.
- Localize visible strings through `useT()`/`translate()` in `frontend/src/lib/i18n.tsx`; add matching keys to every module under `frontend/src/locales/`.

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

## System Overview

```text

```

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

- Keep deployment cohesive: nginx, API, MCP, and worker run as separate processes but ship from one image (`Dockerfile`, `deploy/supervisord.conf`).
- Keep HTTP modules thin enough to delegate reusable write workflows into domain modules; blueprints remain the transport boundary (`backend/app/api/`, `backend/app/ingest/`, `backend/app/catalog.py`).
- Normalize all provider input to `NormalizedEvent` before persistence, regardless of file import, API sync, or live scrobble source (`backend/app/ingest/models.py`, `backend/app/ingest/normalize.py`, `backend/app/ingest/scrobble.py`).
- Extend source ingestion through registered `SourceAdapter` classes and metadata through manifest-discovered plugins (`backend/app/ingest/adapters/base.py`, `backend/app/ingest/adapters/__init__.py`, `backend/app/plugins/runtime.py`).
- Treat PostgreSQL as the system of record, transaction manager, queue, aggregate engine, and revision source (`backend/app/db.py`, `backend/migrations/0004_plugins_jobs_audit.sql`, `backend/migrations/0005_aggregates.sql`, `backend/app/api/sync.py`).
- Scope user-facing reads and writes to the authenticated household/profile (`backend/app/api/_common.py`, `backend/app/auth/sessions.py`).

## Layers

- Purpose: Start migrations, supervise processes, serve static assets, and route external traffic.
- Location: `Dockerfile`, `deploy/entrypoint.sh`, `deploy/supervisord.conf`, `deploy/nginx.conf`
- Contains: Multi-stage image build, boot sequencing, Supervisor programs, nginx upstreams, upload limits, and SPA fallback.
- Depends on: Built assets from `frontend/dist/` and executable entry points in `backend/`.
- Used by: Browser/PWA clients, MCP clients, Docker Compose, and the GHCR image pipeline in `.github/workflows/docker.yml`.
- Purpose: Render authenticated household watch data and collect user actions.
- Location: `frontend/src/pages/`, `frontend/src/components/`, `frontend/src/styles/`
- Contains: Route pages, shared visual components, charts, layout editing, responsive shell, and CSS tokens.
- Depends on: State/data helpers in `frontend/src/lib/` and routes declared in `frontend/src/App.tsx`.
- Used by: The browser entry point `frontend/src/main.tsx`.
- Purpose: Centralize session state, profile scope, preferences, localization, formatting, and HTTP access.
- Location: `frontend/src/lib/`
- Contains: `AppProvider`, `api`, `useFetch`, WebAuthn helpers, i18n, branding, and formatting.
- Depends on: Browser APIs, React context/hooks, and `/api` endpoints.
- Used by: Pages and components under `frontend/src/pages/` and `frontend/src/components/`.
- Purpose: Expose JSON endpoints, validate input, enforce permissions, scope data, and shape response view models.
- Location: `backend/app/api/`, `backend/app/auth/`
- Contains: Flask blueprints, WebAuthn routes, JWT/API-token resolution, decorators, and shared API helpers.
- Depends on: Domain modules in `backend/app/`, transaction helpers in `backend/app/db.py`, and configuration in `backend/app/config.py`.
- Used by: Gunicorn via `backend/wsgi.py` and the PWA through `frontend/src/lib/api.ts`.
- Purpose: Implement ingestion, normalization, deduplication, title progress, metadata composition, tags, network attribution, and manual watch operations.
- Location: `backend/app/ingest/`, `backend/app/catalog.py`, `backend/app/networks.py`, `backend/app/genres.py`
- Contains: Provider-neutral dataclasses, transaction-aware workflows, catalog merge rules, and aggregate/progress maintenance.
- Depends on: SQL transactions from `backend/app/db.py`, provider adapters in `backend/app/ingest/adapters/`, and plugin enrichment in `backend/app/plugins/`.
- Used by: API routes in `backend/app/api/`, jobs in `backend/worker.py`, and live scrobbling in `backend/app/ingest/scrobble.py`.
- Purpose: Isolate provider-specific import/API behavior and external metadata capabilities.
- Location: `backend/app/ingest/adapters/`, `backend/app/plugins/`, `plugins/tmdb/`
- Contains: `SourceAdapter`, adapter registry/implementations, plugin discovery, plugin manifests, and enrichment orchestration.
- Depends on: `NormalizedEvent` in `backend/app/ingest/models.py`, shared catalog helpers in `backend/app/catalog.py`, and plugin code under `plugins/`.
- Used by: Ingestion routes in `backend/app/api/ingest.py` and jobs in `backend/worker.py`.
- Purpose: Own pooled connections, transaction boundaries, schema evolution, relational constraints, aggregate functions, and revision tracking.
- Location: `backend/app/db.py`, `backend/app/migrations_runner.py`, `backend/migrations/`
- Contains: psycopg helpers and ordered SQL migrations.
- Depends on: PostgreSQL configuration from `backend/app/config.py`.
- Used by: All backend processes, including `backend/wsgi.py`, `backend/worker.py`, and `backend/server.py`.

## Data Flow

### Primary Browser Request Path

### File Import and Normalization

### Scheduled Provider Sync

### Live Scrobble Path

### Metadata Enrichment

### Offline Revision Sync

- Browser session/profile/preferences/toasts live in React context; page request state lives in local hooks (`frontend/src/lib/app.tsx`, `frontend/src/lib/useFetch.ts`).
- Durable identity, domain, queue, aggregate, live-session, and sync state lives in PostgreSQL (`backend/migrations/0001_identity.sql`, `backend/migrations/0003_domain.sql`, `backend/migrations/0004_plugins_jobs_audit.sql`, `backend/migrations/0005_aggregates.sql`, `backend/migrations/0016_scrobble_sessions.sql`).
- Process-local caches are limited to configuration, connection pools, plugin manifests, and plugin instances (`backend/app/config.py`, `backend/app/db.py`, `backend/app/plugins/runtime.py`).

## Key Abstractions

- Purpose: Partition API transport concerns by feature.
- Examples: `backend/app/api/stats.py`, `backend/app/api/search.py`, `backend/app/api/ingest.py`, `backend/app/auth/routes.py`
- Pattern: Define `bp`, decorate routes, apply `require_auth`/`require_perm`, and register the module in `create_app()` (`backend/app/__init__.py`).
- Purpose: Represent one provider-neutral watch event before central persistence.
- Examples: `backend/app/ingest/models.py`, `backend/app/ingest/normalize.py`, `backend/app/ingest/scrobble.py`
- Pattern: Adapters/parsers populate a dataclass; only normalization resolves catalog entities and inserts deduplicated events.
- Purpose: Isolate file/API source behavior behind one provider contract.
- Examples: `backend/app/ingest/adapters/base.py`, `backend/app/ingest/adapters/netflix.py`, `backend/app/ingest/adapters/plex.py`, `backend/app/ingest/adapters/trakt.py`
- Pattern: Subclass `SourceAdapter`, implement supported operations, and register one instance in `backend/app/ingest/adapters/__init__.py`.
- Purpose: Add metadata services without coupling enrichment orchestration to a concrete SDK.
- Examples: `plugins/tmdb/manifest.json`, `plugins/tmdb/plugin.py`, `backend/app/plugins/runtime.py`
- Pattern: Discover `manifest.json`, load sibling `plugin.py`, instantiate `Plugin(settings, secrets)`, and dispatch by declared capability.
- Purpose: Make commit-on-success and rollback-on-error the default persistence boundary.
- Examples: `backend/app/db.py`, `backend/app/ingest/normalize.py`, `backend/app/catalog.py`
- Pattern: Use `with connection() as conn, conn.cursor() as cur`; pass `cur` into multi-step domain operations that must share locks and atomicity.
- Purpose: Decouple slow synchronization/enrichment from request handling.
- Examples: `backend/worker.py`, `backend/migrations/0004_plugins_jobs_audit.sql`
- Pattern: Insert JSON payloads into `background_jobs`, claim with row locks and `SKIP LOCKED`, then mark done, retry, or error.
- Purpose: Separate durable global UI state from page-scoped remote request state.
- Examples: `frontend/src/lib/app.tsx`, `frontend/src/lib/useFetch.ts`, `frontend/src/pages/Dashboard.tsx`
- Pattern: Put auth/profile/preferences in context; keep endpoint-specific data in `useFetch` within pages.

## Entry Points

- Location: `deploy/entrypoint.sh`
- Triggers: Docker image startup from `Dockerfile`.
- Responsibilities: Run `backend/migrate.py` before serving traffic, then exec Supervisor.
- Location: `backend/wsgi.py`
- Triggers: Gunicorn command in `deploy/supervisord.conf`.
- Responsibilities: Construct the Flask application through `backend/app/__init__.py:create_app`.
- Location: `backend/worker.py`
- Triggers: Supervisor process in `deploy/supervisord.conf`.
- Responsibilities: Schedule, claim, execute, retry, and complete database-backed jobs; expire stale scrobbles.
- Location: `backend/server.py`
- Triggers: Supervisor process or direct `python backend/server.py --http`.
- Responsibilities: Serve JSON-RPC initialize/tool operations and health over `/mcp`/`/`.
- Location: `frontend/src/main.tsx`
- Triggers: Browser loading `frontend/index.html`.
- Responsibilities: Mount the React PWA and install global providers.
- Location: `backend/migrate.py`
- Triggers: `deploy/entrypoint.sh` or direct Python execution.
- Responsibilities: Delegate to checksum-guarded migration execution in `backend/app/migrations_runner.py`.
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

### Duplicated MCP Authentication

### Bypassing the Normalized Ingestion Spine

## Error Handling

- Flask HTTP exceptions become `{error, message}` responses; unhandled errors are logged with method/path and hide details in production (`backend/app/__init__.py:56`).
- Permission decorators return explicit 401/403 JSON before invoking route logic (`backend/app/auth/sessions.py:116`, `backend/app/auth/sessions.py:126`).
- `connection()` commits on success and rolls back/re-raises on failure (`backend/app/db.py:29`).
- Parse/validation failures that are expected client input errors are caught near the route and returned as 400 responses (`backend/app/api/ingest.py:81`).
- Background jobs record `last_error`, retry after 60 seconds, and become `error` after `max_attempts` (`backend/worker.py:46`).
- The worker's outer loop catches all exceptions so one failed poll cannot terminate processing (`backend/worker.py:161`).
- Frontend HTTP failures become `ApiError`; `useFetch` exposes error/retry while silent refresh preserves existing data (`frontend/src/lib/api.ts`, `frontend/src/lib/useFetch.ts`).

## Cross-Cutting Concerns

<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.github/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
