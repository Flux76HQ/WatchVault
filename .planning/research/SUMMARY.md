# Project Research Summary

**Project:** WatchVault full-app cinematic redesign
**Domain:** Self-hosted household media-tracking PWA
**Researched:** 2026-07-21
**Confidence:** MEDIUM-HIGH

## Executive Summary

WatchVault is a mature, self-hosted React/Flask media-tracking application, not a greenfield entertainment product. Experts would redesign it through an incremental frontend migration that preserves routes, permissions, profile and household scope, PWA behavior, localization, and every existing operation. The target is an artwork-led, dark-first interface with an equally deliberate light theme, but premium quality must come from coherent hierarchy, resilient states, responsive composition, and accessible interaction rather than visual effects alone.

The recommended approach is to retain React 18, TypeScript, Vite, Flask, PostgreSQL, and the modular monolith. Establish delivery gates and a behavioral baseline first, then strengthen the typed API and remote-state boundary, build semantic design foundations and wrapped accessible primitives, and replace the shell. Only then migrate the dashboard → search → title detail → watch-history journey as the first complete vertical slice. Secondary catalog, analytics, settings, import, profile, and integration surfaces follow using the proven system. Supporting Flask changes should be additive and limited to shaping existing data.

The greatest risks are capability loss during large page rewrites, inaccessible “cinematic” controls, dark/light and desktop/mobile drift, weak API contracts, authenticated service-worker cache leakage, artwork performance regressions, and releasing an unversioned or operationally unsafe image. Mitigate them with a route/action capability matrix, layered behavior and visual tests, centralized semantics and focus behavior, validated endpoint contracts, network-only private API data, explicit image budgets, and release gates for SemVer, secrets, reproducibility, PWA upgrades, rollback, backup, and restore.

## Key Findings

### Recommended Stack

Keep the existing application stack and introduce new frontend infrastructure only at stable seams. Use application-owned semantic tokens, CSS Modules, and wrapped headless primitives rather than replacing the styling or component architecture wholesale. Add typed server-state and regression tooling incrementally before route migration.

**Core technologies:**
- **React / React DOM 18.3.1:** retain the current runtime; defer React 19 to avoid combining a framework migration with the redesign.
- **TypeScript 5.9.x and Vite 8.1.x:** retain strict typing and the existing build system; take patch updates separately.
- **React Router 6.30.x, Recharts 2.15.x, and vite-plugin-pwa 1.3.x:** preserve route, chart, and PWA behavior during visual migration.
- **Node.js 24 LTS with npm and lockfile v3:** replace EOL Node 20 in a separately verifiable, version-bumped foundation change; use `npm ci`.
- **CSS custom properties, cascade layers, and CSS Modules:** primary design-system mechanism for semantic themes, component isolation, and controlled legacy coexistence.
- **Radix UI primitives, wrapped by WatchVault:** use selectively for dialogs, menus, tabs, tooltips, and other focus-intensive controls; feature pages must not import Radix directly.
- **TanStack Query 5 and Zod 4:** own scoped remote state and validate JSON at migrated endpoint boundaries without requiring OpenAPI or backend-wide refactoring.
- **Native responsive images and scroll overflow:** default for artwork and rails; add Embla or virtualization only after a measured need.
- **Storybook, Vitest, Testing Library, MSW, Playwright, and axe:** provide component states, behavior, contracts, critical journeys, responsive visual checks, and automated accessibility coverage.
- **ESLint 9, typescript-eslint, jsx-a11y, Prettier, and Stylelint:** enforce correctness without triggering an unrelated whole-repository formatting rewrite.

**Critical version constraints:**
- Pin ESLint 9 rather than 10 because the selected accessibility plugin does not declare ESLint 10 compatibility.
- Keep React 18, Router 6, and Recharts 2 for this milestone.
- Do not persist TanStack Query data in the first redesign release.
- Add Motion only after layout and semantics are stable, with user reduced-motion behavior configured at the app boundary.

### Expected Features

The milestone is successful only if it improves presentation and workflow quality while preserving the complete current capability set. Search, progress, editable history, household scope, provider provenance, statistics, administration, and PWA behavior are table stakes; the distinctive value is making those capabilities trustworthy and coherent for a private household.

**Must have (table stakes):**
- Semantic tokens and reusable primitives covering both themes, all interaction states, artwork, typography, spacing, motion, and focus.
- One adaptive application shell with equivalent desktop/mobile destinations, visible active location, deep-link recovery, and permission-aware navigation.
- Globally visible profile/household scope that cannot silently reset or leak stale data across scopes.
- A preserved, personalized dashboard with now playing, summaries, trends, recent/unfinished/unknown items, and meaningful zero states.
- Intent-first search with keyboard-usable suggestions, facets, active-filter summaries, URL/back-state preservation, and responsive results.
- Artwork-led title detail with robust metadata fallbacks, visible watch/progress state, complete media actions, and scalable season/episode navigation.
- History as a safe editable ledger with add/edit/remove, source and profile context, confirmation, pending/error feedback, and aggregate reconciliation.
- Complete statistics with consistent scope/range controls and non-color, non-pointer-dependent interpretations.
- Reorganized settings and administration that preserve profiles, imports, providers, plugins, tokens, tags, scrobbling, attribution, repair, and danger-zone operations.
- Dark, light, and system theme parity; 320 CSS-pixel reflow; keyboard operation; visible focus; semantic feedback; WCAG AA contrast; reduced motion.
- Specific loading, refreshing, empty, partial, error, forbidden, stale, and offline states.
- Capability inventory and automated frontend regression coverage for permissions, themes, locales, viewports, API contracts, and critical workflows.

**Should have (competitive differentiators):**
- A household viewing cockpit where one explicit scope control changes the product’s story.
- Source-visible history and integration health that make imported and scrobbled data trustworthy.
- A coherent repair workflow for unknown titles, attribution, metadata overrides, and history correction.
- Cross-provider now playing with honest stale/offline treatment.
- Progressive expert mode that reduces everyday clutter without acting as authorization.
- Privacy and ownership cues appropriate to a self-hosted product.
- Graceful metadata degradation and multilingual catalog context.
- Bounded dashboard personalization and a focused one-off cinema logging flow.

**Defer (v2+ or outside this milestone):**
- Recommendations, social feeds, follows, comments, public profiles, ratings, and reviews.
- Native mobile applications, net-new watchlists, release calendars, notifications, and streaming-availability discovery.
- Arbitrary dashboard widgets, autoplay video heroes, parallax, per-poster color extraction, and blanket carousel or virtualization abstractions.
- React 19, Router 7, Recharts 3, OpenAPI generation, broad Flask refactoring, or modular-monolith replacement.

### Architecture Approach

Use a strangler-style migration inside the existing application. The dependency direction is tokens → primitives → interaction patterns → shared media UI → feature modules → thin route pages, while feature hooks call typed endpoint contracts through the retained same-origin API client. `AppProvider` owns session-wide client state, TanStack Query owns remote state, URLs own navigable state, and local components own ephemeral state. Legacy and redesigned routes may coexist only behind explicit compatibility wrappers and CSS cascade layers.

**Major components:**
1. **App composition and shell** — compose providers, stable routing, landmarks, one typed navigation model, route announcements, safe areas, and responsive desktop/mobile presentations.
2. **Design-system foundations** — semantic theme, typography, layout, artwork, focus, motion, status, and responsive tokens.
3. **Accessible primitives and interaction patterns** — centralized controls, dialogs, menus, tabs, comboboxes, toasts, page states, and focus restoration.
4. **Shared domain UI** — pure `PosterCard`, `ArtworkHero`, `MediaRail`, progress, provider, profile, and history components separated from actions and fetching.
5. **Feature modules** — dashboard, search, titles, history, analytics, imports, profiles, and settings, each with contracts, hooks, view models, components, and screens.
6. **Typed remote-state boundary** — decode JSON as `unknown`, validate with feature-level Zod schemas, normalize errors, cancel stale requests, and use scope-complete query keys.
7. **Existing Flask modular monolith** — continue enforcing authorization and domain rules; make only additive serializers or focused response-shaping changes backed by API tests.
8. **Regression and release architecture** — layered unit, contract, component, API, E2E, visual, accessibility, PWA, and manual acceptance gates.

**Key patterns:**
- Branch by component boundary, then remove compatibility props after callers migrate.
- Pair a feature screen hook with a pure view and exhaustive loading/error/empty/ready states.
- Make API changes additive and purpose-built for existing workflows.
- Isolate legacy global CSS in the final cascade layer.
- Render desktop and mobile navigation from one route metadata model.
- Invalidate precise query-key families after mutations instead of dispatching global browser events.

### Critical Pitfalls

1. **Screen-by-screen reskinning loses capabilities** — inventory every route, action, permission, scope, preference, locale, theme, and state before replacement; require parity sign-off per route.
2. **Premium visuals undermine accessibility and theme parity** — centralize native semantics, keyboard/focus behavior, contrast-tested tokens, artwork scrims, reduced motion, zoom/reflow, and manual assistive checks before page styling.
3. **Large page rewrites mix extraction, data changes, and design** — characterize behavior first, extract typed hooks without visual change, then migrate focused vertical sections in reversible commits.
4. **Weak API typing and stale remote state cause production-only failures** — parse `unknown`, add focused Flask contract tests, include all scope values in query keys, cancel superseded requests, and explicitly invalidate aggregates.
5. **PWA caching exposes stale or cross-session private data** — remove authenticated API runtime caching, clear personalized caches on identity changes, version caches, and test install/upgrade/offline/logout/rollback paths.
6. **Artwork density harms mobile performance** — use one responsive artwork component, prioritize only the actual LCP image, lazy-load lower content, cap caches, lazy-load heavy routes, and set cold-mobile budgets.
7. **Desktop-first approval hides mobile failures** — test safe areas, virtual keyboards, orientation, 200% zoom, long translations, browser and installed PWA modes, and explicit alternatives to hover/drag/long-press.
8. **Late tests and weak release discipline make regressions irreproducible** — establish CI gates before visual work and publish only validated matching `vX.Y.Z` tags from locked inputs with immutable digests and operational rehearsal.

## Implications for Roadmap

Based on the combined research, use nine dependency-driven phases. Do not begin broad page restyling until Phases 1–4 establish safety, data, component, and shell contracts.

### Phase 1: Delivery Gates and Behavioral Baseline
**Rationale:** Every later phase needs a trustworthy definition of preserved behavior and enforceable delivery rules.
**Delivers:** Route/action capability matrix; deterministic fixtures; baseline reference-flow, permission, visual, and accessibility tests; backend tests in CI; canonical SemVer; protected-path bump guard and helper; git hooks; secret checks.
**Addresses:** Capability preservation, automated regression suite, measurable release discipline.
**Avoids:** Screen-reskin regressions, tests added after redesign, unversioned runtime changes, and secrets treated as cleanup.

### Phase 2: Typed API and PWA State Safety
**Rationale:** Redesigned data-heavy screens must not cement `any` payload assumptions or unsafe cross-session caching.
**Delivers:** Typed endpoint descriptors, Zod validation for bootstrap and reference-journey endpoints, normalized errors, TanStack Query provider and key factories, cancellation, mutation invalidation, logout teardown, and network-only authenticated API data.
**Addresses:** Scope correctness, reliable loading/error/stale behavior, safe history reconciliation.
**Avoids:** Backend drift, fetch races, global-context caching, and cross-session data leakage.

### Phase 3: Cinematic Design System and Accessible Primitives
**Rationale:** Shared semantic and interaction contracts must precede visual route migration.
**Delivers:** Dark/light/system tokens, typography, artwork and motion policies, CSS layers, component workshop, layout and feedback primitives, wrapped dialogs/menus/tabs/comboboxes, responsive and accessibility state tests.
**Addresses:** Theme parity, artwork treatment, keyboard/focus completeness, reduced motion, state-specific feedback.
**Avoids:** Design-system drift, text on uncontrolled artwork, page-local controls, and accessibility as a final audit.

### Phase 4: Adaptive Application Shell and Global Scope
**Rationale:** All routes need a stable responsive frame before their content is redesigned.
**Delivers:** `AppProviders`, stable router, one navigation model rendered for desktop/mobile, skip link and landmarks, route titles/announcements, visible scope control, permission-aware destinations, safe-area handling, and legacy-route compatibility.
**Addresses:** Navigation, deep links, profile/household scope, responsive PWA parity.
**Avoids:** Desktop/mobile forks, hidden active location, focus churn, and divergent permission navigation.

### Phase 5: Reference Journey Vertical Slice
**Rationale:** Dashboard → search → title detail → watch history exercises the architecture’s highest-value reads, mutations, scope, artwork, and feedback before broad rollout.
**Delivers:** Reference-quality dashboard, search/facets, title/episode detail, media actions, and add/edit/remove history across themes, desktop/mobile, keyboard, permission, empty/error/offline, and representative locale states.
**Addresses:** The milestone’s primary journey plus dashboard personalization, progress, repair, source-visible history, and one-off logging.
**Avoids:** Stale aggregates, missing history operations, artwork LCP regressions, and visually complete but behaviorally incomplete pages.

### Phase 6: Catalog and Analytics Surfaces
**Rationale:** Person, genre, overview, and statistics routes can reuse media cards, filters, scoped queries, and chart patterns proven in the reference slice.
**Delivers:** Catalog traversal, overviews, statistics, accessible chart summaries, range/granularity controls, and responsive analytical layouts.
**Addresses:** Existing analytical views, cast/crew/person/genre traversal, scoped statistics.
**Avoids:** Hover-only chart meaning, color-only encoding, eager heavy bundles, and snapshots becoming the specification.

### Phase 7: Household, Sources, and Administration
**Rationale:** Permission-heavy settings, imports, profiles, and integrations are broad and risky; migrate them after forms, dialogs, feedback, and scope behavior are proven.
**Delivers:** Reorganized preferences, household/profile management, imports and connections, plugins/tokens/tags/scrobbling, attribution and repair, expert mode, authentication/recovery surfaces, and danger-zone workflows.
**Addresses:** Full capability preservation and WatchVault’s integration-health, privacy, repair, and operational-confidence differentiators.
**Avoids:** Buried advanced features, UI-only authorization, leaked provider secrets, vague long-running states, and destructive actions without confirmation.

### Phase 8: Cross-App Hardening and Legacy Removal
**Rationale:** Cleanup is safe only after every route has passed parity; full-system accessibility, responsive, performance, localization, and PWA behavior require an integrated audit.
**Delivers:** Legacy CSS/adaptor/event removal; dependency-boundary enforcement; complete route parity matrix; both-theme contrast; keyboard, screen-reader, zoom/reflow, device, locale, performance, cache, upgrade, offline, and auth-transition verification.
**Addresses:** WCAG AA, responsive feature parity, PWA reliability, regression completeness.
**Avoids:** Distant global CSS regressions, hidden mobile failures, PWA split-brain, and cleanup-driven capability loss.

### Phase 9: Tagged Release and Operational Readiness
**Rationale:** The redesign is not complete until self-hosters can identify, deploy, update, roll back, back up, and restore it safely.
**Delivers:** Matching `vX.Y.Z` release, reproducible artifact and immutable digest promotion, stable/latest/beta policy, provenance/SBOM, final screenshots and claims, complete operational README, and clean-host install/update/rollback/backup/restore rehearsal.
**Addresses:** Versioning, CI, release, secrets, and operations constraints.
**Avoids:** Mutable “latest” releases, mismatched tags, irreproducible images, stale documentation, and unrehearsed recovery.

### Phase Ordering Rationale

- Capability inventory and test gates must precede structural and visual change.
- Typed endpoint and cache contracts must precede data-heavy redesigned screens.
- Tokens and accessible patterns must precede the shell; the shell must precede route migration.
- The reference journey validates the shared architecture before secondary and high-risk administrative routes.
- Legacy removal follows route parity, while release operations follow full integrated hardening.
- Backend changes remain focused within the phase whose existing UI workflow needs them; no separate broad backend phase is warranted.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1:** inspect existing CI/version surfaces and define the exact protected-path, fixture, and browser baseline contracts.
- **Phase 2:** verify service-worker lifecycle and authenticated cache removal against real upgrade/logout scenarios; finalize high-value response schemas.
- **Phase 5:** profile production-sized artwork and data, validate dashboard customization semantics, and define the history invalidation matrix.
- **Phase 7:** inventory every permission-heavy settings/import/provider workflow and supporting status payload before splitting large pages.
- **Phase 8:** define the supported browser/device matrix, measurable performance budgets, and PWA upgrade/rollback scenarios.
- **Phase 9:** research artifact provenance/SBOM implementation and current deployment-channel behavior before release planning.

Phases with standard patterns (skip research-phase unless new evidence emerges):
- **Phase 3:** token, CSS Module, wrapped primitive, Storybook, and accessibility patterns are well documented.
- **Phase 4:** shared route metadata, semantic shell, responsive navigation, and route announcement patterns are established.
- **Phase 6:** media grids and accessible chart summaries can reuse patterns proven by Phase 5.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Existing stack fit is direct repository evidence; package/version claims use official docs and npm but were conservatively classified by the research seam. |
| Features | MEDIUM-HIGH | Current capabilities and constraints are repository-backed; competitor expectations and product comparisons are secondary evidence. |
| Architecture | MEDIUM-HIGH | Current boundaries and risks are directly observed; the target decomposition is an established incremental-migration recommendation that still needs implementation validation. |
| Pitfalls | HIGH | Most critical risks map to concrete current code, CI, PWA, page-size, typing, and operations evidence; ecosystem mitigations are medium confidence. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **No `.planning/STATE.md`:** scope was validated against `.planning/PROJECT.md`; create or refresh state when the roadmap workflow initializes milestone tracking.
- **Incomplete live capability inventory:** derive the route/action/permission/state matrix from the running app before any route is replaced.
- **Target browser and device support:** define an explicit matrix, including iOS Safari and installed PWA behavior, during Phase 1/8 planning.
- **Production performance data:** establish representative library sizes, cold-mobile baselines, bundle limits, image transfer/cache budgets, and route-specific thresholds.
- **Exact API contracts:** inspect real nullability, legacy records, provider variants, and permission responses before finalizing Zod schemas.
- **Headless primitive proof:** validate the chosen wrapped Radix primitives against React 18, portals, iOS behavior, and WatchVault styling in Phase 3.
- **PWA update policy:** decide whether auto-update can remain without losing unsaved work; verify old-tab, rollback, and cache cleanup behavior.
- **Release infrastructure:** identify the canonical version file, Python/base-image pinning strategy, provenance/SBOM tooling, and digest promotion mechanism.

## Sources

### Primary (HIGH confidence)
- `.planning/PROJECT.md` — active milestone scope, constraints, capabilities, and release requirements.
- `.planning/codebase/ARCHITECTURE.md`, `STRUCTURE.md`, `CONCERNS.md`, and `TESTING.md` — current modular-monolith boundaries, frontend structure, risks, and test coverage.
- Current WatchVault frontend app, page, API, PWA, token, layout, interaction, and route files — concrete implementation evidence.
- Current Dockerfile, Compose files, GitHub workflow, `.gitignore`, `.env.example`, and README — build, release, secret, and operational evidence.

### Secondary (MEDIUM confidence)
- W3C WCAG 2.2 and WAI-ARIA Authoring Practices — contrast, keyboard, focus, reflow, status, and widget behavior.
- React, React Router, TypeScript, Zod, and TanStack Query official documentation — component boundaries, route composition, `unknown` validation, query keys, and invalidation.
- Vite, Vite PWA, MDN CacheStorage, color-scheme, and reduced-motion documentation — styling and PWA/cache behavior.
- Vitest, Testing Library, Storybook, Playwright, and axe guidance — layered behavior, visual, responsive, and accessibility testing.
- Node.js release schedule, npm registry, npm `ci`, Docker CI guidance, GitHub Actions secret guidance, and Semantic Versioning — runtime and release recommendations.
- Trakt, Letterboxd, Jellyfin, Microsoft PWA, Carbon Design System, and web.dev guidance — media-tracking expectations, household management, PWA behavior, state patterns, targets, images, and LCP.

### Tertiary (LOW confidence or requires local validation)
- Exact 2026 package versions and compatibility claims retrieved directly from npm/official web pages under the configured confidence seam.
- Optional Embla Carousel and TanStack Virtual adoption; neither should be added without a demonstrated component or performance need.
- TV Time as a historical interaction reference; its homepage was observed as a shutdown page on the research date.

---
*Research completed: 2026-07-21*
*Ready for roadmap: yes*
