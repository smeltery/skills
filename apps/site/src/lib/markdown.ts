import { Marked } from "marked";
import { highlightCode } from "./highlight.ts";
import GithubSlugger from "github-slugger";
import sanitizeHtml from "sanitize-html";
import { repository } from "./catalog.ts";

export function renderMarkdown(markdown: string, sourcePath: string): string {
  const slugger = new GithubSlugger();
  const renderer = new Marked({
    renderer: {
      code({ text, lang }) {
        return highlightCode(text, lang);
      },
      heading({ tokens, depth, text }) {
        return `<h${depth} id="${slugger.slug(text)}">${this.parser.parseInline(tokens)}</h${depth}>`;
      },
    },
  });
  const readable = markdown.replaceAll("dotbrains/skills", "smeltery/skills");
  return sanitizeHtml(renderer.parse(readable, { async: false }) as string, {
    allowedTags: [
      ...sanitizeHtml.defaults.allowedTags,
      "img",
      "details",
      "summary",
    ],
    allowedAttributes: {
      ...sanitizeHtml.defaults.allowedAttributes,
      "*": ["id"],
      code: ["class"],
      div: ["class"],
      pre: ["class", "style", "tabindex"],
      span: ["class", "style"],
      img: ["src", "alt"],
    },
    allowedStyles: {
      "*": {
        color: [/^#[0-9a-f]{3,8}$/i],
        "background-color": [/^#[0-9a-f]{3,8}$/i],
        "font-style": [/^italic$/],
        "font-weight": [/^bold$/],
        "text-decoration": [/^underline$/],
      },
    },
    transformTags: {
      a: (_tag, attributes) => {
        const href = attributes.href;
        if (href && !/^(?:[a-z][a-z\d+.-]*:|#|\/\/)/i.test(href)) {
          attributes.href = new URL(
            href,
            `${repository}/blob/main/${sourcePath}/`,
          ).href;
        }
        return { tagName: "a", attribs: attributes };
      },
    },
  });
}
