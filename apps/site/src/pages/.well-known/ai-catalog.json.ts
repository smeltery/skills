import type { APIRoute } from "astro";
import { skills } from "../../lib/catalog";
export const GET: APIRoute = ({ site }) => {
  if (!site) throw new Error("A site URL is required for the agent catalog");
  return new Response(
    JSON.stringify({
      specVersion: "1.0",
      host: { displayName: "Smeltery Skills" },
      entries: skills.map((skill) => ({
        identifier: `urn:air:${site.hostname}:skill:${skill.name}`,
        displayName: skill.name,
        description: skill.summary,
        type: "text/plain",
        url: new URL(`/markdown/skills/${skill.name}.txt`, site).href,
      })),
    }),
    { headers: { "Content-Type": "application/json; charset=utf-8" } },
  );
};
