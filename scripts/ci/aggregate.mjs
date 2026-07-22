#!/usr/bin/env node
import process from "node:process";
import { pathToFileURL } from "node:url";

const alwaysRequired = ["select", "contracts", "version", "inventory"];
const conditionallyRequired = {
  backend: "backend",
  frontend: "frontend",
  browser: "browser",
};

function assertResult(jobs, name, expected) {
  const actual = jobs[name]?.result;
  if (actual !== expected) {
    throw new Error(`CI job ${name} must be ${expected}, received ${actual ?? "missing"}`);
  }
}

export function aggregateGate({ jobs, event, generateBaselines = false }) {
  if (!jobs || typeof jobs !== "object" || Array.isArray(jobs)) {
    throw new Error("NEEDS_JSON must describe the required CI jobs");
  }

  for (const name of alwaysRequired) assertResult(jobs, name, "success");

  const selected = jobs.select.outputs ?? {};
  for (const [output, job] of Object.entries(conditionallyRequired)) {
    if (!["true", "false"].includes(selected[output])) {
      throw new Error(`Selection output ${output} must be true or false`);
    }
    assertResult(jobs, job, selected[output] === "true" ? "success" : "skipped");
  }

  const baselineRequested = event === "workflow_dispatch" && generateBaselines;
  assertResult(jobs, "baselines", baselineRequested ? "success" : "skipped");
  return true;
}

function main() {
  let jobs;
  try {
    jobs = JSON.parse(process.env.NEEDS_JSON ?? "");
  } catch {
    throw new Error("NEEDS_JSON is not valid JSON");
  }
  aggregateGate({
    jobs,
    event: process.env.GITHUB_EVENT_NAME ?? "",
    generateBaselines: process.env.GENERATE_BASELINES === "true",
  });
  console.log("All selected delivery checks passed.");
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? "").href) {
  try {
    main();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  }
}
