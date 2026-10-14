import { openOverlay, closeOverlay } from "./overlays";
import "../styles/diagrams.css";

const blocks = [
  ...document.querySelectorAll<HTMLElement>("pre > code.language-mermaid"),
];
let mermaidPromise: Promise<(typeof import("mermaid"))["default"]> | undefined;
let sequence = 0;
function getMermaid() {
  mermaidPromise ??= import("mermaid").then(async ({ default: mermaid }) => {
    await document.fonts.ready;
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "strict",
      suppressErrorRendering: true,
      theme: "base",
      fontFamily: "DM Sans Variable, sans-serif",
      themeVariables: {
        primaryColor: "#eceee5",
        primaryTextColor: "#292b25",
        primaryBorderColor: "#9aaa8a",
        lineColor: "#69785d",
        secondaryColor: "#f7f7f2",
        tertiaryColor: "#ffffff",
        background: "#fff",
        fontSize: "14px",
      },
      flowchart: { htmlLabels: false, useMaxWidth: true },
    });
    return mermaid;
  });
  return mermaidPromise;
}
const viewer = document.createElement("dialog");
viewer.className = "diagram-dialog";
viewer.setAttribute("aria-labelledby", "diagram-dialog-title");
viewer.innerHTML =
  '<div class="diagram-dialog-heading"><div><p class="eyebrow">Take a closer look</p><h2 id="diagram-dialog-title">Workflow diagram</h2></div><button class="close-overlay" type="button" data-close-overlay aria-label="Close diagram">×</button></div><div class="diagram-viewer-controls"><button type="button" data-zoom="out" aria-label="Zoom out">−</button><output aria-live="polite">100%</output><button type="button" data-zoom="in" aria-label="Zoom in">+</button><button type="button" data-zoom="fit">Fit to view</button></div><div class="diagram-expanded" tabindex="0" role="region" aria-label="Expanded diagram, scroll to explore"></div><p class="diagram-viewer-hint">Scroll to explore the diagram. Press Escape to return.</p>';
if (blocks.length) document.body.append(viewer);
const expanded = viewer.querySelector<HTMLElement>(".diagram-expanded")!;
let originalContainer: HTMLElement | null = null;
let zoom = 1;
function setZoom(next: number) {
  zoom = Math.min(3, Math.max(0.5, next));
  const svg = expanded.querySelector("svg");
  if (svg) {
    svg.style.width = `${zoom * 100}%`;
    svg.style.maxWidth = "none";
  }
  viewer.querySelector("output")!.textContent = `${Math.round(zoom * 100)}%`;
}
viewer.querySelectorAll<HTMLButtonElement>("[data-zoom]").forEach((button) => {
  button.addEventListener("click", () =>
    setZoom(
      button.dataset.zoom === "fit"
        ? 1
        : zoom + (button.dataset.zoom === "in" ? 0.25 : -0.25),
    ),
  );
});
viewer.addEventListener("close", () => {
  if (viewer.open) return;
  const svg = expanded.querySelector("svg");
  if (svg && originalContainer) {
    svg.style.width = "100%";
    svg.style.maxWidth = `${svg.viewBox.baseVal.width}px`;
    originalContainer.append(svg);
  }
  originalContainer = null;
});

async function renderBlock(code: HTMLElement) {
  const pre = code.parentElement!;
  const source = code.textContent || "";
  const figure = document.createElement("figure");
  figure.className = "workflow-diagram";
  figure.setAttribute("aria-busy", "true");
  const toolbar = document.createElement("figcaption");
  toolbar.className = "diagram-toolbar";
  toolbar.innerHTML =
    '<span>Workflow diagram</span><button type="button" hidden>Expand diagram</button>';
  const status = document.createElement("p");
  status.className = "diagram-status";
  status.setAttribute("role", "status");
  status.textContent = "Drawing the workflow…";
  const canvas = document.createElement("div");
  canvas.className = "diagram-canvas";
  canvas.tabIndex = 0;
  canvas.setAttribute("role", "region");
  canvas.setAttribute("aria-label", "Workflow diagram");
  const details = document.createElement("details");
  const summary = document.createElement("summary");
  summary.textContent = "Diagram source";
  pre.replaceWith(figure);
  details.append(summary, pre);
  figure.append(toolbar, status, canvas, details);
  try {
    const mermaid = await getMermaid();
    const id = `workflow-${++sequence}`;
    const { svg } = await mermaid.render(id, source);
    canvas.innerHTML = svg;
    const rendered = canvas.querySelector("svg")!;
    rendered.setAttribute("role", "img");
    rendered.setAttribute(
      "aria-label",
      "Skill workflow diagram. The source is available below.",
    );
    status.remove();
    const expand = toolbar.querySelector("button")!;
    expand.hidden = false;
    expand.addEventListener("click", () => {
      originalContainer = canvas;
      expanded.append(rendered);
      openOverlay(viewer, expand);
      const naturalWidth = rendered.viewBox.baseVal.width;
      const availableWidth = Math.max(1, expanded.clientWidth - 48);
      setZoom(Math.max(1, Math.ceil((naturalWidth / availableWidth) * 4) / 4));
    });
    figure.dataset.rendered = "true";
  } catch (error) {
    status.textContent =
      "This diagram could not be drawn. Its source is available below.";
    details.open = true;
    canvas.remove();
    figure.dataset.rendered = "error";
    console.error("Unable to render workflow diagram", error);
  } finally {
    figure.setAttribute("aria-busy", "false");
  }
}
// Render only when visible, including diagrams inside collapsed instructions.
const observer = new IntersectionObserver(
  (entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      observer.unobserve(entry.target);
      void renderBlock(entry.target as HTMLElement);
    }
  },
  { rootMargin: "250px" },
);
blocks.forEach((code) => observer.observe(code));
window.addEventListener("pagehide", () => {
  if (viewer.open) closeOverlay(viewer);
});
