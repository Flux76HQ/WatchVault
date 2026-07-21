import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const adapterPath = join(ROOT, "scripts", "docker-version.mjs");

if (!existsSync(adapterPath)) {
  throw new Error("Docker/Compose contract not implemented: scripts/docker-version.mjs missing");
}

const dockerfile = readFileSync(join(ROOT, "Dockerfile"), "utf8");
const compose = readFileSync(join(ROOT, "docker-compose.build.yml"), "utf8");
const readme = readFileSync(join(ROOT, "README.md"), "utf8");
const adapter = readFileSync(adapterPath, "utf8");

test("Docker requires VERSION and embeds one OCI/runtime value", () => {
  assert.match(dockerfile, /^ARG VERSION$/m);
  assert.match(dockerfile, /org\.opencontainers\.image\.version=.*VERSION/);
  assert.match(dockerfile, /COPY VERSION \/app\/VERSION/);
  assert.match(dockerfile, /RUN npm ci/);
  assert.doesNotMatch(dockerfile, /RUN npm install/);
});

test("Compose receives required WATCHVAULT_VERSION without a duplicate default", () => {
  assert.match(compose, /context:\s*\./);
  assert.match(compose, /VERSION:\s*\$\{WATCHVAULT_VERSION:\?/);
  assert.doesNotMatch(compose, /WATCHVAULT_VERSION:-\d/);
  assert.doesNotMatch(compose, /^\s*VERSION:\s*["']?\d+\.\d+\.\d+/m);
});

test("adapter reads root VERSION and invokes the existing two-file Compose path with argument arrays", () => {
  assert.match(adapter, /VERSION/);
  assert.match(adapter, /docker-compose\.yml/);
  assert.match(adapter, /docker-compose\.build\.yml/);
  assert.match(adapter, /spawnSync|execFileSync/);
  assert.doesNotMatch(adapter, /\bexecSync\s*\(/);
});

test("documented local build routes through the canonical adapter", () => {
  const command = "node scripts/docker-version.mjs compose up -d --build";
  assert.match(compose, new RegExp(command.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  assert.match(readme, new RegExp(command.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
});
