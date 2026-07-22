# Feature Landscape

**Domain:** Self-hosted household media-tracking PWA redesign
**Project:** WatchVault
**Researched:** 2026-07-21
**Overall confidence:** MEDIUM

## Research Position

The redesign should borrow the clarity and immediacy of leading media trackers, not their product scope or branded interaction patterns. Current Trakt surfaces reinforce that users expect quick tracking, visible progress, detailed history, strong search, and personal statistics. Letterboxd similarly makes dated logging and history understandable. WatchVault should express those expectations through its existing household, source-aware, self-hosted model.

TV Time is now a legacy reference rather than a current benchmark: its official homepage was observed as a shutdown thank-you page on the research date. Its historical emphasis on effortless episode progress can still inspire the experience, but active products, accessibility standards, and WatchVault's real workflows should drive requirements.

This is a redesign milestone, not a product expansion. Watchlists, calendars, streaming-availability discovery, recommendations, ratings, reviews, social activity, and notifications may be common elsewhere, but they are not reasons to expand WatchVault's domain here.

## Table Stakes

Features and qualities users expect. Missing or inconsistent behavior makes the redesign feel incomplete.

| Feature | Why Expected | Complexity | Dependencies / Notes |
|---------|--------------|------------|----------------------|
| Semantic design tokens | A full-app redesign needs one source for color, typography, spacing, radii, elevation, opacity, motion, and breakpoints | High | Establish before page work; tokens must support dark, light, system, accent colors, contrast, and reduced motion |
| Reusable interaction primitives | Buttons, fields, selects, menus, tabs, dialogs, cards, badges, tooltips, toasts, tables, and charts must behave consistently | High | Include default, hover, active, focus, disabled, busy, error, and selected states; avoid page-local substitutes |
| Artwork treatment system | Posters and backdrops are central to a premium media product | Med | Define crop ratios, focal positioning, overlays, gradients, lazy loading, broken-image fallbacks, and metadata-free placeholders |
| Cinematic but readable hierarchy | Artwork-led presentation must still make title, progress, actions, and scope immediately legible | Med | Never rely on artwork alone for text contrast; preserve semantic heading order |
| Adaptive application shell | Desktop and mobile need stable, recognizable primary navigation | High | Desktop may use top/side navigation; mobile may use a compact bottom bar plus overflow; destinations and permissions remain equivalent |
| Clear active location and route recovery | Users must know where they are and return predictably from title, person, genre, and settings subviews | Med | Active states, page titles, browser history, deep links, contextual back/breadcrumb behavior |
| First-class profile/household scope | Every dashboard, search, history, and statistics result can change meaning by scope | High | Scope control stays visible, names the active profile or household, persists intentionally, and never silently resets |
| Permission-aware navigation | Members should not see unusable administration controls; admins must still find them | Med | Driven by existing permissions, not client-only hiding; direct routes still handle forbidden states |
| Dashboard at-a-glance hierarchy | Home should answer what is happening now, what was watched, and what needs attention | High | Preserve now playing, totals, trends, month summary, platform split, recent activity, unfinished items, and unknown items |
| Dashboard personalization | Existing edit-layout and restore-default behavior must remain understandable | Med | Prefer reorder/show/hide of curated modules, with a keyboard-operable alternative; preserve a sensible semantic reading order |
| Useful dashboard zero state | A new or empty household should not see a wall of empty cards | Med | Explain the value and route to import, connection setup, or manual cinema/history entry |
| Intent-first global search | Search must be easy to start and fast to refine | High | Support existing title, genre, person/actor, provider/platform, year, kind, and tag dimensions |
| Search facets and active-filter summary | Complex filters are only usable when users can see and clear the active constraints | Med | Facet values, active chips/summary, individual removal, clear-all, result count, and URL/back-state preservation where practical |
| Keyboard-usable search suggestions and filters | Search is a primary route and cannot depend on pointer interaction | Med | Use native controls or the WAI-ARIA combobox pattern; announce loading and result counts |
| Responsive search results | Poster grids must remain scannable from narrow mobile to wide desktop | Med | Stable aspect ratios, useful metadata, no clipped actions, progressive loading or explicit load-more |
| Artwork-led title overview | A title page should quickly communicate identity, kind, year/date, network/provider, genres, and description | High | Graceful behavior for incomplete or unknown metadata; do not hide core actions in the hero artwork |
| Visible watch and progress state | Users expect watched status and episode progress without calculating it themselves | High | Preserve watched counts, total time, unfinished progress, last position, now-playing state, and per-scope meaning |
| Series season/episode navigation | Episode tracking must make season structure and watched state easy to scan and update | High | Preserve specials, individual episodes, mark-season-watched, and progress indicators; scalable for long-running series |
| Cast, crew, person, and genre traversal | Existing enriched relationships are part of title understanding | Med | Links remain keyboard-accessible and route to current person/genre views; use stable artwork fallbacks |
| Complete title actions | All current metadata and tracking operations must remain available | High | Add watch, mark watched, remove watch, manual title/kind/poster override, TMDB enrichment, Trakt sync, unknown-title controls, and platform attribution are permission/state gated |
| History as an editable ledger | Trust in a tracker depends on correcting the record, not merely viewing it | High | Show date/time, title/episode, profile, provider/source, and relevant context; preserve add, edit, and remove capabilities |
| Safe history mutations | Editing or deleting history affects aggregates and must feel deliberate | High | Clear labels, validation, confirmation for destructive/bulk operations, pending state, success/error feedback, and refetch/reconciliation |
| Efficient repeat and bulk actions | Episode and season workflows should not require excessive repeated clicks | Med | Preserve mark-season/title behavior; provide accessible alternatives to long-press, drag, or swipe gestures |
| Scoped statistics overview | Users expect understandable summaries of their own or household viewing | High | Preserve total watch time, unique titles, watched counts, month/year ranges, and profile/household scope |
| Existing analytical views | The redesign cannot reduce the current statistics set | High | Preserve watched-per-month, daily activity heatmap, watch-time trend by day/week/month, platform split, genre time, actor time, and year/range selection |
| Accessible chart interpretation | Colorful charts alone are not sufficient | High | Text summary, labels/tooltips, non-color distinctions, keyboard or table alternative where needed, and meaningful empty states |
| Settings information architecture | A long mixed settings page makes a self-hosted app feel unsafe and difficult | High | Separate Personal/Appearance, Household, Profiles, Sources & Imports, Integrations, Advanced, and Danger Zone concepts |
| Personal preferences | Existing language, theme, accent, default profile, and expert-mode preferences must remain polished | Med | Saved state, immediate preview where safe, system-theme behavior, and reset/default affordances |
| Household profile administration | Multi-profile management is core, not ancillary | High | Preserve create/edit/remove, photos, admin role, member/recovery onboarding, counts, and permission-aware controls |
| Source and import administration | Users must be able to understand and operate provider connections | High | Preserve file import, provider selection, connection add/remove, sync, Trakt authorization, library selection, account mapping, last-sync state, and aggregate rebuild |
| Plugin, token, tag, and integration controls | Existing advanced capabilities must not disappear behind the redesign | High | Preserve plugin configuration, API tokens, tags, scrobble settings/endpoints, thresholds, and account mapping with clear security copy |
| Attribution and repair administration | Existing unknown-title and source-repair workflows protect data quality | High | Preserve attribution log, bulk platform assignment, re-attribution, unknown items, manual overrides, and audit-oriented feedback |
| Explicit destructive-action design | Reset-all, connection removal, profile removal, and other dangerous actions require special treatment | Med | Dedicated danger zone, consequence copy, confirmation, disabled/busy states, and permission checks |
| Dark, light, and system theme parity | A polished light theme is a requirement, not a dark-theme inversion | High | Every token, chart, poster overlay, focus ring, loading state, and error state must be verified in both themes |
| Responsive feature parity | The PWA is the only client; mobile cannot be a reduced administration viewer | High | Support 320 CSS-pixel reflow, touch and keyboard inputs, landscape, safe areas, zoom, and installed standalone mode |
| Purposeful mobile transformations | Dense desktop layouts need redesigned mobile compositions | High | Tables may become labeled rows/cards; dialogs may become sheets/full-screen; chart legends and actions must remain available |
| Loading-state hierarchy | Users need to know whether a route, section, image, or action is loading | Med | Skeleton only for structured content; inline busy state for actions; progress for long imports/syncs; preserve already-loaded data during refresh |
| Distinct empty states | First use, no search results, no activity in range, filtered-empty, no permission, and missing configuration are different situations | Med | Each state explains why and offers the most relevant next action |
| Recoverable error states | Raw failures or blank screens destroy confidence in a self-hosted product | High | Plain-language summary, retry, preserved input, optional technical detail for experts, and route-level error boundaries |
| Offline and stale-data clarity | An installable PWA can be open when the server or network is unavailable | High | Keep usable cached shell/data where supported, label stale/offline state, disable impossible mutations, and offer retry/reconnect |
| Internationalized layouts and content | WatchVault already supports six UI languages and localized metadata | High | No hard-coded strings; allow text expansion; keep language selection accessible; define fallback behavior for untranslated metadata |
| Keyboard and focus completeness | Premium quality includes operation without a pointer | High | Logical focus order, skip link, visible/unobscured focus, focus restoration, no traps, and keyboard access to all actions |
| Semantic and screen-reader feedback | Dynamic PWA updates must be perceivable | High | Landmarks/headings, labels, names/roles/values, live status for search/save/sync/errors, dialog focus containment, and meaningful image alternatives |
| Contrast, target size, and reflow | WCAG AA is a release requirement | High | 4.5:1 normal text, 3:1 required UI/graphic cues, minimum 24 CSS-pixel targets; prefer 44–48 CSS pixels for primary touch controls |
| Reduced-motion behavior | Large artwork transitions and animated charts can cause discomfort | Med | Honor `prefers-reduced-motion`; remove parallax, large scale/pan, and nonessential looping animation |
| Capability inventory regression gate | A redesign must prove that every existing screen and operation still exists | High | Map each current route, permission, action, loading/empty/error state, theme, and viewport to acceptance coverage before replacement |
| Automated frontend regression suite | Current absence of frontend tests makes a full-app redesign unusually risky | High | Component behavior, accessibility scans, visual baselines, responsive projects, API contracts, and critical end-to-end flows |

## Differentiators

Features and qualities that fit WatchVault's self-hosted household identity rather than imitating social media trackers.

| Feature | Value Proposition | Complexity | Dependencies / Notes |
|---------|-------------------|------------|----------------------|
| Household viewing cockpit | One clear switch changes the whole product between an individual and combined household story | High | Scope model, permission rules, scoped API responses, persistent shell control |
| Source-visible history | Provider, profile, and attribution context makes imported and scrobbled data trustworthy | High | Consistent provenance fields and badges; source must not overpower the title/date hierarchy |
| Repair-oriented UX | Unknown items, incorrect attribution, metadata overrides, and history corrections become a coherent repair workflow | High | Search, title detail, attribution log, permissions, audit feedback |
| Cross-provider now playing | Live sessions from Plex, Home Assistant, and other integrations make the dashboard feel alive without a social feed | High | Existing scrobble state; resilient stale-session and offline treatment |
| Progressive expert mode | Everyday users get a calm interface while operators can reveal tokens, scrobbling, attribution, rebuild, and reset tools | Med | One consistent disclosure model; expert mode must not become a permission boundary |
| Local privacy and ownership cues | Users can understand that household watch data stays on their server and which public metadata is sent externally | Med | Concise privacy/provenance copy near plugins, imports, and tokens; avoid repetitive banners |
| Integration health at a glance | Connection, last sync, library selection, account mapping, and failures are legible without reading logs | High | Normalized connection states and actionable errors; supporting API shaping may be justified |
| Personalized but bounded dashboard | Members can reorder or hide curated cards without creating an unmaintainable widget platform | Med | Existing dashboard preferences, semantic order, reset default |
| Graceful metadata degradation | The app remains useful when TMDB is absent, enrichment is pending, artwork fails, or a title is unknown | Med | Fallback artwork, source-native metadata, explicit enrichment status |
| Multilingual catalog context | Localized UI plus localized biographies/overviews is unusually strong for a household tracker | Med | Existing language fallback and lazy enrichment behavior |
| One-off cinema logging | A focused quick action captures offline viewing without turning WatchVault into a general diary/social app | Med | Search, profile/date selection, history mutation feedback |
| Self-hosted operational confidence | Admin actions show what is connected, syncing, queued, stale, failed, or safe to retry | High | Status vocabulary shared across settings, imports, dashboard, and worker-backed actions |

## Anti-Features

Features or approaches to explicitly avoid during this milestone.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Recommendation or personalized-discovery engine | Explicitly out of scope and creates a new data/algorithm product | Improve search, unfinished items, recent history, and existing catalog traversal |
| Social feed, follows, comments, public profiles, ratings, or reviews | Conflicts with private household positioning and adds moderation/privacy complexity | Keep activity private and scoped to the household |
| Native iOS or Android application | Splits effort and violates the single responsive PWA constraint | Make installed PWA behavior excellent across mobile and desktop |
| Net-new watchlists, release calendars, notifications, or streaming-availability discovery | Common competitor features, but they expand product scope rather than redesign current capability | Preserve unfinished items, current history, search, and provider metadata without implying a roadmap commitment |
| Copying TV Time, Trakt, or Letterboxd layouts or branding | Creates an imitation, possible IP/design risk, and poor fit for household administration | Extract principles—clarity, progress, artwork, fast logging—and express them through WatchVault's own system |
| Removing or burying current advanced capabilities | A visually simpler redesign that weakens imports, repair, profiles, or administration fails the milestone | Use progressive disclosure, permissions, and expert mode while keeping all operations findable |
| Gesture-only actions | Long-press, hover, swipe, or drag-only behavior excludes keyboard and assistive-technology users | Pair gestures with explicit buttons/menus and keyboard-operable alternatives |
| Autoplaying hero motion, parallax, or video backgrounds | Distracts from data, increases load, and conflicts with reduced-motion needs | Use static artwork, restrained transitions, and optional/reduced motion |
| Text directly on uncontrolled artwork | Contrast varies by poster/backdrop and will fail in one theme or title | Use tested scrims, solid surfaces, and tokenized foreground colors |
| Endless horizontal carousels | Hide content, perform poorly with keyboard, and make mobile/desktop behavior inconsistent | Use prioritized sections, responsive grids, and explicit “view all” navigation |
| Dashboard widget platform | Arbitrary widgets, sizing, and layout rules would create a new product and accessibility burden | Allow bounded reorder/show/hide of supported modules |
| Admin controls mixed into everyday content | Raises cognitive load and makes destructive actions feel casual | Separate personal, household, integrations, advanced, and danger-zone navigation |
| Silent optimistic destructive updates | Failed history/profile/source mutations can leave users believing data is correct when it is not | Show pending state, confirm consequences, reconcile server response, and provide retry/undo where feasible |
| Generic empty state everywhere | “Nothing here” does not distinguish first use, filters, permissions, configuration, or failures | Design state-specific explanation and next action |
| Full-screen spinner for independent sections | Blocks already-useful content and makes dashboards feel slower | Load stable shell first, then section skeletons/inline indicators |
| Theme-by-inversion | Automatic color inversion breaks artwork, charts, focus, elevation, and contrast | Design and test semantic tokens independently in dark and light modes |
| “Desktop shrunk to mobile” | Dense tables, side-by-side controls, and hover interactions will fail on the only mobile client | Define mobile composition and interaction behavior per component and route |
| Accessibility as a final audit | Late fixes force component and information-architecture rewrites | Build semantics, focus, contrast, target size, motion, and tests into primitives first |
| Visual snapshots as the only tests | Pixel checks cannot prove permissions, semantics, mutations, or data integrity | Combine component, behavior, accessibility, contract, visual, and end-to-end coverage |
| Broad backend rewrite | Unrelated refactoring increases redesign risk and violates milestone constraints | Make only response-shaping or state-contract changes required by the redesigned UI |

## Expected Behavior by Surface

### Design System

- Define semantic tokens, not page-specific color names. Components consume roles such as surface, elevated surface, primary text, muted text, accent, danger, focus, and artwork scrim.
- Document every reusable component in representative states across dark/light themes, narrow/wide viewports, long translated text, keyboard focus, reduced motion, and missing artwork.
- Keep cinematic personality in typography, artwork, depth, and restrained motion; keep controls conventional and predictable.

### Navigation and Shell

- Desktop and mobile expose the same core destinations: dashboard, overviews/statistics, search, imports/sources, profiles where applicable, and settings.
- Profile/household scope is globally visible. Changing it updates scoped pages predictably and announces the change.
- Search is reachable from primary navigation without forcing users through a discovery feed.
- Deep links to title, person, genre, and settings views survive refresh and provide a clear path back.

### Dashboard

- Prioritize now playing and the current viewing story, then summary/progress, then analytical and repair-oriented modules.
- Preserve current modules and customization; do not force every module above the fold.
- Each module handles loading, populated, zero, error, permission, and stale states independently.
- Quick actions such as import history or add a cinema visit appear only where context and permission make them useful.

### Search

- Search supports a simple title query immediately and reveals advanced filters without making them mandatory.
- Active facets are visible and reversible. Back/forward navigation should not unexpectedly erase the user's query.
- Result cards show enough metadata to distinguish similarly named titles without becoming miniature detail pages.
- No-results behavior differentiates an empty query, restrictive filters, unavailable metadata, and a genuine miss.

### Title Detail and History

- The title identity and primary tracking action remain visible even when artwork is missing or enrichment is pending.
- Series pages make watched/remaining progress and season/episode state scannable; film pages avoid empty series scaffolding.
- Watch history is a chronological, editable record with explicit add/edit/remove controls. Destructive and bulk changes state their scope.
- Manual overrides, unknown-title actions, platform attribution, enrichment, and Trakt sync are grouped as management actions rather than mixed into the primary viewing summary.
- Now-playing and last-position state should be timely but clearly labeled if stale.

### Statistics

- Start each view with a plain-language summary before detailed charts.
- Range, granularity, and profile scope controls remain consistent across charts.
- Charts use consistent category colors, legends, units, and date formatting across themes.
- Every chart has an accessible interpretation that does not depend only on color or pointer hover.

### Settings and Administration

- Separate member preferences from household administration and source/integration operations.
- Show capability and permission boundaries before a user attempts an action.
- Connection cards communicate configured/not configured, enabled/disabled, syncing, last success, warning/error, and available next action.
- Expert mode reduces everyday clutter but never substitutes for authorization.
- Danger-zone actions are visually and structurally separate, with clear impact and confirmation.

### Responsive PWA

- Verify at narrow mobile, large mobile, tablet, laptop, and wide desktop widths, plus zoom/reflow at 320 CSS pixels.
- Support touch, mouse, and keyboard based on input capability rather than assuming device type from width.
- Account for installed-mode safe areas and virtual keyboards; bottom navigation and dialogs must not obscure focused controls.
- Surface offline/stale state rather than presenting cached information as current.

### Loading, Empty, Error, and Feedback States

- Skeletons match the final card/list geometry and are reserved for initial structured content.
- Save, sync, import, and rebuild actions use inline progress and prevent accidental duplicate submission.
- Status messages such as “18 results,” “saved,” “sync failed,” or “profile scope changed” are available to assistive technology without stealing focus.
- Errors preserve user input and offer retry; technical diagnostics may be progressively disclosed for self-hosters.

### Accessibility

- Use native elements before custom ARIA widgets. When custom dialogs, tabs, or comboboxes are necessary, follow WAI-ARIA keyboard and focus patterns.
- Provide a skip link, landmarks, one clear page heading, logical subheadings, descriptive control names, and visible focus.
- Avoid drag-only dashboard editing and hover-only chart detail.
- Automated accessibility checks are a gate, not a replacement for keyboard, zoom/reflow, screen-reader, contrast, reduced-motion, and touch review.

### Regression Protection

- Create a baseline capability matrix from current routes, endpoints, permissions, themes, languages, and responsive screenshots before replacing screens.
- Add component tests for primitives and state variants; test behavior rather than implementation details.
- Add end-to-end coverage for profile switching; dashboard-to-search-to-title; add/edit/remove history; season marking; statistics scope/range; settings permissions; import/connection operations; and retry/error flows.
- Add deterministic visual baselines for core routes in dark/light and desktop/mobile projects. Keep the screenshot environment fixed.
- Run automated accessibility scans on route defaults and revealed states such as menus, dialogs, filters, errors, and mobile navigation.
- Keep manual release checks for screen-reader announcements, focus restoration, reduced motion, artwork contrast, and complex chart interpretation.

## Feature Dependencies

```text
Current capability inventory
  → API/view-model contracts
  → regression harness
  → safe full-screen migration

Semantic tokens
  → dark/light/system theme parity
  → artwork treatments and chart palette
  → reusable primitives
  → application shell
  → all route redesigns

Accessibility rules + responsive rules
  → primitive acceptance criteria
  → shell/navigation behavior
  → every page composition

Authentication + permissions + profile/household scope
  → navigation visibility
  → dashboard/search/detail/stats data meaning
  → settings/admin actions

Shared remote-state model
  → loading/empty/error/stale patterns
  → dashboard modules
  → search and detail
  → sync/import/settings feedback

Search result model
  → title/person/genre traversal
  → manual cinema/history add flows

Title progress + episode model
  → title detail
  → unfinished dashboard module
  → history mutation verification

History mutation contract
  → add/edit/remove actions
  → aggregate refresh
  → statistics and dashboard consistency

Connection/plugin/scrobble status contracts
  → imports and settings redesign
  → integration health
  → now-playing and repair feedback
```

## MVP Recommendation

For this redesign, “MVP” should mean the first reference-quality implementation slice, not a partial milestone release.

Prioritize:

1. **Regression baseline and design-system foundations** — inventory existing capability, establish tokens/primitives, remote-state patterns, accessibility rules, and test tooling before broad page changes.
2. **Adaptive shell and global scope** — deliver navigation, profile/household scope, themes, responsive behavior, and route feedback as the frame for every screen.
3. **Reference journey** — redesign dashboard → search → title detail → add/edit/remove watch history end to end, including loading/empty/error/offline and mobile behavior.
4. **Statistics and administration preservation** — migrate overviews, profiles, imports, plugins, tokens, tags, scrobbling, attribution, expert mode, and danger-zone behavior without capability loss.
5. **Cross-app hardening** — complete visual, accessibility, responsive, language, permission, and end-to-end regression matrices before release.

Defer:

- **Recommendations, social features, ratings/reviews, native apps, watchlists/calendars, and notification systems:** they are new product domains, not redesign requirements.
- **Unrelated backend refactoring:** only reshape existing responses or status data when a redesigned workflow cannot be clear and reliable without it.
- **Arbitrary dashboard widgets:** retain bounded customization instead of creating a layout platform.

## Sources

Source confidence follows the project research seam. Critical conclusions were cross-checked where possible; findings based on web research remain MEDIUM rather than authoritative.

- [MEDIUM] Trakt official web overview — https://trakt.tv/
- [MEDIUM] Trakt App Store feature listing — https://apps.apple.com/us/app/trakt-tv-time-to-watch/id1514873602
- [MEDIUM] Letterboxd product/about and diary behavior — https://letterboxd.com/about/
- [LOW] TV Time official homepage, observed shutdown thank-you page on 2026-07-21 — https://www.tvtime.com/
- [MEDIUM] Jellyfin user-management documentation — https://jellyfin.org/docs/general/server/users/adding-managing-users/
- [MEDIUM] WCAG 2.2 — https://www.w3.org/TR/WCAG22/
- [MEDIUM] WAI-ARIA Authoring Practices: dialog, tabs, combobox, alert — https://www.w3.org/WAI/ARIA/apg/patterns/
- [MEDIUM] Understanding WCAG status messages — https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html
- [MEDIUM] Microsoft PWA overview, updated 2025-10-01 — https://learn.microsoft.com/en-us/microsoft-edge/progressive-web-apps/
- [MEDIUM] web.dev accessible tap targets — https://web.dev/articles/accessible-tap-targets
- [MEDIUM] Carbon Design System empty states — https://carbondesignsystem.com/patterns/empty-states-pattern/
- [MEDIUM] Carbon Design System loading — https://carbondesignsystem.com/patterns/loading-pattern/
- [MEDIUM] MDN `prefers-color-scheme` — https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme
- [MEDIUM] MDN `prefers-reduced-motion` — https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- [MEDIUM] Playwright visual comparisons — https://playwright.dev/docs/test-snapshots
- [MEDIUM] Playwright accessibility testing — https://playwright.dev/docs/accessibility-testing
- [MEDIUM] Playwright browser/device projects — https://playwright.dev/docs/test-projects
- [MEDIUM] Storybook visual testing — https://storybook.js.org/docs/writing-tests/visual-testing
- [HIGH, project evidence] `.planning/PROJECT.md`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`, `README.md`, and current frontend routes/pages
