import type { APIRoute } from "astro";
import { skills } from "../lib/catalog";
export const GET: APIRoute = ({ site }) =>
  new Response(
    `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${["/", "/guides/installation/", "/guides/approach/", "/brand/", "/about/", "/contact/", "/privacy/", ...skills.map((s) => `/skills/${s.name}/`)].map((path) => `<url><loc>${new URL(path, site)}</loc></url>`).join("")}</urlset>`,
    { headers: { "Content-Type": "application/xml; charset=utf-8" } },
  );
