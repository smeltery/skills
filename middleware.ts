export const config = { matcher: "/(.*)" };
export default async function middleware(request: Request) {
  const accept = request.headers.get("accept") || "";
  if (!accept.includes("text/markdown")) return;
  const url = new URL(request.url);
  if (/\.[a-z0-9]+$/i.test(url.pathname)) return;
  const path = url.pathname.replace(/\/$/, "") || "/index";
  const source = new URL(`/markdown${path}.txt`, url);
  const response = await fetch(source, { headers: { Accept: "text/plain" } });
  const headers = {
    "Content-Type": "text/markdown; charset=utf-8",
    Vary: "Accept",
  };
  if (response.status === 404)
    return new Response(
      "# Page not found\n\nThis page does not exist. Browse [the skill library](/), read [the agent guide](/llms.txt), or use [the sitemap](/sitemap.xml) to find a workflow.\n",
      { status: 404, headers },
    );
  if (!response.ok)
    return new Response(
      "# Content temporarily unavailable\n\nPlease retry or browse [the skill library](/).\n",
      { status: 503, headers },
    );
  return new Response(await response.text(), { headers });
}
