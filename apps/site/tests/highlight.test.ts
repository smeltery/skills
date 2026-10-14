import { test } from "node:test";
import assert from "node:assert/strict";
import { renderMarkdown } from "../src/lib/markdown.ts";
import { highlightCommand } from "../src/lib/highlight.ts";

test("syntax colors survive sanitization and preserve the code text", () => {
  const html = renderMarkdown(
    "```typescript\nconst answer: number = 42;\n```",
    "skills/engineering/tdd",
  );
  assert.match(html, /class="syntax-label">typescript/);
  assert.match(html, /class="shiki github-light"/);
  assert.ok(new Set(html.match(/color:#[0-9a-f]+/gi)).size >= 3);
  assert.match(html, />const</);
});
test("unknown languages remain escaped plain text", () => {
  const html = renderMarkdown(
    '```custom-format\n<script>alert("test")</script>\n```',
    "skills/engineering/tdd",
  );
  assert.match(html, /&lt;script&gt;/);
  assert.doesNotMatch(html, /<script>/);
});
test("inline shell commands are colored without allowing HTML injection", () => {
  const html = highlightCommand(
    "npx skills@latest add smeltery/skills --skill diagnose",
  );
  assert.match(html, /style="color:#[0-9a-f]+"/i);
  assert.match(html, /npx/);
  assert.doesNotMatch(
    highlightCommand("Use <script>alert(1)</script>"),
    /<script>/,
  );
});
