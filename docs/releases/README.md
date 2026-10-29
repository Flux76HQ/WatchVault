# Release notes

Every version has a notes file here, `vX.Y.Z.md`, written in English and reviewed **before** the
release is cut. The `Release` workflow (`.github/workflows/release.yml`, run by hand from `main`)
refuses to run without the file for the version in `VERSION`, creates the tag and the GitHub
Release in one call, and publishes the file as the body of the Release. Do not push a version tag
by hand.

Rules (App-Guidance `shared/guidelines/project-baseline.md` §5, template
`shared/templates/github/RELEASE_NOTE_TEMPLATE.md`):

1. User-facing first: Highlights, Features, Bug fixes, then Docs / Internal.
2. Name the PR next to each entry.
3. Say what was broken, not only that it is fixed.
4. An empty section says so in one line. "Upgrade notes: Nothing to do." is information.
5. List every PR (and commit) in the release.

A version bump (`node scripts/version.mjs bump`) that changes the app is therefore followed by a
notes file for that version in the same pull request.
