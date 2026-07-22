# WatchVault

## What This Is

WatchVault is a self-hosted watch-history platform for media enthusiasts who want to manage personal and household viewing data in one place. It imports and synchronizes activity from media providers, supports live scrobbling and manual history management, enriches a shared media catalog, and presents the result through an installable web application.

This milestone redesigns the full existing interface into a modern, cinematic, premium experience comparable in quality to leading media-tracking products such as TV Time and Trakt, without expanding the product into a social network or recommendation service.

## Core Value

Self-hosting media enthusiasts can move effortlessly from their dashboard to finding a title, understanding its details, and maintaining accurate personal or household watch history.

## Requirements

### Validated

- ✓ Users can authenticate with passkeys, sessions, recovery codes, and API tokens — existing
- ✓ Users can manage personal and household profiles, permissions, preferences, and themes — existing
- ✓ Users can import, synchronize, and live-scrobble watch activity from supported providers — existing
- ✓ Users can manually add, edit, and remove watch-history data — existing
- ✓ Users can browse and search titles, people, genres, networks, history, and statistics — existing
- ✓ Users can inspect enriched title, episode, cast, crew, progress, and provider metadata — existing
- ✓ Users can use an installable PWA with incremental offline data synchronization — existing
- ✓ Authenticated clients can query WatchVault search and statistics through MCP — existing

### Active

- [ ] Establish a cohesive cinematic design system with reusable tokens, typography, spacing, surfaces, artwork treatments, motion, and interaction states
- [ ] Redesign the navigation and application shell for intuitive desktop and mobile use
- [ ] Redesign every existing user-facing screen without removing or weakening current capabilities
- [ ] Make the dashboard-to-search-to-title-detail-to-watch-history journey the reference-quality experience
- [ ] Preserve a dark-first cinematic presentation and an equally polished light theme, including existing appearance preferences
- [ ] Ensure layouts and interactions are responsive across supported desktop and mobile viewports
- [ ] Ensure keyboard operation, visible focus, semantic structure, and WCAG AA color contrast
- [ ] Add supporting API response changes only where the redesigned interface needs better-shaped existing data
- [ ] Add frontend regression coverage for critical workflows and reusable UI behavior
- [ ] Preserve versioning, CI, release, secret-management, and operational-documentation enforcement while the redesign changes runtime behavior

### Out of Scope

- New recommendation or personalized-discovery engines — this milestone improves presentation of existing capabilities
- Social feeds, follows, reviews, comments, or public profiles — WatchVault remains a private self-hosted household product
- Native iOS or Android applications — the installable responsive PWA remains the client
- Replacing React, Flask, PostgreSQL, or the modular-monolith deployment model — the redesign builds on the established architecture
- Broad backend refactoring unrelated to supporting the redesigned user experience — avoid coupling UI work to unrelated technical debt

## Context

The current product is a React 18 and TypeScript PWA served by nginx, backed by a Flask API, PostgreSQL, provider adapters, metadata plugins, a background worker, and a custom MCP service. It is packaged as one application container plus PostgreSQL and already has a broad set of working product capabilities.

The existing interface has route pages and shared components, but presentation and workflow logic are concentrated in several large page modules. The shared API layer returns weakly typed data, and no frontend unit, component, or end-to-end test runner is currently declared. These gaps increase regression risk during a full-app redesign and make reusable UI patterns harder to enforce.

The redesign should feel artwork-led, immersive, and premium rather than merely reskinned. Navigation, information hierarchy, responsive behavior, feedback states, loading and empty states, and interaction consistency are part of the product outcome. Existing dashboard customization, profile scope, permissions, provider management, data management, statistics, and appearance preferences must remain usable.

## Constraints

- **Existing stack**: Continue with React, TypeScript, Vite, Flask, PostgreSQL, and the current self-hosted deployment architecture — minimize migration risk and preserve proven capabilities
- **Feature preservation**: Every current user-facing capability must remain available and understandable — this is a redesign, not a product reset
- **Backend scope**: Backend changes must directly support existing data in the redesigned UI — no unrelated platform expansion
- **Accessibility**: Keyboard usability, visible focus, semantic structure, and WCAG AA contrast are release requirements — premium quality includes inclusive operation
- **Responsive UX**: The complete interface must support desktop and mobile use — the PWA is the only client
- **Themes**: Use a cinematic dark-first direction while retaining a polished light mode and saved user preferences
- **Versioning**: Runtime, build, deploy, or CI changes require a SemVer project-version bump — default to a patch bump unless scope requires otherwise
- **CI enforcement**: Protected runtime paths must fail CI when changed without a version bump, with an exact remediation message
- **Local enforcement**: Provide an idempotent version-bump helper and fast repository-configured git hooks; keep heavyweight checks in CI
- **Secrets**: Keep `.env` variants ignored, maintain safe `.env.example` placeholders, and never commit production credentials
- **Release discipline**: Publish from `vX.Y.Z` tags through CI with reproducible artifacts and documented stable/latest/beta channel rules
- **Operations**: Keep the README operationally complete for setup, run/stop, health checks, deploy/update, backup/restore, architecture, and data locations
- **Measurability**: Every mandatory process rule must be enforceable through CI or hooks rather than documentation alone

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Redesign the full application in one tracked milestone | A partial redesign would leave inconsistent navigation, interaction patterns, and visual quality across core workflows | — Pending |
| Use a cinematic, premium, artwork-led visual direction | This best matches the media domain and the quality bar set by comparable tracking products | — Pending |
| Optimize first for self-hosting media enthusiasts managing personal and household history | This is the existing product's strongest audience and differentiates it from public social tracking services | — Pending |
| Preserve current capabilities and limit new backend work to UI support | The goal is a coherent redesign without uncontrolled product-scope expansion | — Pending |
| Treat the dashboard-to-title-to-history journey as the reference flow | It represents the most frequent end-to-end value the redesigned interface must deliver | — Pending |
| Preserve polished dark and light themes | Dark mode anchors the cinematic direction while existing appearance preferences remain supported | — Pending |
| Require responsive, keyboard-accessible, WCAG AA behavior | Visual modernization cannot come at the cost of usability or accessibility | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? Move to Out of Scope with reason
2. Requirements validated? Move to Validated with phase reference
3. New requirements emerged? Add to Active
4. Decisions to log? Add to Key Decisions
5. "What This Is" still accurate? Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-07-21 after initialization*
