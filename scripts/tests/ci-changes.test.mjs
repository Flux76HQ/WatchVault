import assert from "node:assert/strict";
import test from "node:test";

import { selectJobs } from "../ci-changes.mjs";

const expected = {
  "docs/guide.md": [false, false, false],
  "backend/app/api/meta.py": [true, false, true],
  "plugins/example/plugin.py": [true, false, true],
  "frontend/src/App.tsx": [false, true, true],
  "homeassistant/custom_components/watchvault/manifest.json": [false, false, false],
  "Dockerfile": [true, true, true],
  "docker-compose.yml": [true, true, true],
  ".github/workflows/ci.yml": [true, true, true],
  "scripts/version.mjs": [true, true, true],
};

for (const [path, [backend, frontend, browser]] of Object.entries(expected)) {
  test(`PR selection classifies ${path}`, () => {
    const selected = selectJobs({ event: "pull_request", ref: "refs/pull/1/merge", paths: [path] });
    assert.deepEqual(
      [selected.backend, selected.frontend, selected.browser],
      [backend, frontend, browser],
    );
    assert.equal(selected.version, true);
    assert.equal(selected.inventory, true);
    assert.ok(selected.reasons.length > 0);
  });
}

test("empty PR diff keeps always-on checks and verifies all heavy jobs unselected", () => {
  const selected = selectJobs({ event: "pull_request", ref: "refs/pull/1/merge", paths: [] });
  assert.deepEqual(selected, {
    version: true,
    inventory: true,
    backend: false,
    frontend: false,
    browser: false,
    reasons: ["no changed paths"],
  });
});

test("main and release tags force the full suite", () => {
  for (const ref of ["refs/heads/main", "refs/tags/v1.0.1"]) {
    const selected = selectJobs({ event: "push", ref, paths: [] });
    assert.equal(selected.backend, true);
    assert.equal(selected.frontend, true);
    assert.equal(selected.browser, true);
  }
});

test("unsafe paths and unknown events fail closed", () => {
  assert.throws(
    () => selectJobs({ event: "pull_request", ref: "refs/pull/1/merge", paths: ["../secret"] }),
    /path|traversal/i,
  );
  assert.throws(
    () => selectJobs({ event: "workflow_run", ref: "refs/heads/main", paths: [] }),
    /event/i,
  );
});
