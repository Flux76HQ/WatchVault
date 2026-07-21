# External Integrations

**Analysis Date:** 2026-07-21

## APIs & External Services

**Metadata Enrichment:**
- The Movie Database (TMDB) API v3 - searches titles and people, fetches movie/TV/person details, seasons, credits, translations, posters, and backdrops through `plugins/tmdb/plugin.py`.
  - SDK/Client: `requests>=2.32` from `backend/requirements.txt`; no TMDB-specific SDK is used.
  - Endpoint: `https://api.themoviedb.org/3` in `plugins/tmdb/plugin.py`.
  - Images: `https://image.tmdb.org/t/p` is normalized by `backend/app/api/_common.py` and cached by `frontend/vite.config.ts`.
  - Auth: `TMDB_API_KEY` from `backend/app/config.py`, with a database-stored plugin `api_key` taking precedence through `backend/app/plugins/runtime.py`.
  - Data sent: public title/person search terms and IDs; the plugin explicitly excludes watch history in `plugins/tmdb/plugin.py`.

**Watch-History Sync:**
- Plex Media Server - pulls accounts, libraries, history, and native title metadata from a user-configured server in `backend/app/ingest/adapters/plex.py`.
  - SDK/Client: `requests>=2.32` plus Python XML parsing in `backend/app/ingest/adapters/plex.py`.
  - Auth: per-connection `X-Plex-Token`, stored in `source_connections.config` by `backend/app/api/ingest.py`.
  - Endpoints: `/accounts`, `/library/sections`, `/status/sessions/history/all`, and `/library/metadata/{rating_key}` relative to the configured `base_url` in `backend/app/ingest/adapters/plex.py`.
- Jellyfin - pulls views and played movies/episodes from a user-configured server in `backend/app/ingest/adapters/jellyfin.py`.
  - SDK/Client: `requests>=2.32` from `backend/requirements.txt`.
  - Auth: per-connection Jellyfin API key sent as `X-Emby-Token`, stored in `source_connections.config` by `backend/app/api/ingest.py`.
  - Endpoints: `/Users/{user_id}/Views` and `/Users/{user_id}/Items` relative to the configured `base_url` in `backend/app/ingest/adapters/jellyfin.py`.
- Trakt API v2 - pulls public user history or authenticated private history, performs per-title cross-sync, and refreshes OAuth tokens in `backend/app/ingest/adapters/trakt.py` and `backend/app/ingest/trakt_sync.py`.
  - SDK/Client: `requests>=2.32` from `backend/requirements.txt`.
  - Endpoint: `https://api.trakt.tv` in `backend/app/ingest/adapters/trakt.py`.
  - Auth: Trakt Client ID headers plus optional OAuth access token; Client Secret, access token, refresh token, and expiration are stored in `source_connections.config` by `backend/app/api/ingest.py`.
  - OAuth flow: Trakt device authorization starts at `/oauth/device/code`, polls `/oauth/device/token`, and refreshes at `/oauth/token` in `backend/app/ingest/adapters/trakt.py`.

**Home Automation and Playback Sources:**
- Home Assistant 2024.10+ - blueprint sends real-time `media_player` playback events to WatchVault every state change and 30-second tick in `homeassistant/watchvault_realtime.yaml`.
  - SDK/Client: Home Assistant `rest_command`; no Python/TypeScript SDK is used in `homeassistant/watchvault_realtime.yaml`.
  - Auth: user-supplied WatchVault `wvapi_` token with `ingest.write`, configured as a password input in `homeassistant/watchvault_realtime.yaml`.
  - Destination: user-configured `/api/scrobble/generic` endpoint implemented by `backend/app/api/scrobble.py`.
- Plex native webhook - Plex posts playback events to `/api/scrobble/plex` in `backend/app/api/scrobble.py`.
  - Auth: WatchVault `wvapi_` token in the `token` query parameter because Plex cannot set the Authorization header, as implemented in `backend/app/api/scrobble.py`.
  - Payload: multipart `payload` JSON or JSON request bodies parsed by `backend/app/api/scrobble.py`.
- Generic scrobble clients - Home Assistant, Apple Shortcuts, and other clients post JSON to `/api/scrobble/generic` in `backend/app/api/scrobble.py`.
  - Auth: WatchVault session, Bearer JWT, or `wvapi_` API token resolved by `backend/app/auth/sessions.py`.

**AI Assistant Access:**
- Model Context Protocol (MCP) streamable HTTP bridge - exposes `search` and `stats` tools over JSON-RPC at `/mcp` in `backend/server.py`.
  - SDK/Client: custom Flask implementation; no MCP SDK dependency is declared in `backend/requirements.txt`.
  - Protocol: version `2024-11-05` in `backend/server.py`.
  - Auth: per-user WatchVault `wvapi_` Bearer token plus `mcp.use` and tool-specific RBAC permissions in `backend/server.py`.
  - Routing: nginx proxies public `/mcp` to internal port 7211 in `deploy/nginx.conf`.

## Data Storage

**Databases:**
- PostgreSQL 17 Alpine is the sole database service in `docker-compose.yml`.
  - Connection: assembled from `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, and `POSTGRES_PORT` by `backend/app/config.py`.
  - Client: psycopg 3 binary driver and `psycopg_pool.ConnectionPool` in `backend/app/db.py`.
  - Pooling: process-local pool with minimum 1 and maximum 10 connections in `backend/app/db.py`.
  - Extensions/features: `pgcrypto`, UUIDs, JSONB, PL/pgSQL triggers, transactional migrations, and a database-backed job queue in `backend/migrations/0001_identity.sql` and `backend/migrations/0004_plugins_jobs_audit.sql`.
  - Migrations: forward-only, checksum-guarded SQL files under `backend/migrations/`, applied at startup by `backend/migrate.py` and `deploy/entrypoint.sh`.

**File Storage:**
- Local filesystem only - persistent app data is rooted at `DATA_DIR` in `backend/app/config.py` and mounted from `DATA_PATH` by `docker-compose.yml`.
- Profile avatar uploads are written under `DATA_DIR/media/avatars` and served from `/api/media/avatars/{name}` by `backend/app/api/profiles.py`.
- Imported history files are read into memory and ingested directly rather than retained by `backend/app/api/ingest.py`.
- Generated frontend assets are copied to `/app/web` by `Dockerfile` and served by `deploy/nginx.conf`.

**Caching:**
- No Redis, Memcached, or external server-side cache is present in `backend/requirements.txt` or `docker-compose.yml`.
- The PWA service worker uses a `NetworkFirst` cache named `wv-data` for `/api/stats` and `/api/search` in `frontend/vite.config.ts`.
- TMDB images use a `CacheFirst` cache named `wv-posters`, limited to 600 entries and 30 days, in `frontend/vite.config.ts`.
- PostgreSQL table `watch_daily_agg` acts as a persisted aggregate for statistics in `backend/migrations/0005_aggregates.sql`.

## Authentication & Identity

**Auth Provider:**
- Custom self-hosted WebAuthn/passkey identity; there is no external identity provider in `backend/app/auth/routes.py`.
  - Browser implementation: `@simplewebauthn/browser` in `frontend/src/lib/auth.ts`.
  - Server implementation: Python `webauthn` package in `backend/app/auth/routes.py`.
  - Relying-party configuration: `RP_ID`, `RP_NAME`, and `RP_ORIGINS` in `backend/app/config.py`.
  - Session implementation: HS256 JWTs signed with `SESSION_SECRET`, stored in an HttpOnly SameSite=Lax cookie and backed by revocable session rows in `backend/app/auth/sessions.py` and `backend/app/auth/routes.py`.
  - Recovery: salted hashes of one-time recovery codes are stored in PostgreSQL by `backend/app/auth/routes.py` and `backend/migrations/0001_identity.sql`.
  - Authorization: database roles and permission keys are enforced by decorators in `backend/app/auth/sessions.py` and defined in `backend/migrations/0002_rbac_prefs.sql`.
  - API clients: generated `wvapi_` tokens are stored only as salted hashes with a display prefix in `backend/migrations/0004_plugins_jobs_audit.sql`.
  - Native-client bridge: WatchVault implements its own OAuth2-style authorization-code + PKCE exchange at `/api/auth/oauth/authorize` and `/api/auth/oauth/token` in `backend/app/auth/routes.py`; it does not delegate identity to a third party.
- Trakt OAuth is connection authorization, not WatchVault user authentication, and is isolated in `backend/app/ingest/adapters/trakt.py`.

## Monitoring & Observability

**Error Tracking:**
- No external error-tracking or APM service is configured in `backend/requirements.txt`, `frontend/package.json`, or `docker-compose.yml`.
- Flask logs uncaught exceptions with request method/path through global handlers in `backend/app/__init__.py`.

**Logs:**
- Python logging level is configured by `LOG_LEVEL` and initialized with `logging.basicConfig` in `backend/app/__init__.py`.
- The worker writes startup messages and tracebacks to stdout/stderr in `backend/worker.py`.
- Gunicorn, MCP, worker, and nginx output is routed to container stdout/stderr by `deploy/supervisord.conf`.
- Nginx access and error logs use stdout/stderr in `deploy/nginx.conf`.
- Audit and domain events are also persisted in PostgreSQL tables created by `backend/migrations/0004_plugins_jobs_audit.sql`.

## CI/CD & Deployment

**Hosting:**
- Self-hosted Docker Compose is the supported runtime in `docker-compose.yml` and `README.md`.
- Default application image is hosted at GitHub Container Registry as `ghcr.io/helmerznl/watchvault:latest` in `docker-compose.yml`.
- Production topology is one nginx/Gunicorn/MCP/worker application container plus one PostgreSQL 17 container in `Dockerfile`, `deploy/supervisord.conf`, and `docker-compose.yml`.
- External reverse proxies may terminate HTTPS and forward to port 7210; no specific proxy provider is coupled in `README.md`.

**CI Pipeline:**
- GitHub Actions workflow `.github/workflows/docker.yml` runs on `main`, `release/**`, version tags, and manual dispatch.
- Docker Buildx uses GitHub Actions cache and publishes branch, tag, SHA, and latest image tags to GHCR in `.github/workflows/docker.yml`.
- Registry authentication uses GitHub's repository-scoped workflow token in `.github/workflows/docker.yml`.
- No automated test, lint, dependency scan, or deployment job is present in `.github/workflows/docker.yml`.

## Environment Configuration

**Required env vars:**
- `SESSION_SECRET` - signs WatchVault JWT sessions; consumed by `backend/app/config.py`.
- `POSTGRES_PASSWORD` - authenticates database connections; consumed by `backend/app/config.py` and substituted by `docker-compose.yml`.
- `POSTGRES_USER`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT` - database identity and location in `backend/app/config.py`.
- `RP_ID`, `RP_ORIGINS` - WebAuthn relying-party hostname and accepted origins in `backend/app/config.py` and `backend/app/auth/routes.py`.
- `RP_NAME`, `SESSION_TTL_HOURS`, `REGISTRATION_INVITE_CODE`, `APP_ENV`, and `LOG_LEVEL` - optional authentication and runtime behavior in `backend/app/config.py`.
- `TMDB_API_KEY` - optional environment fallback for the TMDB plugin in `backend/app/plugins/runtime.py`.
- `DATA_DIR` and deployment-side `DATA_PATH` - container and host persistence paths in `backend/app/config.py` and `docker-compose.yml`.
- `PLUGINS_DIR` - optional plugin discovery override in `backend/app/plugins/runtime.py`.
- `WEB_PORT` - public host port substitution in `docker-compose.yml`.

**Secrets location:**
- `.env.example` exists as a non-secret template; runtime Docker Compose expects an uncommitted `.env` through `env_file` in `docker-compose.yml`.
- TMDB plugin credentials can be stored in PostgreSQL `plugins.secrets` JSONB by `backend/app/plugins/runtime.py` and `backend/migrations/0004_plugins_jobs_audit.sql`.
- Plex, Jellyfin, and Trakt connection credentials and OAuth tokens are stored in PostgreSQL `source_connections.config` JSONB through `backend/app/api/ingest.py` and `backend/migrations/0003_domain.sql`.
- WatchVault API tokens and recovery codes are stored as salted hashes in tables defined by `backend/migrations/0004_plugins_jobs_audit.sql` and `backend/migrations/0001_identity.sql`.
- Session JWT signing uses `SESSION_SECRET` from the process environment in `backend/app/config.py`; JWT revocation state is stored in PostgreSQL by `backend/app/auth/sessions.py`.

## Webhooks & Callbacks

**Incoming:**
- `POST /api/scrobble/plex` receives Plex playback webhooks as multipart or JSON in `backend/app/api/scrobble.py`.
- `POST /api/scrobble/generic` receives Home Assistant, Apple TV/Shortcuts, and generic playback JSON in `backend/app/api/scrobble.py`.
- `POST /mcp` and `POST /` on internal port 7211 receive MCP JSON-RPC calls in `backend/server.py`; nginx exposes `/mcp` through `deploy/nginx.conf`.
- WatchVault's native-client PKCE bridge receives authorization and token exchange requests at `/api/auth/oauth/authorize` and `/api/auth/oauth/token` in `backend/app/auth/routes.py`.

**Outgoing:**
- No outgoing webhook delivery system is implemented in `backend/`.
- The worker performs scheduled pull syncs every 15 minutes for enabled API connections through `backend/worker.py`.
- TMDB enrichment issues on-demand outbound HTTPS requests through `plugins/tmdb/plugin.py`.
- Plex and Jellyfin adapters issue outbound requests to user-configured server URLs in `backend/app/ingest/adapters/plex.py` and `backend/app/ingest/adapters/jellyfin.py`.
- Trakt device authorization, token refresh, history sync, and per-title sync issue outbound HTTPS requests through `backend/app/ingest/adapters/trakt.py`.
- The Home Assistant blueprint is an external caller that posts to WatchVault; its outbound action is defined in `homeassistant/watchvault_realtime.yaml`.

---

*Integration audit: 2026-07-21*
