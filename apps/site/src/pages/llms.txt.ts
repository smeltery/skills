import type { APIRoute } from "astro";
import { skills, installCommand } from "../lib/catalog";
export const GET: APIRoute = ({ site }) =>
  new Response(
    `# Smeltery Skills\n\n> Portable workflows for coding agents. Read a skill, install it, and apply its instructions to your task.\n\nInstall: ${installCommand()}\n\nThis is a public documentation library, not a hosted agent service. No account, payment, API key, or MCP connection is required. The source is licensed under PolyForm Shield; see https://github.com/smeltery/skills/blob/main/LICENSE for terms.\n\n## When to use\nUse diagnose for investigating bugs, tdd for test-first implementation, design for planning, review for reviewing changes, and handoff for transferring work. Read the chosen skill before invoking it. Do not use this site as a hosted execution service.\n\n## Guides\n- [Installation](${new URL("/guides/installation/", site)}): Install and invoke skills.\n- [Approach](${new URL("/guides/approach/", site)}): Why these workflows exist.\n- [Full text](${new URL("/llms-full.txt", site)}): All skill instructions in one document.\n- [Brand](${new URL("/brand/", site)}): Brand assets and usage.\n\n## Skills\n${skills.map((s) => `- [${s.name}](${new URL(`/skills/${s.name}/`, site)}): ${s.summary}`).join("\n")}\n`,
    { headers: { "Content-Type": "text/plain; charset=utf-8" } },
  );
