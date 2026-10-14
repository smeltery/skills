import { test } from "node:test";
import assert from "node:assert/strict";
import { searchEntries, type SearchEntry } from "../src/lib/search.ts";
const entries: SearchEntry[] = [
  {
    title: "performance-engineer",
    description: "Measure and diagnose performance.",
    keywords: "engineering debug",
    kind: "skills",
    href: "/skills/performance-engineer/",
  },
  {
    title: "diagnose",
    description: "Debug hard bugs.",
    keywords: "engineering",
    kind: "skills",
    href: "/skills/diagnose/",
  },
  {
    title: "Getting started",
    description: "Install your first skill.",
    keywords: "setup help",
    kind: "guides",
    href: "/guides/installation/",
  },
];
test("global search ranks exact skill names ahead of description matches", () => {
  assert.deepEqual(
    searchEntries(entries, "diagnose").map((entry) => entry.title),
    ["diagnose", "performance-engineer"],
  );
  assert.equal(entries[0].title, "performance-engineer");
});
test("search scope, multiple words, and hyphenated names combine correctly", () => {
  assert.equal(
    searchEntries(entries, "  DEBUG  ENGINEERING ", "skills").length,
    2,
  );
  assert.equal(
    searchEntries(entries, "performance engineer")[0].title,
    "performance-engineer",
  );
  assert.equal(searchEntries(entries, "install", "skills").length, 0);
  assert.equal(
    searchEntries(entries, "setup", "guides")[0].title,
    "Getting started",
  );
  assert.equal(searchEntries(entries, "no-such-result").length, 0);
});
