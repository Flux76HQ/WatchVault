# Technology Stack

**Project:** WatchVault full-app cinematic redesign  
**Researched:** 2026-07-21  
**Overall confidence:** MEDIUM — repository fit is based on direct inspection; external version and capability claims were cross-checked against official documentation and npm, but the configured confidence seam classifies direct web/npm retrieval as LOW.

## Recommendation

Keep the established React 18 + TypeScript + Vite PWA and its Flask/PostgreSQL backend. Build the redesign as an incremental, application-owned design system using semantic CSS custom properties, CSS Modules, and accessible unstyled Radix primitives. Add TanStack Query and Zod only at the frontend API boundary, not as an architecture rewrite. Establish Storybook, Vitest/Testing Library, Playwright, and axe before migrating screens.

The redesign should not introduce Tailwind, a styled component suite, CSS-in-JS, Redux, a new router, or a React 19 migration. Those choices create unrelated churn or constrain the visual language precisely where WatchVault needs custom artwork-led presentation.

## Recommended Stack

### Core Framework — Retain

| Technology | Version | Purpose | Decision and migration fit | Confidence |
|------------|---------|---------|----------------------------|------------|
| React / React DOM | 18.3.1 | Existing UI runtime | **Keep for this milestone.** React's official guide identifies 18.3 as the warning-enabled bridge to React 19. WatchVault is already on it; combining React 19 with a full UI rewrite would make regressions harder to isolate. | MEDIUM |
| TypeScript | 5.9.3 resolved | Existing strict frontend language | Keep. Its existing `strict` configuration is compatible with Zod 4 and the proposed tooling. Do not introduce TypeScript 6 during the redesign. | MEDIUM |
| Vite | 8.1.2 resolved; 8.1.5 current | Existing build and development server | Stay on Vite 8; take the 8.1.5 patch in a dedicated foundational tooling change, not mixed into a screen migration. CSS Modules are built in, so no styling compiler is needed. | MEDIUM |
| React Router DOM | 6.30.4 | Existing route shell | Keep route definitions and URLs stable. Router 7 is unrelated to visual quality and should be a later migration. | MEDIUM |
| `vite-plugin-pwa` | 1.3.0 | Existing manifest and Workbox service worker | Keep. Test redesign routes and image behavior against the current app-shell and caching rules rather than replacing the PWA layer. | MEDIUM |
| Recharts | 2.15.4 | Existing dashboard/statistics charts | Keep 2.x and wrap it in design-system chart components. Do not combine a Recharts major upgrade with chart restyling. | MEDIUM |

### Build Runtime

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Node.js | 24 LTS | Frontend build, tests, Storybook, Playwright tooling | Replace the Docker build stage's Node 20, which reached EOL in March 2026. Node 24 is LTS and supports the retained Vite/Vitest toolchain. Make this a separately testable, version-bumped infrastructure change. | LOW |
| npm + lockfile | npm bundled with pinned Node 24 image; lockfile v3 | Reproducible installs | Continue npm and commit `package-lock.json`; use `npm ci` in CI and container builds. Do not switch package managers during the redesign. | MEDIUM |

### Design System Foundation

| Technology | Version | Purpose | When to Use | Confidence |
|------------|---------|---------|-------------|------------|
| CSS custom properties + `@layer` + CSS Modules | Native / Vite 8 | Tokens, themes, component styles, legacy isolation | **Primary styling approach.** Expand `tokens.css` into primitive, semantic, and component tokens; preserve `data-theme`; put redesigned components in `*.module.css`. Use cascade layers to prevent legacy `app.css` from leaking into new components. | MEDIUM |
| Radix UI Primitives | Dialog 1.1.20; Dropdown Menu 2.1.21; Tooltip 1.2.13; Tabs 1.1.18; Slot 1.3.0 | Accessible behavior for complex controls | Use only for dialogs, menus, tooltips, tabs, popovers/selects, and composition where focus management or keyboard behavior is non-trivial. Wrap each primitive in WatchVault-owned components; pages should not import Radix directly. | LOW |
| `class-variance-authority` | 0.7.1 | Typed visual variants | Use inside design-system components for size, tone, emphasis, and state variants. It should compose semantic classes, not become a utility-CSS substitute. | LOW |
| `clsx` | 2.1.1 | Conditional class composition | Use with CSS Modules and CVA. | LOW |
| `lucide-react` | 1.25.0 | Consistent SVG icon set | Replace ad hoc icon markup through one `Icon` wrapper with standardized size, stroke, labels, and decorative handling. Import icons individually. | LOW |
| `@fontsource-variable/manrope` | 5.3.0 | Self-hosted variable UI/display typography | Use one variable family for headings and UI with weight/size/tracking tokens. It works offline and avoids a third-party font request. Keep system fallbacks and avoid multiple display-font payloads. | LOW |
| Motion for React (`motion`) | 12.42.2 | Intentional transitions and shared-element polish | Use after layout and accessibility are stable: drawer/dialog transitions, card state changes, route-level fades, and small feedback. Put `MotionConfig reducedMotion="user"` at the app boundary and eliminate large transforms/parallax for reduced-motion users. | LOW |

### Artwork and Dense Content

| Technology | Version | Purpose | When to Use | Confidence |
|------------|---------|---------|-------------|------------|
| Native responsive images | Browser platform | Posters, backdrops, avatars | Build a WatchVault `Artwork` component using TMDB size variants, `srcset`, `sizes`, fixed `aspect-ratio`, `object-fit`, decode/error states, and `loading="lazy"` below the fold. Eager-load only the page's LCP hero. No image framework is needed. | MEDIUM |
| Native CSS overflow + scroll snap | Browser platform | Artwork rails | Default for horizontally scrolling media rails; it is smaller and easier to keep keyboard/scroll accessible than a JavaScript carousel. | MEDIUM |
| `embla-carousel-react` | 8.6.0 | Advanced controlled carousels | Optional only when a rail needs snap controls, selected-slide state, or programmatic paging that native scrolling cannot provide. WatchVault must still provide semantic region labels, visible buttons, and keyboard behavior. | LOW |
| `@tanstack/react-virtual` | 3.14.7 | Virtualized long history rows | Add only after profiling proves DOM size is a problem. Do not virtualize compact media rails or ordinary settings lists; virtualization complicates focus, measurement, screenshots, and browser find. | LOW |

### Frontend Data Boundary

| Technology | Version | Purpose | Migration rule | Confidence |
|------------|---------|---------|----------------|------------|
| `@tanstack/react-query` | 5.101.3 | Server-state loading, caching, retries, mutation invalidation | Add one `QueryClientProvider` and migrate route-by-route. Keep auth, profiles, permissions, theme, and toasts in the existing `AppProvider`. Query keys must include household/profile scope, locale where relevant, and endpoint parameters. | LOW |
| Zod | 4.4.3 | Runtime API-response validation and inferred types | Define schemas for redesigned high-value endpoints first: dashboard, search, title detail, and history. Parse at `api.ts` adapters and expose typed view models to components. Do not require an OpenAPI/backend rewrite. | LOW |
| Existing `api.ts` | Existing | Same-origin transport and `ApiError` | Keep as the only HTTP transport. TanStack query functions call typed adapters built on this client; components should not call `fetch` directly. | MEDIUM |

**Important PWA rule:** do not persist the TanStack Query cache in the first redesign release. Workbox already caches selected GETs, and persisting a second cache adds stale-data and household-data-remanence risks. Coordinate query `staleTime`, mutation invalidation, profile switches, logout clearing, and existing Workbox rules before considering persistence.

### Component Workshop and Regression Tooling

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Storybook + `@storybook/react-vite` | 10.5.3 | Isolated design-system development | Supports React 18 and Vite 8. Create stories for primitives and reusable patterns in dark/light, narrow/wide, loading, empty, error, long-text, and reduced-motion states. Do not require a story for every route page. | LOW |
| `@storybook/addon-a11y` | 10.5.3 | Fast component-level axe feedback | Catch obvious semantic, label, and contrast failures while building. Treat it as a first line, not WCAG certification. | LOW |
| Vitest | 4.1.10 | Frontend unit/component runner | Native fit with Vite 8 and Node 24. Use for pure formatting/view-model tests, hooks, and component behavior. | LOW |
| jsdom | 29.1.1 | DOM environment for Vitest | Use for component tests that do not require real layout or browser APIs. | LOW |
| React Testing Library / DOM Testing Library | 16.3.2 / 10.4.1 | User-facing component tests | Query by role/name and test observable behavior rather than component internals. | LOW |
| `@testing-library/user-event` | 14.6.1 | Realistic keyboard/pointer interactions | Use for focus order, menus, dialogs, forms, and keyboard operation. | LOW |
| `@testing-library/jest-dom` | 7.0.0 | Accessible DOM assertions | Use with Vitest setup for visibility, names, descriptions, and state assertions. | LOW |
| MSW | 2.15.0 | API fixtures at the network boundary | Reuse deterministic response fixtures across component tests and Storybook. Never copy real household data into fixtures. | LOW |
| Playwright Test | 1.61.1 | Critical E2E, responsive and visual regression | Cover login/session bootstrap, dashboard → search → title → history, theme switching, profile scope, and settings. Use Chromium on every PR; add WebKit/mobile projects for critical flows. | LOW |
| `@axe-core/playwright` | 4.12.1 | Automated route-level accessibility scans | Scan both themes and representative responsive states. Pair with manual keyboard, screen-reader smoke, zoom/reflow, and contrast review because automation finds only part of WCAG issues. | LOW |

### Static Quality Tooling

| Technology | Version | Purpose | Decision | Confidence |
|------------|---------|---------|----------|------------|
| ESLint | **9.39.5**, not 10 | TypeScript/React correctness | Use flat config. Pin major 9 because `eslint-plugin-jsx-a11y` 6.10.2 does not yet declare ESLint 10 compatibility. | LOW |
| `typescript-eslint` | 8.65.0 | Type-aware TypeScript rules | Enable type-aware rules selectively; avoid turning initial lint adoption into a whole-repository rewrite. | LOW |
| `eslint-plugin-react-hooks` | 7.1.1 | Hook correctness | Enforce hook rules for refactored components and query hooks. | LOW |
| `eslint-plugin-jsx-a11y` | 6.10.2 | Static accessibility checks | Enable recommended rules, then document narrow exceptions. It complements rather than replaces browser tests. | LOW |
| Prettier | 3.9.6 | Stable TSX/CSS formatting | Add one repository configuration matching existing double-quote/two-space conventions. Apply to touched frontend files first to avoid a noisy all-repository diff. | LOW |
| Stylelint + `stylelint-config-standard` | 17.14.1 / 40.0.0 | CSS correctness | Apply to redesigned CSS Modules and token files. Configure modern CSS features used by Vite; do not mass-reformat legacy CSS in the same PR. | LOW |

## Design-System Structure

Recommended frontend boundaries:

```text
frontend/src/
├── design-system/
│   ├── tokens/          # palette, semantic, typography, space, motion
│   ├── primitives/      # Button, IconButton, TextField, Dialog, Menu, Tabs
│   ├── patterns/        # MediaCard, Artwork, Rail, Hero, EmptyState, Skeleton
│   └── test/            # shared render helpers and fixture factories
├── features/            # optional extraction from oversized pages by domain
├── lib/
│   ├── api.ts           # retained transport
│   ├── contracts/       # Zod schemas and inferred API types
│   └── queries/         # query keys and endpoint hooks
├── pages/               # route composition; migrate one route at a time
└── styles/
    ├── tokens.css       # retained entry, expanded semantic tokens
    ├── base.css
    └── legacy.css       # existing app.css isolated during migration
```

Rules:

1. Pages consume WatchVault components, never raw Radix primitives.
2. New components use CSS Modules and semantic tokens; no raw color in component CSS.
3. Maintain dark, light, system, accent, reduced-motion, focus-visible, disabled, loading, empty, and error states as explicit component contracts.
4. Keep server data out of presentational components. Typed query hooks adapt API data to stable view models.
5. Preserve route URLs, permissions, profile scope, localization keys, and PWA behavior while presentation moves screen-by-screen.

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Styling | CSS tokens + CSS Modules | Tailwind CSS / shadcn | Introduces a second styling model and utility vocabulary across a large existing custom-CSS app; shadcn also brings Tailwind-oriented copied components. It increases migration diff without improving WatchVault's domain architecture. |
| Accessible primitives | Radix Primitives wrapped by WatchVault | MUI, Chakra, Ant Design, Mantine | Styled suites impose visual defaults, theming APIs, and component anatomy that fight a custom cinematic identity and encourage broad replacement. |
| Component styling | Static CSS | styled-components, Emotion, other runtime CSS-in-JS | Adds runtime/style-injection complexity and a parallel theme system when CSS variables already solve dual themes. |
| Server state | TanStack Query incrementally | Redux/Redux Toolkit for all state | WatchVault's durable state is server-owned and its small global client state already fits context. Redux would expand architecture rather than solve the redesign's primary risks. |
| API typing | Zod schemas at critical boundaries | Immediate OpenAPI generation or full client regeneration | The Flask API does not currently expose a complete OpenAPI contract. Requiring one first would couple visual work to broad backend refactoring. |
| Motion | Motion, centrally governed | GSAP for general UI | GSAP is powerful but excessive for standard app transitions and easier to misuse for inaccessible cinematic effects. Reserve it only if a later, measured interaction cannot be expressed with CSS or Motion. |
| Rails | Native scroll snap first | Carousel everywhere | JS carousels add focus, touch, sizing, and reduced-motion complexity. Most artwork rails need overflow, not a slideshow. |
| Visual regression | Playwright screenshots in pinned CI | Percy/Chromatic as a requirement | A self-contained Playwright baseline is reproducible without adding a mandatory third-party service. Storybook can still be published as a CI artifact. |
| Framework | React 18 during redesign | React 19 now | React's upgrade is feasible, but combining major runtime and type changes with every-screen replacement reduces fault isolation. |
| Router/charts | Existing Router 6 and Recharts 2 | Router 7 / Recharts 3 | These migrations do not create cinematic quality and add unrelated behavior/API changes. |

## Installation

Install in a foundational frontend-tooling change and commit the resulting lockfile. Add Radix packages only when their wrapped WatchVault primitive is implemented.

```bash
cd frontend

# Runtime design-system and data-boundary dependencies
npm install \
  @radix-ui/react-dialog@1.1.20 \
  @radix-ui/react-dropdown-menu@2.1.21 \
  @radix-ui/react-tooltip@1.2.13 \
  @radix-ui/react-tabs@1.1.18 \
  @radix-ui/react-slot@1.3.0 \
  @tanstack/react-query@5.101.3 \
  zod@4.4.3 \
  motion@12.42.2 \
  lucide-react@1.25.0 \
  class-variance-authority@0.7.1 \
  clsx@2.1.1 \
  @fontsource-variable/manrope@5.3.0

# Component workshop and frontend tests
npm install -D \
  storybook@10.5.3 \
  @storybook/react-vite@10.5.3 \
  @storybook/addon-a11y@10.5.3 \
  vitest@4.1.10 \
  @vitest/coverage-v8@4.1.10 \
  jsdom@29.1.1 \
  @testing-library/react@16.3.2 \
  @testing-library/dom@10.4.1 \
  @testing-library/user-event@14.6.1 \
  @testing-library/jest-dom@7.0.0 \
  msw@2.15.0 \
  @playwright/test@1.61.1 \
  @axe-core/playwright@4.12.1

# Static quality gates
npm install -D \
  eslint@9.39.5 \
  typescript-eslint@8.65.0 \
  eslint-plugin-react-hooks@7.1.1 \
  eslint-plugin-jsx-a11y@6.10.2 \
  prettier@3.9.6 \
  stylelint@17.14.1 \
  stylelint-config-standard@40.0.0

# Optional, only after a documented component need or performance measurement
npm install embla-carousel-react@8.6.0 @tanstack/react-virtual@3.14.7
```

Recommended scripts:

```json
{
  "scripts": {
    "build": "tsc -b && vite build",
    "lint": "eslint . && stylelint \"src/**/*.css\"",
    "format:check": "prettier --check .",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:e2e": "playwright test",
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build"
  }
}
```

## Adoption Order

1. **Toolchain safety:** move the frontend build/test image to Node 24 LTS; add lint, formatting, Vitest, Playwright, and CI gates.
2. **Design-system contract:** expand semantic tokens; establish CSS layers, typography, icons, focus, motion policy, and Storybook.
3. **Primitive layer:** wrap Radix only for complex behaviors; add buttons, fields, feedback, skeletons, artwork, cards, and rails with tests.
4. **Typed server state:** introduce QueryClient and Zod for dashboard/search/title/history; leave unaffected pages on `useFetch` until migrated.
5. **Reference journey:** migrate shell, dashboard, search, title detail, and history with desktop/mobile, dark/light, keyboard, axe, and screenshot coverage.
6. **Remaining screens:** migrate feature-by-feature; remove legacy CSS and `useFetch` usage only when no consumers remain.

## What Not to Add

- No backend framework, database, deployment-topology, or authentication replacement.
- No React 19, React Router 7, Recharts 3, package-manager switch, or broad dependency modernization inside redesign phases.
- No Tailwind, shadcn, MUI/Chakra/Ant/Mantine, runtime CSS-in-JS, or a second theme provider.
- No Redux/Zustand for server state; no persisted TanStack Query cache initially.
- No blanket carousel or virtualization abstraction.
- No per-poster color extraction, autoplay video hero, heavy parallax, or blurhash pipeline in the first release; these increase image/CORS, performance, motion, and backend complexity before core UX is proven.
- No claim of accessibility based only on Radix, lint, Storybook, or axe. Manual keyboard, zoom/reflow, contrast, and screen-reader smoke checks remain release criteria.

## Sources

Version checks were performed against the npm registry on 2026-07-21. Capability and compatibility claims were checked against:

- [React 19 Upgrade Guide](https://react.dev/blog/2024/04/25/react-19-upgrade-guide) — official; source confidence LOW
- [Node.js release schedule](https://nodejs.org/en/about/previous-releases) — official; source confidence LOW
- [Vite CSS features](https://vite.dev/guide/features.html#css-modules) — official; source confidence LOW
- [Radix accessibility](https://www.radix-ui.com/primitives/docs/overview/accessibility) and [styling](https://www.radix-ui.com/primitives/docs/guides/styling) — official; source confidence LOW
- [Motion accessibility guidance](https://motion.dev/docs/react-accessibility) — official; source confidence LOW
- [TanStack Query React quick start](https://tanstack.com/query/latest/docs/framework/react/quick-start) — official; source confidence LOW
- [Zod 4 documentation](https://zod.dev/) — official; source confidence LOW
- [Vitest guide](https://vitest.dev/guide/) — official; source confidence LOW
- [React Testing Library introduction](https://testing-library.com/docs/react-testing-library/intro/) — official; source confidence LOW
- [Storybook React/Vite](https://storybook.js.org/docs/get-started/frameworks/react-vite) and [accessibility testing](https://storybook.js.org/docs/writing-tests/accessibility-testing) — official; source confidence LOW
- [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots), [device emulation](https://playwright.dev/docs/emulation), and [accessibility testing](https://playwright.dev/docs/accessibility-testing) — official; source confidence LOW
- Existing WatchVault `frontend/package.json`, lockfile-derived stack map, architecture map, conventions, testing analysis, and CSS token file — direct repository evidence

## Research Gaps

- Embla's expected official documentation URLs returned 404 during this run; its version and React peer compatibility were verified from npm, but its use remains deliberately optional.
- No live web-search provider was configured (`BRAVE_API_KEY` absent), so ecosystem popularity claims were not used.
- Bundle-size and runtime-performance effects must be measured against WatchVault's actual production build; no package should be justified by generic benchmarks alone.
