# Technology Stack

**Analysis Date:** 2026-07-21

## Languages

**Primary:**
- Python 3.12 - Flask API, custom MCP server, ingestion adapters, plugin runtime, background worker, and migrations tooling under `backend/`; the production version is fixed by `Dockerfile`.
- TypeScript 5.9.3 (resolved; `^5.5.4` declared) - React PWA source under `frontend/src/`, configured by `frontend/tsconfig.json` and locked in `frontend/package-lock.json`.
- SQL / PL/pgSQL for PostgreSQL 17 - forward-only schema migrations, triggers, aggregates, and seed data in `backend/migrations/`.

**Secondary:**
- TSX / React JSX - pages and reusable UI in `frontend/src/pages/` and `frontend/src/components/`.
- CSS - design tokens and application styling in `frontend/src/styles/tokens.css` and `frontend/src/styles/app.css`.
- HTML - Vite application shell in `frontend/index.html`.
- YAML - Docker Compose, GitHub Actions, and Home Assistant automation in `docker-compose.yml`, `docker-compose.build.yml`, `.github/workflows/docker.yml`, and `homeassistant/watchvault_realtime.yaml`.
- Bash - container startup and migration orchestration in `deploy/entrypoint.sh`.
- Nginx and Supervisor configuration - reverse proxy and multi-process supervision in `deploy/nginx.conf` and `deploy/supervisord.conf`.

## Runtime

**Environment:**
- Python 3.12 on Debian slim runs the Flask API, custom Flask-based MCP server, and background worker in `Dockerfile`.
- Node.js 20 Alpine is build-time only for the PWA in `Dockerfile`; production serves generated static assets through nginx.
- PostgreSQL 17 Alpine is the persistent database service in `docker-compose.yml`.
- Nginx and Supervisor are installed from Debian repositories without pinned package versions in `Dockerfile`.

**Package Manager:**
- npm, version not pinned - frontend scripts and dependencies are declared in `frontend/package.json`.
- Lockfile: present as npm lockfile v3 at `frontend/package-lock.json`.
- pip, version not pinned - Python runtime and test requirements are declared in `backend/requirements.txt` and `backend/requirements-dev.txt`.
- Python lockfile: missing; dependencies use compatible version ranges in `backend/requirements.txt`.

## Frameworks

**Core:**
- Flask `>=3.0,<4` - application factory, HTTP API blueprints, error handling, and custom MCP HTTP service in `backend/app/__init__.py`, `backend/app/api/`, and `backend/server.py`.
- React 18.3.1 - browser UI and component model in `frontend/src/App.tsx`, `frontend/src/pages/`, and `frontend/src/components/`.
- React Router DOM 6.30.4 resolved (`^6.26.2` declared) - client-side navigation in `frontend/src/App.tsx`.
- PostgreSQL 17 with `pgcrypto` - relational system of record, UUID generation, JSONB configuration, triggers, and job queue in `docker-compose.yml` and `backend/migrations/0001_identity.sql`.
- Gunicorn `>=22.0` - production WSGI server with three workers and a 300-second timeout in `backend/requirements.txt` and `deploy/supervisord.conf`.
- Vite PWA / Workbox via `vite-plugin-pwa` 1.3.0 - service worker, install manifest, offline shell, API caching, and TMDB image caching in `frontend/vite.config.ts`.

**Testing:**
- pytest `>=8.0` - backend unit tests in `backend/tests/`, declared in `backend/requirements-dev.txt`.
- No frontend test runner or browser E2E framework is declared in `frontend/package.json`.

**Build/Dev:**
- Vite 8.1.2 - development server on port 7212 and production frontend bundling in `frontend/vite.config.ts`.
- TypeScript project build (`tsc -b`) - strict type checking before Vite bundling via `frontend/package.json` and `frontend/tsconfig.json`.
- `@vitejs/plugin-react` 6.0.3 - React transformation for Vite in `frontend/vite.config.ts`.
- Docker multi-stage builds - Node frontend compilation followed by Python/nginx runtime assembly in `Dockerfile`.
- Docker Buildx and GitHub Actions - cached multi-platform-capable image build and GHCR publication in `.github/workflows/docker.yml`.

## Key Dependencies

**Critical:**
- `psycopg[binary,pool]>=3.2` - PostgreSQL driver and process-local connection pool used by `backend/app/db.py`.
- `PyJWT>=2.9` - HS256 session token issuance and verification in `backend/app/auth/sessions.py`.
- `webauthn>=2.2,<3` - server-side WebAuthn registration and authentication ceremonies in `backend/app/auth/routes.py`.
- `@simplewebauthn/browser` 11.0.0 - browser passkey registration and login in `frontend/src/lib/auth.ts`.
- `requests>=2.32` - TMDB, Plex, Jellyfin, and Trakt HTTP clients in `plugins/tmdb/plugin.py` and `backend/app/ingest/adapters/`.
- React DOM 18.3.1 - browser rendering entry point in `frontend/src/main.tsx`.
- Recharts 2.15.4 resolved (`^2.12.7` declared) - dashboard and overview visualizations in `frontend/src/components/charts.tsx`.

**Infrastructure:**
- `gunicorn>=22.0` - API process hosting configured in `deploy/supervisord.conf`.
- `python-dotenv>=1.0` - installed as a runtime dependency in `backend/requirements.txt`; direct imports are not present in `backend/`.
- Nginx - serves `frontend/dist` output and proxies `/api` and `/mcp` in `deploy/nginx.conf`.
- Supervisor - runs Gunicorn, the MCP Flask process, the background worker, and nginx in `deploy/supervisord.conf`.
- Vite Workbox integration - applies `NetworkFirst` caching to statistics/search requests and `CacheFirst` caching to TMDB imagery in `frontend/vite.config.ts`.

## Configuration

**Environment:**
- Central backend configuration is loaded from process environment by `backend/app/config.py`; use that module rather than reading environment variables in feature code.
- Runtime variables are `APP_ENV`, `LOG_LEVEL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`, `RP_ID`, `RP_NAME`, `RP_ORIGINS`, `SESSION_SECRET`, `SESSION_TTL_HOURS`, `REGISTRATION_INVITE_CODE`, `TMDB_API_KEY`, and `DATA_DIR` in `backend/app/config.py`.
- Plugin discovery additionally accepts `PLUGINS_DIR` in `backend/app/plugins/runtime.py`.
- Deployment accepts `WEB_PORT` and `DATA_PATH`, passes application configuration through `env_file: .env`, and substitutes database settings in `docker-compose.yml`.
- `.env.example` is present as the deployment template; `docker-compose.yml` expects a local `.env` at runtime, but no `.env` is present in this worktree.
- Vite development proxies `/api` to port 7200 and `/mcp` to port 7211 in `frontend/vite.config.ts`; production uses same-origin nginx routing in `deploy/nginx.conf`.

**Build:**
- `frontend/package.json` defines `dev`, `build`, and `preview`; production build is `tsc -b && vite build`.
- `frontend/tsconfig.json` targets ES2021, uses strict mode, bundler module resolution, React JSX, and no emit.
- `frontend/vite.config.ts` writes to `frontend/dist`, disables source maps, and splits React and chart vendor chunks.
- `Dockerfile` builds frontend assets with Node 20, installs `backend/requirements.txt`, then copies `backend/` and `plugins/` into the Python 3.12 runtime image.
- `deploy/entrypoint.sh` runs checksum-guarded SQL migrations before Supervisor starts any serving processes.
- `.github/workflows/docker.yml` builds on pushes to `main`, `release/**`, version tags, and manual dispatch.

## Platform Requirements

**Development:**
- Docker Engine 24+ with Docker Compose v2 is the documented full-stack path in `README.md`.
- Source-based frontend work requires Node.js 20-compatible tooling because the canonical builder is `node:20-alpine` in `Dockerfile`.
- Source-based backend work requires Python 3.12 and the packages in `backend/requirements.txt`; tests add `backend/requirements-dev.txt`.
- PostgreSQL must support `pgcrypto`, PL/pgSQL triggers, JSONB, `FOR UPDATE SKIP LOCKED`, and generated UUIDs used throughout `backend/migrations/`.
- Passkeys require `localhost` or HTTPS with matching `RP_ID` and `RP_ORIGINS`, as documented in `README.md` and enforced by `backend/app/auth/routes.py`.

**Production:**
- Target is a self-hosted Linux container deployment: one application image plus a PostgreSQL 17 container in `docker-compose.yml`.
- The application image is pulled from GHCR by default (`ghcr.io/helmerznl/watchvault:latest`) in `docker-compose.yml`, or built locally through `docker-compose.build.yml`.
- Only nginx port 7210 is intended for publication; Gunicorn port 7200 and MCP port 7211 stay internal behind `deploy/nginx.conf`.
- Persistent PostgreSQL and application media data are mounted beneath `DATA_PATH` by `docker-compose.yml`.
- A reverse proxy with HTTPS is required for non-localhost passkeys; deployment guidance is in `README.md`.

---

*Stack analysis: 2026-07-21*
