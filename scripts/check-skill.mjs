import { spawnSync } from "node:child_process";
import { resolve } from "node:path";
import { checkRegistration } from "../apps/site/scripts/skill-checks.ts";

const root = resolve(import.meta.dirname, "..");
const [name, ...extra] = process.argv.slice(2);
if (!name || extra.length) {
  console.error("Usage: npm run skill:check -- <skill-name>");
  process.exit(1);
}
const errors = checkRegistration(root, name);
if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}
for (const script of ["check", "test", "build"]) {
  const result = spawnSync(
    process.platform === "win32" ? "npm.cmd" : "npm",
    ["run", script],
    {
      cwd: root,
      stdio: "inherit",
    },
  );
  if (result.error) console.error(result.error.message);
  if (result.error || result.status !== 0) process.exit(result.status || 1);
}
console.log(`Skill registration and website verified: /skills/${name}/`);
console.log(
  "Inspect the production page at desktop/mobile sizes before finishing.",
);
