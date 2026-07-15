#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const repository = path.resolve(scriptDirectory, "..");
const uv = process.platform === "win32" ? "uv.exe" : "uv";
const command = [
  "run",
  "--no-project",
  "python",
  path.join(repository, "scripts", "install.py"),
  ...process.argv.slice(2),
];

const result = spawnSync(uv, command, { stdio: "inherit" });
if (result.error) {
  console.error(`flonat-research: could not run uv: ${result.error.message}`);
  console.error("Install uv first: https://docs.astral.sh/uv/");
  process.exit(1);
}
process.exit(result.status ?? 1);
