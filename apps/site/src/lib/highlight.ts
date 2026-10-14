import { createHighlighter } from "shiki";

// One build-time instance; no highlighter or grammar is sent to the browser.
const highlighter = await createHighlighter({
  themes: ["github-light"],
  langs: [
    "bash",
    "json",
    "markdown",
    "typescript",
    "javascript",
    "tsx",
    "jsx",
    "yaml",
    "html",
    "css",
    "sql",
    "python",
    "diff",
    "mermaid",
  ],
});
const aliases: Record<string, string> = {
  sh: "bash",
  shell: "bash",
  shellscript: "bash",
  console: "bash",
  ts: "typescript",
  js: "javascript",
  md: "markdown",
  yml: "yaml",
  py: "python",
  plaintext: "text",
};
export function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
function languageFor(language: string): string {
  const normalized = aliases[language] ?? language;
  return highlighter.getLoadedLanguages().includes(normalized)
    ? normalized
    : "text";
}
export function highlightCode(code: string, language = "text"): string {
  const requested = language.trim().split(/\s+/)[0].toLowerCase() || "text";
  const html = highlighter.codeToHtml(code, {
    lang: languageFor(requested),
    theme: "github-light",
  });
  // Preserve the Mermaid hook while coloring the source disclosure too.
  if (requested === "mermaid")
    return html.replace("<code>", '<code class="language-mermaid">');
  return `<div class="syntax-block"><div class="syntax-label">${escapeHtml(requested)}</div>${html}</div>`;
}
export function highlightCommand(command: string): string {
  const language = /^(?:npx|npm|pnpm|bun|curl|mkdir|git|cd|python|node)\b/.test(
    command,
  )
    ? "bash"
    : "text";
  const { tokens } = highlighter.codeToTokens(command, {
    lang: language,
    theme: "github-light",
  });
  return tokens
    .map((line) =>
      line
        .map(
          (token) =>
            `<span style="color:${token.color}">${escapeHtml(token.content)}</span>`,
        )
        .join(""),
    )
    .join("\n");
}
