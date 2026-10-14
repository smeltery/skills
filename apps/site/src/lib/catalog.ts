import { readdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { parse } from "yaml";

export const repository = "https://github.com/smeltery/skills";
export const installCommand = (name?: string) =>
  `npx skills@latest add smeltery/skills${name ? ` --skill ${name}` : ""}`;
export const groups: Record<string, string[]> = {
  "Plan & design": [
    "architecture",
    "architecture-review",
    "design",
    "grill-with-docs",
    "to-prd",
    "to-issues",
    "wayfinder",
    "triage",
    "zoom-out",
    "prototype",
    "ui-studio",
    "html-doc",
  ],
  "Build & debug": [
    "tdd",
    "diagnose",
    "performance-engineer",
    "workon",
    "workon-event",
    "cloud-factory",
    "feature-gap",
    "port",
    "website-studio",
  ],
  "Review & improve": [
    "review",
    "verify",
    "simplify",
    "lean-diff",
    "improve-codebase-architecture",
    "loc-budget",
    "pr-workflow",
    "pr-monitor",
    "ci-monitoring",
    "gho",
  ],
  "Git & commits": [
    "branch-conventions",
    "commit-conventions",
    "git-commit",
    "git-safety",
    "worktree",
  ],
  "Work & communicate": [],
};
export interface Skill {
  name: string;
  description: string;
  summary: string;
  category: string;
  group: string;
  sourcePath: string;
  invocation: "User only" | "Agent only" | "You or your agent";
  argumentHint: string;
  content: string;
  readme: string;
}
// npm workspace scripts run from apps/site in development, tests, and builds.
const root = resolve(process.cwd(), "../../skills");
export function loadSkills(): Skill[] {
  const skills: Skill[] = [];
  for (const category of readdirSync(root, { withFileTypes: true }).filter(
    (entry) => entry.isDirectory(),
  )) {
    for (const directory of readdirSync(`${root}/${category.name}`, {
      withFileTypes: true,
    }).filter((entry) => entry.isDirectory())) {
      const path = `${root}/${category.name}/${directory.name}`;
      if (!readdirSync(path).includes("SKILL.md")) continue;
      const raw = readFileSync(`${path}/SKILL.md`, "utf8");
      const frontmatter = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
      if (!frontmatter)
        throw new Error(`Missing frontmatter: ${path}/SKILL.md`);
      const data = parse(frontmatter[1]);
      const content = raw.slice(frontmatter[0].length);
      if (
        data.name !== directory.name ||
        typeof data.description !== "string" ||
        !data.description.trim()
      ) {
        throw new Error(`Invalid skill metadata: ${path}/SKILL.md`);
      }
      const description = data.description.replace(/\s+/g, " ").trim();
      skills.push({
        name: data.name,
        description,
        summary: description.split(/(?<=\.)\s+(?=[A-Z])/)[0],
        category: category.name,
        group:
          Object.entries(groups).find(([, names]) =>
            names.includes(data.name),
          )?.[0] ??
          (category.name === "productivity"
            ? "Work & communicate"
            : "Build & debug"),
        sourcePath: `skills/${category.name}/${data.name}`,
        invocation:
          data["user-invocable"] === false
            ? "Agent only"
            : data["disable-model-invocation"] === true
              ? "User only"
              : "You or your agent",
        argumentHint:
          typeof data["argument-hint"] === "string"
            ? data["argument-hint"]
            : "",
        content,
        readme: readFileSync(`${path}/README.md`, "utf8"),
      });
    }
  }
  const names = skills.map((skill) => skill.name);
  if (new Set(names).size !== names.length)
    throw new Error("Skill names must be unique.");
  return skills.sort((a, b) => a.name.localeCompare(b.name));
}
export const skills = loadSkills();
export type SkillPreview = Pick<
  Skill,
  "name" | "description" | "summary" | "category" | "group"
>;
export const previews: SkillPreview[] = skills.map(
  ({ name, description, summary, category, group }) => ({
    name,
    description,
    summary,
    category,
    group,
  }),
);
