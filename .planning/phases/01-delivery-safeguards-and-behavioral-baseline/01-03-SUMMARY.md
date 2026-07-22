---
phase: 01-delivery-safeguards-and-behavioral-baseline
plan: "03"
subsystem: release-engineering
tags: [semver, git, node, version-policy]
requires:
  - phase: 01-delivery-safeguards-and-behavioral-baseline
    provides: Fail-first version policy contracts
provides:
  - Root VERSION canonical stable SemVer
  - Shared protected-path policy and pure policy engine
  - Idempotent check bump and print CLI with synchronized manifests
affects: [01-04, 01-09, 01-10]
tech-stack:
  added: []
  patterns: [pure policy engine with thin Git adapter, atomic manifest writes]
key-files:
  created: [VERSION, version-policy.json, scripts/lib/version-policy.mjs, scripts/version.mjs]
  modified: [frontend/package.json, frontend/package-lock.json, scripts/tests/version-policy.test.mjs]
key-decisions:
  - "Legacy bases may read frontend/package.json only when VERSION is absent."
  - "All child processes use argument arrays and reject unsafe refs and paths."
patterns-established:
  - "VERSION is canonical and package records are synchronized mirrors."
requirements-completed: [DELV-01, DELV-02, DELV-03]
coverage:
  - id: D1
    description: "Canonical versioning and protected-path enforcement are executable."
    requirement: DELV-01
    verification:
      - kind: unit
        ref: "node --test scripts/tests/version-policy.test.mjs"
        status: pass
    human_judgment: false
  - id: D2
    description: "Repository version records are synchronized at 1.0.1."
    requirement: DELV-03
    verification:
      - kind: integration
        ref: "node scripts/version.mjs check"
        status: pass
    human_judgment: false
duration: 18min
completed: 2026-07-21
status: complete
---

# Phase 1 Plan 03: Canonical Version Policy Summary

**WatchVault now has one protected-path policy, one canonical `VERSION`, and an idempotent CLI that keeps frontend manifests synchronized at 1.0.1.**

## Performance

- **Duration:** 18 min
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- Implemented stable SemVer parsing, comparison, bumping, safe path normalization, glob policy classification, and mirror synchronization.
- Added `check`, `bump`, and `print` Git-aware commands with staged and branch-diff modes.
- Set `VERSION`, `frontend/package.json`, and the lockfile root records to `1.0.1`.

## Task Commits

1. **Task 1: Build pure protected-path and SemVer engine** - `23b1a47`
2. **Task 2: Implement synchronized check, bump, and print** - `8829974`

## Decisions Made

- Exact remediation is exported by the policy engine and printed as the final diagnostic line.
- Bump writes are atomic and limited to the three authorized version records.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

The Wave 0 fixture initially placed manifests at the temporary repository root; it was corrected to mirror the real `frontend/` layout.

## User Setup Required

None.

## Next Phase Readiness

Runtime metadata, Docker/Compose, local hooks, and CI can now consume the canonical CLI.

---
*Phase: 01-delivery-safeguards-and-behavioral-baseline*
*Completed: 2026-07-21*
