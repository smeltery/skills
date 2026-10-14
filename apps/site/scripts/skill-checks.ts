import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { parse } from "yaml";

export function skillDirectories(root: string): string[] {
  const directory = join(root, "skills");
  return readdirSync(directory, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .flatMap((category) =>
      readdirSync(join(directory, category.name), { withFileTypes: true })
        .filter((entry) => entry.isDirectory())
        .map((entry) => `skills/${category.name}/${entry.name}`),
    )
    .filter((path) => existsSync(join(root, path, "SKILL.md")))
    .sort();
}

export function checkRegistration(root: string, name: string): string[] {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name))
    return ["Use a lowercase, hyphenated skill name."];
  const matches = skillDirectories(root).filter((path) =>
    path.endsWith(`/${name}`),
  );
  if (matches.length !== 1)
    return [
      `Expected one canonical skill named ${name}; found ${matches.length}.`,
    ];
  const directory = matches[0];
  const errors: string[] = [];
  const source = readFileSync(join(root, directory, "SKILL.md"), "utf8");
  const frontmatter = source.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
  try {
    const data = frontmatter ? parse(frontmatter[1]) : null;
    if (data?.name !== name)
      errors.push("Frontmatter name must match the directory.");
    for (const key of ["description", "argument-hint"])
      if (typeof data?.[key] !== "string" || !data[key].trim())
        errors.push(`Frontmatter requires a nonempty ${key}.`);
  } catch (error) {
    errors.push(`Invalid YAML frontmatter: ${error}`);
  }
  const readme = join(root, directory, "README.md");
  if (!existsSync(readme) || !readFileSync(readme, "utf8").trim())
    errors.push(
      `Missing nonempty ${directory}/README.md (the website overview).`,
    );
  for (const catalog of [
    "README.md",
    "docs/skills.md",
    `${dirname(directory)}/README.md`,
  ]) {
    const path = join(root, catalog);
    const text = existsSync(path) ? readFileSync(path, "utf8") : "";
    const links = [...text.matchAll(/\]\(([^)\s]+)\)/g)].map((match) =>
      resolve(dirname(path), match[1].split("#")[0]),
    );
    if (!links.includes(readme))
      errors.push(`${catalog} must link to ${directory}/README.md.`);
  }
  return errors;
}

export function checkBuiltSkills(root: string): string[] {
  const output = join(root, "apps/site/dist");
  const errors: string[] = [];
  const read = (path: string) => {
    const file = join(output, path);
    if (!existsSync(file)) {
      errors.push(`Missing generated file: ${path}`);
      return "";
    }
    return readFileSync(file, "utf8");
  };
  const index = read("index.html");
  const sitemap = read("sitemap.xml");
  const agentIndex = read("llms.txt");
  for (const directory of skillDirectories(root)) {
    const name = directory.split("/").at(-1)!;
    const route = `/skills/${name}/`;
    const html = read(`skills/${name}/index.html`);
    const markdown = read(`markdown/skills/${name}.txt`);
    if (!html.includes(`>${name}</h1>`))
      errors.push(`${route}: missing skill heading.`);
    if (!html.includes(`--skill ${name}`))
      errors.push(`${route}: missing installation command.`);
    for (const section of ["overview", "instructions"])
      if (!html.includes(`id="${section}"`))
        errors.push(`${route}: missing ${section}.`);
    if (!index.includes(`href="${route}"`))
      errors.push(`Catalog does not link to ${route}`);
    if (!sitemap.includes(`${route}</loc>`))
      errors.push(`Sitemap does not include ${route}`);
    if (!agentIndex.includes(`${route})`))
      errors.push(`Agent index does not include ${route}`);
    if (!markdown.startsWith(`# ${name}\n`))
      errors.push(`${route}: missing Markdown representation.`);
  }
  return errors;
}
