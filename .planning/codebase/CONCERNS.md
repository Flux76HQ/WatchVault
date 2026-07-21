# Codebase Concerns

**Analysis Date:** 2026-07-21

## Tech Debt

**Large, multi-responsibility modules:**
- Issue: API, state, rendering, and workflow logic are concentrated in several files over 500 lines, especially `frontend/src/pages/TitleDetail.tsx`, `frontend/src/pages/Settings.tsx`, `frontend/src/pages/Imports.tsx`, `backend/app/api/ingest.py`, `backend/app/api/stats.py`, and `backend/app/ingest/scrobble.py`.
- Files: `frontend/src/pages/TitleDetail.tsx`, `frontend/src/pages/Settings.tsx`, `frontend/src/pages/Imports.tsx`, `backend/app/api/ingest.py`, `backend/app/api/stats.py`, `backend/app/ingest/scrobble.py`
- Impact: Changes have broad regression surfaces, frontend state transitions are difficult to isolate, and endpoint behavior cannot be tested independently without extensive monkeypatching.
- Fix approach: Split route handlers into domain services, extract typed frontend feature hooks/components, and keep HTTP parsing, domain mutation, and response serialization in separate units.

**Weak frontend API typing:**
- Issue: The shared fetch layer returns `Promise<any>`, and major pages propagate `any` through component props and response handling despite strict TypeScript mode.
- Files: `frontend/src/lib/api.ts`, `frontend/src/lib/useFetch.ts`, `frontend/src/pages/Dashboard.tsx`, `frontend/src/pages/TitleDetail.tsx`, `frontend/src/pages/Settings.tsx`, `frontend/src/pages/Imports.tsx`
- Impact: Backend response drift and nullability mistakes become runtime failures rather than compile-time errors.
- Fix approach: Define endpoint request/response types, make `api` methods generic, replace page-level `any` values incrementally, and validate high-risk responses at the boundary.

**Generated compiler state is committed:**
- Issue: TypeScript incremental build artifacts are tracked and are not excluded by `.gitignore`.
- Files: `frontend/tsconfig.tsbuildinfo`, `frontend/tsconfig.node.tsbuildinfo`, `.gitignore`
- Impact: Local builds can create noisy or machine-dependent diffs and merge conflicts unrelated to source behavior.
- Fix approach: Ignore `*.tsbuildinfo`, remove the tracked artifacts, and let local and CI builds regenerate them.

**Audit infrastructure is mostly unused:**
- Issue: The schema defines `audit_events` and `domain_events`, but application code writes only one import audit event and does not emit records for authentication, role changes, token operations, destructive title operations, settings changes, or plugin-secret changes.
- Files: `backend/migrations/0004_plugins_jobs_audit.sql`, `backend/app/api/ingest.py`, `backend/app/api/profiles.py`, `backend/app/api/plugins.py`, `backend/app/auth/routes.py`
- Impact: Security-sensitive and destructive actions cannot be reconstructed reliably after an incident.
- Fix approach: Centralize audit emission and cover authentication, authorization changes, token lifecycle, connection changes, catalog deletion, resets, and secret updates.

**Operational records have no retention policy:**
- Issue: Completed/error jobs, expired/revoked sessions, used recovery codes, expired WebAuthn challenges, consumed OAuth authorizations, and audit/domain events are not periodically purged.
- Files: `backend/worker.py`, `backend/app/auth/routes.py`, `backend/migrations/0001_identity.sql`, `backend/migrations/0004_plugins_jobs_audit.sql`
- Impact: Tables and indexes grow indefinitely, auth lookups degrade, and sensitive metadata remains longer than necessary.
- Fix approach: Add indexed expiry fields where needed and a scheduled retention task with explicit per-table retention periods.

## Known Bugs

**Genre detail endpoint casts integer IDs to UUID:**
- Symptoms: Opening a genre detail page returns a server error instead of its title grid.
- Files: `backend/app/api/stats.py`, `backend/migrations/0003_domain.sql`, `frontend/src/pages/GenreTitles.tsx`
- Trigger: Call `/api/stats/genre-titles?genre=<integer>`; both genre predicates use `%s::uuid` although `genres.id` and `title_genres.genre_id` are integers.
- Workaround: None in the UI; change the predicates to integer parameters and add an endpoint test.

**Offline sync can skip changes permanently:**
- Symptoms: A native client can miss users, titles, events, or preferences after a large import/update burst.
- Files: `backend/app/api/sync.py`, `backend/migrations/0001_identity.sql`, `backend/migrations/0003_domain.sql`
- Trigger: More than one response limit changes after the supplied revision (`1000` users, `2000` titles, or `5000` events). The response still returns the global sequence's latest value, so advancing to it skips rows omitted by `LIMIT`.
- Workaround: Re-sync from an older revision or zero; return a page-safe cursor and `has_more`, or page each entity independently before exposing the global high-water mark.

**Concurrent WebAuthn ceremonies interfere with each other:**
- Symptoms: Parallel login, initial registration, or passkey-add flows fail verification or complete against another browser's latest challenge.
- Files: `backend/app/auth/routes.py`, `backend/migrations/0001_identity.sql`
- Trigger: Start two ceremonies with the same purpose before either completes. `_take_challenge()` selects the newest global row by purpose and does not bind it to a browser/session or atomically consume it.
- Workaround: Retry serially; return a challenge identifier, bind it to the ceremony/user, and consume it transactionally exactly once.

**Crashed jobs remain `running` forever:**
- Symptoms: A sync or enrichment never retries, and deduplication prevents an equivalent job from being queued.
- Files: `backend/worker.py`, `backend/migrations/0004_plugins_jobs_audit.sql`, `backend/app/api/people.py`, `backend/app/ingest/trakt_sync.py`
- Trigger: Terminate the worker after `_claim_job()` commits `status='running'` but before `_finish()` or `_retry_or_fail()`.
- Workaround: Manually reset the row; add a lease/heartbeat and reclaim stale running jobs on worker startup and during polling.

**Large Jellyfin histories are silently truncated:**
- Symptoms: Older played items never enter WatchVault for a user/library with more than 5,000 matching items.
- Files: `backend/app/ingest/adapters/jellyfin.py`
- Trigger: Jellyfin returns the configured `Limit` of 5,000; the adapter does not inspect total count or request subsequent pages.
- Workaround: Import smaller libraries separately; implement `StartIndex` pagination until all results are fetched.

**Malformed query parameters become 500 responses:**
- Symptoms: Non-numeric or negative `limit`, `since`, `year`, date, UUID, and similar query values can reach Python/PostgreSQL exceptions and the global 500 handler.
- Files: `backend/app/api/search.py`, `backend/app/api/stats.py`, `backend/app/api/sync.py`, `backend/app/__init__.py`
- Trigger: Examples include a non-integer `limit` on search/actor statistics, a non-integer `since` on sync, or a malformed UUID tag filter.
- Workaround: Use valid client-generated values; introduce shared parsers that clamp ranges and return consistent 400 responses.

**Admin status has two unsynchronized sources:**
- Symptoms: A profile can display `is_admin=false` while retaining every admin role permission, or gain wildcard access without an admin role row.
- Files: `backend/app/api/profiles.py`, `backend/app/auth/sessions.py`, `backend/migrations/0002_rbac_prefs.sql`
- Trigger: Update `is_admin` through the profile endpoint; `user_roles` is not updated, while `_load_user()` combines role permissions with an `is_admin` wildcard.
- Workaround: Treat role membership as the single authority and derive `is_admin`, or update both in one transaction with last-admin protection.

## Security Considerations

**Registration fails open when the optional invite gate is unset:**
- Risk: Anyone who can reach the application can register into the existing household as a member; two first-user attempts also race on the global user count.
- Files: `backend/app/config.py`, `backend/app/auth/routes.py`, `README.md`
- Current mitigation: An optional registration invite code can be configured, and the first account is the only automatically selected administrator.
- Recommendations: Require an explicit production opt-in for open registration, fail startup on insecure production auth defaults, rate-limit registration, and serialize first-user bootstrap.

**Authentication and recovery have no abuse controls:**
- Risk: Login/registration challenge creation, recovery-code redemption, and token endpoints can be spammed. Recovery verifies a submitted code against every unused code, making each request increasingly expensive.
- Files: `backend/app/auth/routes.py`, `backend/app/auth/sessions.py`, `backend/migrations/0001_identity.sql`
- Current mitigation: Challenges expire after five minutes, recovery codes are hashed, and sessions are revocable.
- Recommendations: Add per-IP and per-account rate limits, bounded challenge creation, indexed recovery lookup using a keyed hash, generic errors, and cleanup of expired rows.

**Standard members can mutate other profiles and globally shared data:**
- Risk: The seeded member role has `ingest.write`; `_target_user()` accepts any household profile, default scoped deletes affect all household profiles, and the title-delete endpoint removes a global title plus every user's matching watch events. UI-only expert mode is not authorization.
- Files: `backend/migrations/0002_rbac_prefs.sql`, `backend/app/api/ingest.py`, `backend/app/api/_common.py`, `backend/app/ingest/manual.py`, `backend/app/api/stats.py`
- Current mitigation: Target IDs must belong to the current household, and destructive reset requires `settings.manage`.
- Recommendations: Separate own-history permissions from household/catalog administration, default writes to self, require an explicit privileged permission for cross-profile mutation and global title deletion, and enforce this in backend integration tests.

**Connector and plugin credentials are plaintext in PostgreSQL:**
- Risk: A database backup/read compromise exposes Plex, Jellyfin, Trakt, and metadata-provider credentials.
- Files: `backend/migrations/0003_domain.sql`, `backend/migrations/0004_plugins_jobs_audit.sql`, `backend/app/plugins/runtime.py`, `backend/app/api/ingest.py`
- Current mitigation: API responses generally expose only configured/not-configured hints, and WatchVault API tokens are hashed separately.
- Recommendations: Encrypt connector/plugin secrets with an application-managed key, restrict DB privileges, redact secrets from diagnostics, and document rotation/backup handling.

**Exception text can disclose connector secrets and internal topology:**
- Risk: Connector routes return raw `requests` exceptions. Plex credentials are sent as URL query parameters, and exception URLs or persisted `last_status` can include those values.
- Files: `backend/app/api/ingest.py`, `backend/app/ingest/adapters/plex.py`, `backend/worker.py`
- Current mitigation: The global production error handler hides unhandled exceptions, but these handlers intentionally serialize caught exception strings.
- Recommendations: Map upstream failures to sanitized error codes, scrub URLs and tokens before logging/persisting, and never return raw client-library exceptions.

**Webhook query tokens are written to access logs:**
- Risk: Plex webhook tokens supplied through `?token=` become part of the nginx request line and can leak through logs, proxies, browser history, and monitoring.
- Files: `backend/app/api/scrobble.py`, `deploy/nginx.conf`
- Current mitigation: API tokens are hashed at rest and can be revoked.
- Recommendations: Use a dedicated least-privilege token, suppress/redact query strings for the webhook path, prefer a secret path or supported header, and rotate any token exposed to logs.

**User-controlled connector URLs create an SSRF capability:**
- Risk: A member with `ingest.write` can make the server issue authenticated HTTP requests to arbitrary hosts, including internal services.
- Files: `backend/app/api/ingest.py`, `backend/app/ingest/adapters/plex.py`, `backend/app/ingest/adapters/jellyfin.py`, `backend/migrations/0002_rbac_prefs.sql`
- Current mitigation: Requests have timeouts and connector access requires authentication.
- Recommendations: Restrict connector management to administrators, validate schemes, block link-local/cloud-metadata and unsafe address ranges unless explicitly allowlisted, and re-resolve DNS at connection time.

**Authenticated API responses are cached across logout:**
- Risk: The service worker caches `/api/stats` and `/api/search` responses in a shared browser cache, while normal logout clears React state but not Cache Storage. Offline fallback can display a previous session's data.
- Files: `frontend/vite.config.ts`, `frontend/src/lib/app.tsx`, `frontend/src/components/ErrorBoundary.tsx`
- Current mitigation: `NetworkFirst` prefers a live response, and error recovery can clear all caches manually.
- Recommendations: Do not cache personalized API responses, or partition caches by user and purge them on logout/session change.

**Container and proxy defaults are not hardened:**
- Risk: nginx workers, supervisor, API, MCP server, and worker run as root in one container; compromise of one process reaches all application files and persisted uploads. The bundled proxy also lacks CSP, HSTS, frame, MIME-sniffing, and permissions headers.
- Files: `Dockerfile`, `deploy/supervisord.conf`, `deploy/nginx.conf`, `docker-compose.yml`
- Current mitigation: API and MCP bind to loopback inside the container, and the README recommends an external HTTPS reverse proxy.
- Recommendations: Run application processes as non-root, split privileges where practical, make the filesystem read-only except `/data` and runtime paths, drop capabilities, and define defense-in-depth response headers.

## Performance Bottlenecks

**Long-running work occupies HTTP workers:**
- Problem: File import, provider sync, immediate enrichment, reattribution, aggregate rebuilds, and reset operations run synchronously in Gunicorn requests with a 300-second timeout.
- Files: `backend/app/api/ingest.py`, `backend/app/api/people.py`, `backend/app/api/plugins.py`, `deploy/supervisord.conf`
- Cause: Routes execute outbound requests and large database loops directly even though a background-job worker exists.
- Improvement path: Enqueue expensive work, return job IDs/202 responses, expose status, and reserve request workers for bounded operations.

**Search performs repeated unindexed scans:**
- Problem: Each search runs a grouped result query plus a separate count query using leading-wildcard `ILIKE`, correlated `EXISTS`, and offset pagination over watch events.
- Files: `backend/app/api/search.py`, `backend/migrations/0003_domain.sql`
- Cause: Title/person/genre text has no trigram or full-text index, and the filter work is duplicated for totals.
- Improvement path: Add appropriate text/search indexes, consider a materialized household catalog view, and use keyset pagination or a window count.

**Plex sync has per-title outbound request amplification:**
- Problem: A history sync can issue one metadata request for each distinct title in addition to history and account requests.
- Files: `backend/app/ingest/adapters/plex.py`
- Cause: `_title_metadata()` caches only within one sync and fetches records sequentially.
- Improvement path: Use batch APIs where available, persist source metadata/cache timestamps, cap enrichment concurrency, and decouple metadata from history ingestion.

**Single serial worker limits throughput:**
- Problem: One worker processes one job at a time; a slow provider request blocks enrichment, sync, reattribution, and scheduled maintenance behind it.
- Files: `backend/worker.py`, `deploy/supervisord.conf`
- Cause: The deployment starts one polling process with no job classes, priorities, leases, or per-job timeout.
- Improvement path: Run multiple workers safely, add priorities and leases, isolate long syncs from short enrichment jobs, and measure queue age.

**Database connection usage scales per process:**
- Problem: Every Gunicorn process and auxiliary process lazily creates its own pool of up to ten connections.
- Files: `backend/app/db.py`, `deploy/supervisord.conf`, `backend/server.py`, `backend/worker.py`
- Cause: The pool is a module-level singleton, not a deployment-wide limit.
- Improvement path: Size pools against PostgreSQL capacity, use smaller per-process pools or an external pooler, and expose pool saturation metrics.

## Fragile Areas

**Derived data requires manual synchronization:**
- Files: `backend/app/ingest/normalize.py`, `backend/app/ingest/manual.py`, `backend/app/networks.py`, `backend/migrations/0005_aggregates.sql`, `backend/migrations/0017_title_progress.sql`
- Why fragile: Watch events, daily aggregates, title progress, provider attribution, and dedup hashes are updated by several custom paths; missing one recomputation leaves dashboards inconsistent.
- Safe modification: Route all watch-event mutations through one service/transaction and add invariant tests that compare derived tables with raw events.
- Test coverage: Unit tests cover important helpers, but no PostgreSQL integration suite validates all triggers/functions and mutation paths together.

**Authentication logic is duplicated:**
- Files: `backend/app/auth/sessions.py`, `backend/server.py`
- Why fragile: The MCP server implements token resolution, user loading, permission expansion, and household lookup separately from the main application.
- Safe modification: Share one auth/token service and one permission policy between Flask applications.
- Test coverage: No MCP authentication/permission tests or end-to-end token revocation tests were detected.

**Dynamic plugin loading trusts local plugin code completely:**
- Files: `backend/app/plugins/runtime.py`, `plugins/tmdb/plugin.py`
- Why fragile: Manifests receive limited validation, modules execute in-process with application/DB privileges, and broad exception handling can turn load failures into silent “not configured” states.
- Safe modification: Validate manifest schemas and interfaces, log structured failures, pin trusted plugins, and isolate third-party plugins before supporting external installation.
- Test coverage: Tests cover TMDB normalization but not runtime discovery, malformed manifests, enable/disable state, or plugin isolation.

**Forward-only startup migrations are an availability gate:**
- Files: `backend/app/migrations_runner.py`, `deploy/entrypoint.sh`, `backend/migrations/`
- Why fragile: Any migration failure or checksum drift prevents the entire combined container from starting, and there is no rollback path.
- Safe modification: Back up before upgrades, test migrations against production-sized snapshots, use expand/contract changes, and document recovery for partially deployed versions.
- Test coverage: No migration-runner or clean-database migration test was detected.

## Scaling Limits

**Single-household application behavior:**
- Current capacity: Bootstrap and later open registration select the first/only household, while titles and metadata are globally shared.
- Limit: True multi-household hosting would mix catalog mutations and allow global title edits/deletes to affect unrelated households.
- Scaling path: Declare and enforce single-tenant deployment, or add explicit tenant ownership/policies to mutable catalog data and remove “first household” selection.
- Files: `backend/app/auth/routes.py`, `backend/migrations/0001_identity.sql`, `backend/migrations/0003_domain.sql`, `backend/app/api/titles_edit.py`

**Unbounded queue and history tables:**
- Current capacity: PostgreSQL stores every completed job, session, challenge, authorization, and audit/domain event.
- Limit: No retention or partitioning prevents indefinite growth; some expiration/status columns lack supporting indexes.
- Scaling path: Add retention jobs, partial indexes for active rows, metrics, and partition high-volume append-only tables if usage grows.
- Files: `backend/migrations/0001_identity.sql`, `backend/migrations/0004_plugins_jobs_audit.sql`, `backend/worker.py`

**Fixed offline-sync batch sizes:**
- Current capacity: One call returns at most 1,000 users, 2,000 titles, and 5,000 watch events.
- Limit: Bursts above those limits are not merely paginated; they can be skipped by the returned high-water mark.
- Scaling path: Implement deterministic pagination with per-stream cursors and snapshot boundaries.
- Files: `backend/app/api/sync.py`

## Dependencies at Risk

**Python runtime dependencies are not reproducibly locked:**
- Risk: `>=` ranges allow materially different Flask, Gunicorn, psycopg, JWT, requests, and related transitive versions on each build; no hashes or compiled lockfile are present.
- Impact: Builds can change without source changes, and urgent vulnerable transitive versions are difficult to inventory reliably.
- Migration plan: Generate a reviewed lock/constraints file with hashes, update it through automated dependency PRs, and scan it in CI.
- Files: `backend/requirements.txt`, `backend/requirements-dev.txt`, `Dockerfile`

**Build and CI inputs use mutable tags:**
- Risk: Base images, PostgreSQL, GitHub Actions, and the deployment's `latest` application image are referenced by mutable tags rather than immutable digests/commit SHAs.
- Impact: Supply-chain inputs and deployed code can change without a repository diff, weakening rollback and provenance.
- Migration plan: Pin release images/digests and action commit SHAs, publish immutable application versions, and deploy a selected version instead of `latest`.
- Files: `Dockerfile`, `docker-compose.yml`, `.github/workflows/docker.yml`

**Dependency security is not gated in CI:**
- Risk: The only workflow builds and publishes the image; it does not run Python tests, TypeScript builds, linting, dependency review, SBOM generation, or image scanning first.
- Impact: Vulnerable or broken dependencies can be published automatically from `main`, release branches, and tags.
- Migration plan: Add test/build jobs, dependency review/Dependabot, lockfile auditing, SBOM/provenance attestation, and container scanning before publish.
- Files: `.github/workflows/docker.yml`, `frontend/package-lock.json`, `backend/requirements.txt`

## Missing Critical Features

**Production configuration validation:**
- Problem: Production mode accepts insecure fallback authentication/database settings and optional open registration instead of refusing startup.
- Blocks: Safe internet-facing deployment cannot rely on application-enforced configuration requirements.
- Files: `backend/app/config.py`, `backend/app/auth/routes.py`

**Observability and operational health:**
- Problem: Health reports only a basic DB check; there are no metrics, queue-age alerts, error tracking, structured request IDs, storage-capacity checks, or worker liveness checks.
- Blocks: Operators cannot detect stuck jobs, exhausted pools, repeated upstream failures, or growing tables before users report symptoms.
- Files: `backend/app/api/meta.py`, `backend/worker.py`, `deploy/supervisord.conf`

**Automated restore and upgrade verification:**
- Problem: Backups are documented as manual operations, while migrations run automatically at startup without a restore rehearsal or compatibility gate.
- Blocks: Recovery time and upgrade safety are unknown until an incident.
- Files: `README.md`, `backend/app/migrations_runner.py`, `deploy/entrypoint.sh`

## Test Coverage Gaps

**Authentication and authorization:**
- What's not tested: WebAuthn registration/login/replay/concurrency, recovery abuse controls, OAuth PKCE/client binding, session revocation, admin role changes, open registration, and cross-profile/member authorization.
- Files: `backend/app/auth/routes.py`, `backend/app/auth/sessions.py`, `backend/app/api/ingest.py`, `backend/app/api/profiles.py`
- Risk: Account takeover, privilege, and household-integrity regressions can ship unnoticed.
- Priority: High

**Database-backed API behavior:**
- What's not tested: Real PostgreSQL route execution, schema type compatibility, transaction boundaries, aggregate triggers/functions, offline-sync pagination, job claiming, and migrations.
- Files: `backend/app/api/stats.py`, `backend/app/api/sync.py`, `backend/worker.py`, `backend/migrations/`, `backend/tests/`
- Risk: Defects such as the integer/UUID genre mismatch and sync high-water data loss are not caught by the mostly helper-level mocked suite.
- Priority: High

**Frontend behavior:**
- What's not tested: No frontend test files or test script are present for routing, passkey UX, imports, destructive actions, PWA updates, cache privacy, polling cleanup, or error states.
- Files: `frontend/package.json`, `frontend/src/`
- Risk: Large page components and broad `any` usage can regress without automated detection.
- Priority: High

**CI and deployment:**
- What's not tested: The publish workflow does not execute the 153-test backend suite or a frontend type/build check. A local backend run passes all 153 tests; the frontend build cannot run in a clean worktree until npm dependencies are installed.
- Files: `.github/workflows/docker.yml`, `backend/tests/`, `frontend/package.json`
- Risk: The registry can receive an image whose application tests and type checks were never run by CI.
- Priority: High

**Security regression coverage:**
- What's not tested: Rate limiting, SSRF controls, raw error redaction, query-token logging, secret-at-rest handling, service-worker cache clearing, non-root operation, and security headers.
- Files: `backend/app/api/ingest.py`, `backend/app/api/scrobble.py`, `frontend/vite.config.ts`, `deploy/nginx.conf`, `Dockerfile`
- Risk: Security hardening can be absent or regress silently.
- Priority: High

---

*Concerns audit: 2026-07-21*
