import type { SkillPreview } from "./catalog.ts";
export function filterSkills(
  skills: SkillPreview[],
  query: string,
  group = "All skills",
): SkillPreview[] {
  const words = query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  return skills.filter((skill) => {
    const searchable =
      `${skill.name.replaceAll("-", " ")} ${skill.name} ${skill.description} ${skill.group} ${skill.category}`.toLowerCase();
    return (
      (group === "All skills" ||
        skill.group === group ||
        skill.category === group) &&
      words.every((word) => searchable.includes(word))
    );
  });
}
