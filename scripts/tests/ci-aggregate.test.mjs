import assert from "node:assert/strict";
import test from "node:test";

import { aggregateGate } from "../ci/aggregate.mjs";

function jobs({ backend = "true", frontend = "true", browser = "true", baselines = "skipped" } = {}) {
  return {
    select: { result: "success", outputs: { backend, frontend, browser } },
    contracts: { result: "success" },
    version: { result: "success" },
    inventory: { result: "success" },
    backend: { result: backend === "true" ? "success" : "skipped" },
    frontend: { result: frontend === "true" ? "success" : "skipped" },
    browser: { result: browser === "true" ? "success" : "skipped" },
    baselines: { result: baselines },
  };
}

test("aggregate accepts successful selected jobs and explicit skips", () => {
  assert.equal(
    aggregateGate({
      jobs: jobs({ backend: "false", browser: "false" }),
      event: "pull_request",
    }),
    true,
  );
});

test("aggregate requires successful baseline generation when requested", () => {
  assert.throws(
    () => aggregateGate({
      jobs: jobs(),
      event: "workflow_dispatch",
      generateBaselines: true,
    }),
    /baselines must be success/i,
  );
  assert.equal(
    aggregateGate({
      jobs: jobs({ baselines: "success" }),
      event: "workflow_dispatch",
      generateBaselines: true,
    }),
    true,
  );
});

test("aggregate rejects failures and skips that contradict selection", () => {
  const failed = jobs();
  failed.frontend.result = "failure";
  assert.throws(
    () => aggregateGate({ jobs: failed, event: "pull_request" }),
    /frontend must be success/i,
  );

  const unexpectedlySkipped = jobs();
  unexpectedlySkipped.browser.result = "skipped";
  assert.throws(
    () => aggregateGate({ jobs: unexpectedlySkipped, event: "pull_request" }),
    /browser must be success/i,
  );
});
