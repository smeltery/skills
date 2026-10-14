import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync } from "node:fs";
import { skills, previews, installCommand } from "../src/lib/catalog.ts";
import { filterSkills } from "../src/lib/filter.ts";
import { renderMarkdown } from "../src/lib/markdown.ts";

test("every canonical skill has a unique, discoverable catalog entry", () => {
  const sources = readdirSync("../../skills", { recursive: true }).filter(
    (path) => /^[^/]+\/[^/]+\/SKILL\.md$/.test(String(path)),
  );
  assert.equal(skills.length, sources.length);
  assert.equal(new Set(skills.map((skill) => skill.name)).size, sources.length);
  for (const skill of skills) {
    assert.ok(skill.description && skill.summary && skill.content);
    assert.match(skill.name, /^[a-z0-9-]+$/);
  }
});

test("search combines words and categories without changing source order", () => {
  assert.ok(
    filterSkills(previews, " HARD   BUG ", "Build & debug").some(
      (skill) => skill.name === "diagnose",
    ),
  );
  assert.equal(filterSkills(previews, "diagnose", "Git & commits").length, 0);
  assert.equal(filterSkills(previews, "not-a-real-skill-123").length, 0);
  assert.ok(
    filterSkills(previews, "", "productivity").every(
      (skill) => skill.category === "productivity",
    ),
  );
  assert.equal(filterSkills(previews, "").length, skills.length);
});

test("installation and invocation respect special skill modes", () => {
  assert.equal(
    installCommand("diagnose"),
    "npx skills@latest add smeltery/skills --skill diagnose",
  );
  assert.equal(
    skills.find((skill) => skill.name === "teach")?.invocation,
    "User only",
  );
  assert.equal(
    skills.find((skill) => skill.name === "workon-event")?.invocation,
    "Agent only",
  );
  assert.equal(
    skills.find((skill) => skill.name === "diagnose")?.invocation,
    "You or your agent",
  );
});

test("rendered repository Markdown keeps safe links and removes executable HTML", () => {
  const html = renderMarkdown(
    '[source](./SKILL.md)\n\n<script>alert(1)</script><img src=x onerror="alert(1)">\n\n[bad](javascript:alert(1))',
    "skills/engineering/diagnose",
  );
  assert.match(
    html,
    /https:\/\/github.com\/smeltery\/skills\/blob\/main\/skills\/engineering\/diagnose\/SKILL.md/,
  );
  assert.doesNotMatch(html, /<script|onerror|javascript:/);
});

test("workflow diagram source remains escaped and available to the renderer", () => {
  const html = renderMarkdown(
    "```mermaid\nflowchart LR\n A --> B\n```",
    "skills/engineering/diagnose",
  );
  assert.match(html, /class="language-mermaid"/);
  assert.match(html, /flowchart/);
  assert.match(html, /--&gt;/);
  assert.match(html, /style="color:#[0-9a-f]+"/i);
});

test("Markdown heading anchors remain usable", () => {
  const html = renderMarkdown(
    "## Standup log schema\n\n[Jump](#standup-log-schema)",
    "skills/productivity/track-my-work",
  );
  assert.match(html, /id="standup-log-schema"/);
  assert.match(html, /href="#standup-log-schema"/);
});
