# Phase 1: Delivery Safeguards and Behavioral Baseline - Research

**Researched:** 2026-07-21  
**Domain:** Repository delivery controls, capability baselining, and regression automation  
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### Implementation Decisions

### Canonical version source and synchronization
- **D-01:** A plain root `VERSION` file is the single source of truth for the full product.
- **D-02:** The version helper synchronizes `frontend/package.json` and `frontend/package-lock.json`; the Docker image embeds OCI version labels; backend metadata exposes the version; CI verifies matching `vX.Y.Z` release tags.
- **D-03:** The helper compares protected changes with the merge base, defaults to a patch bump only when needed, becomes a no-op after a sufficient bump, and accepts explicit `--minor` and `--major` overrides.
- **D-04:** Phase 1 adopts the existing `1.0.0` package version as its baseline and leaves the repository at `1.0.1`.

### Protected-path policy and remediation
- **D-05:** Version-protected paths are `backend/**`, `frontend/**`, `plugins/**`, `homeassistant/**`, `deploy/**`, `scripts/**`, `Dockerfile`, compose files, and `.github/workflows/**`.
- **D-06:** One machine-readable root policy file owns include and exclude rules; CI, the helper, and the hook consume this same policy rather than duplicating path lists.
- **D-07:** Every version-policy failure prints the exact remediation command `node scripts/version.mjs bump`; the same command supports `--minor` and `--major`.
- **D-08:** The pre-commit hook blocks staged protected changes without a sufficient staged version bump and blocks synchronized-version drift. It does not run builds or test suites.
- **D-09:** Repository setup configures `core.hooksPath` to the committed hooks directory so local enforcement is active through repository configuration.

### Capability inventory structure and ownership
- **D-10:** Machine-readable JSON is the canonical capability inventory, with a generated Markdown report for human review.
- **D-11:** Inventory entries use stable atomic IDs. A distinct entry represents each route, action, permission rule, scope behavior, preference, locale or theme obligation, and important UI state.
- **D-12:** Every entry records its source location, current behavior, applicable permission/scope/theme/locale/state dimensions, owning roadmap requirement and phase, and planned or existing regression evidence.
- **D-13:** CI blocks invalid schemas, duplicate IDs, invalid source or requirement references, stale generated Markdown, and gaps in discoverable route, locale, theme, or preference catalogs.
- **D-14:** Existing capabilities cannot be silently deferred or omitted; all current behavior must have explicit redesign ownership.

### Regression gates and local-check boundaries
- **D-15:** Backend regression coverage remains on pytest. Frontend coverage uses Vitest, Testing Library, and axe for component/accessibility checks, plus Playwright for browser journeys and visual snapshots.
- **D-16:** Initial Playwright journeys use deterministic browser-level API fixtures to exercise the real React application and routing; backend behavior remains independently covered by pytest.
- **D-17:** The blocking browser baseline uses pinned Chromium at desktop and mobile sizes and captures both dark and light states across the dashboard-to-search-to-title-to-history reference journey.
- **D-18:** Version and inventory validation always run in CI. Pull requests use changed paths to select backend, frontend, and browser jobs; pushes to `main` and release tags run the complete suite.
- **D-19:** Heavy type, component, accessibility, visual, journey, and backend checks remain in CI rather than the pre-commit hook.

### the agent's Discretion
- Exact filenames and JSON schemas for the version policy and capability inventory.
- Exact repository setup command or bootstrap script that applies `core.hooksPath`.
- Snapshot thresholds, artifact names, and CI retention periods, provided intentional updates are reviewable and the pinned browser baseline remains deterministic.
- Exact component fixtures and Playwright fixture organization.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DELV-01 | One canonical SemVer project version across application, build, image metadata, and release tag. [VERIFIED: `.planning/REQUIREMENTS.md`] | Root-version architecture, legacy-baseline migration, backend runtime lookup, OCI label, and tag-check contract |
| DELV-02 | Protected changes fail with an exact remediation command when no sufficient bump exists. [VERIFIED: `.planning/REQUIREMENTS.md`] | Shared policy shape, merge-base/index algorithm, CI and hook interfaces, and failure tests |
| DELV-03 | Idempotent helper bumps only when required. [VERIFIED: `.planning/REQUIREMENTS.md`] | Pure numeric target calculation, migration fallback, synchronization rules, and temporary-repository tests |
| DELV-04 | Fast repository-configured pre-commit enforcement; heavy checks stay in CI. [VERIFIED: `.planning/REQUIREMENTS.md`] | `.githooks/pre-commit`, idempotent setup command, staged-index checks, and aggregate CI gate |
| DELV-05 | Reviewable capability inventory covers all existing behavior and acceptance dimensions. [VERIFIED: `.planning/REQUIREMENTS.md`] | JSON Schema, discovery checks, deterministic Markdown generation, exact source catalogs, and review workflow |
| DELV-06 | CI runs backend, type, component, accessibility, visual, and critical-journey gates selected by changed surfaces. [VERIFIED: `.planning/REQUIREMENTS.md`] | Exact test stack, deterministic Playwright fixture architecture, four browser projects, and path-aware workflow design |
</phase_requirements>

## Summary

WatchVault has a strong backend baseline—`153` pytest tests pass in `1.25s`—but it has no root version source, committed hook directory, scripts directory, frontend test runner, browser suite, or CI test gate. The current version is duplicated as `1.0.0` in both frontend manifests and `backend/app/api/meta.py`, while the Docker workflow publishes without running pytest. [VERIFIED: codebase grep]

Plan this phase as one delivery system rather than five unrelated additions. A dependency-free Node version engine should own merge-base/index semantics and feed the hook and CI; a separate Ajv-backed inventory validator should own schema, discovery, and report generation; Vitest should establish component behavior before Playwright adds stateful browser fixtures and visual baselines; the Docker publish workflow must become downstream of one always-present aggregate CI gate. [VERIFIED: codebase grep] [CITED: https://git-scm.com/docs/githooks]

The most important non-code constraint is live repository enforcement. GitHub currently has an active ruleset that prevents deletion and non-fast-forward updates, but it has no pull-request or required-status-check rule. A failing workflow is therefore evidence, not yet a merge barrier. The plan needs a post-workflow checkpoint to require the stable aggregate check on `main`. [VERIFIED: GitHub API]

**Primary recommendation:** Build and test shared version/inventory tooling first, establish component and browser evidence second, then route all CI and image publication through an always-running `delivery / gate` check and make that check required.

## Project Constraints (from copilot-instructions.md)

- Continue with React, TypeScript, Vite, Flask, PostgreSQL, and the modular-monolith deployment; avoid platform migration. [VERIFIED: `.github/copilot-instructions.md`]
- Preserve every current user-facing capability; backend changes must directly support existing UI behavior. [VERIFIED: `.github/copilot-instructions.md`]
- Keyboard operation, visible focus, semantic structure, WCAG AA contrast, desktop/mobile support, and dark/light parity are release constraints. [VERIFIED: `.github/copilot-instructions.md`]
- Runtime, build, deploy, and CI changes require a SemVer bump; enforcement must be executable in hooks or CI. [VERIFIED: `.github/copilot-instructions.md`]
- Keep environment files ignored, placeholders safe, and production credentials out of source and artifacts. [VERIFIED: `.github/copilot-instructions.md`]
- Keep heavy validation in CI; the frontend build remains `tsc -b && vite build`, and Python tests follow existing `backend/tests/test_<area>.py` conventions. [VERIFIED: `.github/copilot-instructions.md`]
- Preserve the phase's explicit `--skip-ui` intent: component/browser work records current behavior only and must not redesign product TSX, CSS, routes, or interactions.
- Frontend source uses two-space TypeScript/TSX formatting, direct relative imports, and app-wide state in `frontend/src/lib/app.tsx`; Python uses four spaces and existing pytest fake/monkeypatch patterns. [VERIFIED: `.github/copilot-instructions.md`]
- This research is operating through a GSD workflow; no implementation is part of this phase-research task. [VERIFIED: `.github/copilot-instructions.md`]

No project-defined skills exist under `.github/skills/` or `.agents/skills/`, and no researcher skills are configured in `.planning/config.json`. [VERIFIED: repository inspection]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Canonical version and protected-path decisions | Repository tooling | CI / Build | Git history and the staged index are the authoritative comparison inputs; runtime tiers only consume the result. [VERIFIED: codebase grep] |
| Local commit enforcement | Git client | Repository tooling | Git invokes the committed hook through `core.hooksPath`; the hook delegates logic instead of duplicating it. [CITED: https://git-scm.com/docs/git-config#Documentation/git-config.txt-corehooksPath] |
| Backend version exposure | API / Backend | Build image | Flask exposes the value copied from root `VERSION`; the image carries the same value as an OCI label. [VERIFIED: codebase grep] |
| Capability inventory | Repository tooling | Frontend / Backend source catalogs | JSON is canonical; source scanners and reference checks prove discoverable catalog coverage. [VERIFIED: codebase grep] |
| Component and DOM accessibility evidence | Browser / Client | CI | Vitest/jsdom executes React behavior and axe DOM checks without a backend service. [CITED: https://vitest.dev/config/environment] |
| Critical journey and visual evidence | Browser / Client | CI / Static Vite server | Playwright drives the real built React routes while intercepting API traffic at the browser boundary. [CITED: https://playwright.dev/docs/mock] |
| Changed-surface selection and release gating | CI | Build / Registry | CI computes changed paths, runs selected jobs, aggregates results, and only then permits image publication. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax] |

## Existing Baseline and Exact Integration Points

| Area | Current state | Planning implication |
|------|---------------|----------------------|
| Version | `frontend/package.json`, lockfile root package, and `backend/app/api/meta.py` each say `1.0.0`; root `VERSION` is absent. [VERIFIED: codebase grep] | The first comparison against `main` needs a one-time fallback to the base revision's frontend package version. |
| Protected surfaces | All locked directories/files exist except `scripts/`; there is one workflow, `.github/workflows/docker.yml`. [VERIFIED: repository inspection] | Add `version-policy.json` and test every include/exclude branch with Git-style `/` paths. |
| Git hooks | `core.hooksPath` is unset; Git reports `core.filemode=false` in this Windows worktree. [VERIFIED: git config probe] | Commit the hook with executable mode in Git and test via Git for Windows as well as Linux CI. |
| Backend tests | 12 modules contain 153 test functions; `python -m pytest backend/tests -q` passes all 153. [VERIFIED: pytest run] | Preserve this exact command as the backend gate. |
| Frontend tests | No frontend tests, test script, browser framework, or installed `frontend/node_modules` exist in this worktree. [VERIFIED: repository inspection] | Frontend harness files and package installation are Wave 0 work. |
| Routes | `App.tsx` has an index route, eight explicit authenticated paths, and a wildcard fallback; unauthenticated users see `Login` outside the router. [VERIFIED: codebase grep] | Inventory the login gate and wildcard as states/surfaces, not invented redesign routes. |
| History journey | No dedicated history route exists; current watch-history mutation is initiated from title/episode controls and reflected in existing detail/dashboard data. [VERIFIED: codebase grep] | Baseline the existing dashboard → search → title → add-watch → refreshed dashboard behavior; do not create a new history screen in Phase 1. |
| Catalog discovery | The live tree contains 6 locale modules, 8 seeded permission keys, 10 route declarations including wildcard, 116 Flask route decorators, 115 frontend API-call sites, and 178 raw UI action markers. [VERIFIED: codebase grep] | Treat counts as discovery inputs, not as the final number of atomic inventory entries. |
| Preferences/themes/scopes | Frontend preferences include theme, accent, default profile, language, expert mode, cinema-add, dashboard layout, and unknown-card position; themes are light/dark/system; scope is household `all` or one profile ID. [VERIFIED: codebase grep] | Discovery must compare inventory IDs with typed/default catalogs and report mismatches. |
| GitHub enforcement | An active repository ruleset only prevents deletion and non-fast-forward changes; no required CI check or PR requirement is configured. [VERIFIED: GitHub API] | Add a human/API checkpoint after the first named check run. |

## Standard Stack

### Core

| Library / tool | Pin | Purpose | Why standard here |
|----------------|-----|---------|-------------------|
| Node built-ins (`node:test`, `fs`, `child_process`) | Project Node `>=20.19` | Version policy, setup, and pure tooling tests | Existing Vite 8.1.2 already requires Node `^20.19 || >=22.12`; use argument arrays with `spawnSync`/`execFileSync`. [VERIFIED: npm registry] |
| `vitest` [WARNING: flagged as suspicious — verify before using.] | `4.1.10` (2026-07-06) | Frontend unit/component runner | Official docs support Vite 8 and Node 20 and document jsdom/setup files. [CITED: https://vitest.dev/guide/] |
| `jsdom` | `29.1.1` (2026-04-30) | Browser-like component environment | Vitest documents jsdom for web applications; its Node floor is compatible with the existing Vite floor. [VERIFIED: npm registry] |
| `@testing-library/react` | `16.3.2` (2026-01-19) | React rendering and semantic queries | Supports React 18 and encourages user-observable tests. [VERIFIED: npm registry] |
| `@testing-library/dom` | `10.4.1` (2025-07-27) | Required DOM peer for Testing Library packages | It satisfies React Testing Library 16's declared `^10` peer. [VERIFIED: npm registry] |
| `@testing-library/user-event` | `14.6.1` (2025-01-21) | Realistic keyboard/pointer interaction | Official examples use `userEvent.setup()` before interaction. [VERIFIED: npm registry] |
| `@testing-library/jest-dom` [WARNING: flagged as suspicious — verify before using.] | **`6.9.1`** (2025-10-01) | DOM assertions through `/vitest` setup | Do not use current `7.0.0`: it requires Node 22, while `6.9.1` supports Node 14+. [VERIFIED: npm registry] |
| `axe-core` | `4.12.1` (2026-06-10) | Component DOM accessibility rules | Use the engine directly in a shared Vitest helper; browser-only checks remain in Playwright. [VERIFIED: npm registry] |
| `@playwright/test` [WARNING: flagged as suspicious — verify before using.] | `1.61.1` (2026-06-23) | Browser journey and visual runner | Official docs provide projects, emulation, route interception, and screenshots. [CITED: https://playwright.dev/docs/intro] |
| `@axe-core/playwright` [WARNING: flagged as suspicious — verify before using.] | `4.12.1` (2026-06-23) | Browser accessibility scans | This is the integration named by Playwright's official accessibility guide. [CITED: https://playwright.dev/docs/accessibility-testing] |
| `ajv` | `8.20.0` (2026-04-24) | Capability JSON Schema validation | Compile one strict schema once and format all errors before exiting nonzero. [VERIFIED: npm registry] |
| `yaml` | `2.8.1` | Parse GitHub workflow YAML in executable contract tests | Use its document parser so syntax errors are rejected before semantic workflow assertions; supports the repository Node floor. [VERIFIED: npm registry] |

### Existing Supporting Stack

| Tool | Version | Purpose | Planning note |
|------|---------|---------|---------------|
| pytest | `>=8.0` | Backend behavioral baseline | Already declared and passing 153 tests. [VERIFIED: pytest run] |
| TypeScript | resolved `5.9.3` | Strict compile gate and source-catalog AST | Reuse its compiler API for route/locale/theme/preference discovery instead of regex parsing TSX. [VERIFIED: package lock] |
| Vite | `8.1.2` | Build and test web server | Keep `npm run build`; Playwright may start Vite without a backend because API calls are intercepted. [VERIFIED: package lock] |
| Git | local `2.53.0.windows.3` | Merge base, index reads, and changed paths | Use Git plumbing with explicit argument arrays and full CI history. [VERIFIED: environment probe] |
| GitHub Actions | existing workflow | PR/main/tag orchestration | Keep the workflow trigger always present; select jobs after startup. [CITED: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax] |

### Alternatives Considered

No framework alternatives should be planned: pytest, Vitest/Testing Library/axe, Playwright, Chromium, and browser-level API fixtures are locked decisions.

**Installation:**

```bash
cd frontend
npm install --save-dev --save-exact \
  vitest@4.1.10 jsdom@29.1.1 \
  @testing-library/react@16.3.2 @testing-library/dom@10.4.1 \
  @testing-library/user-event@14.6.1 @testing-library/jest-dom@6.9.1 \
  axe-core@4.12.1 @playwright/test@1.61.1 \
  @axe-core/playwright@4.12.1 ajv@8.20.0 yaml@2.8.1
npm exec playwright install chromium
```

Use `npm ci` in CI; npm documents that it fails on package/lock disagreement and does not rewrite either file. [CITED: https://docs.npmjs.com/cli/v11/commands/npm-ci]

## Package Legitimacy Audit

The gate was run against the npm ecosystem. No checked package exposes a registry `postinstall` script. [VERIFIED: npm registry]

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `vitest` | npm | 4.6 years | 79.3M/week | github.com/vitest-dev/vitest | SUS (`too-new` latest release) | Flagged — checkpoint before install. [VERIFIED: package-legitimacy seam] |
| `jsdom` | npm | 14.7 years | 82.2M/week | github.com/jsdom/jsdom | OK | Approved. [VERIFIED: npm registry] |
| `@testing-library/react` | npm | 7.1 years | 47.6M/week | github.com/testing-library/react-testing-library | OK | Approved. [VERIFIED: npm registry] |
| `@testing-library/dom` | npm | 7.1 years | 58.2M/week | github.com/testing-library/dom-testing-library | OK | Approved. [VERIFIED: npm registry] |
| `@testing-library/user-event` | npm | 7.1 years | 41.3M/week | github.com/testing-library/user-event | OK | Approved. [VERIFIED: npm registry] |
| `@testing-library/jest-dom` | npm | 7.0 years | 53.3M/week | github.com/testing-library/jest-dom | SUS (`too-new` latest release) | Flagged; pin Node-20-compatible `6.9.1`. [VERIFIED: package-legitimacy seam] |
| `axe-core` | npm | 11.1 years | 57.6M/week | github.com/dequelabs/axe-core | OK | Approved. [VERIFIED: npm registry] |
| `@axe-core/playwright` | npm | 5.1 years | 6.5M/week | github.com/dequelabs/axe-core-npm | SUS (`too-new` latest release) | Flagged — checkpoint before install. [VERIFIED: package-legitimacy seam] |
| `@playwright/test` | npm | 5.8 years | 46.6M/week | github.com/microsoft/playwright | SUS (`too-new` latest release) | Flagged — checkpoint before install. [VERIFIED: package-legitimacy seam] |
| `ajv` | npm | 11.1 years | 340.2M/week | github.com/ajv-validator/ajv | OK | Approved. [VERIFIED: npm registry] |
| `yaml` | npm | established | registry verified | github.com/eemeli/yaml | OK | Exact `2.8.1`; Node >=14.6; no registry postinstall. [VERIFIED: npm registry] |

**Packages removed due to SLOP verdict:** none  
**Packages flagged as suspicious (planner must insert a blocking `checkpoint:human-action` before installation):** `vitest`, `@testing-library/jest-dom`, `@axe-core/playwright`, `@playwright/test`

## Recommended File and Command Contract

### Recommended Project Structure

```text
VERSION                                      # canonical stable X.Y.Z
version-policy.json                          # exact directories/files/excludes
.githooks/pre-commit                         # shell shim; delegates to Node
scripts/
├── version.mjs                              # public CLI
├── setup.mjs                                # idempotent core.hooksPath setup
├── docker-version.mjs                       # root VERSION adapter for Compose/CI
├── ci-changes.mjs                           # emits selected job booleans
├── lib/version-policy.mjs                   # pure parsing/diff/version logic
└── tests/version-policy.test.mjs            # node:test + temporary Git repos
capabilities/
├── schema.json                              # strict inventory schema
└── inventory.json                           # canonical capability records
docs/CAPABILITIES.md                         # deterministic generated review
frontend/
├── scripts/
│   ├── capabilities.mjs                     # check/generate/discover CLI
│   ├── capabilities.test.mjs                # validator/discovery fixtures
│   └── workflow-contract.test.mjs            # resolves yaml from frontend install
├── src/test/
│   ├── setup.ts                             # cleanup + jest-dom/vitest
│   ├── render.tsx                           # providers/router helper
│   └── a11y.ts                              # axe helper
├── e2e/
│   ├── fixtures/api.ts                      # strict stateful API router
│   ├── fixtures/data.ts                     # fixed IDs/times/payloads
│   └── reference-journey.spec.ts
├── vitest.config.ts
└── playwright.config.ts
backend/
├── app/version.py                           # reads root VERSION
└── tests/test_meta.py                       # exposed-version contract
.github/workflows/
├── ci.yml                                   # always-present test/gate workflow
└── docker.yml                               # reusable publish workflow
```

Recommended public commands:

```text
node scripts/version.mjs check --base <sha> --head <sha>
node scripts/version.mjs check --staged
node scripts/version.mjs bump [--minor | --major] [--base <ref>]
node scripts/version.mjs print
node scripts/setup.mjs
node scripts/docker-version.mjs print
node scripts/docker-version.mjs compose up -d --build
node frontend/scripts/capabilities.mjs check
node frontend/scripts/capabilities.mjs generate
node frontend/scripts/capabilities.mjs discover
npm --prefix frontend run test
npm --prefix frontend run test:e2e
npm --prefix frontend run test:e2e:update
npm --prefix frontend run test:contracts
npm --prefix frontend run validate:phase
python -m pytest backend/tests
```

Every version-policy failure path must end with exactly `node scripts/version.mjs bump`; additional diagnostic lines may explain the base/current version and protected paths. This exact command is a locked interface.

## Architecture Patterns

### System Architecture Diagram

```text
Contributor changes
      |
      +--> node scripts/setup.mjs --> git config --local core.hooksPath .githooks
      |
      +--> git commit --> pre-commit --> version.mjs check --staged
                                      --> version-policy.json
                                      --> staged index + merge base
                                      --> allow OR exact remediation

Pull request / main push / vX.Y.Z tag
      |
      v
GitHub Actions: changes job (full history)
      |
      +--> ALWAYS: version + inventory validation
      +--> SELECT: backend pytest
      +--> SELECT: frontend build + Vitest + axe
      +--> SELECT: Chromium journey + axe + screenshots
      |
      v
delivery / gate (always executes and validates selected results)
      |
      +--> PR: required merge check
      +--> main/tag: reusable Docker publish job

Source catalogs --> capability discovery --> inventory.json --> Ajv/reference checks
                                                        \--> generated CAPABILITIES.md

Playwright --> Vite-served real React app --> strict browser API fixture
                                        \--> committed snapshots + failure artifacts
```

### Pattern 1: One Pure Version Engine, Three Adapters

**What:** Keep parsing, path classification, version comparison, and target calculation in pure functions. The CLI, pre-commit hook, and CI pass different Git inputs into the same engine. [CITED: https://git-scm.com/docs/githooks]

**Required semantics:**

1. Normalize Git paths to `/`; classify exact files and directory prefixes from `version-policy.json`.
2. Resolve the base from explicit `--base`, then CI inputs, then local `origin/main` merge base.
3. For the initial migration only, read base `VERSION`; if absent, read base `frontend/package.json.version` as `1.0.0`.
4. Read current data from the working tree for `bump`, from the index for `--staged`, and from the requested commit for CI.
5. Require current stable `X.Y.Z` to be numerically greater than base when the aggregate branch diff contains a protected path.
6. Treat an already sufficient patch/minor/major version as a no-op, even across later commits in the same branch.
7. Synchronize the root package records in both frontend manifests atomically; never invoke `npm version`, which can add unrelated Git/tag behavior.

**Policy shape:**

```json
{
  "schemaVersion": 1,
  "include": {
    "directories": [
      "backend", "frontend", "plugins", "homeassistant",
      "deploy", "scripts", ".github/workflows"
    ],
    "files": ["Dockerfile", "docker-compose.yml", "docker-compose.build.yml"]
  },
  "exclude": []
}
```

Use exact directory-prefix and file matching rather than implementing a custom glob language. Validate that every root `docker-compose*.yml` file is explicitly present so future compose files cannot silently escape policy.

### Pattern 2: Index-Accurate Hook

The hook must inspect the staged snapshot, not working-tree files. A developer with an unstaged `VERSION` edit must still fail. The branch-level merge-base comparison prevents repeated bumps on every commit after the branch has already moved from `1.0.0` to `1.0.1`. A nonzero pre-commit exit aborts `git commit`. [CITED: https://git-scm.com/docs/githooks#_pre_commit]

```sh
#!/bin/sh
exec node scripts/version.mjs check --staged
```

`node scripts/setup.mjs` should run `git config --local core.hooksPath .githooks`, read the value back, and return success when already configured. Commit the hook executable bit explicitly despite this worktree reporting `core.filemode=false`. [VERIFIED: git config probe]

### Pattern 3: Runtime Reads Canonical Version

`backend/app/version.py` should resolve repository/image root and read `VERSION`; `Dockerfile` must copy `VERSION` to `/app/VERSION`. `meta.py` imports that accessor rather than retaining a constant. The Docker build accepts a required `VERSION` argument and emits `LABEL org.opencontainers.image.version=$VERSION`; OCI defines that annotation as the packaged software version. [CITED: https://github.com/opencontainers/image-spec/blob/main/annotations.md]

`scripts/docker-version.mjs` is the canonical build adapter. Its `print` operation reads and validates root VERSION for CI; its `compose` operation injects the same value as `WATCHVAULT_VERSION` while invoking the existing two-file Compose workflow through argument arrays. `docker-compose.build.yml` maps that required environment value to `build.args.VERSION` without a default. A missing/malformed root file, conflicting caller value, absent Compose mapping, or hardcoded drift fails clearly. README and the Compose override document `node scripts/docker-version.mjs compose up -d --build`, preserving the existing source-build services/files/flags without creating a second version record. On a tag, `version.mjs check` also requires `GITHUB_REF_NAME === "v" + VERSION`.

### Pattern 4: Strict Inventory with Discovery, Not Generation from Source

Source scanning should produce **candidates and missing IDs**, not overwrite human-authored behavior. Ajv validates shape; TypeScript's compiler API discovers React route JSX and exported locale/theme/preference catalogs; source-reference checks verify file and anchor existence; requirement checks parse the 64 IDs and roadmap mappings. [VERIFIED: codebase grep] [CITED: https://ajv.js.org/guide/getting-started.html]

Recommended record:

```json
{
  "id": "action.title.add-watch",
  "kind": "action",
  "source": [{"path": "frontend/src/pages/TitleDetail.tsx", "anchor": "addWatch"}],
  "behavior": "Authorized user adds a dated watch for the selected profile.",
  "dimensions": {
    "permissions": ["ingest.write"],
    "scopes": ["personal", "household"],
    "themes": ["dark", "light"],
    "locales": ["de", "en", "es", "fr", "it", "nl"],
    "states": ["idle", "pending", "success", "error"]
  },
  "owner": {"requirement": "TITL-04", "phase": 5},
  "evidence": [
    {"status": "existing", "kind": "playwright", "ref": "reference-journey:add-watch"}
  ]
}
```

Schema rules should use `additionalProperties: false`, stable ID pattern `^(route|action|permission|scope|preference|locale|theme|state)\.[a-z0-9.-]+$`, enums for `kind/status/evidence`, nonempty dimensions, and unique IDs enforced after schema validation. Generated Markdown sorts by owning phase, requirement, kind, and ID and ends with one newline.

### Pattern 5: Stateful, Fail-Closed Browser API Fixture

Install `context.route("**/api/**", handler)` before the first navigation. The fixture should authenticate a fixed user, return fixed profile/preferences/catalog data, mutate in-memory watch state on the expected POST, and return refreshed title/dashboard responses afterward. Any unhandled request, unexpected method/body, external font, or image request must be recorded and fail the test after cleanup. [CITED: https://playwright.dev/docs/mock]

The current application has no history route, so the baseline journey should be:

1. Render dashboard with fixed recent/summary data.
2. Navigate to search and select the fixed title.
3. Add a dated watch from title detail and assert the exact API mutation.
4. Return to dashboard and assert the new recent-history state.

Use four projects:

| Project | Viewport | Theme |
|---------|----------|-------|
| `chromium-desktop-dark` | 1440×900 | dark |
| `chromium-desktop-light` | 1440×900 | light |
| `chromium-mobile-dark` | 390×844, touch/mobile | dark |
| `chromium-mobile-light` | 390×844, touch/mobile | light |

Capture four checkpoints per project (dashboard, search, title detail, post-mutation history), yielding 16 committed baseline images. Set `animations: "disabled"`, CSS-scale screenshots, fixed locale/timezone/time, and `maxDiffPixelRatio: 0.001`. Store HTML report, traces, and diffs only on failure for 14 days.

Playwright warns that rendering varies by OS/browser/settings; generate and compare authoritative baselines in the matching `mcr.microsoft.com/playwright:v1.61.1-noble` environment. [CITED: https://playwright.dev/docs/test-snapshots]

### Pattern 6: Always-Present Aggregate CI Gate

Do not put top-level PR `paths` filters on the required workflow. GitHub documents that a workflow skipped by path filters can leave required checks pending. Instead:

1. Trigger `ci.yml` for every PR and for pushes to `main` and `v*` tags.
2. Checkout with full history/tags (`fetch-depth: 0`).
3. Run an always-present `changes` job using `git diff --name-only` and repository-owned classification logic.
4. Always run version and inventory validation.
5. Always run the explicit frontend `test:contracts` package script covering version-policy, Docker/OCI/Compose, change-selection, workflow semantics, and capability tooling.
6. Provision clean runners explicitly: Python 3.12 plus both checked-in backend requirement files; Node 20.19.x plus `npm ci --prefix frontend`; and Playwright 1.61.1 Chromium in `mcr.microsoft.com/playwright:v1.61.1-noble`.
7. Conditionally run backend, frontend, and browser jobs on PRs; force all booleans true on `main` and tags.
8. Run ordinary visual comparison and baseline generation in the identical pinned Playwright container/browser environment.
9. Run `delivery / gate` with `if: always()` and fail unless all selected dependencies succeeded.
10. Call the reusable Docker workflow only after the gate on `main`/tag pushes; feed its VERSION build argument from `scripts/docker-version.mjs print`.

`frontend/**` selects frontend and browser; `backend/**`/`plugins/**` select backend; browser also runs for backend API/auth contract changes. Changes to CI, scripts, Docker/deploy/compose, test selectors, or fixture infrastructure select the full suite. Home Assistant-only changes run version/inventory unless shared scrobble code also changed.

Place `workflow-contract.test.mjs` under `frontend/scripts`, not root `scripts/tests`. ESM package resolution then climbs to `frontend/node_modules/yaml` after the ordinary lockfile-clean install. The contract must reject a CI workflow that omits any explicit contract suite or clean-runner provisioning step; do not rely on `NODE_PATH`, a root package installation, or broad test globs.

### Anti-Patterns to Avoid

- **Comparing only `HEAD~1`:** misses the aggregate PR diff and breaks multi-commit idempotency.
- **Reading the working tree in pre-commit:** lets an unstaged bump satisfy a staged protected change.
- **Duplicating protected paths in YAML/hook/scripts:** causes policy drift; all adapters consume `version-policy.json`.
- **Using top-level workflow path filters:** can leave a required check pending rather than producing a stable aggregate result. [CITED: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions]
- **Publishing in a parallel workflow:** the existing Docker job can currently publish without tests; publication must depend on the gate. [VERIFIED: codebase grep]
- **Permissive browser fixtures:** returning generic success for unknown API calls masks accidental contract changes.
- **Generating inventory behavior from syntax:** source code can reveal candidates but cannot infer current UX, permissions, failure states, or future ownership safely.
- **Accepting new snapshots in the normal PR job:** intentional updates must be a separate command/artifact and reviewed as image diffs.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON Schema execution | Recursive ad-hoc field checks | Ajv strict mode | Handles schema keywords, nested paths, and complete error reporting. [CITED: https://ajv.js.org/strict-mode.html] |
| TypeScript/TSX discovery | Regex parser for routes and object literals | Existing TypeScript compiler API | JSX and typed object syntax exceed safe regex parsing. [VERIFIED: package lock] |
| DOM/user interactions | Direct DOM selectors and synthetic low-level events | Testing Library + user-event | Queries and interaction should reflect user-observable behavior. [CITED: https://testing-library.com/docs/guiding-principles/] |
| Accessibility rules | Custom ARIA heuristics | axe-core / `@axe-core/playwright` | The standard engine covers common machine-detectable violations. [CITED: https://playwright.dev/docs/accessibility-testing] |
| Device/browser/screenshot engine | Puppeteer scripts or image-diff code | Playwright projects and `toHaveScreenshot` | It owns browser binaries, emulation, retries, artifacts, and comparison. [CITED: https://playwright.dev/docs/test-snapshots] |
| Full SemVer implementation | Prerelease/build parser | Explicit stable `X.Y.Z` policy | This release contract only accepts stable numeric versions and `vX.Y.Z` tags. [CITED: https://semver.org/] |
| General path-glob engine | Homegrown `**` matcher | Exact file/directory-prefix policy | Locked paths fit a simpler, testable representation without another root dependency. |

**Key insight:** custom code should express WatchVault-specific policy and inventory ownership; standards libraries should own schema, DOM, accessibility, browser, and visual edge cases.

## Common Pitfalls

### Pitfall 1: Initial Base Revision Has No `VERSION`
**What goes wrong:** the first PR cannot compare versions or incorrectly treats `1.0.1` as an arbitrary new version.  
**Why:** `main` currently stores the baseline only in the frontend manifests. [VERIFIED: codebase grep]  
**Avoid:** implement and test the one-time base fallback before enforcing CI; current/head revisions must still require root `VERSION`.

### Pitfall 2: A Bump Is Required for Every Commit
**What goes wrong:** a multi-commit PR reaches `1.0.5` despite one patch-level change set.  
**Why:** hook logic compares index version to `HEAD` instead of merge-base version.  
**Avoid:** compare the aggregate merge-base-to-index diff; once `1.0.1 > 1.0.0`, later protected commits are valid and `bump` is a no-op.

### Pitfall 3: Manifest Drift Is Hidden
**What goes wrong:** root `VERSION` changes but package-lock's root package or package.json does not.  
**Avoid:** parse JSON and verify all three values on every hook/CI invocation, even when no protected path changed; update both manifests atomically.

### Pitfall 4: Latest jest-dom Breaks the Existing Node Contract
**What goes wrong:** clean Node 20 installs fail because `@testing-library/jest-dom@7.0.0` declares Node `>=22`. [VERIFIED: npm registry]  
**Avoid:** pin `6.9.1` and keep the package checkpoint explicit.

### Pitfall 5: Visual Baselines Flake Across Hosts
**What goes wrong:** font rendering, browser revisions, animation, time, or images produce unexplained diffs.  
**Avoid:** same Playwright package/container, Chromium only, fixed data/time/theme/viewport, local assets, disabled animation, and reviewed update artifacts. [CITED: https://playwright.dev/docs/test-snapshots]

### Pitfall 6: Browser Fixtures Accidentally Test a Fake UI
**What goes wrong:** broad route mocks return shapes that no real API returns, so the journey passes while backend contracts regress.  
**Avoid:** fixture payloads mirror checked-in backend response shapes; backend remains independently covered by pytest; unhandled browser requests fail. [VERIFIED: codebase grep]

### Pitfall 7: Static Discovery Is Mistaken for Completeness
**What goes wrong:** 116 endpoint decorators or 178 button/form markers become one entry each, producing duplicates and missing stateful behavior. [VERIFIED: codebase grep]  
**Avoid:** discovery reports candidates; a maintainer reviews atomic behavior, permissions, dimensions, and ownership in generated Markdown.

### Pitfall 8: CI Fails but Merge Is Still Allowed
**What goes wrong:** the workflow is red but repository rules do not require it.  
**Why:** the live ruleset currently has no pull-request or required-check rule. [VERIFIED: GitHub API]  
**Avoid:** after `delivery / gate` has run once, configure the main-branch ruleset to require pull requests and that exact check.

### Pitfall 9: axe Is Treated as Full Accessibility Proof
**What goes wrong:** tests pass despite keyboard order, focus, announcements, or contrast over dynamic artwork remaining unusable.  
**Avoid:** use axe as automated regression evidence, not a replacement for later manual WCAG verification. [CITED: https://playwright.dev/docs/accessibility-testing]

### Pitfall 10: Required Docker ARG Breaks Local Compose
**What goes wrong:** changing Dockerfile to require VERSION makes the existing scalar `build: .` override fail or encourages a duplicated `.env` version.
**Avoid:** route local Compose and CI through `scripts/docker-version.mjs`, require Compose interpolation with no default, preserve the two-file `up -d --build` flow through the adapter, and contract-test missing/conflicting/drifted input.

## Code Examples

### Vitest Configuration

```typescript
// Source: https://vitest.dev/config/environment
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    clearMocks: true,
    restoreMocks: true,
  },
});
```

### Testing Library Setup

```typescript
// Source: https://testing-library.com/docs/react-testing-library/setup/
import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(cleanup);
```

### Stateful Playwright Fixture Boundary

```typescript
// Source: https://playwright.dev/docs/mock
await context.route("**/api/**", async (route) => {
  const request = route.request();
  const response = scenario.handle(request.method(), new URL(request.url()), request.postDataJSON());
  if (!response) {
    unhandled.push(`${request.method()} ${request.url()}`);
    await route.abort("failed");
    return;
  }
  await route.fulfill({ status: response.status, json: response.body });
});
```

### Visual Assertion

```typescript
// Source: https://playwright.dev/docs/test-snapshots
await expect(page).toHaveScreenshot("dashboard.png", {
  animations: "disabled",
  maxDiffPixelRatio: 0.001,
  scale: "css",
});
```

### OCI Image Version

```dockerfile
# Source: https://github.com/opencontainers/image-spec/blob/main/annotations.md
ARG VERSION
RUN test -n "$VERSION"
LABEL org.opencontainers.image.version=$VERSION
COPY VERSION /app/VERSION
```

## State of the Art

| Old/current approach | Phase 1 approach | Impact |
|----------------------|------------------|--------|
| Three hardcoded `1.0.0` values | Root `VERSION` plus consuming metadata | One reviewable product identity. [VERIFIED: codebase grep] |
| `npm install` in Docker build | `npm ci` against synchronized lockfile | Clean install fails on lock drift instead of rewriting it. [CITED: https://docs.npmjs.com/cli/v11/commands/npm-ci] |
| Docker publish workflow with no test dependency | Aggregate CI gate before reusable publish | Failed selected evidence prevents image publication. [VERIFIED: codebase grep] |
| Manual frontend verification | Vitest + Testing Library + axe + Playwright | Behavior, accessibility, journeys, and visuals produce artifacts. [CITED: https://playwright.dev/docs/intro] |
| No machine-readable parity baseline | Strict JSON plus generated Markdown and discovery | Existing behavior receives explicit redesign ownership. [VERIFIED: codebase grep] |

**Deprecated/outdated for this phase:**
- `@testing-library/jest-dom@7.0.0` is incompatible with the repository's Node 20 build contract; pin `6.9.1`. [VERIFIED: npm registry]
- `npm install` should not be used in CI once the new exact dependencies are committed; use `npm ci`. [CITED: https://docs.npmjs.com/cli/v11/commands/npm-ci]

## Planning Sequence and Dependencies

1. **Version core first:** policy, legacy-base fallback, pure tests, `VERSION=1.0.0`, synchronization, and CLI.
2. **Activate local enforcement:** hook, setup command, staged-index integration tests, backend version read, and Docker label path.
3. **Build inventory tooling before content:** schema, discovery/reference checks, deterministic generation, then populate/review the complete inventory.
4. **Install exact frontend stack after the package checkpoint:** add Vitest setup and focused routing/theme/action accessibility tests.
5. **Add Playwright after stable app fixtures exist:** fail-closed API state, four projects, mutation journey, axe scans, and reviewed screenshots.
6. **Integrate CI last:** changed-surface outputs, always-present validations, aggregate gate, reusable publish, failure artifacts, and live ruleset checkpoint.
7. **Run the required patch bump:** compare against the legacy `1.0.0` base, write/synchronize `1.0.1`, then prove a second `bump` is a no-op.

Do not enable the hook before the helper and migration tests pass. Do not configure a required GitHub check until its final stable name has appeared in a workflow run.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|

All implementation recommendations above derive from locked decisions, live repository inspection, registry checks, or cited official documentation; no training-only factual claims are relied upon.

## Open Questions (RESOLVED)

1. **Ruleset ownership:** A repository administrator must configure the live GitHub `main` ruleset as a blocking human action after the exact `delivery / gate` context has appeared in a real workflow run. The action requires pull requests, requires that exact status check, and permits no bypass. Repository tooling and the execution agent may verify the result through `gh api`, but must not claim or automate administrator approval.

2. **Authoritative visual generation:** `.github/workflows/ci.yml` must expose an explicit `workflow_dispatch` baseline-generation input that runs the exact Playwright 1.61.1 suite and Chromium revision inside the pinned Linux image `mcr.microsoft.com/playwright:v1.61.1-noble`. That route generates the 16 desktop/mobile × dark/light PNGs plus a manifest containing commit SHA, package/browser versions, container identity, and image hashes, then uploads them as a review artifact. Plan 01-10 downloads that Linux artifact before human approval and records the approved files in the repository; local Docker is neither required nor authoritative.

3. **CI/Compose version adapter and clean-runner contract:** `scripts/docker-version.mjs` reads the sole root VERSION for both local Compose and CI Docker build arguments. CI installs Python 3.12 dependencies from both backend requirement files, Node 20.19.x dependencies via `npm ci --prefix frontend`, and pinned Chromium in the Playwright 1.61.1 Noble container. Ordinary visual comparison uses the same container as generation. Workflow semantics live under `frontend/scripts` so `yaml@2.8.1` resolves from the frontend lockfile on a clean runner.

## Environment Availability

| Dependency | Required By | Available | Version / state | Fallback |
|------------|-------------|-----------|-----------------|----------|
| Node.js | Tooling/frontend | ✓ | `24.14.0` local; project floor `20.19`. [VERIFIED: environment/npm probe] | CI Node 20.19+ |
| npm | Frontend dependencies | ✓ | `11.9.0`. [VERIFIED: environment probe] | CI setup-node bundled npm |
| Python | Backend tests | ✓ | `3.14.3`; 153 tests pass. [VERIFIED: pytest run] | Project/CI Python 3.12 |
| Git | Merge-base/index/hook tests | ✓ | `2.53.0.windows.3`. [VERIFIED: environment probe] | GitHub runner Git |
| Docker | Authoritative visual container and image build | ✗ | Not installed. [VERIFIED: environment probe] | GitHub Actions container/buildx |
| Chromium | Playwright | ✗ | Package/browser not installed. [VERIFIED: repository inspection] | `npm exec playwright install chromium` after `npm ci` |
| GitHub API | Ruleset checkpoint | ✓ | Authenticated; read-default workflow permissions. [VERIFIED: GitHub API] | Manual repository settings UI |
| PostgreSQL | Phase regression suite | not required | Browser uses fixtures; pytest is DB-independent. [VERIFIED: codebase grep] | Existing CI test architecture |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:**
- Docker is missing locally; use GitHub Actions for authoritative Linux visual generation and image validation.
- Chromium is not installed; install the exact Playwright Chromium after dependency installation.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Backend framework | pytest `>=8.0` |
| Backend config | none; existing discovery under `backend/tests/` |
| Tooling framework | built-in `node:test` |
| Component framework | Vitest `4.1.10`, jsdom `29.1.1`, Testing Library, axe-core |
| Browser framework | Playwright Test `1.61.1`, Chromium only, `@axe-core/playwright` |
| Quick backend command | `python -m pytest backend/tests -q` |
| Quick tooling command | `npm --prefix frontend run test:contracts` |
| Quick frontend command | `npm --prefix frontend run test -- --run` |
| Full suite command | `npm --prefix frontend run validate:phase` in the pinned CI visual environment |

### Phase Requirements → Test Map

| Req ID | Behavior | Test type | Automated command | File exists? |
|--------|----------|-----------|-------------------|--------------|
| DELV-01 | Root/package/lock/backend/image/tag versions agree | unit + integration + CI | `node --test scripts/tests/version-policy.test.mjs && python -m pytest backend/tests/test_meta.py -q && node scripts/version.mjs check` | ❌ Wave 0 |
| DELV-02 | Protected diff without sufficient bump fails and prints exact command | temp-Git integration | `node --test scripts/tests/version-policy.test.mjs` | ❌ Wave 0 |
| DELV-03 | patch/minor/major bumps are correct and idempotent | unit + temp workspace | `node --test scripts/tests/version-policy.test.mjs` | ❌ Wave 0 |
| DELV-04 | configured hook reads staged index, blocks drift, and runs no heavy checks | temp-Git commit integration | `node --test scripts/tests/version-policy.test.mjs` | ❌ Wave 0 |
| DELV-05 | schema/IDs/refs/discovery/generated Markdown are valid and complete | validator + snapshot/reference | `node frontend/scripts/capabilities.mjs check` | ❌ Wave 0 |
| DELV-06 | existing backend, type/build, component, axe, visual, and journey checks pass | unit/component/a11y/E2E | full suite command above | pytest ✅; frontend/browser ❌ Wave 0 |

### Required Test Scenarios

**Version/tooling:**
- no protected changes → `bump` no-op;
- protected change from legacy base → patch to `1.0.1`;
- already-patched branch plus later protected commit → no-op/pass;
- explicit minor/major target and sufficient higher current version;
- malformed, equal, lower, prerelease, and unsynchronized versions fail;
- staged protected path plus unstaged `VERSION` fails;
- exact/prefix/exclude and Windows separator normalization;
- tag mismatch and Docker build-argument absence fail;
- every failure includes the exact remediation command.

**Inventory:**
- schema rejection, unknown/additional fields, duplicate IDs;
- missing/ambiguous source path or anchor;
- missing requirement, wrong roadmap phase, or missing evidence;
- route/locale/theme/preference candidate missing from inventory;
- generated Markdown byte drift;
- stable sort and line endings on Windows/Linux.

**Frontend/component:**
- auth loading/login/authenticated route gates;
- theme and preference application;
- semantic loading/error/action controls;
- keyboard/user-event behavior for one representative mutation;
- axe scan on representative login, shell, and action component.

**Playwright:**
- fixed dashboard renders without unhandled network;
- search finds and opens fixed title;
- add-watch sends exact body and updates fixture state;
- return dashboard shows the mutation;
- axe scan at each checkpoint;
- four projects produce 16 reviewed snapshots;
- fixture fails on unknown API method/path or external asset.

### Sampling Rate

- **Per task commit:** run the focused test file plus `node scripts/version.mjs check --staged` when staging.
- **Per wave merge:** version/inventory checks, all pytest, frontend build, and all Vitest.
- **Browser wave:** all four Playwright projects with screenshots and axe.
- **Phase gate:** complete suite green; verify `VERSION=1.0.1`; run `node scripts/version.mjs bump` again and assert no diff; verify live `delivery / gate` is required.

### Wave 0 Gaps

- [ ] `scripts/tests/version-policy.test.mjs` — DELV-01 through DELV-04 pure and temp-Git coverage
- [ ] `backend/tests/test_meta.py` — canonical runtime version
- [ ] `frontend/scripts/capabilities.test.mjs` — DELV-05 validator/discovery/generation
- [ ] `frontend/vitest.config.ts` and `frontend/src/test/setup.ts`
- [ ] representative `*.test.tsx` component/accessibility files
- [ ] `frontend/playwright.config.ts`, fixtures, journey spec, and 16 snapshots
- [ ] package installation and Chromium provisioning
- [ ] `.github/workflows/ci.yml` with stable aggregate check
- [ ] `frontend/scripts/workflow-contract.test.mjs` with frontend-local yaml resolution, explicit contract-suite execution, and fresh-runner provisioning assertions
- [ ] `scripts/docker-version.mjs` plus Compose/CI root-VERSION adapter contract
- [ ] post-run GitHub ruleset checkpoint

## CI Job Selection Matrix

| Changed surface | Version/inventory | Backend | Frontend | Browser |
|-----------------|-------------------|---------|----------|---------|
| Any PR | always | selected | selected | selected |
| `backend/**`, `plugins/**` | ✓ | ✓ | API-shape dependent | API/auth paths ✓ |
| `frontend/**` | ✓ | — | ✓ | ✓ |
| `scripts/**`, workflow, Docker/deploy/compose | ✓ | ✓ | ✓ | ✓ |
| `capabilities/**`, generated report | ✓ | — | — | — |
| `homeassistant/**` only | ✓ | — | — | — |
| push `main` or `v*` tag | ✓ | ✓ | ✓ | ✓ |

Upload `playwright-report`, traces, and screenshot diffs on browser failure with 14-day retention. Upload generated inventory diff on validation failure so stale documentation is diagnosable. GitHub supports named artifact paths and retention configuration. [CITED: https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts]

## Security Domain

`security_enforcement` is enabled at ASVS level 1. [VERIFIED: `.planning/config.json`]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard control |
|---------------|---------|------------------|
| V2 Authentication | no runtime auth change | Browser uses fixed fake identities; do not weaken existing Flask auth |
| V3 Session Management | no runtime session change | Never use real session cookies in fixtures or artifacts |
| V4 Access Control | yes for inventory evidence | Inventory every seeded permission and every UI/API permission rule; pytest remains authoritative |
| V5 Input Validation | yes | Ajv strict schema; stable version parser; normalized Git paths; reject unknown fixture requests |
| V6 Cryptography | no | No cryptographic implementation in this phase |

### Known Threat Patterns

| Pattern | STRIDE | Standard mitigation |
|---------|--------|---------------------|
| Shell/argument injection through refs or paths | Tampering / Elevation | Use `spawnSync`/`execFileSync` argument arrays; never concatenate refs into a shell command |
| Path traversal or separator bypass | Tampering | Normalize Git paths to `/`, reject absolute/`..` paths, compare exact prefixes |
| Malicious PR receiving write credentials | Elevation / Disclosure | Use `pull_request`, read-only permissions, no `pull_request_target`, and skip publish/login on PR |
| Real credentials captured in traces | Information disclosure | Fully synthetic browser API fixtures; failure-only artifacts; no environment dumps |
| Schema ambiguity/prototype keys | Tampering | Ajv strict mode, `additionalProperties:false`, plain parsed data, bounded enums |
| CI bypass through optional/skipped checks | Tampering | Always-running aggregate gate plus required main-branch ruleset |
| Hook bypass with `--no-verify` | Tampering | Treat hook as feedback only; CI/ruleset remains authoritative |

## Sources

### Primary (HIGH confidence)
- Live WatchVault repository files and Git history — version duplicates, route/API/catalog counts, workflow behavior, test baseline, and integration points.
- GitHub REST API for `Flux76HQ/WatchVault` — live ruleset and Actions permissions.

### Secondary (MEDIUM confidence)
- None; Context7 and Jina providers were unavailable in this runtime.

### Tertiary (LOW confidence per provider-classification seam, official sources cited inline)
- https://vitest.dev/guide/ and configuration docs
- https://testing-library.com/docs/
- https://playwright.dev/docs/
- https://ajv.js.org/
- https://git-scm.com/docs/
- https://docs.github.com/en/actions/
- https://docs.npmjs.com/cli/v11/commands/npm-ci
- https://semver.org/
- https://github.com/opencontainers/image-spec/blob/main/annotations.md
- npm registry metadata and package-legitimacy seam

## Metadata

**Confidence breakdown:**
- Standard stack: LOW — official docs and registry were checked directly, but four mature official packages were conservatively marked SUS by the legitimacy seam because their latest releases are under 30 days old.
- Architecture: HIGH — derived from locked decisions, live source, passing tests, Git behavior, and live GitHub configuration.
- Pitfalls: MEDIUM — cross-checked against repository state and official docs, with visual and package-age uncertainty called out.

**Research date:** 2026-07-21  
**Valid until:** 2026-07-28 for package/browser pins; 2026-08-20 for repository architecture
