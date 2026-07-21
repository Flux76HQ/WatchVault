# Coding Conventions

**Analysis Date:** 2026-07-21

## Naming Patterns

**Files:**
- Use `snake_case.py` for Python modules, such as `backend/app/migrations_runner.py`, `backend/app/ingest/trakt_sync.py`, and `backend/app/api/titles_edit.py`.
- Name Python tests `test_<behavior-area>.py` under `backend/tests/`, for example `backend/tests/test_scrobble.py` and `backend/tests/test_title_key.py`.
- Use PascalCase for React component and page files, such as `frontend/src/components/ErrorBoundary.tsx` and `frontend/src/pages/TitleDetail.tsx`.
- Use camelCase for frontend library files, such as `frontend/src/lib/useFetch.ts` and `frontend/src/lib/lazyEnrich.ts`.
- Use lowercase language codes for locale modules, such as `frontend/src/locales/en.ts` and `frontend/src/locales/nl.ts`.

**Functions:**
- Use `snake_case` for Python functions and route handlers: `compose_display_name`, `query_all`, and `create_connection` in `backend/app/api/profiles.py`, `backend/app/db.py`, and `backend/app/api/ingest.py`.
- Prefix non-public Python helpers with `_`, such as `_provider_by_key()` in `backend/app/api/ingest.py` and `_avatars_dir()` in `backend/app/api/profiles.py`.
- Use `camelCase` for TypeScript functions and callbacks: `applyTheme`, `refreshProfiles`, and `savePrefs` in `frontend/src/lib/app.tsx`.
- Name React hooks with the `use` prefix, as in `useApp()` in `frontend/src/lib/app.tsx`, `useT()` in `frontend/src/lib/i18n.tsx`, and `useFetch()` in `frontend/src/lib/useFetch.ts`.
- Name React components and exported visual helpers in PascalCase, as in `Dashboard`, `ErrorState`, and `RangeSeg` in `frontend/src/pages/Dashboard.tsx` and `frontend/src/components/ui.tsx`.

**Variables:**
- Use `snake_case` for Python locals that map to domain or database fields, such as `provider_key`, `profile_id`, and `last_seen_at` in `backend/app/api/profiles.py` and `backend/app/api/ingest.py`.
- Use `camelCase` for TypeScript locals and state setters, such as `defaultProfile`, `setToastState`, and `recentRange` in `frontend/src/lib/app.tsx`, `frontend/src/pages/Settings.tsx`, and `frontend/src/pages/Dashboard.tsx`.
- Use leading underscores for intentionally private TypeScript/Python helpers or unused callback parameters, such as `_tmdb_plugin()` in `backend/tests/test_metadata.py` and `_t` in `frontend/src/lib/i18n.tsx`.
- Use `UPPER_SNAKE_CASE` for module constants: `DEFAULT_PREFS` in `backend/app/api/profiles.py`, `LIVE_MIN_WATCH_SECONDS` in `backend/app/ingest/scrobble.py`, and `LANGUAGES`/`DICTS` in `frontend/src/lib/i18n.tsx`.

**Types:**
- Use PascalCase for Python classes and dataclasses: `Config`, `NormalizedEvent`, and `SourceAdapter` in `backend/app/config.py`, `backend/app/ingest/models.py`, and `backend/app/ingest/adapters/base.py`.
- Use PascalCase for TypeScript interfaces and type aliases: `User`, `Prefs`, `DashboardLayout`, and `LangCode` in `frontend/src/lib/app.tsx` and `frontend/src/lib/i18n.tsx`.
- Keep backend-shaped frontend properties in `snake_case` (`display_name`, `household_id`, `is_admin`) in `frontend/src/lib/app.tsx`; these names deliberately mirror JSON returned by `backend/app/api/profiles.py`.
- Use string-literal unions for bounded UI state, as with `Range` in `frontend/src/components/ui.tsx` and `RecentRange`/`BlockId` in `frontend/src/pages/Dashboard.tsx`.

## Code Style

**Formatting:**
- No dedicated formatter configuration is present; `.prettierrc*`, `pyproject.toml`, `setup.cfg`, and `ruff.toml` are not detected.
- Format Python with four-space indentation, blank lines between top-level definitions, double-quoted strings by default, and manually wrapped calls/imports. Representative files are `backend/app/db.py` and `backend/app/api/ingest.py`.
- Format TypeScript/TSX with two-space indentation, double-quoted strings, semicolons, and trailing commas in multiline literals. Representative files are `frontend/src/lib/app.tsx` and `frontend/src/components/ErrorBoundary.tsx`.
- Keep compact expressions on one line only when they remain readable; multiline JSX props and Python SQL arguments are manually aligned in `frontend/src/components/ui.tsx` and `backend/app/api/profiles.py`.
- Use section-divider comments (`# ── ...` or `// ── ...`) in long domain modules and tests, as in `backend/app/util.py`, `backend/tests/test_scrobble.py`, and `frontend/src/lib/i18n.tsx`.

**Linting:**
- No ESLint, Ruff, Flake8, Black, or Prettier runner/configuration is detected in the repository.
- Treat `frontend/tsconfig.json` as the enforced frontend quality gate: `strict`, `isolatedModules`, and `noFallthroughCasesInSwitch` are enabled.
- Do not assume unused symbols fail the build: `noUnusedLocals` and `noUnusedParameters` are explicitly disabled in `frontend/tsconfig.json`.
- Existing source uses targeted suppression comments such as `# noqa: E402` in `backend/tests/test_adapters.py`, `# noqa: BLE001` in `backend/app/api/ingest.py`, and `// eslint-disable-next-line react-hooks/exhaustive-deps` in `frontend/src/lib/useFetch.ts`; add suppressions only beside the intentional exception and explain why.
- Validate frontend changes through the `build` script in `frontend/package.json`, which runs `tsc -b` before Vite.

## Import Organization

**Order:**
1. Put `from __future__ import annotations` immediately after the module docstring in Python modules, as in `backend/app/__init__.py`.
2. Group Python standard-library imports before third-party imports, then project-relative imports; separate groups with blank lines as in `backend/app/api/profiles.py`.
3. In tests, establish `ROOT` and prepend `backend/` to `sys.path` before importing `app`; mark resulting late imports with `# noqa: E402`, as in `backend/tests/test_scrobble.py`.
4. In TypeScript, import React/router or other packages first, then `../lib`, `../components`, or sibling modules. Keep type-only imports explicit with `type`, as in `frontend/src/components/ui.tsx`.
5. Import frontend modules directly from their defining file; do not introduce an index barrel solely for convenience.

**Path Aliases:**
- Not detected. `frontend/tsconfig.json` has no `paths` mapping; use explicit relative paths such as `../lib/api` and `../components/ui`.
- Python application code uses package-relative imports inside `backend/app/`, while entry points such as `backend/wsgi.py` import from the top-level `app` package.

## Error Handling

**Patterns:**
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

**Framework:** Python standard `logging`; `console` only for the frontend render boundary.

**Patterns:**
- Configure the Python log level once in `create_app()` in `backend/app/__init__.py`.
- Create module loggers with `logging.getLogger(__name__)`, as in `backend/app/api/ingest.py` and `backend/app/api/search.py`.
- Use `logger.exception()`/`app.logger.exception()` inside exception handlers when a traceback and request/domain context are useful.
- Keep expected 4xx validation responses quiet; `backend/app/__init__.py` logs HTTP exceptions only at 5xx.
- CLI/process entry points may use flushed `print()` for lifecycle output, as in `backend/app/migrations_runner.py` and `backend/worker.py`.
- Frontend business code has no remote logger. Use `console.error` only for uncaught render diagnostics, following `frontend/src/components/ErrorBoundary.tsx`.

## Comments

**When to Comment:**
- Explain domain invariants, regression-sensitive behavior, and non-obvious fallbacks rather than restating syntax. Examples include title matching in `backend/app/util.py`, transactional deadlock guards in `backend/tests/test_scrobble.py`, and PWA recovery behavior in `frontend/src/components/ErrorBoundary.tsx`.
- Put short rationale comments beside best-effort catches, security boundaries, and intentionally unusual state behavior in `backend/app/api/ingest.py` and `frontend/src/lib/useFetch.ts`.
- Use section headers to make long modules navigable, but keep small modules free of decorative commentary.

**JSDoc/TSDoc:**
- Python module, class, and complex helper docstrings are common and use concise prose plus occasional reStructuredText-style literals, as in `backend/app/ingest/adapters/base.py` and `backend/app/ingest/models.py`.
- Public TypeScript APIs generally rely on types and line comments rather than JSDoc. Preserve this pattern in `frontend/src/lib/app.tsx` and `frontend/src/components/ui.tsx`.

## Function Design

**Size:** Prefer small pure helpers for normalization, formatting, branching, and serialization, as in `backend/app/util.py`, `frontend/src/lib/i18n.tsx`, and `frontend/src/lib/api.ts`. Route handlers and page components may orchestrate larger flows, but extract reusable behavior into helpers/hooks/components.

**Parameters:** Type reusable Python helpers with modern annotations (`str | None`, `list[dict]`, `tuple[...]`) as in `backend/app/api/profiles.py` and `backend/app/ingest/adapters/base.py`. Type TypeScript props inline for small components and use named interfaces for shared domain/context shapes, following `frontend/src/components/ui.tsx` and `frontend/src/lib/app.tsx`.

**Return Values:** Return JSON-serializable dictionaries/lists from backend helpers and Flask `jsonify` responses from routes. Return explicit state objects from hooks (`{ data, error, loading, reload, refresh, setData }` in `frontend/src/lib/useFetch.ts`) and use `null` for absent React data.

## Module Design

**Exports:** Python modules expose route blueprints as `bp`, public helpers without an underscore, and implementation helpers with an underscore. TypeScript modules use named exports for components, hooks, types, and singleton helpers; default exports are primarily locale dictionaries in `frontend/src/locales/`.

**Barrel Files:** Python package `__init__.py` files provide intentional registries/re-exports, notably `backend/app/ingest/__init__.py` and `backend/app/ingest/adapters/__init__.py`. Frontend barrel files are not used; import directly from the implementation module.

**Database Access:**
- Use `%s` placeholders and pass parameters separately; examples are `backend/app/db.py` and `backend/app/api/profiles.py`.
- Use `connection()` plus a cursor for multi-statement transactions, and `query_one`, `query_all`, or `execute` for isolated operations from `backend/app/db.py`.
- Preserve `dict_row` assumptions: production and fake cursors return mapping-like rows throughout `backend/app/` and `backend/tests/`.

**React State:**
- Keep application-wide auth, preferences, profiles, scope, permissions, and toasts in `AppProvider` at `frontend/src/lib/app.tsx`.
- Keep page-local interaction state in `useState`, server reads in `useFetch`, and reusable presentation in `frontend/src/components/`.
- Localize visible strings through `useT()`/`translate()` in `frontend/src/lib/i18n.tsx`; add matching keys to every module under `frontend/src/locales/`.

---

*Convention analysis: 2026-07-21*
