import type { APIRoute } from "astro";
import { skills, installCommand } from "../lib/catalog";
export const GET: APIRoute = () =>
  new Response(
    `# Smeltery Skills\n\nSource: https://github.com/smeltery/skills\nLicense: PolyForm Shield 1.0.0\nInstall: ${installCommand()}\n\n${skills.map((s) => `# ${s.name}\n\n${s.description}\n\nInstall: ${installCommand(s.name)}\n\n${s.content}`).join("\n\n---\n\n")}`,
    { headers: { "Content-Type": "text/plain; charset=utf-8" } },
  );
