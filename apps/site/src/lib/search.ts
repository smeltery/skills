export interface SearchEntry {
  title: string;
  description: string;
  keywords: string;
  kind: "skills" | "guides";
  href: string;
}
export function searchEntries(
  entries: SearchEntry[],
  query: string,
  scope = "all",
): SearchEntry[] {
  const normalized = query.trim().toLowerCase();
  const words = normalized.split(/\s+/).filter(Boolean);
  const score = (entry: SearchEntry) =>
    entry.title.toLowerCase() === normalized
      ? 0
      : entry.title.toLowerCase().startsWith(normalized)
        ? 1
        : 2;
  return entries
    .filter((entry) => {
      const text =
        `${entry.title} ${entry.title.replaceAll("-", " ")} ${entry.description} ${entry.keywords}`.toLowerCase();
      return (
        (scope === "all" || entry.kind === scope) &&
        words.every((word) => text.includes(word))
      );
    })
    .sort((a, b) => score(a) - score(b));
}
