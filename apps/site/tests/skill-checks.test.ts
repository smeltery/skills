import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { test } from "node:test";
import {
  checkBuiltSkills,
  checkRegistration,
} from "../scripts/skill-checks.ts";

function fixture(t: { after: (callback: () => void) => void }) {
  const root = mkdtempSync(join(tmpdir(), "skill-coverage-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const write = (path: string, text: string) => {
    const file = join(root, path);
    mkdirSync(dirname(file), { recursive: true });
    writeFileSync(file, text);
  };
  write(
    "skills/engineering/example/SKILL.md",
    '---\nname: example\ndescription: Example workflow\nargument-hint: "<task>"\n---\n# Example\n',
  );
  write(
    "skills/engineering/example/README.md",
    "# Example\nUse this workflow.\n",
  );
  write("README.md", "[Example](skills/engineering/example/README.md)");
  write("docs/skills.md", "[Example](../skills/engineering/example/README.md)");
  write("skills/engineering/README.md", "[Example](example/README.md)");
  const built = "apps/site/dist/";
  write(built + "index.html", '<a href="/skills/example/">Example</a>');
  write(
    built + "sitemap.xml",
    "<url><loc>https://example.com/skills/example/</loc></url>",
  );
  write(built + "llms.txt", "[Example](https://example.com/skills/example/)");
  write(
    built + "skills/example/index.html",
    '<h1>example</h1><section id="overview">Overview</section><section id="instructions">Instructions</section> --skill example',
  );
  write(built + "markdown/skills/example.txt", "# example\nInstructions");
  return { root, write, built };
}

test("a registered skill has all generated website surfaces", (t) => {
  const { root } = fixture(t);
  assert.deepEqual(checkRegistration(root, "example"), []);
  assert.deepEqual(checkBuiltSkills(root), []);
});

test("a missing README and catalog links give actionable failures", (t) => {
  const { root, write } = fixture(t);
  rmSync(join(root, "skills/engineering/example/README.md"));
  write("docs/skills.md", "Example is mentioned but not linked.");
  const errors = checkRegistration(root, "example");
  assert.ok(errors.some((error) => error.includes("website overview")));
  assert.ok(errors.some((error) => error.includes("docs/skills.md must link")));
});

test("new skills require complete metadata and unique names", (t) => {
  const { root, write } = fixture(t);
  write(
    "skills/engineering/example/SKILL.md",
    "---\nname: example\ndescription: Example\n---\n",
  );
  assert.ok(
    checkRegistration(root, "example").some((error) =>
      error.includes("argument-hint"),
    ),
  );
  write("skills/productivity/example/SKILL.md", "# Duplicate");
  assert.match(checkRegistration(root, "example")[0], /found 2/);
});

test("build guard catches omitted pages and discovery links", (t) => {
  const { root, write, built } = fixture(t);
  rmSync(join(root, built, "skills/example/index.html"));
  write(built + "index.html", "<h1>Skills</h1>");
  write(built + "sitemap.xml", "<urlset/>");
  write(built + "llms.txt", "# Skills");
  const errors = checkBuiltSkills(root);
  for (const fragment of [
    "Missing generated file",
    "Catalog",
    "Sitemap",
    "Agent index",
  ])
    assert.ok(
      errors.some((error) => error.includes(fragment)),
      fragment,
    );
});

test("build guard discovers new canonical skills independently of the site catalog", (t) => {
  const { root, write } = fixture(t);
  write("skills/engineering/forgotten/SKILL.md", "# Newly added skill");
  assert.ok(
    checkBuiltSkills(root).some((error) =>
      error.includes("skills/forgotten/index.html"),
    ),
  );
});
