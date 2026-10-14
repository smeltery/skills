import { openOverlay, closeOverlay, registerOverlay } from "./overlays";
import { searchEntries, type SearchEntry } from "../lib/search";

const search = document.querySelector<HTMLDialogElement>("#site-search")!;
const menu = document.querySelector<HTMLDialogElement>("#mobile-menu")!;
const input = search.querySelector<HTMLInputElement>("#global-search")!;
const resultList = search.querySelector<HTMLElement>("#search-results")!;
const links = [
  ...resultList.querySelectorAll<HTMLAnchorElement>("[data-search-entry]"),
];
const entries = links.map(
  (link) => JSON.parse(link.dataset.searchEntry!) as SearchEntry,
);
const linksByHref = new Map(
  links.map((link, index) => [entries[index].href, link]),
);
const menuToggle = document.querySelector<HTMLButtonElement>(".menu-toggle")!;
const scopes = [
  ...search.querySelectorAll<HTMLButtonElement>("[data-search-scope]"),
];
const clear = search.querySelector<HTMLButtonElement>("[data-clear-search]")!;
const status = search.querySelector<HTMLElement>("[data-search-status]")!;
const heading = search.querySelector<HTMLElement>("#search-section-title")!;
let scope = "all";
let visible: HTMLAnchorElement[] = [];

function filter() {
  const matched = searchEntries(entries, input.value, scope);
  const suggested = !input.value.trim() && scope === "all";
  const shown = suggested ? matched.slice(0, 9) : matched;
  visible = shown.map((entry) => linksByHref.get(entry.href)!);
  links.forEach((link) => {
    link.hidden = !visible.includes(link);
  });
  visible.forEach((link) => resultList.append(link));
  scopes.forEach((button) =>
    button.setAttribute(
      "aria-pressed",
      String(button.dataset.searchScope === scope),
    ),
  );
  clear.hidden = !input.value;
  search.querySelector<HTMLElement>(".search-no-results")!.hidden =
    shown.length > 0;
  heading.hidden = shown.length === 0;
  heading.textContent = suggested
    ? "Good places to start"
    : input.value.trim()
      ? "Search results"
      : `All ${scope}`;
  status.textContent = suggested
    ? "Skills and guides, one search away."
    : `${matched.length} ${matched.length === 1 ? "result" : "results"}`;
  search.querySelector(".search-results-scroll")!.scrollTop = 0;
}
function showSearch(trigger: HTMLElement | null) {
  scope = "all";
  input.value = "";
  filter();
  openOverlay(search, trigger);
  input.focus();
}
registerOverlay(search);
registerOverlay(menu);
document
  .querySelectorAll<HTMLButtonElement>("[data-open-search]")
  .forEach((button) => {
    button.hidden = false;
    button.addEventListener("click", () => showSearch(button));
  });
document.querySelectorAll("[data-search-shortcut]").forEach((label) => {
  label.textContent = /Mac|iPhone|iPad/.test(navigator.userAgent)
    ? "⌘ K"
    : "Ctrl K";
});
menuToggle.hidden = false;
menuToggle.addEventListener("click", () => {
  openOverlay(menu, menuToggle);
  menuToggle.setAttribute("aria-expanded", "true");
});
menu.addEventListener("close", () =>
  menuToggle.setAttribute("aria-expanded", "false"),
);
menu
  .querySelectorAll("a")
  .forEach((link) => link.addEventListener("click", () => closeOverlay(menu)));
matchMedia("(min-width: 781px)").addEventListener("change", (event) => {
  if (event.matches && menu.open) closeOverlay(menu);
});
document.addEventListener("keydown", (event) => {
  if (
    (event.metaKey || event.ctrlKey) &&
    event.key.toLowerCase() === "k" &&
    !event.isComposing
  ) {
    event.preventDefault();
    if (search.open) closeOverlay(search);
    else showSearch(document.activeElement as HTMLElement);
  }
});
input.addEventListener("input", filter);
const reset = () => {
  input.value = "";
  scope = "all";
  filter();
  input.focus();
};
clear.addEventListener("click", () => {
  input.value = "";
  filter();
  input.focus();
});
search.querySelector("[data-reset-search]")!.addEventListener("click", reset);
scopes.forEach((button) =>
  button.addEventListener("click", () => {
    scope = button.dataset.searchScope!;
    filter();
    input.focus();
  }),
);
links.forEach((link) =>
  link.addEventListener("click", () => closeOverlay(search)),
);
search.addEventListener("keydown", (event) => {
  if (event.isComposing || event.altKey || event.ctrlKey || event.metaKey)
    return;
  if (event.key === "Enter" && event.target === input) {
    event.preventDefault();
    visible[0]?.click();
  }
  if (!["ArrowDown", "ArrowUp"].includes(event.key) || !visible.length) return;
  if (
    event.target !== input &&
    !visible.includes(document.activeElement as HTMLAnchorElement)
  )
    return;
  event.preventDefault();
  const index = visible.indexOf(document.activeElement as HTMLAnchorElement);
  const next =
    index < 0
      ? event.key === "ArrowDown"
        ? 0
        : visible.length - 1
      : (index + (event.key === "ArrowDown" ? 1 : -1) + visible.length) %
        visible.length;
  visible[next].focus({ preventScroll: true });
  visible[next].scrollIntoView({ block: "nearest", behavior: "instant" });
});
