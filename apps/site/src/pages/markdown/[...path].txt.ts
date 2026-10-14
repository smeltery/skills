import type { APIRoute } from "astro";
import { skills, installCommand } from "../../lib/catalog";
import { informationPages } from "../../lib/information";
export function getStaticPaths() {
  return [
    {
      params: { path: "index" },
      props: {
        content: `# Smeltery Skills\n\nPortable workflows for coding agents.\n\nInstall: \`${installCommand()}\`\n\n## When to use\nUse diagnose to investigate bugs, tdd to implement test-first, review to assess changes, and design to plan a feature. Read the skill instructions before applying them.\n\n## Skills\n${skills.map((s) => `- [${s.name}](/skills/${s.name}/): ${s.summary}`).join("\n")}\n\n[Installation](/guides/installation/) · [Agent guide](/llms.txt) · [Brand assets](/brand/)`,
      },
    },
    ...skills.map((s) => ({
      params: { path: `skills/${s.name}` },
      props: {
        content: `# ${s.name}\n\n${s.description}\n\nInstall: \`${installCommand(s.name)}\`\n\n${s.content}`,
      },
    })),
    ...Object.entries(informationPages).map(([path, page]) => ({
      params: { path },
      props: {
        content: `# ${page.title}\n\n${page.paragraphs.join("\n\n")}\n\n[Skill library](/) · [Agent guide](/llms.txt)`,
      },
    })),
    {
      params: { path: "guides/installation" },
      props: {
        content: `# Install Smeltery Skills\n\nRun \`${installCommand()}\` in your terminal, choose your skills and supported agent, then follow the installer prompts. Install one skill with \`${installCommand("diagnose")}\`. Read its SKILL.md instructions and invoke it through your agent's skill interface.\n\n[All skill instructions](/llms-full.txt) · [Source installation guide](https://github.com/smeltery/skills/blob/main/docs/installation.md)`,
      },
    },
    {
      params: { path: "guides/approach" },
      props: {
        content:
          "# Our approach\n\nSmeltery skills encode reusable workflows for planning, debugging, reviewing, and communicating. Each workflow provides structure while leaving the agent room to reason. Install only what your task needs.\n\n[Full motivation](https://github.com/smeltery/skills/blob/main/docs/motivation.md) · [Skill library](/)",
      },
    },
    {
      params: { path: "brand" },
      props: {
        content:
          "# Smeltery brand & assets\n\nUse Smeltery in prose and smeltery / skills in the lockup. Preserve the pixel plant proportions and colors.\n\nPalette: Paper #f7f7f2, Charcoal #292b25, Sage #526447, Soft sage #e9eddf, White #ffffff.\nTypography: DM Sans, Georgia, IBM Plex Mono.\n\n[SVG mark](/mark.svg) · [OG image, 1200×630 PNG](/brand/og.png) · [Editable OG SVG](/brand/og.svg) · [Favicon](/favicon.png) · [Apple touch icon](/apple-touch-icon.png)",
      },
    },
  ];
}
export const GET: APIRoute = ({ props }) =>
  new Response(props.content, {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
