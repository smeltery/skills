import assert from "node:assert/strict";
import { test } from "node:test";
import middleware from "../../../middleware.ts";

test("ordinary browser requests continue to static HTML", async () => {
  assert.equal(
    await middleware(
      new Request("https://example.com/", { headers: { Accept: "text/html" } }),
    ),
    undefined,
  );
});
test("Markdown requests receive the corresponding generated document", async (t) => {
  t.mock.method(globalThis, "fetch", async (url: URL) => {
    assert.equal(url.pathname, "/markdown/skills/diagnose.txt");
    return new Response("# Diagnose\n\nInvestigate the cause.");
  });
  const response = await middleware(
    new Request("https://example.com/skills/diagnose/", {
      headers: { Accept: "text/markdown" },
    }),
  );
  assert.equal(response?.status, 200);
  assert.equal(response?.headers.get("Vary"), "Accept");
  assert.match(response?.headers.get("Content-Type") || "", /text\/markdown/);
  assert.match(await response!.text(), /^# Diagnose/);
});
test("missing Markdown pages preserve 404 and provide recovery links", async (t) => {
  t.mock.method(
    globalThis,
    "fetch",
    async () => new Response("missing", { status: 404 }),
  );
  const response = await middleware(
    new Request("https://example.com/missing/", {
      headers: { Accept: "text/markdown" },
    }),
  );
  assert.equal(response?.status, 404);
  assert.match(await response!.text(), /\/llms.txt/);
});
test("upstream failures are not disguised as successful documents", async (t) => {
  t.mock.method(
    globalThis,
    "fetch",
    async () => new Response("unavailable", { status: 500 }),
  );
  const response = await middleware(
    new Request("https://example.com/", {
      headers: { Accept: "text/markdown" },
    }),
  );
  assert.equal(response?.status, 503);
});
