# Codebase Structure

**Analysis Date:** 2026-07-21

## Directory Layout

```text
WatchVault/
├── .github/
│   └── workflows/
│       └── docker.yml                 # Build and publish the application image
├── .planning/
│   └── codebase/                      # GSD codebase reference documents
├── backend/
│   ├── app/
│   │   ├── api/                       # Flask feature blueprints and API helpers
│   │   ├── auth/                      # WebAuthn, session, token, and RBAC handling
│   │   ├── ingest/
│   │   │   └── adapters/              # Provider adapter contract and implementations
│   │   ├── plugins/                   # Plugin discovery and enrichment orchestration
│   │   ├── __init__.py                # Flask application factory
│   │   ├── catalog.py                 # Shared catalog merge/provenance rules
│   │   ├── config.py                  # Environment-backed configuration
│   │   ├── db.py                      # psycopg pool and transaction helpers
│   │   ├── genres.py                  # Genre canonicalization
│   │   ├── migrations_runner.py       # Ordered migration executor
│   │   ├── networks.py                # Provider/network attribution logic
│   │   └── util.py                    # Shared normalization/hash/time utilities
│   ├── migrations/                    # Forward-only numbered PostgreSQL migrations
│   ├── tests/                         # Python unit and behavior tests
│   ├── migrate.py                     # Migration CLI
│   ├── server.py                      # Standalone MCP JSON-RPC process
│   ├── worker.py                      # Database-backed background worker
│   ├── wsgi.py                        # Gunicorn API entry point
│   ├── requirements.txt               # Runtime Python dependencies
│   └── requirements-dev.txt           # Development/test Python dependencies
├── deploy/
│   ├── entrypoint.sh                  # Migrate-before-serve container bootstrap
│   ├── nginx.conf                     # Static host and API/MCP reverse proxy
│   └── supervisord.conf               # API, MCP, worker, and nginx process definitions
├── docs/
│   └── screenshots/
│       ├── desktop/                    # Desktop product screenshots
│       └── mobile/                     # Mobile product screenshots
├── frontend/
│   ├── public/                         # PWA icons and static public assets
│   ├── src/
│   │   ├── components/                 # Shared and feature-level React components
│   │   ├── lib/                        # API, state, auth, i18n, formatting, hooks
│   │   ├── locales/                    # Per-language translation dictionaries
│   │   ├── pages/                      # Browser route components
│   │   ├── styles/                     # Design tokens and application CSS
│   │   ├── App.tsx                     # Auth gate and route table
│   │   └── main.tsx                    # React browser entry point
│   ├── index.html                      # Vite HTML entry
│   ├── package.json                    # Frontend scripts/dependencies
│   ├── package-lock.json               # Locked npm dependency graph
│   ├── tsconfig.json                   # Browser TypeScript project
│   ├── tsconfig.node.json              # Vite config TypeScript project
│   └── vite.config.ts                  # React/PWA/build/dev-proxy configuration
├── homeassistant/
│   └── watchvault_realtime.yaml        # Live scrobble automation blueprint
├── plugins/
│   └── tmdb/
│       ├── manifest.json               # Metadata capability declaration
│       └── plugin.py                   # TMDB plugin implementation
├── sample-data/                        # Example provider imports
├── Dockerfile                          # Frontend-build/runtime multi-stage image
├── docker-compose.yml                  # Published image + PostgreSQL deployment
├── docker-compose.build.yml            # Local image-build override
├── README.md                           # Product, deployment, integration, and dev guide
└── .gitignore                          # Generated, local, data, and environment exclusions
```

## Directory Purposes

**`.github/`:**
- Purpose: Repository automation.
- Contains: GitHub Actions workflow YAML.
- Key files: `.github/workflows/docker.yml`

**`.planning/codebase/`:**
- Purpose: Persist architecture, structure, stack, convention, testing, integration, and concern maps for GSD workflows.
- Contains: Uppercase Markdown reference documents.
- Key files: `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`

**`backend/`:**
- Purpose: Host all Python runtime processes, backend dependencies, SQL migrations, and backend tests.
- Contains: Flask application package, MCP server, queue worker, migration CLI, WSGI entry, requirements, migrations, and tests.
- Key files: `backend/wsgi.py`, `backend/server.py`, `backend/worker.py`, `backend/migrate.py`, `backend/requirements.txt`

**`backend/app/api/`:**
- Purpose: Define REST endpoints by feature and shape API view models.
- Contains: Flask blueprint modules plus shared scoping/image helpers.
- Key files: `backend/app/api/_common.py`, `backend/app/api/stats.py`, `backend/app/api/search.py`, `backend/app/api/ingest.py`, `backend/app/api/scrobble.py`, `backend/app/api/sync.py`

**`backend/app/auth/`:**
- Purpose: Implement authentication and authorization boundaries.
- Contains: WebAuthn registration/login/recovery/OAuth routes and session/API-token resolution/decorators.
- Key files: `backend/app/auth/routes.py`, `backend/app/auth/sessions.py`

**`backend/app/ingest/`:**
- Purpose: Convert imports, API histories, manual actions, and live playback into the central watch model.
- Contains: Provider-neutral models, normalization/deduplication, manual writes, progress, scrobbling, Trakt cross-sync, and adapters.
- Key files: `backend/app/ingest/models.py`, `backend/app/ingest/normalize.py`, `backend/app/ingest/manual.py`, `backend/app/ingest/scrobble.py`, `backend/app/ingest/progress.py`, `backend/app/ingest/trakt_sync.py`

**`backend/app/ingest/adapters/`:**
- Purpose: Isolate provider-specific import and remote-history behavior.
- Contains: The `SourceAdapter` contract, registry, and Netflix/generic/cinema/Plex/Jellyfin/Trakt implementations.
- Key files: `backend/app/ingest/adapters/base.py`, `backend/app/ingest/adapters/__init__.py`, `backend/app/ingest/adapters/netflix.py`, `backend/app/ingest/adapters/plex.py`, `backend/app/ingest/adapters/trakt.py`

**`backend/app/plugins/`:**
- Purpose: Discover metadata plugins and orchestrate title/person enrichment.
- Contains: Folder/manifest runtime and catalog enrichment workflows.
- Key files: `backend/app/plugins/runtime.py`, `backend/app/plugins/enrich.py`

**`backend/migrations/`:**
- Purpose: Define the complete PostgreSQL schema and forward-only evolution.
- Contains: Ordered `NNNN_description.sql` files for identity, RBAC, domain data, jobs, aggregates, sync revisions, scrobbling, progress, tags, and manual overrides.
- Key files: `backend/migrations/0001_identity.sql`, `backend/migrations/0003_domain.sql`, `backend/migrations/0004_plugins_jobs_audit.sql`, `backend/migrations/0005_aggregates.sql`, `backend/migrations/0016_scrobble_sessions.sql`, `backend/migrations/0023_tags_and_unknown.sql`

**`backend/tests/`:**
- Purpose: Verify adapters and backend domain/endpoint behavior.
- Contains: `pytest` modules named after tested features.
- Key files: `backend/tests/test_adapters.py`, `backend/tests/test_scrobble.py`, `backend/tests/test_metadata.py`, `backend/tests/test_stats.py`

**`frontend/`:**
- Purpose: Build the installable browser PWA.
- Contains: Vite/TypeScript configuration, npm manifests, public assets, and React source.
- Key files: `frontend/package.json`, `frontend/vite.config.ts`, `frontend/index.html`, `frontend/src/main.tsx`

**`frontend/src/pages/`:**
- Purpose: Implement route-level screens and feature data orchestration.
- Contains: Named React function components for dashboard, overviews, search, imports, profiles, settings, and entity details.
- Key files: `frontend/src/pages/Dashboard.tsx`, `frontend/src/pages/Imports.tsx`, `frontend/src/pages/Settings.tsx`, `frontend/src/pages/TitleDetail.tsx`

**`frontend/src/components/`:**
- Purpose: Provide reusable layout, controls, visualizations, and feature widgets.
- Contains: PascalCase components plus consolidated lower-case icon/chart/UI modules.
- Key files: `frontend/src/components/Layout.tsx`, `frontend/src/components/ui.tsx`, `frontend/src/components/charts.tsx`, `frontend/src/components/WatchedGrid.tsx`

**`frontend/src/lib/`:**
- Purpose: Centralize non-visual frontend infrastructure and shared helpers.
- Contains: HTTP client, app context, WebAuthn API, translations, formatting, branding, lazy enrichment, and fetch hooks.
- Key files: `frontend/src/lib/api.ts`, `frontend/src/lib/app.tsx`, `frontend/src/lib/auth.ts`, `frontend/src/lib/i18n.tsx`, `frontend/src/lib/useFetch.ts`

**`frontend/src/locales/`:**
- Purpose: Store complete translation dictionaries per supported language.
- Contains: Lowercase ISO-language TypeScript modules.
- Key files: `frontend/src/locales/en.ts`, `frontend/src/locales/nl.ts`, `frontend/src/locales/de.ts`, `frontend/src/locales/fr.ts`, `frontend/src/locales/es.ts`, `frontend/src/locales/it.ts`

**`frontend/src/styles/`:**
- Purpose: Define design variables and global component/page styling.
- Contains: CSS custom-property tokens and application styles.
- Key files: `frontend/src/styles/tokens.css`, `frontend/src/styles/app.css`

**`deploy/`:**
- Purpose: Assemble and run the production application processes inside the container.
- Contains: Startup script, nginx routing, and Supervisor program definitions.
- Key files: `deploy/entrypoint.sh`, `deploy/nginx.conf`, `deploy/supervisord.conf`

**`plugins/`:**
- Purpose: Host discoverable metadata provider implementations outside the core application package.
- Contains: One directory per plugin, each with `manifest.json` and `plugin.py`.
- Key files: `plugins/tmdb/manifest.json`, `plugins/tmdb/plugin.py`

**`homeassistant/`:**
- Purpose: Integrate external media-player state with the generic scrobble API.
- Contains: A reusable Home Assistant automation blueprint.
- Key files: `homeassistant/watchvault_realtime.yaml`

**`sample-data/`:**
- Purpose: Provide safe examples for import development and manual verification.
- Contains: CSV and JSON files matching supported file-adapter formats.
- Key files: `sample-data/netflix-viewing-activity.csv`, `sample-data/hbomax-generic.csv`, `sample-data/videoland-generic.json`

**`docs/screenshots/`:**
- Purpose: Supply README/product visuals for desktop and mobile layouts.
- Contains: Numbered PNG/JPG screenshots.
- Key files: `docs/screenshots/desktop/01-dashboard.png`, `docs/screenshots/mobile/01-dashboard.jpg`

## Key File Locations

**Entry Points:**
- `frontend/src/main.tsx`: Mounts the browser application.
- `frontend/src/App.tsx`: Declares authenticated routes and the login gate.
- `backend/wsgi.py`: Creates the production Flask API app for Gunicorn.
- `backend/worker.py`: Starts queue polling and scheduled background work.
- `backend/server.py`: Starts the standalone MCP HTTP/JSON-RPC process.
- `backend/migrate.py`: Starts migration execution.
- `deploy/entrypoint.sh`: Runs migrations and launches Supervisor.

**Configuration:**
- `backend/app/config.py`: Reads runtime environment configuration.
- `frontend/vite.config.ts`: Configures React, PWA behavior, bundles, and development proxies.
- `frontend/tsconfig.json`: Configures the browser TypeScript project.
- `frontend/tsconfig.node.json`: Configures TypeScript for Vite configuration code.
- `Dockerfile`: Defines frontend build and Python/nginx runtime stages.
- `docker-compose.yml`: Defines application/PostgreSQL production-style services.
- `docker-compose.build.yml`: Switches the app service to a local build.
- `deploy/nginx.conf`: Defines public routes, static serving, and upstreams.
- `deploy/supervisord.conf`: Defines all long-running application processes.
- `.github/workflows/docker.yml`: Defines image build/publish automation.

**Core Logic:**
- `backend/app/__init__.py`: Flask factory and blueprint composition root.
- `backend/app/db.py`: Connection pool and transaction boundary.
- `backend/app/auth/sessions.py`: Request identity and permission decorators.
- `backend/app/ingest/normalize.py`: Central title/event resolution, deduplication, aggregation, and enrichment queueing.
- `backend/app/ingest/scrobble.py`: Live playback normalization/session handling.
- `backend/app/catalog.py`: Metadata composition and catalog identity.
- `backend/app/networks.py`: Streaming provider attribution.
- `backend/app/plugins/runtime.py`: Plugin discovery/loading.
- `backend/app/plugins/enrich.py`: Metadata enrichment orchestration.
- `frontend/src/lib/app.tsx`: Global browser state.
- `frontend/src/lib/api.ts`: HTTP transport.
- `frontend/src/lib/useFetch.ts`: Page-level remote data lifecycle.

**API Routing:**
- `backend/app/api/meta.py`: Health and public metadata.
- `backend/app/api/stats.py`: Dashboard/overview analytics.
- `backend/app/api/search.py`: Catalog search and title detail.
- `backend/app/api/ingest.py`: Imports, connections, syncs, and manual watch operations.
- `backend/app/api/profiles.py`: Household profiles, preferences, settings, and API tokens.
- `backend/app/api/scrobble.py`: Push scrobble, now-playing, progress, and account mapping.
- `backend/app/api/tags.py`: Tag CRUD and entity links.
- `backend/app/api/titles_edit.py`: Manual title kind/name/poster overrides.
- `backend/app/api/sync.py`: Revision-based incremental synchronization.

**Database:**
- `backend/app/migrations_runner.py`: Checksum-guarded migration runner.
- `backend/migrations/0001_identity.sql`: Household, user, credential, session, challenge, and OAuth foundation.
- `backend/migrations/0002_rbac_prefs.sql`: Permissions, roles, settings, and preferences.
- `backend/migrations/0003_domain.sql`: Providers, connections, catalog, and watch events.
- `backend/migrations/0004_plugins_jobs_audit.sql`: Plugins, API clients, jobs, domain events, and audit.
- `backend/migrations/0005_aggregates.sql`: Daily watch aggregate.

**Testing:**
- `backend/tests/`: All detected automated test modules.
- `backend/requirements-dev.txt`: Test/development dependencies.
- Frontend automated tests are not present under `frontend/src/`; route/page changes currently rely on build validation and manual verification (`frontend/package.json`).

## Naming Conventions

**Files:**
- Use `snake_case.py` for Python modules: `backend/app/migrations_runner.py`, `backend/app/ingest/trakt_sync.py`.
- Use `test_<feature>.py` for Python tests: `backend/tests/test_scrobble.py`, `backend/tests/test_title_key.py`.
- Use `<provider>.py` for adapter implementations and register the class centrally: `backend/app/ingest/adapters/jellyfin.py`, `backend/app/ingest/adapters/__init__.py`.
- Use `NNNN_snake_case.sql` for forward-only migrations: `backend/migrations/0016_scrobble_sessions.sql`.
- Use `PascalCase.tsx` for route pages and most named React components: `frontend/src/pages/TitleDetail.tsx`, `frontend/src/components/ErrorBoundary.tsx`.
- Use lowercase/camel-like utility filenames for shared frontend modules: `frontend/src/lib/useFetch.ts`, `frontend/src/lib/lazyEnrich.ts`, `frontend/src/components/ui.tsx`.
- Use lowercase two-letter locale filenames: `frontend/src/locales/en.ts`, `frontend/src/locales/nl.ts`.
- Use numbered screenshot names so README order remains stable: `docs/screenshots/desktop/01-dashboard.png`.
- Use `manifest.json` plus `plugin.py` inside each lowercase plugin directory: `plugins/tmdb/manifest.json`, `plugins/tmdb/plugin.py`.

**Directories:**
- Use lowercase feature or technology names: `backend/app/ingest/`, `frontend/src/components/`, `homeassistant/`.
- Keep Python package directories marked by `__init__.py`: `backend/app/`, `backend/app/api/`, `backend/app/auth/`, `backend/app/ingest/`.
- Keep external plugins one directory per plugin ID: `plugins/tmdb/`.
- Keep screenshots grouped by target form factor: `docs/screenshots/desktop/`, `docs/screenshots/mobile/`.

## Where to Add New Code

**New Backend API Feature:**
- Primary route code: `backend/app/api/<feature>.py`
- Registration: add the blueprint import and `app.register_blueprint(...)` call in `backend/app/__init__.py`
- Reusable domain logic: `backend/app/<feature>.py` or `backend/app/<feature>/`
- Shared household/profile helpers: extend `backend/app/api/_common.py` only when the helper is transport-specific.
- Tests: `backend/tests/test_<feature>.py`

**New Provider Adapter:**
- Contract implementation: `backend/app/ingest/adapters/<provider>.py`
- Registry: `backend/app/ingest/adapters/__init__.py`
- Provider catalog/schema seed: a new migration under `backend/migrations/NNNN_<provider>.sql`
- Parsing/behavior tests: `backend/tests/test_adapters.py` or `backend/tests/test_<provider>.py`
- Sample import data when useful: `sample-data/<provider>-<format>.<ext>`

**New Metadata Plugin:**
- Manifest: `plugins/<plugin-id>/manifest.json`
- Implementation: `plugins/<plugin-id>/plugin.py`
- Runtime changes only for a new plugin contract/capability: `backend/app/plugins/runtime.py`
- Shared catalog merge behavior: `backend/app/catalog.py`
- Enrichment orchestration: `backend/app/plugins/enrich.py`
- Tests: `backend/tests/test_metadata.py` or `backend/tests/test_<plugin-id>.py`

**New Database Entity or Constraint:**
- Schema change: add the next immutable `backend/migrations/NNNN_description.sql`
- Data access: keep parameterized SQL near the owning domain module under `backend/app/`
- API exposure: add/extend a blueprint under `backend/app/api/`
- Tests: add a focused module under `backend/tests/`

**New Frontend Route/Page:**
- Page: `frontend/src/pages/<Feature>.tsx`
- Route import/declaration: `frontend/src/App.tsx`
- Navigation when global: `frontend/src/components/Layout.tsx`
- API calls/state: use `frontend/src/lib/api.ts` and `frontend/src/lib/useFetch.ts`
- Translations: add matching keys to every module in `frontend/src/locales/`
- Styling: reusable variables in `frontend/src/styles/tokens.css`; global feature styles in `frontend/src/styles/app.css`

**New React Component:**
- Shared or feature widget: `frontend/src/components/<Component>.tsx`
- Route-only composition: keep it with the owning page in `frontend/src/pages/<Feature>.tsx` unless reused.
- Generic primitives/icons/charts: extend `frontend/src/components/ui.tsx`, `frontend/src/components/icons.tsx`, or `frontend/src/components/charts.tsx`.

**New Frontend Utility:**
- HTTP/auth/state/i18n/format helper: `frontend/src/lib/<utility>.ts` or `frontend/src/lib/<utility>.tsx`
- Keep visual behavior in `frontend/src/components/`, not `frontend/src/lib/`.

**New Background Job:**
- Producer: insert the job from its owning domain/API module under `backend/app/`.
- Dispatcher: add the job kind to `_handle` in `backend/worker.py`.
- Handler: place reusable work in the owning domain module, not directly in `backend/worker.py`.
- Schema changes when required: `backend/migrations/NNNN_<job>.sql`
- Tests: `backend/tests/test_<domain>.py`

**New Home Assistant Behavior:**
- Blueprint changes: `homeassistant/watchvault_realtime.yaml`
- Generic payload parsing/platform mapping: `backend/app/ingest/scrobble.py`
- API transport behavior: `backend/app/api/scrobble.py`
- Tests: `backend/tests/test_scrobble.py`

## Special Directories

**`.planning/`:**
- Purpose: GSD project/codebase metadata.
- Generated: Yes, by GSD workflows.
- Committed: Intended to be committed; it is not excluded by `.gitignore`.

**`backend/migrations/`:**
- Purpose: Ordered database history and schema source of truth.
- Generated: No.
- Committed: Yes.

**`frontend/public/`:**
- Purpose: Static files copied directly into the Vite build and PWA manifest.
- Generated: No.
- Committed: Yes.

**`frontend/dist/`:**
- Purpose: Production frontend output served from `/app/web` in the image.
- Generated: Yes, by `npm run build` and the frontend stage in `Dockerfile`.
- Committed: No; excluded by `.gitignore`.

**`frontend/tsconfig.tsbuildinfo` and `frontend/tsconfig.node.tsbuildinfo`:**
- Purpose: TypeScript incremental build metadata.
- Generated: Yes.
- Committed: Yes in the current repository, despite being build artifacts.

**`plugins/`:**
- Purpose: Runtime-discovered metadata provider folders.
- Generated: No.
- Committed: Yes.

**`sample-data/`:**
- Purpose: Example imports for development and documentation.
- Generated: No.
- Committed: Yes.

**`docs/screenshots/`:**
- Purpose: Product screenshots referenced by `README.md`.
- Generated: No.
- Committed: Yes.

**`data/`:**
- Purpose: Runtime persistent data mounted at `/data`.
- Generated: Yes, at deployment/runtime.
- Committed: No; excluded by `.gitignore`.

**`.env`:**
- Purpose: Local/deployment environment configuration.
- Generated: User-created.
- Committed: No; excluded by `.gitignore`. Its contents must not be copied into code or planning documents.

---

*Structure analysis: 2026-07-21*
