#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import process from "node:process";

const options = { cwd: process.cwd(), encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] };
execFileSync("git", ["config", "--local", "core.hooksPath", ".githooks"], options);
const configured = execFileSync(
  "git",
  ["config", "--local", "--get", "core.hooksPath"],
  options,
).trim();
if (configured !== ".githooks") {
  throw new Error(`Expected core.hooksPath=.githooks, received ${configured}`);
}
console.log("Configured core.hooksPath=.githooks");
