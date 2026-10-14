import { useEffect, useRef, useState } from "react";
import type { SkillPreview } from "../lib/catalog";
import { iconPaths, taskIcons } from "../lib/icons";
import { filterSkills } from "../lib/filter";

function TaskIcon({ group }: { group: string }) {
  return (
    <svg
      className="icon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      dangerouslySetInnerHTML={{
        __html: iconPaths[taskIcons[group] || "grid"],
      }}
    />
  );
}
const featured = [
  "diagnose",
  "tdd",
  "review",
  "design",
  "zoom-out",
  "workon",
  "simplify",
  "architecture",
  "handoff",
  "verify",
  "wayfinder",
  "unslop",
];
export default function SkillFinder({
  skills,
  groups,
}: {
  skills: SkillPreview[];
  groups: string[];
}) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All skills");
  const [sort, setSort] = useState("recommended");
  const [limit, setLimit] = useState(skills.length);
  const [ready, setReady] = useState(false);
  const input = useRef<HTMLInputElement>(null);
  useEffect(() => {
    const restore = () => {
      const params = new URLSearchParams(window.location.search);
      setQuery(params.get("q") || "");
      const requested = params.get("category") || "All skills";
      setCategory(
        ["All skills", "engineering", "productivity", ...groups].includes(
          requested,
        )
          ? requested
          : "All skills",
      );
      setSort(params.get("sort") === "az" ? "az" : "recommended");
      setLimit(12);
    };
    restore();
    setReady(true);
    window.addEventListener("popstate", restore);
    return () => {
      window.removeEventListener("popstate", restore);
    };
  }, [groups]);
  useEffect(() => {
    if (!ready) return;
    const url = new URL(window.location.href);
    for (const [key, value] of [
      ["q", query],
      ["category", category === "All skills" ? "" : category],
      ["sort", sort === "az" ? sort : ""],
    ]) {
      if (value) url.searchParams.set(key, value);
      else url.searchParams.delete(key);
    }
    window.history.replaceState(null, "", url);
  }, [query, category, sort, ready]);
  const results = filterSkills(skills, query, category).sort((a, b) => {
    if (sort === "az") return a.name.localeCompare(b.name);
    const rank = (name: string) =>
      featured.includes(name) ? featured.indexOf(name) : featured.length;
    return rank(a.name) - rank(b.name) || a.name.localeCompare(b.name);
  });
  const reset = () => {
    setQuery("");
    setCategory("All skills");
    setLimit(12);
    input.current?.focus();
  };
  return (
    <div className="finder">
      <aside className="library-sidebar">
        <p className="eyebrow">Find your workflow</p>
        <div
          className="filter-list"
          role="group"
          aria-label="Filter skills by task"
        >
          {["All skills", ...groups].map((group) => (
            <button
              type="button"
              key={group}
              aria-pressed={category === group}
              disabled={!ready}
              onClick={() => {
                setCategory(group);
                setLimit(12);
              }}
            >
              <span>
                <span className="filter-symbol" aria-hidden="true">
                  <TaskIcon group={group} />
                </span>
                {group}
              </span>
              <span className="filter-count">
                {filterSkills(skills, "", group).length}
              </span>
            </button>
          ))}
        </div>
        <div className="sidebar-note">
          <span className="eyebrow">New to skills?</span>
          <h3>
            Start with one.
            <br />
            Make it your own.
          </h3>
          <p>
            A skill is a set of instructions that helps your agent do a specific
            job well.
          </p>
          <a href="/guides/installation/">How skills work </a>
        </div>
      </aside>
      <div className="library-results">
        <div className="search-box">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="10.5" cy="10.5" r="6.5" />
            <path d="m16 16 4 4" />
          </svg>
          <label className="sr-only" htmlFor="skill-search">
            Search skills
          </label>
          <input
            id="skill-search"
            ref={input}
            type="search"
            placeholder="What do you want to work on?"
            value={query}
            disabled={!ready}
            onChange={(event) => {
              setQuery(event.target.value);
              setLimit(12);
            }}
          />
        </div>
        <div className="results-toolbar">
          <p role="status" aria-live="polite">
            <strong>{results.length}</strong>{" "}
            {results.length === 1 ? "skill" : "skills"}
            {category !== "All skills" && (
              <>
                {" "}
                in <span>{category}</span>
              </>
            )}
            {query && <> matching “{query}”</>}
          </p>
          <label>
            Sort by{" "}
            <select
              value={sort}
              disabled={!ready}
              onChange={(event) => setSort(event.target.value)}
            >
              <option value="recommended">Recommended</option>
              <option value="az">Name: A–Z</option>
            </select>
          </label>
        </div>
        {(query || category !== "All skills") && (
          <button className="clear-filters" type="button" onClick={reset}>
            Clear filters ×
          </button>
        )}
        <div className="skill-grid">
          {results.slice(0, limit).map((skill) => (
            <a
              className="skill-card"
              href={`/skills/${skill.name}/`}
              key={skill.name}
            >
              <div className="card-top">
                <span
                  className={`skill-symbol tone-${groups.indexOf(skill.group)}`}
                  aria-hidden="true"
                >
                  <TaskIcon group={skill.group} />
                </span>
                <span className="card-category">{skill.group}</span>
              </div>
              <h3>{skill.name}</h3>
              <p>{skill.summary}</p>
              <div className="card-bottom">
                <span>{skill.category}</span>
                <span>View skill</span>
              </div>
            </a>
          ))}
        </div>
        {results.length === 0 && (
          <div className="empty-state">
            <span aria-hidden="true">⌕</span>
            <h3>No skills found. A fresh start?</h3>
            <p>
              Try a task like “debug”, “review”, or “handoff”, or clear your
              filters.
            </p>
            <button className="button" type="button" onClick={reset}>
              Show all skills
            </button>
          </div>
        )}
        {results.length > limit && (
          <div className="load-more">
            <p>
              Showing {limit} of {results.length} skills
            </p>
            <button
              className="button secondary"
              type="button"
              onClick={() => setLimit(limit + 12)}
            >
              Show more skills <span aria-hidden="true">↓</span>
            </button>
          </div>
        )}
        <noscript>
          <p>
            All skills are listed below. Use your browser’s Find command to
            search, or open a skill to install it.
          </p>
        </noscript>
      </div>
    </div>
  );
}
