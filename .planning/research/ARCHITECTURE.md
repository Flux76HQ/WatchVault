# Architecture Patterns

**Project:** WatchVault full-app UI redesign  
**Domain:** Migration-safe redesign of an existing React/Flask media-tracking PWA  
**Researched:** 2026-07-21  
**Overall confidence:** MEDIUM  
**Scope basis:** `.planning/STATE.md` is absent; the active redesign requirements in `.planning/PROJECT.md` define this work.

## Recommended Architecture

Retain the existing modular monolith and same-origin React PWA/Flask API boundary. Modernize the frontend through stable seams rather than a parallel rewrite:

```text
Browser / installable PWA
┌──────────────────────────────────────────────────────────────────────┐
│ App composition                                                     │
│ ErrorBoundary → AppProvider → QueryClient → Router                  │
├──────────────────────────────────────────────────────────────────────┤
│ App shell                                                           │
│ skip link + landmarks + desktop/mobile nav + route status + Outlet  │
├──────────────────────────────────────────────────────────────────────┤
│ Thin route pages                                                    │
│ compose feature screens; own URL params; no raw fetch or styling    │
├──────────────────────────────────────────────────────────────────────┤
│ Feature modules                                                     │
│ dashboard | search | titles | history | imports | profiles | prefs  │
│ screen + feature components + hooks + endpoint contracts            │
├──────────────────────────────────────────────────────────────────────┤
│ Shared UI                                                           │
│ domain components → interaction patterns → visual primitives        │
├──────────────────────────────────────────────────────────────────────┤
│ Foundations                                                         │
│ semantic tokens + themes + typography + motion + responsive rules   │
├──────────────────────────────────────────────────────────────────────┤
│ Typed remote-state boundary                                         │
│ endpoint schemas → API client → TanStack Query key/hook adapters     │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ same-origin /api, cookie credentials
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Existing Flask modular monolith                                     │
│ blueprints → domain services → PostgreSQL                            │
│ Only reshape existing responses when a redesigned screen needs it.  │
└──────────────────────────────────────────────────────────────────────┘
```

**Architectural stance:** this is a strangler-style frontend migration inside one application. Preserve route URLs, authentication, permissions, profile scope, preferences, API behavior, PWA installation, and backend modules. Replace the shell, shared abstractions, and feature screens incrementally behind those contracts.

**Confidence: HIGH** for current-state boundaries, based on direct repository inspection. **Confidence: MEDIUM** for the target decomposition, based on those boundaries and established React migration patterns.

## Architectural Principles

1. **Preserve behavior before changing presentation.** Every route gets a capability checklist and regression coverage before its visual replacement.
2. **Build from foundations upward.** Tokens and interaction primitives must precede page redesigns; otherwise each page creates a competing mini-design-system.
3. **Migrate vertical workflows, not isolated screenshots.** Dashboard → search → title detail → watch history is the first complete slice.
4. **One owner per kind of state.** Context owns session-wide client state, TanStack Query owns remote state, the URL owns navigable state, and components own ephemeral interaction state.
5. **Decode data once.** Network JSON is `unknown` until an endpoint contract validates it; pages never cast API payloads.
6. **Accessibility is primitive behavior.** Focus, keyboard, semantics, reduced motion, and live announcements are centralized below feature pages.
7. **Responsive components are intrinsic.** The shell responds to viewport width; reusable components respond to their container and content.
8. **Legacy and redesigned UI may coexist only through explicit seams.** Use compatibility wrappers and CSS layers, not duplicated global selectors.

## Target Frontend Structure

Introduce the structure incrementally; do not move all files before behavior is covered.

```text
frontend/src/
├── app/
│   ├── AppProviders.tsx          # AppProvider, QueryClient, i18n composition
│   ├── AppRouter.tsx             # stable URLs and route-level lazy boundaries
│   ├── AppShell.tsx              # landmarks, navigation, Outlet
│   ├── navigation.ts             # one typed desktop/mobile navigation model
│   └── RouteAnnouncer.tsx
├── design-system/
│   ├── tokens/                   # palette inputs and semantic theme tokens
│   ├── primitives/               # Button, TextField, Surface, Text, IconButton
│   ├── patterns/                 # Dialog, Menu, Tabs, Toast, Combobox
│   └── index.ts                  # intentionally small public API
├── shared/
│   ├── media/                    # PosterCard, Artwork, MediaRail, Progress
│   ├── feedback/                 # PageState, EmptyState, ErrorState, Skeleton
│   └── layout/                   # PageFrame, Cluster, Stack, ResponsiveGrid
├── features/
│   ├── dashboard/
│   ├── search/
│   ├── titles/
│   ├── history/
│   ├── imports/
│   ├── profiles/
│   └── settings/
│       ├── api.ts                # endpoint definitions for this feature
│       ├── hooks.ts              # query/mutation hooks
│       ├── model.ts              # pure view-model transformations
│       ├── components/
│       └── screens/
├── services/
│   └── api/
│       ├── client.ts             # credentials, errors, abort, unknown JSON
│       ├── endpoint.ts           # typed endpoint descriptor
│       ├── schemas.ts            # shared IDs, paging, error envelopes
│       └── queryKeys.ts
├── pages/                        # thin route adapters during migration
├── lib/                          # retained utilities; shrink over time
└── legacy/                       # temporary adapters/styles only, then delete
```

Do not make `design-system/index.ts` a dump of feature-specific components. A component belongs in the design system only when its API is domain-neutral and it has behavior tests across themes, keyboard use, and responsive states.

## Component Boundaries

| Component | Responsibility | May Depend On | Must Not Depend On |
|---|---|---|---|
| `AppProviders` | Compose app-wide providers and teardown behavior | app context, query client, i18n | feature screens |
| `AppRouter` | Preserve URLs, route lazy loading, route error boundaries | thin pages, shell | endpoint implementation details |
| `AppShell` | Landmarks, skip link, navigation variants, safe areas, route outlet | navigation model, design-system patterns | page-specific permissions or API calls |
| Route page | Read route/search params, set document metadata, compose one screen | feature screen | raw `api`, global CSS selectors |
| Feature screen | Orchestrate feature states and compose feature components | feature hooks, shared UI | unrelated feature internals |
| Feature hook | Own query key, endpoint call, mutation invalidation, view-model mapping | API service, query layer | DOM or visual tokens |
| Endpoint contract | Define request/query schema, response schema, result type | shared API schemas | React |
| API client | Send request, normalize errors, parse JSON as `unknown`, validate response | endpoint contract | feature/UI behavior |
| Design primitive | Provide one visual/semantic unit and interaction states | tokens, accessible behavior | media-domain data |
| Interaction pattern | Implement focus, dismissal, keyboard model, portals, announcements | primitives | route state or feature fetches |
| Domain component | Present reusable media concepts | primitives/patterns, typed props | endpoint calls |
| Feature component | Present one workflow-specific unit | domain/shared UI, feature model | global context except through explicit props/hooks |
| Flask serializer/route | Scope, authorize, shape existing domain data | existing domain modules | frontend layout concerns |

### Dependency Direction

```text
app/pages
    ↓
features
    ↓
shared domain UI
    ↓
design-system patterns
    ↓
design-system primitives
    ↓
tokens

features → services/api
services/api → no React/UI dependencies
```

Cross-feature imports are prohibited. Shared behavior must be promoted deliberately to `shared/` or the design system.

## Design-System Layers

### Layer 1: Foundations and Semantic Tokens

Expand the existing `tokens.css` rather than replacing it with page-local variables.

Token groups:

- **Color roles:** canvas, surface levels, text roles, borders, overlay, focus, accent, success, warning, danger.
- **Artwork treatment:** scrim gradients, image saturation, fallback backgrounds, backdrop blur, poster aspect ratio.
- **Typography:** display, title, body, label, caption, numeric/stat styles with responsive `clamp()`.
- **Layout:** spacing scale, content widths, gutters, safe-area insets, density.
- **Shape/elevation:** radii, borders, shadow/overlay levels.
- **Motion:** duration, easing, distance, stagger, and a zero/reduced-motion mapping.
- **Interaction:** minimum target size, focus-ring width/offset, disabled opacity.

Use two stages:

```css
@layer reset, tokens, base, primitives, patterns, features, legacy;

:root {
  --color-neutral-950: #090a0d;        /* foundation input */
  --color-canvas: var(--color-neutral-950); /* semantic role */
  --color-text-primary: #f7f8fa;
  --motion-duration-enter: 180ms;
}

@media (prefers-reduced-motion: reduce) {
  :root {
    --motion-duration-enter: 1ms;
    --motion-distance: 0px;
  }
}
```

Theme overrides may redefine semantic roles, never component selectors. Validate dark, light, and system modes as separate supported themes. The saved preference continues to set `data-theme`; `color-scheme` must match so native controls and browser chrome render coherently.

### Layer 2: Visual and Layout Primitives

Build and test:

- `Button`, `IconButton`, `LinkButton`
- `TextField`, `SelectField`, `Checkbox`, `Switch`
- `Text`, `Heading`, `Badge`
- `Surface`, `Divider`
- `Stack`, `Cluster`, `PageFrame`, `ResponsiveGrid`
- `Skeleton`, `Spinner`, `VisuallyHidden`, `FocusRing`
- `Artwork`, `Avatar`, `Icon`

These own variants and states. Feature code must not recreate hover, focus, disabled, loading, destructive, or selected styling.

### Layer 3: Accessible Interaction Patterns

Centralize behaviors that are currently hand-built in modules such as `Menu.tsx`:

- `Dialog` and `AlertDialog`
- `Menu` and `Popover`
- `Tabs` and segmented controls
- `Combobox`/search suggestions
- `ToastRegion` and inline status
- `Disclosure`, action sheet, and tooltip

Each pattern owns its correct role, label relationships, keyboard model, initial focus, focus containment where required, Escape behavior, outside-click behavior, and focus restoration. Feature pages supply content and actions only.

The current `Dropdown` uses `role="listbox"` around arbitrary button children and does not manage arrow-key navigation or return focus. Do not copy it into the redesign; replace it behind the existing call sites with the centralized pattern.

### Layer 4: Shared Media Components

Build domain-aware but workflow-neutral components:

- `PosterCard`
- `MediaRail`
- `ArtworkHero`
- `MetadataList`
- `ProgressIndicator`
- `WatchStatus`
- `ProfileAvatar`
- `ProviderBadge`
- `HistoryEventRow`

Separate presentation from actions. The current `Poster` mixes image rendering, enrichment, permissions, deletion, editing, long-press, navigation, global events, and toast behavior. Replace it with:

```text
PosterCard (pure presentation and link)
└── MediaActionMenu (accessible interaction)
    └── useMediaActions (permissions + mutations + invalidation)
```

### Layer 5: Feature Composites and Screens

Feature composites combine domain components into a workflow: dashboard rails, search results, title hero, episode browser, history timeline, import wizard, and settings sections. They consume feature view models rather than raw API payloads.

### Layer 6: Route Templates

Route pages become small adapters. They own:

- route and search parameters;
- canonical URL and document title;
- route-level loading/error boundary;
- focus/announcement behavior on navigation;
- one feature screen.

They do not own endpoint details, reusable widgets, or large blocks of CSS.

## Typed API Boundary

The current `handle(): Promise<any>`, `Record<string, any>`, broad page `any` values, and unvalidated `res.json()` make a redesign unsafe. Replace them before migrating data-heavy screens.

### Contract Shape

```typescript
import type { ZodType } from "zod";

export interface Endpoint<Q, B, R> {
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  path: (input: { params?: Record<string, string> }) => string;
  response: ZodType<R>;
}

export async function request<Q, B, R>(
  endpoint: Endpoint<Q, B, R>,
  input: { query?: Q; body?: B; signal?: AbortSignal },
): Promise<R> {
  const response = await fetch(/* same-origin request */, {
    credentials: "include",
    signal: input.signal,
  });
  const payload: unknown = await readPayload(response);
  if (!response.ok) throw decodeApiError(response.status, payload);
  return endpoint.response.parse(payload);
}
```

### Boundary Rules

1. JSON enters as `unknown`, never `any`.
2. Zod schemas are the source for frontend response types; infer types from schemas.
3. Define endpoint contracts by feature, not one giant generated interface file.
4. Validate every endpoint migrated into the redesigned UI. Start with auth status, profiles/preferences, dashboard, search, title detail, and history mutations.
5. Normalize error envelopes centrally and preserve HTTP status.
6. Support `AbortSignal` so route/filter changes cannot commit stale responses.
7. Keep IDs opaque strings in TypeScript even where the database uses UUID/integer IDs.
8. Keep Flask response changes additive until all consumers migrate.
9. Add backend tests for response shape and permissions whenever a response is reshaped.
10. Do not expose database rows directly merely to satisfy a component.

Do not make OpenAPI generation a prerequisite for the redesign. The Flask API is broad and not currently schema-first; forcing a backend-wide contract migration would couple the UI milestone to unrelated refactoring. Explicit frontend contracts plus focused Flask response tests provide a safer incremental seam. Revisit generated cross-language contracts after endpoint serializers are consistently explicit.

## State and Data Flow

### State Ownership

| State | Owner | Examples | Persistence |
|---|---|---|---|
| Session-wide client state | `AppProvider` | current user, permissions, profiles, active scope, preferences, theme | server preference/session |
| Remote server state | TanStack Query | dashboard stats, search results, title detail, history, connections | PostgreSQL/API |
| Navigable UI state | URL | search term, filters, selected tab, date range, edit intent | browser history/deep link |
| Ephemeral interaction state | nearest component/pattern | dialog open, menu open, draft input, pressed state | none |
| Form state | owning feature form | dirty fields, validation, submit state | API on submit |
| PWA asset cache | service worker | shell/static assets and public artwork | Cache Storage |

Do not put API result collections into `AppProvider`. Do not use context as a second server-state cache.

### Query-Key Architecture

Use key factories and include every value that changes the server result:

```typescript
const keys = {
  dashboard: (scope: ProfileScope, range: Range) =>
    ["dashboard", { scope, range }] as const,
  search: (scope: ProfileScope, query: SearchQuery) =>
    ["search", { scope, ...query }] as const,
  title: (scope: ProfileScope, id: TitleId, language: string) =>
    ["title", { scope, id, language }] as const,
};
```

Feature hooks hide query-library details from screens:

```text
URL/profile scope
      ↓
useTitleScreen(id, scope)
      ↓
typed endpoint contract → API client → Flask
      ↓                         ↓
validated data          normalized ApiError
      ↓
view-model transform
      ↓
TitleScreen → shared/domain/design-system components
```

Mutations invalidate precise key families rather than dispatching global browser events. Replace `watchvault:title-deleted` and `watchvault:title-updated` with mutation hooks that invalidate title, search, dashboard, and history keys as required.

On logout or authenticated-user change:

1. clear the in-memory query cache;
2. clear any personalized Cache Storage entries;
3. reset profile scope;
4. navigate to the login gate.

The existing service worker caches personalized `/api/stats` and `/api/search` responses across logout. Remove authenticated API runtime caching during the redesign. Keep only static shell and public artwork caching unless cache partitioning and purge behavior are implemented and tested.

## Responsive Architecture

### Shell

- Render desktop and mobile navigation from one typed `navigation.ts` model so labels, permissions, routes, and active matching cannot drift.
- Use one `AppShell` route with `Outlet`; preserve all current URLs.
- Use viewport queries for shell mode only: desktop navigation, compact tablet mode, and mobile bottom navigation.
- Include `env(safe-area-inset-*)` in fixed/sticky mobile navigation and modal sheets.
- Keep the main landmark stable; do not key the entire `<main>` by pathname because it destroys local state and can create avoidable focus/animation churn.

### Components

- Use mobile-first layout and intrinsic sizing.
- Use container queries for cards, rails, metadata panels, and settings sections embedded at different widths.
- Prefer `minmax()`, `auto-fit`, `clamp()`, aspect ratios, and content wrapping over JavaScript viewport checks.
- Define density variants only where information hierarchy truly differs; do not maintain separate desktop/mobile component trees for the same content.
- Keep touch targets at least 44×44 CSS pixels as a product standard, while maintaining visible keyboard focus.
- Test long translated labels, 200% zoom, narrow widths, landscape PWA mode, and missing artwork.

## Accessibility Architecture

Accessibility requirements are enforced at four layers:

### 1. Foundations

- Semantic color pairs are contrast-tested in both themes.
- Focus tokens are visible on every surface and artwork backdrop.
- Motion tokens collapse under `prefers-reduced-motion`.
- Typography supports zoom and reflow; avoid fixed-height text containers.

### 2. Primitives and Patterns

- Native elements are preferred where they express the behavior.
- Icon-only controls require accessible names.
- Dialogs, menus, tabs, comboboxes, and action sheets use centralized keyboard/focus behavior.
- Destructive actions use an alert dialog with explicit action naming.
- Disabled/loading states remain perceivable and do not silently trap focus.

### 3. Shell and Navigation

- Provide a first-focus skip link to the main content.
- Use `header`, `nav`, `main`, and complementary landmarks with unique labels.
- Mark active navigation semantically.
- Update the document title and announce route changes without forcing focus into arbitrary content.
- Restore logical focus after closing overlays and after destructive mutations.

### 4. Feature Screens

- One meaningful `h1` per route and a logical heading hierarchy.
- Loading, success, and error updates use appropriately scoped live regions.
- Charts have textual summaries and do not encode meaning by color alone.
- Poster/artwork alt text follows purpose: informative artwork gets the title; decorative backdrops use empty alt text.
- Reorderable dashboard controls provide keyboard operations and announce position changes.

Automated accessibility tests are a gate, not proof of conformance. Add manual keyboard, zoom/reflow, screen-reader smoke, reduced-motion, and dark/light contrast checks to release acceptance.

## Regression Architecture

### Test Layers

| Layer | Tooling/Location | Protects | Run |
|---|---|---|---|
| Pure unit | Vitest | token helpers, formatters, view-model transforms, query keys | every PR |
| Contract/schema | Vitest + Zod fixtures | endpoint response decoding and nullability | every PR |
| Component interaction | React Testing Library + user-event | primitives, patterns, feature workflows | every PR |
| Automated accessibility | axe integration in component tests | common semantic and ARIA regressions | every PR |
| API behavior | existing pytest suite plus focused response tests | authorization, scoping, response shape | every PR |
| End-to-end | Playwright | login, navigation, dashboard → search → title → history, settings/import critical paths | every PR/scheduled subset |
| Visual | Playwright screenshots | both themes at representative desktop/mobile viewports | changed surfaces and release |
| Manual acceptance | keyboard/screen reader/zoom/PWA install | issues automation cannot establish | phase and release gates |

Tests should select elements by role, accessible name, label, and user-visible text. Avoid CSS-class and component-instance selectors; they make visual refactoring unnecessarily expensive.

### Migration Test Contract

Each route receives:

1. a capability inventory covering reads, writes, permissions, loading, empty, error, and destructive states;
2. characterization tests for current behavior;
3. redesigned component tests;
4. one route-level smoke test in both themes and key viewports;
5. parity sign-off before legacy code is deleted.

## Migration Sequencing

### Phase 1: Safety Rails and Contract Inventory

**Build first because every later phase depends on it.**

- Inventory routes, user actions, permissions, profile scope, preferences, translations, and API calls.
- Add Vitest, React Testing Library, axe integration, and Playwright.
- Capture reference-flow tests and representative visual baselines.
- Fix or quarantine known blockers that make parity tests unreliable.

### Phase 2: Typed Boundary and Remote-State Spine

- Replace the raw `any` API client with endpoint descriptors and `unknown` decoding.
- Add TanStack Query at the app composition root.
- Migrate auth/profile/preferences bootstrap first.
- Add key factories, logout cache clearing, abort behavior, and mutation invalidation.
- Remove authenticated service-worker API caching.

This phase precedes visual page work because otherwise redesigned components will cement weak payload assumptions.

### Phase 3: Design Foundations and Accessible Primitives

- Define semantic dark/light tokens, typography, spacing, artwork, motion, focus, and responsive rules.
- Build primitive and interaction test harnesses.
- Replace toast, menu, dialog, segmented control, loading, empty, and error patterns.
- Keep compatibility class names only where necessary to let legacy pages use new primitives.

### Phase 4: Application Shell and Navigation

- Introduce `AppProviders`, `AppRouter`, and `AppShell`.
- Preserve all route URLs and the authenticated gate.
- Add one navigation model, desktop/mobile rendering, skip link, route title/announcement, safe areas, and shell responsiveness.
- Ensure old route pages still render inside the new shell before redesigning them.

### Phase 5: Reference Journey Vertical Slice

Migrate in dependency order:

```text
Poster/Artwork + PageState + MediaRail
        ↓
Dashboard
        ↓
Search and filters
        ↓
Title detail and media actions
        ↓
Watch-history add/edit/delete
```

This slice exercises artwork, responsive layout, profile scope, navigation, typed reads, mutations, permissions, dialogs, feedback, and cache invalidation. It validates the architecture before broad rollout.

### Phase 6: Catalog and Analytics Surfaces

- Overviews/statistics
- Person detail
- Genre title grids
- Shared charts with textual summaries

These reuse the media and filtering components established by the reference slice.

### Phase 7: Operational and Administrative Workflows

- Imports and provider connections
- Profiles and household controls
- Settings, appearance, plugins, tokens, and destructive data management
- Authentication and recovery surfaces where included in the redesign

These are sequenced later because they are large, permission-heavy modules with high regression cost. They still reuse the established forms, dialogs, feedback, and responsive section patterns.

### Phase 8: Legacy Removal and Release Audit

- Remove legacy styles, adapters, browser custom events, and dead components.
- Enforce dependency boundaries and ban direct `api` imports from pages/components.
- Run route capability parity, both-theme contrast, keyboard, responsive, PWA, and full regression audits.
- Update screenshots and operational documentation only after UI behavior is stable.

## Build-Order Dependencies

```text
Capability inventory + test harness
               ↓
typed API client + endpoint schemas
               ↓
query/provider composition + cache policy
               ↓
semantic tokens
               ↓
primitives → interaction patterns
               ↓
AppShell/navigation
               ↓
shared media components
               ↓
reference journey
               ↓
secondary catalog/analytics
               ↓
imports/profiles/settings/auth
               ↓
legacy removal + release audit
```

| Deliverable | Depends On | Blocks |
|---|---|---|
| Visual page redesign | tokens, primitives, characterization tests | route migration |
| New shell | navigation model, focus primitives, route tests | all route acceptance |
| Title detail | typed title contract, artwork/domain components | history mutation workflow |
| History mutations | dialog/form patterns, query invalidation | reference-journey completion |
| Settings redesign | form primitives, permission patterns | legacy cleanup |
| Visual regression | deterministic fixtures and stable shell | release audit |
| Legacy CSS deletion | all route parity checks | final release |

## Patterns to Follow

### Pattern 1: Branch by Component Boundary

**What:** Introduce a stable wrapper API, route old call sites through it, replace the implementation, then remove compatibility props.

**When:** Replacing `Poster`, dropdowns, page states, charts, or shell elements used by multiple routes.

**Example:**

```typescript
// Compatibility adapter while callers migrate.
export function LegacyPoster(props: LegacyPosterProps) {
  const model = toPosterCardModel(props);
  return (
    <PosterCard
      media={model}
      actions={<MediaActionMenu media={model} />}
    />
  );
}
```

### Pattern 2: Screen Hook + Pure View

**What:** A feature hook orchestrates typed remote state and mutations; the screen renders a discriminated view state.

```typescript
type ScreenState<T> =
  | { status: "loading" }
  | { status: "error"; error: ApiError; retry: () => void }
  | { status: "empty" }
  | { status: "ready"; data: T };
```

**Why:** Loading, error, empty, and ready states become exhaustive and testable instead of ad hoc branches inside 500–750 line pages.

### Pattern 3: Additive API Reshaping

**What:** Add fields or a purpose-built view endpoint while preserving existing response fields until migrated consumers are gone.

**When:** The redesigned title hero, history timeline, or dashboard needs data currently assembled through several requests.

**Rule:** Backend response shaping may support an existing capability; it must not introduce a new recommendation/social domain.

### Pattern 4: CSS Layer Isolation

**What:** Put new tokens, primitives, patterns, and features in explicit cascade layers; keep old global CSS in `legacy`.

**Why:** The current global `app.css` and class names can coexist during migration without specificity escalation or accidental restyling.

### Pattern 5: One Navigation Model, Multiple Presentations

**What:** A typed route metadata array supplies label key, icon, permission, active matching, and placement; desktop and mobile components render it differently.

**Why:** Responsive presentation changes without duplicating information architecture.

## Anti-Patterns to Avoid

### Big-Bang Parallel Frontend

**What:** Build a second app tree and switch when every screen is “finished.”  
**Why bad:** Behavior drift remains hidden until integration; permissions, profile scope, PWA behavior, and secondary workflows are rediscovered late.  
**Instead:** Replace route and component seams incrementally in the production tree.

### Screenshot-Driven Components

**What:** Create page-specific markup and pixel values to match one viewport.  
**Why bad:** Produces duplicate cards, inconsistent states, poor translation/zoom behavior, and fragile mobile layouts.  
**Instead:** Build tokenized primitives and intrinsic shared components first.

### Fetching in Presentation Components

**What:** `PosterCard`, `ArtworkHero`, or buttons call `api` directly.  
**Why bad:** Recreates the current `Poster` coupling and prevents deterministic tests.  
**Instead:** Pass typed models/actions from feature hooks.

### Global Context as a Data Cache

**What:** Add dashboard, search, title, and history payloads to `AppProvider`.  
**Why bad:** Broad rerenders, unclear invalidation, stale cross-scope data, and difficult logout cleanup.  
**Instead:** Keep context small and use scoped query keys.

### Type Assertions at Call Sites

**What:** Cast `await api.get(...) as TitleDetail`.  
**Why bad:** Silences TypeScript without validating Flask output.  
**Instead:** Parse `unknown` at the endpoint contract.

### Desktop and Mobile Forks

**What:** Maintain separate screen component trees per viewport.  
**Why bad:** Capability and accessibility drift.  
**Instead:** Share content/components and vary shell/layout composition.

### Accessibility Added After Styling

**What:** Audit keyboard and semantics after every screen is visually complete.  
**Why bad:** Focus models and DOM order become expensive to correct.  
**Instead:** Make accessible primitives a prerequisite for feature migration.

### Persistent Authenticated Runtime Caches

**What:** Continue service-worker caching of profile-specific API responses without identity partitioning.  
**Why bad:** Previous-session data can appear after logout or account change.  
**Instead:** Network-only authenticated API data during this milestone; clear all client caches on identity transitions.

## Scalability Considerations

| Concern | Small household | Large personal library | Future larger deployment |
|---|---|---|---|
| Frontend bundles | Route-level lazy loading optional | Lazy-load charts/admin routes | Measure per-route budgets and split heavy features |
| Search results | Normal pagination | Virtualize only proven long result sets | Cursor pagination/API indexing is backend work |
| Artwork | Lazy images and stable aspect boxes | Public artwork cache with bounded entries | CDN/image proxy only if deployment needs it |
| Query cache | Short session memory | Scope/filter-aware keys and bounded retention | Persist only after privacy-safe partitioning |
| Dashboard | Shared components | Avoid refetch storms through dedupe | Backend aggregate work remains authoritative |
| Responsive rendering | CSS layout | Container queries avoid JS resize churn | Same component model scales across embeddings |
| Design-system growth | Curated public API | Promote only proven shared patterns | Add ownership/deprecation policy |

The redesign should not pre-emptively virtualize every list, normalize all server entities in the browser, or split the modular monolith. Measure first and keep the migration focused.

## Phase-Specific Architecture Risks

| Phase Topic | Risk | Mitigation |
|---|---|---|
| Test foundation | Brittle snapshots freeze legacy markup | Test roles, outcomes, and user flows |
| API typing | Manual schemas drift from Flask | Runtime parsing plus focused Flask response tests |
| Tokens/themes | User accent breaks contrast | Constrain derived foregrounds and test representative accents |
| Shell | Mobile/desktop nav diverges | One navigation model and shared route metadata |
| Reference journey | Mutations leave stale dashboards/search | Central key factories and explicit invalidation matrix |
| Settings/imports | Large pages are split by visual sections only | Split by workflow and permission boundary |
| PWA | Cached authenticated data survives logout | Remove API runtime caching and test identity teardown |
| Cleanup | Legacy CSS removal causes hidden regressions | Route parity matrix and visual baselines before deletion |

## Sources

### Direct Repository Evidence

- `.planning/PROJECT.md` — active milestone requirements and constraints. **Confidence: HIGH**
- `.planning/codebase/ARCHITECTURE.md` — current modular-monolith, frontend, API, and PWA boundaries. **Confidence: HIGH**
- `.planning/codebase/STRUCTURE.md` — current module locations and absence of frontend tests. **Confidence: HIGH**
- `.planning/codebase/CONCERNS.md` — large pages, weak API typing, service-worker cache privacy, and test gaps. **Confidence: HIGH**
- `frontend/src/App.tsx`, `components/Layout.tsx`, `lib/app.tsx`, `lib/api.ts`, `lib/useFetch.ts`, `components/ui.tsx`, `components/Menu.tsx`, `styles/tokens.css`, `vite.config.ts`. **Confidence: HIGH**

### External References

The research seam classified direct web fetches as LOW even when the fetched page was an official source; these references support, but do not independently determine, the recommendation.

- React, “Thinking in React” and “Reusing Logic with Custom Hooks”:  
  https://react.dev/learn/thinking-in-react  
  https://react.dev/learn/reusing-logic-with-custom-hooks  
  **Seam confidence: LOW**
- React Router 6.30.1, `Outlet` and routing concepts:  
  https://reactrouter.com/6.30.1/components/outlet  
  https://reactrouter.com/6.30.1/start/concepts  
  **Seam confidence: LOW**
- TypeScript narrowing and Zod 4 runtime validation:  
  https://www.typescriptlang.org/docs/handbook/2/narrowing.html#the-unknown-type  
  https://zod.dev/  
  **Seam confidence: LOW**
- TanStack Query v5 server state, query keys, and invalidation:  
  https://tanstack.com/query/latest/docs/framework/react/overview  
  https://tanstack.com/query/latest/docs/framework/react/guides/query-keys  
  https://tanstack.com/query/latest/docs/framework/react/guides/query-invalidation  
  **Seam confidence: LOW**
- W3C WCAG 2.2 understanding documents for contrast, focus visibility, and keyboard operation:  
  https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html  
  https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html  
  https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html  
  **Seam confidence: LOW**
- MDN, reduced motion and color scheme:  
  https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion  
  https://developer.mozilla.org/en-US/docs/Web/CSS/color-scheme  
  **Seam confidence: LOW**
- Vitest, Testing Library, and Playwright testing guidance:  
  https://vitest.dev/guide/  
  https://testing-library.com/docs/guiding-principles  
  https://playwright.dev/docs/best-practices  
  **Seam confidence: LOW**
- Martin Fowler, incremental replacement and branching patterns:  
  https://martinfowler.com/bliki/StranglerFigApplication.html  
  https://martinfowler.com/articles/branching-patterns.html#BranchByAbstraction  
  **Seam confidence: LOW**

## Research Gaps

- The exact accessible headless-component package should be finalized by stack research; the architectural requirement is a locally wrapped primitive layer, not direct package use in feature screens.
- Representative production-sized data and target browser/device support were not provided; performance budgets and visual-regression viewport matrices need phase-specific validation.
- A complete route/action capability inventory must be generated from the running application before route migration begins.
- The backend has no schema-first API description. Generated OpenAPI contracts should remain deferred unless a focused spike proves they can be introduced without broad Flask refactoring.
