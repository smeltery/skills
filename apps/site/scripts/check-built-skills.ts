import { resolve } from "node:path";
import { checkBuiltSkills, skillDirectories } from "./skill-checks.ts";

const root = resolve(import.meta.dirname, "../../..");
const errors = checkBuiltSkills(root);
if (errors.length) {
  console.error(errors.join("\n"));
  process.exitCode = 1;
} else {
  console.log(
    `Verified pages and discovery entries for ${skillDirectories(root).length} skills.`,
  );
}
