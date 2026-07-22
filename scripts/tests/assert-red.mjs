import { spawnSync } from "node:child_process";
import { resolve } from "node:path";
import process from "node:process";

const [, , targetArg, expectedDiagnostic] = process.argv;

if (!targetArg || !expectedDiagnostic) {
  console.error("Usage: node scripts/tests/assert-red.mjs <test-file> <expected-diagnostic>");
  process.exit(2);
}

const target = resolve(targetArg);
const syntax = spawnSync(process.execPath, ["--check", target], {
  encoding: "utf8",
  shell: false,
});

if (syntax.status !== 0) {
  process.stderr.write(syntax.stderr || syntax.stdout);
  console.error(`RED contract is not syntax-valid: ${targetArg}`);
  process.exit(1);
}

const result = spawnSync(process.execPath, ["--test", target], {
  encoding: "utf8",
  shell: false,
});
const output = `${result.stdout ?? ""}${result.stderr ?? ""}`;

if (result.status === 0) {
  console.error(`Expected ${targetArg} to fail before implementation, but it passed.`);
  process.exit(1);
}

if (!output.includes(expectedDiagnostic)) {
  process.stderr.write(output);
  console.error(`Expected RED diagnostic to contain: ${expectedDiagnostic}`);
  process.exit(1);
}

console.log(`RED confirmed for ${targetArg}: ${expectedDiagnostic}`);
