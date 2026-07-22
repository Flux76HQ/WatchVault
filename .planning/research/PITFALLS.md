# Domain Pitfalls

**Domain:** Full-application redesign of a mature self-hosted React media-tracking PWA  
**Project:** WatchVault  
**Researched:** 2026-07-21  
**Overall confidence:** HIGH for repository-specific findings; MEDIUM for ecosystem guidance

> Scope note: `.planning/STATE.md` is absent in this worktree. Scope was checked against the active redesign requirements and constraints in `.planning/PROJECT.md`.

## Recommended Phase Labels

These labels make the phase assignments below actionable for roadmap creation:

1. **Phase 0 — Delivery gates and behavioral baseline**
2. **Phase 1 — Design system, artwork primitives, and application shell**
3. **Phase 2 — Typed API and shared interaction foundations**
4. **Phase 3 — Reference journey: dashboard, search, title detail, history**
5. **Phase 4 — Remaining routes and administrative workflows**
6. **Phase 5 — Accessibility, responsive, performance, and PWA hardening**
7. **Phase 6 — Tagged release and operational readiness**

## Critical Pitfalls

Mistakes that can cause rewrites, data exposure, major regressions, or an unsafe release.

### Pitfall 1: Treating the Redesign as a Screen-by-Screen Reskin

**Confidence:** HIGH  
**What goes wrong:** A page looks complete while less-visible behavior disappears: profile scoping, permissions, expert-mode actions, dashboard customization, imports, destructive confirmations, passkeys, localization, provider management, manual history editing, and empty/error/loading states.  
**Why it happens:** The current capability set is broad, but behavior is concentrated inside large route modules. Visual acceptance based on a few happy-path screenshots does not exercise conditional paths.  
**Consequences:** A polished UI ships with hidden feature regressions and may weaken household or administrator controls. Late discovery forces page rewrites.  
**Warning signs:**
- “Done” is defined by visual similarity rather than a capability matrix.
- Only the default profile, English, dark theme, and administrator account are tested.
- Existing controls disappear because their purpose was not understood.
- New components are approved without loading, empty, error, permission-denied, and offline states.
**Prevention:**
- In Phase 0, inventory every route, action, permission, preference, profile scope, theme, locale, and expert-mode branch.
- Record baseline screenshots and behavioral tests before changing markup.
- Give each redesigned route a preservation checklist linked to existing API calls and user-visible actions.
- Require acceptance coverage for viewer/admin, own/household scope, dark/light/system, all supported locales, and narrow/wide viewports.
- Keep new product scope out; supporting API changes must only reshape existing data needed by the UI.
**Detection:** Compare network calls, accessible controls, and workflow outcomes between the baseline and redesigned route; do not compare screenshots alone.  
**Phase:** Phase 0 establishes the contract; Phases 3 and 4 must close it route by route.

### Pitfall 2: Design-System Drift Across Themes and Routes

**Confidence:** HIGH  
**What goes wrong:** “Cinematic” becomes a collection of one-off gradients, blur values, spacing, radii, shadows, artwork overlays, and interaction states. Dark mode receives attention while light or system mode becomes illegible or unfinished.  
**Why it happens:** WatchVault has semantic color tokens, but spacing and component behavior still mix global CSS, route-specific selectors, and many inline styles. Large pages make copying local styles easier than extending shared primitives. User-selected accent colors further expand the contrast matrix.  
**Consequences:** Visual inconsistency, inaccessible contrast, brittle CSS overrides, and expensive cleanup near release.  
**Warning signs:**
- Raw color, shadow, spacing, or blur values appear in page modules.
- A component requires route-specific CSS to look correct.
- New states are reviewed only in dark mode or with the default blue accent.
- Similar cards, dialogs, poster tiles, and buttons have subtly different behavior.
**Prevention:**
- Complete semantic tokens for typography, spacing, surfaces, overlays, focus, motion, artwork scrims, and status states before page redesign.
- Build shared primitives and a review gallery covering all states in light, dark, system, high-contrast accent, reduced motion, and reduced transparency.
- Ban new raw visual values in route components except documented data-driven cases.
- Make contrast testing include user-configurable accents over every surface.
**Detection:** Token lint/review, component-state screenshots, and dark/light visual comparisons should fail on raw-value drift.  
**Phase:** Phase 1; enforced in every later UI phase.

### Pitfall 3: Accessibility Lost Behind Premium Interactions

**Confidence:** HIGH for current risks; MEDIUM for external guidance  
**What goes wrong:** The redesign introduces attractive but inaccessible carousels, custom menus, overlays, long-press actions, motion, truncated labels, and artwork text overlays. Keyboard focus, zoom, semantics, focus containment, announcements, and contrast regress.  
**Why it happens:** Pointer and visual behavior are easier to demo than assistive behavior. Current code already blocks browser zoom in `frontend/index.html`, disables selection globally, exposes some actions primarily through long-press/context menu, and has overlays without complete dialog/focus-management behavior.  
**Consequences:** Failure of the milestone's WCAG AA requirement and inaccessible destructive or account-management workflows.  
**Warning signs:**
- `user-scalable=no`, gesture suppression, or keyboard-inaccessible pointer handlers remain.
- Focus moves behind an open dialog or is not restored to its trigger.
- A custom menu uses ARIA roles without arrow-key behavior.
- Meaning is conveyed only by artwork, color, hover, or motion.
- Focus rings are removed because they conflict with the visual design.
**Prevention:**
- Remove zoom suppression and verify text resize and 320 CSS-pixel reflow.
- Prefer native links, buttons, inputs, headings, landmarks, and dialogs before ARIA.
- Give every long-press/context action an obvious keyboard and touch alternative.
- Implement dialog focus entry, containment, Escape handling, return focus, accessible names, and background inertness.
- Preserve global `:focus-visible`; add skip navigation and route-heading focus behavior.
- Test contrast for text, controls, focus indicators, artwork scrims, themes, and arbitrary accents.
- Respect reduced motion and reduced transparency across all animation and glass effects.
- Run automated accessibility checks, but also perform keyboard, zoom/reflow, and screen-reader smoke tests.
**Detection:** Automated axe checks plus manual keyboard-only completion of authentication, reference journey, import, settings, and destructive workflows.  
**Phase:** Semantics begin in Phase 1, are tested in every feature phase, and receive a release gate in Phase 5.

### Pitfall 4: Desktop-First Approval Hiding Mobile PWA Failures

**Confidence:** HIGH  
**What goes wrong:** Desktop layouts pass while mobile suffers clipped dialogs, inaccessible controls behind the tab bar or virtual keyboard, horizontal overflow, unsafe-area problems, orientation breakage, accidental gestures, and iOS-specific fixed/sticky bugs.  
**Why it happens:** Current responsiveness relies mainly on a small set of width breakpoints. The code already contains iOS portal workarounds, fixed navigation, safe-area padding, horizontal chart/season scrolling, and aggressive gesture suppression—evidence that mobile behavior is not a simple CSS afterthought.  
**Consequences:** The only client—the PWA—becomes unreliable for a major usage mode.  
**Warning signs:**
- QA covers one desktop and one mobile screenshot width.
- Fixed heights or `100vh` are used without testing browser chrome and keyboards.
- Dialog actions or focused inputs sit behind the bottom navigation.
- Landscape, 200% text, long translations, and notched devices are untested.
- Hover-only discovery or drag-only reordering is introduced.
**Prevention:**
- Define a viewport/device matrix including 320, 360, 390, 768, and desktop widths; test portrait and landscape.
- Test installed standalone mode and browser mode on iOS Safari and Chromium.
- Use content-driven layout, safe-area insets, dynamic viewport units where needed, and scrollable dialogs with reachable actions.
- Provide non-drag and non-hover alternatives; preserve 44px touch targets.
- Add browser tests for navigation, virtual-keyboard forms, dialogs, horizontal regions, and scroll restoration.
**Detection:** Real-device or device-cloud smoke tests plus automated viewport suites with horizontal-overflow assertions.  
**Phase:** Phase 1 for shell/layout rules; Phases 3–4 per route; Phase 5 for the full matrix.

### Pitfall 5: Artwork-Led Design Causing LCP, Memory, and Cache Regressions

**Confidence:** HIGH for current implementation; MEDIUM for ecosystem guidance  
**What goes wrong:** Large posters and backdrops, blur effects, charts, and image caches make the interface visually rich but slow to start, janky while scrolling, bandwidth-heavy, or memory-intensive on mobile.  
**Why it happens:** Current poster images use lazy loading but do not use responsive `srcset`/`sizes`; the title hero uses a CSS background; the service worker can retain 600 poster entries for 30 days; and glass blur and chart code add rendering and bundle cost. A redesign usually increases image area before adding an image policy.  
**Consequences:** Slow LCP, layout shifts, excessive downloads, cache/storage pressure, and degraded low-end-device behavior.  
**Warning signs:**
- The hero/LCP image is lazy-loaded or discoverable only through CSS.
- Full-size artwork is served into small cards.
- Image dimensions/aspect ratios are absent.
- New pages load every rail or chart eagerly.
- Performance is judged on warm desktop caches only.
**Prevention:**
- Create one artwork component with explicit aspect ratio, width/height, responsive candidates, error fallback, and loading priority.
- Eagerly load and prioritize only the actual LCP image; lazy-load below-the-fold artwork.
- Request server/provider image sizes appropriate to rendered slots.
- Cap and version image caches; test storage cleanup and broken/expired URLs.
- Lazy-load heavy route/chart code and avoid unbounded DOM rails.
- Set measurable cold-load, mobile-throttled LCP, CLS, transfer, bundle, and cache budgets before increasing artwork density.
**Detection:** Lighthouse/Web Vitals on cold mobile profiles, bundle reports, network inspection, long-grid scroll profiling, and Cache Storage size checks.  
**Phase:** Artwork primitives in Phase 1; reference-flow measurement in Phase 3; hard budgets and cleanup in Phase 5.

### Pitfall 6: Service-Worker Split-Brain and Cross-Session Data Leakage

**Confidence:** HIGH  
**What goes wrong:** Old HTML references removed hashed assets, an automatically activated worker reloads during an active workflow, stale runtime responses survive a deploy, or one household user sees another user's cached search/statistics after logout.  
**Why it happens:** `registerType: "autoUpdate"` is enabled; `/api/stats` and `/api/search` are cached in the origin-wide `wv-data` cache; logout clears React state but not Cache Storage; and blank-page recovery deletes every cache and unregisters every service worker.  
**Consequences:** Blank pages, lost form work, confusing mixed-version behavior, stale data, or privacy exposure on shared devices.  
**Warning signs:**
- Authenticated GET responses are added to runtime caching.
- Cache names change without explicit old-cache cleanup.
- PWA testing covers only a fresh install.
- Recovery logic becomes the normal update path.
- An update can reload while an import, edit, or settings form is active.
**Prevention:**
- Do not cache personalized API responses unless caches are safely partitioned by authenticated identity and purged on every auth transition; the safer default is network-only.
- Version runtime caches and explicitly delete obsolete caches on activation.
- Keep `sw.js` non-cacheable and test asset retention across worker activation.
- Choose an update UX that cannot discard unsaved work; if retaining auto-update, defer reload until a safe point.
- Purge session-bound caches on logout and session replacement.
- Test fresh install, upgrade with an old open tab, offline reopen, logout/login as another profile, rollback, and missing-asset recovery.
**Detection:** Automated multi-context PWA upgrade tests and manual Cache Storage inspection before and after auth transitions.  
**Phase:** Decide policy in Phase 0, implement and verify in Phase 5, block Phase 6 release on the upgrade matrix.

### Pitfall 7: Weak API Typing Moving Backend Drift Into Production

**Confidence:** HIGH  
**What goes wrong:** Redesigned components assume fields, nullability, enum values, or nested shapes that the Flask API does not guarantee. Errors appear only with certain titles, profiles, providers, or old data.  
**Why it happens:** `frontend/src/lib/api.ts` returns `Promise<any>`, query/body parameters are broadly `any`, preferences permit arbitrary keys, and major pages propagate untyped responses despite strict TypeScript.  
**Consequences:** Runtime crashes, incorrect empty states, unsafe optimistic updates, and repeated defensive logic throughout the redesign.  
**Warning signs:**
- New components accept `any` or duplicate local response interfaces.
- Optional chaining is used to mask unknown contracts rather than model them.
- Backend payload changes are merged without frontend contract tests.
- A page rewrite includes unrelated endpoint redesign.
**Prevention:**
- Define endpoint request/response types and make API methods generic before page migration.
- Add runtime validation for high-risk boundaries such as auth, preferences, title detail, search, and destructive mutations.
- Normalize API data in feature adapters/hooks; keep display components free of wire-format knowledge.
- Add backend serialization tests for contracts the UI depends on.
- Change backend response shapes only when directly required by the redesign.
**Detection:** No `any` at migrated boundaries, compile-time fixtures, malformed/null response tests, and backend/frontend contract checks.  
**Phase:** Phase 2 before Phases 3 and 4 consume the contracts.

### Pitfall 8: Oversized Page Rewrites Combining Refactor and Redesign

**Confidence:** HIGH  
**What goes wrong:** A single pull request simultaneously extracts state, changes API calls, replaces markup, introduces shared components, and restyles a 600–750-line page. Reviewers cannot isolate behavior changes, and React state resets when component identity or keys change.  
**Why it happens:** `TitleDetail.tsx` is about 753 lines, `Settings.tsx` 681, `Imports.tsx` 627, and `Dashboard.tsx` 415, with API, state, workflow, and presentation concerns mixed together.  
**Consequences:** Hidden regressions, merge conflicts, stalled reviews, and expensive rollback.  
**Warning signs:**
- A whole large route is deleted and recreated at once.
- Component extraction and visual redesign occur in the same commit.
- Existing keys, URL state, polling, or optimistic state change without focused tests.
- Shared components are designed around one page's data shape.
**Prevention:**
- First add behavioral characterization tests.
- Extract typed hooks and stable feature components without visual change.
- Redesign one vertical workflow or section at a time behind stable route/API boundaries.
- Preserve stable keys and explicitly decide which state survives navigation, scope changes, and refresh.
- Keep commits independently buildable and reversible.
**Detection:** Review diff size and concern count; reject plans that cannot name a focused behavioral verification command for each slice.  
**Phase:** Extraction in Phase 2; sliced execution in Phases 3 and 4.

### Pitfall 9: Building the Test Harness After the Redesign

**Confidence:** HIGH  
**What goes wrong:** The team finishes the visual implementation before adding tests, leaving no trustworthy baseline and making failures impossible to attribute.  
**Why it happens:** There is no frontend unit/component/E2E runner. The existing workflow builds and publishes an image but does not explicitly run the 153 backend tests, accessibility checks, or browser tests.  
**Consequences:** Regressions reach published images, and late test adoption discovers architectural problems when change is most expensive.  
**Warning signs:**
- Phase 0 has no browser-test deliverable.
- CI only proves that the Docker image can build.
- Visual snapshots are the only frontend regression signal.
- Flaky tests are quarantined rather than fixed before route migration.
**Prevention:**
- Before visual work, add component tests for shared interactions and Playwright flows for authentication, reference journey, profile/theme changes, imports, and destructive confirmations.
- Add focused visual snapshots at stable component/page checkpoints, not full-page snapshots for every dynamic dataset.
- Add automated accessibility checks and manual-test evidence.
- Run frontend type/build, frontend tests, browser tests, and backend pytest before any publish job.
- Use deterministic seeded fixtures with representative missing artwork, long text, empty data, provider failures, and permission variants.
**Detection:** Protected branches and publish jobs cannot proceed without all required checks.  
**Phase:** Phase 0, then expanded alongside every later phase.

### Pitfall 10: Release Automation Publishing an Unversioned or Irreproducible Redesign

**Confidence:** HIGH  
**What goes wrong:** Runtime changes merge without a project-version bump; `main` publishes `latest`; a `v*` tag is accepted without exact SemVer/version matching; or rebuilding the same source produces different dependencies and artifacts.  
**Why it happens:** The current workflow publishes from `main`, `release/**`, tags, and manual dispatch; it has no test or SemVer guard. The only visible application version is the frontend package's `1.0.0`. Docker uses `npm install`, Python dependency ranges, mutable base-image tags, and major-version action tags. No release tags exist in the inspected history.  
**Consequences:** Operators cannot identify or reproduce the deployed UI, rollbacks become ambiguous, and broken images can be promoted as `latest`.  
**Warning signs:**
- A protected runtime/build/deploy/CI path changes with no version-file diff.
- The version exists in multiple unsynchronized files.
- Branch builds receive stable or latest channel tags.
- A release is described as “whatever `latest` points to.”
- Two builds of one commit resolve different dependencies or base images.
**Prevention:**
- Establish one canonical SemVer project version.
- Add a CI guard covering runtime, build, deploy, and workflow paths; when a bump is missing, fail with one exact remediation message.
- Provide an idempotent helper that defaults to a patch bump and updates every generated/version surface.
- Configure fast repository git hooks to run the same version guard; keep builds and browser suites in CI.
- Allow production publication only from validated `vX.Y.Z` tags that exactly match the canonical version and commit.
- Define channels explicitly: immutable `X.Y.Z` and digest always; `stable`/`latest` only after stable-tag success; `beta` only from prerelease tags; branch/SHA artifacts never promoted implicitly.
- Use lockfile-frozen frontend installs (`npm ci`), lock Python dependencies, pin build inputs where practical, and emit provenance/SBOM plus image digest.
- Build once and promote the same digest rather than rebuilding per channel.
**Detection:** CI tests missing/mismatched bumps, malformed tags, duplicate tags, forbidden channel promotion, dirty generated versions, and artifact digest/provenance presence.  
**Phase:** Enforcement in Phase 0; tag, channel, and artifact acceptance in Phase 6.

### Pitfall 11: Secrets and Operational Documentation Treated as Release Cleanup

**Confidence:** HIGH  
**What goes wrong:** A redesign-related deployment or CI change leaks credentials, introduces unsafe example values, or ships an image that operators cannot safely health-check, update, back up, restore, or roll back.  
**Why it happens:** UI work appears unrelated to operations. Currently `.gitignore` ignores `.env` but not all `.env.*` variants; `.env.example` is safely templated but contains obvious development placeholders; and the README covers setup, architecture, data locations, start, update, and backup, but lacks a complete app health-check procedure, restore rehearsal, version-pinned deployment, channel policy, and rollback flow.  
**Consequences:** Credential exposure, unrecoverable upgrades, deployment of the wrong channel, or operator confusion during PWA/cache incidents.  
**Warning signs:**
- `.env.production`, exported configs, screenshots, or workflow debug output appear in a diff.
- real tokens are used in fixtures or browser-test traces.
- README update instructions still say only “pull latest.”
- backup instructions exist without a tested restore procedure.
- no command maps a running container/image digest to the WatchVault version.
**Prevention:**
- Ignore `.env` variants while explicitly retaining only safe templates; run secret scanning in CI and pre-commit.
- Keep production credentials only in deployment/GitHub secret stores; use synthetic test credentials and sanitize traces/artifacts.
- Validate that `.env.example` contains placeholders, not working credentials, whenever configuration changes.
- Make the operational README release-gated for setup, run, stop, app and database health checks, version-pinned deploy/update, channel rules, rollback, backup, restore, architecture, and data locations.
- Add a restore rehearsal and verify migration compatibility before tagged release.
- Document PWA cache recovery without normalizing destructive “clear everything” as the first response.
**Detection:** Secret scanning, template checks, README contract checks, and a clean-host install/update/rollback/restore rehearsal using the tagged artifact.  
**Phase:** Secret and documentation gates in Phase 0; full operational rehearsal in Phase 6.

## Moderate Pitfalls

### Pitfall 1: UI Permission Logic Mistaken for Authorization

**Confidence:** HIGH  
**What goes wrong:** The redesign hides controls based on `can(...)`, expert mode, or profile scope and is assumed to secure the action, while backend permission behavior remains broader or inconsistent.  
**Warning signs:** Security acceptance says “button is hidden” rather than verifying the API response; cross-profile mutation paths are not tested.  
**Prevention:** Treat UI permissions as discoverability only. Add backend authorization tests for own/household scope, global title deletion, settings, provider credentials, and last-admin behavior.  
**Phase:** Phase 0 security baseline and Phases 3–4 per affected workflow.

### Pitfall 2: Persisted Preference and Layout IDs Breaking

**Confidence:** HIGH  
**What goes wrong:** Renaming dashboard blocks, theme values, or preference keys silently discards existing layouts and defaults.  
**Warning signs:** New component IDs are based on display labels; old saved layouts are tested only after manual reset.  
**Prevention:** Keep stable identifiers, normalize old preference payloads, version schemas when necessary, and test upgrade fixtures from existing saved layouts.  
**Phase:** Phase 1 for token/theme preferences; Phases 3–4 for route-specific layouts.

### Pitfall 3: Fetch Races and Stale State Masquerading as Visual Bugs

**Confidence:** HIGH  
**What goes wrong:** Rapid profile, filter, route, or locale changes allow an older request to overwrite newer data. Unmounted components update state, and silent refresh failures leave misleading stale content.  
**Warning signs:** Loading flicker, results from the previous profile, duplicate requests, or fixes based on arbitrary delays.  
**Prevention:** Add cancellation/stale-response protection to shared data hooks, model loading versus refreshing explicitly, and test rapid scope/navigation changes and error recovery.  
**Phase:** Phase 2.

### Pitfall 4: Localization and Real Data Breaking the Composition

**Confidence:** HIGH  
**What goes wrong:** German/French labels, long household names, missing images, unknown titles, dense episode metadata, and large histories overflow a design approved with short English fixtures.  
**Warning signs:** Fixed-width controls, ellipsis hiding essential actions, or untranslated strings introduced in JSX.  
**Prevention:** Use all six locales and long/missing/RTL-like stress strings in component fixtures; allow wrapping where meaning matters; keep all user text in the existing i18n layer.  
**Phase:** Phase 1 component states and every feature phase.

### Pitfall 5: Global CSS Changes Producing Distant Regressions

**Confidence:** HIGH  
**What goes wrong:** A selector changed for one redesigned route alters legacy routes, dialogs, charts, or mobile navigation.  
**Warning signs:** Broad selectors gain exceptions; specificity rises; route names appear in shared component rules.  
**Prevention:** Migrate toward scoped component primitives, keep global CSS limited to tokens/reset/layout contracts, and run visual checks across migrated and unmigrated routes after each shared-style change.  
**Phase:** Phase 1 and throughout Phases 3–4.

### Pitfall 6: Visual Snapshots Becoming the Product Specification

**Confidence:** MEDIUM  
**What goes wrong:** Snapshot approval rewards pixel stability while missing keyboard behavior, API outcomes, responsive adaptation, and dynamic content.  
**Warning signs:** Large screenshot updates are approved without explaining behavior; snapshots use only one theme and dataset.  
**Prevention:** Use screenshots only for stable visual contracts and pair them with semantic locators, workflow assertions, accessibility checks, and targeted state matrices.  
**Phase:** Phase 0 test strategy.

## Minor Pitfalls

### Pitfall 1: Stale Screenshots and Product Claims

**Confidence:** HIGH  
**What goes wrong:** README screenshots and “Highlights” continue to depict or describe the old shell.  
**Warning signs:** The release changes navigation but documentation assets do not change.  
**Prevention:** Capture deterministic desktop/mobile screenshots from the release artifact and review feature claims.  
**Phase:** Phase 6.

### Pitfall 2: Generated TypeScript State Polluting Redesign Diffs

**Confidence:** HIGH  
**What goes wrong:** Tracked `frontend/*.tsbuildinfo` files create unrelated build diffs and conflicts.  
**Warning signs:** A visual-only change modifies compiler-state files.  
**Prevention:** Ignore `*.tsbuildinfo`, remove tracked artifacts, and regenerate only in local/CI workspaces.  
**Phase:** Phase 0.

### Pitfall 3: Empty, Error, and Offline States Left Until the End

**Confidence:** HIGH  
**What goes wrong:** Happy-path cards are polished while missing artwork, no results, provider errors, expired sessions, and offline responses use inconsistent or inaccessible fallbacks.  
**Warning signs:** State components are added after page layout approval.  
**Prevention:** Require loading, refreshing, empty, partial, error, permission-denied, and offline states in each component's initial design contract.  
**Phase:** Phase 1 primitives; Phases 3–4 implementation.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Required Mitigation |
|-------------|----------------|---------------------|
| Phase 0 — Delivery gates and baseline | No trustworthy regression baseline; runtime changes evade versioning | Capability matrix, seeded browser flows, backend tests in CI, canonical SemVer, protected-path guard with exact remediation, bump helper, fast hooks, secret scan |
| Phase 1 — Design system and shell | Theme drift, inaccessible primitives, mobile shell breakage | Semantic tokens, state gallery, light/dark/system/accent contrast checks, native semantics, focus rules, zoom/reflow support, safe-area/device matrix |
| Phase 2 — Typed/shared foundations | `any` contracts and large-page extraction reset state | Typed endpoint contracts, high-risk runtime validation, cancellable data hooks, behavior-preserving extractions, stable keys |
| Phase 3 — Reference journey | Artwork/performance regressions and missing history actions | Shared artwork policy, cold mobile budgets, profile/permission variants, dashboard→search→detail→history E2E coverage |
| Phase 4 — Remaining routes | Rare admin/import/settings capabilities disappear | Route-specific preservation checklists, long-running/error states, provider secret redaction, localization and permission matrices |
| Phase 5 — Hardening | PWA split-brain, cross-session caches, inaccessible overlays | Upgrade/rollback/offline/auth-transition test matrix, network-only private APIs, old-cache cleanup, keyboard/screen-reader/reflow/device gates |
| Phase 6 — Release and operations | Mutable `latest`, mismatched tags, unreproducible image, unusable runbook | `vX.Y.Z`-only validated release, immutable digest promotion, stable/latest/beta rules, lockfile-frozen build, SBOM/provenance, clean-host and restore rehearsal, complete README |

## Release Blockers

Do not tag the redesign until all are true:

- The canonical project version is bumped according to SemVer and matches the `vX.Y.Z` tag.
- CI rejects protected runtime/build/deploy/workflow changes without a bump using the required exact remediation message.
- The idempotent bump helper and repository-configured fast git hooks are verified.
- Frontend build/tests, browser/accessibility tests, and backend pytest pass before publication.
- `.env` variants are ignored, `.env.example` remains placeholder-only, and secret scanning passes.
- The release artifact is built reproducibly from locked inputs, identified by immutable version and digest, and accompanied by provenance/SBOM evidence.
- Stable/latest/beta channel promotion follows documented tag rules and promotes the already-built digest.
- The README documents setup, run, stop, health checks, version-pinned deploy/update, rollback, backup, restore, architecture, and data locations.
- A clean-host installation, old-version upgrade, PWA update, rollback, backup, and restore have been rehearsed with the tagged artifact.

## Sources

### Repository Evidence — HIGH confidence

- `.planning/PROJECT.md` — active redesign, accessibility, responsiveness, theme, SemVer, CI, hook, secret, tag, artifact, and operations constraints.
- `.planning/codebase/CONCERNS.md` — large pages, weak API typing, cache privacy issue, missing frontend coverage, mutable build inputs, and CI gaps.
- `.planning/codebase/TESTING.md` — 153 backend tests; no frontend/component/E2E runner; publish workflow does not explicitly run pytest.
- `frontend/src/pages/TitleDetail.tsx`, `Settings.tsx`, `Imports.tsx`, `Dashboard.tsx` — oversized route modules.
- `frontend/src/lib/api.ts`, `useFetch.ts`, `app.tsx` — untyped API boundary, shared fetch behavior, themes/preferences, and logout behavior.
- `frontend/vite.config.ts`, `frontend/index.html`, `deploy/nginx.conf` — auto-update worker, personalized runtime caches, cache recovery, zoom suppression, and service-worker headers.
- `frontend/src/styles/tokens.css`, `app.css`, `components/ui.tsx`, `components/Menu.tsx`, `components/Layout.tsx` — theme, responsive, long-press, dialog/menu, focus, and artwork behavior.
- `.github/workflows/docker.yml`, `Dockerfile`, `docker-compose.yml`, `.gitignore`, `.env.example`, `README.md` — current publish, reproducibility, channel, secret, and operational-documentation state.

### External Guidance — MEDIUM confidence

- W3C, WCAG 2.2 Quick Reference: https://www.w3.org/WAI/WCAG22/quickref/
- W3C, Understanding Reflow: https://www.w3.org/WAI/WCAG22/Understanding/reflow.html
- W3C, Understanding Focus Visible: https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html
- Vite PWA, Automatic Reload: https://vite-pwa-org.netlify.app/guide/auto-update.html
- Vite PWA, Workbox `generateSW`: https://vite-pwa-org.netlify.app/workbox/generate-sw.html
- MDN, CacheStorage: https://developer.mozilla.org/en-US/docs/Web/API/CacheStorage
- web.dev, Optimize Largest Contentful Paint: https://web.dev/articles/optimize-lcp
- web.dev, Browser-level Image Lazy Loading: https://web.dev/articles/browser-level-image-lazy-loading
- web.dev, Responsive Images: https://web.dev/articles/responsive-images
- React, Preserving and Resetting State: https://react.dev/learn/preserving-and-resetting-state
- Testing Library, Guiding Principles: https://testing-library.com/docs/guiding-principles
- Playwright, Visual Comparisons: https://playwright.dev/docs/test-snapshots
- Semantic Versioning 2.0.0: https://semver.org/
- npm, `npm ci`: https://docs.npmjs.com/cli/v11/commands/npm-ci
- Docker, Test Before Push with GitHub Actions: https://docs.docker.com/build/ci/github-actions/test-before-push/
- GitHub, Using Secrets in GitHub Actions: https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions
