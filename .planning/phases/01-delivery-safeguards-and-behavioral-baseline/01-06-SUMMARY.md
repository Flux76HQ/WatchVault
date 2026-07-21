---
phase: 01-delivery-safeguards-and-behavioral-baseline
plan: "06"
subsystem: frontend-regression
tags: [vitest, testing-library, axe, accessibility, permissions]
requires:
  - phase: 01-delivery-safeguards-and-behavioral-baseline
    provides: Deterministic frontend test harness and approved dependencies
provides:
  - Authentication, loading, routing, and wildcard regression evidence
  - Theme, preference, keyboard, and DOM-accessibility evidence
  - Permission-gated scoped watch mutation and error evidence
affects: [01-08, 01-09]
tech-stack:
  added: []
  patterns: [semantic component queries, stable scoped fixtures, API-boundary mocks]
key-files:
  created: [frontend/src/App.test.tsx, frontend/src/pages/Settings.test.tsx, frontend/src/pages/TitleDetail.test.tsx]
  modified: [frontend/src/pages/Settings.tsx, frontend/src/test/render.tsx, .gitignore]
key-decisions:
  - "Route-aware component tests declare their route pattern through the shared render helper."
  - "Scoped title fixtures expose initial and settled profile results separately so interactions begin only after scope reconciliation."
requirements-completed: [DELV-06]
coverage:
  - id: D1
    description: "Authentication, route gates, settings preferences, and representative DOMs have component and axe evidence."
    requirement: DELV-06
    verification:
      - kind: component
        ref: "npm --prefix frontend run test -- --run src/App.test.tsx src/pages/Settings.test.tsx"
        status: pass
    human_judgment: false
  - id: D2
    description: "The ingest.write gate and scoped watch mutation preserve exact request and feedback behavior."
    requirement: DELV-06
    verification:
      - kind: component
        ref: "npm --prefix frontend run test -- --run src/pages/TitleDetail.test.tsx"
        status: pass
      - kind: integration
        ref: "npm --prefix frontend run build"
        status: pass
    human_judgment: false
duration: 18min
completed: 2026-07-21
status: complete
---

# Phase 1 Plan 06: Frontend Behavioral Baseline Summary

**Authentication, settings, accessibility, permission, and scoped watch behavior now have deterministic component-level regression evidence.**

## Accomplishments

- Covered loading, unauthenticated, authenticated, index, known-route, and wildcard application states.
- Covered theme and default-profile persistence with keyboard interaction and representative axe scans.
- Covered the real `ingest.write` gate, exact scoped watch request, success feedback, and `ApiError` feedback.
- Fixed the inaccessible default-profile selector discovered by the blocking axe assertion.

## Task Commits

1. **Task 1: Cover authentication, routing, themes, and preferences** - `eee6f80`
2. **Task 2: Cover permission-gated watch mutation and feedback** - `21a2966`

## Deviations from Plan

- The plan prohibited product source changes, but the new axe evidence found a real missing accessible name. The selector label was linked to its control as the smallest behavior-preserving correction.
- Extended the shared render helper with an optional route pattern because `TitleDetail` requires a real `:id` parameter.

## Issues Encountered

The default profile settles after the first title request. The synthetic fixture now distinguishes initial household data from the settled scoped response, preventing interaction with transient DOM while preserving the production reconciliation behavior.

## Next Phase Readiness

The component baseline is ready to be referenced by the capability inventory, browser journey, and path-aware CI selector.

---
*Completed: 2026-07-21*
