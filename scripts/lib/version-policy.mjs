import { readFileSync, renameSync, writeFileSync } from "node:fs";
import { isAbsolute, join, win32 } from "node:path";

export const REMEDIATION = "node scripts/version.mjs bump";

export function parseStableVersion(value) {
  const normalized = String(value ?? "").trim();
  const match = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/.exec(normalized);
  if (!match) {
    throw new Error(`Expected stable SemVer X.Y.Z, received ${JSON.stringify(normalized)}`);
  }
  return {
    major: Number(match[1]),
    minor: Number(match[2]),
    patch: Number(match[3]),
  };
}

export function formatVersion(version) {
  return `${version.major}.${version.minor}.${version.patch}`;
}

export function compareVersions(left, right) {
  const a = typeof left === "string" ? parseStableVersion(left) : left;
  const b = typeof right === "string" ? parseStableVersion(right) : right;
  for (const key of ["major", "minor", "patch"]) {
    if (a[key] !== b[key]) {
      return a[key] > b[key] ? 1 : -1;
    }
  }
  return 0;
}

export function bumpVersion(value, release = "patch") {
  const parsed = parseStableVersion(value);
  if (release === "major") {
    return formatVersion({ major: parsed.major + 1, minor: 0, patch: 0 });
  }
  if (release === "minor") {
    return formatVersion({ major: parsed.major, minor: parsed.minor + 1, patch: 0 });
  }
  if (release === "patch") {
    return formatVersion({ ...parsed, patch: parsed.patch + 1 });
  }
  throw new Error(`Unknown release type: ${release}`);
}

export function normalizeGitPath(value) {
  const raw = String(value ?? "");
  if (!raw || isAbsolute(raw) || win32.isAbsolute(raw)) {
    throw new Error(`Git path must be a non-empty relative path: ${JSON.stringify(raw)}`);
  }
  const normalized = raw.replaceAll("\\", "/").replace(/^(?:\.\/)+/, "");
  if (normalized.split("/").some((part) => part === "..")) {
    throw new Error(`Git path traversal is not allowed: ${JSON.stringify(raw)}`);
  }
  return normalized;
}

function globToRegExp(glob) {
  let source = "^";
  for (let index = 0; index < glob.length; index += 1) {
    const char = glob[index];
    if (char === "*" && glob[index + 1] === "*") {
      index += 1;
      if (glob[index + 1] === "/") {
        index += 1;
        source += "(?:.*/)?";
      } else {
        source += ".*";
      }
    } else if (char === "*") {
      source += "[^/]*";
    } else if (char === "?") {
      source += "[^/]";
    } else {
      source += char.replace(/[\\^$.[\]{}()+|]/g, "\\$&");
    }
  }
  return new RegExp(`${source}$`);
}

function matchesAny(path, patterns = []) {
  return patterns.some((pattern) => globToRegExp(normalizeGitPath(pattern)).test(path));
}

export function classifyProtectedPath(value, policy) {
  const path = normalizeGitPath(value);
  if (matchesAny(path, policy.exclude)) {
    return false;
  }
  return matchesAny(path, policy.include);
}

export function protectedChangesRequireBump(paths, policy) {
  return [...new Set(paths.map(normalizeGitPath))]
    .sort()
    .some((path) => classifyProtectedPath(path, policy));
}

export function isSufficientVersion(baseVersion, currentVersion, changedPaths, policy) {
  if (!protectedChangesRequireBump(changedPaths, policy)) {
    return compareVersions(currentVersion, baseVersion) >= 0;
  }
  return compareVersions(currentVersion, baseVersion) > 0;
}

export function readVersionPolicy(root) {
  return JSON.parse(readFileSync(join(root, "version-policy.json"), "utf8"));
}

export function readVersionRecords(root) {
  const packageJson = JSON.parse(readFileSync(join(root, "frontend", "package.json"), "utf8"));
  const lockfile = JSON.parse(readFileSync(join(root, "frontend", "package-lock.json"), "utf8"));
  return {
    canonical: formatVersion(parseStableVersion(readFileSync(join(root, "VERSION"), "utf8"))),
    package: formatVersion(parseStableVersion(packageJson.version)),
    lockfile: formatVersion(parseStableVersion(lockfile.packages?.[""]?.version)),
  };
}

function writeAtomic(path, content) {
  const temporary = `${path}.${process.pid}.tmp`;
  writeFileSync(temporary, content);
  renameSync(temporary, path);
}

export function writeVersionRecords(root, version) {
  const stable = formatVersion(parseStableVersion(version));
  const packagePath = join(root, "frontend", "package.json");
  const lockfilePath = join(root, "frontend", "package-lock.json");
  const packageJson = JSON.parse(readFileSync(packagePath, "utf8"));
  const lockfile = JSON.parse(readFileSync(lockfilePath, "utf8"));

  packageJson.version = stable;
  lockfile.version = stable;
  if (!lockfile.packages?.[""]) {
    throw new Error("package-lock.json is missing packages[\"\"]");
  }
  lockfile.packages[""].version = stable;

  writeAtomic(join(root, "VERSION"), `${stable}\n`);
  writeAtomic(packagePath, `${JSON.stringify(packageJson, null, 2)}\n`);
  writeAtomic(lockfilePath, `${JSON.stringify(lockfile, null, 2)}\n`);
}
