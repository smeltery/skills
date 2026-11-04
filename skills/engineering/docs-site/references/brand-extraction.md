# Brand extraction

Match the application's identity using its own sources. Record where each
value came from in `.docs-site/brand-notes.md`.

## Where to look, in order

1. Design tokens: CSS custom properties, Tailwind `theme`, design-token JSON,
   SCSS variables, or a theme file in a component library.
2. The running UI: open the app or its marketing site in a browser and sample
   computed styles for body text, background, borders, links, focus rings, and
   primary buttons.
3. Assets: `logo.svg`, `favicon.svg`, `apple-touch-icon`, Open Graph images,
   and brand folders. Prefer SVG; trace nothing by hand.
4. Copy: the README first line, `package.json` description, site `<title>` and
   meta description, and CLI `--help` text.

## Map to tokens

| Token                          | Take it from                                                   |
| ------------------------------ | -------------------------------------------------------------- |
| `ink`                          | Body text color                                                |
| `muted`, `subtle`              | Secondary text, captions                                       |
| `paper`                        | Page background                                                |
| `surface`                      | Card or code background, slightly lighter or darker than paper |
| `line`                         | Hairline borders                                               |
| `accent`                       | Focus ring and primary interactive color                       |
| `accent-ink`                   | Accent used as text (active links); darken if contrast fails   |
| `accent-mid`                   | Diagram arrows, icons                                          |
| `accent-soft`                  | Selected nav background, notices                               |
| `accent-line`, `accent-border` | Accent-tinted borders, from light to strong                    |
| `button`, `button-hover`       | Primary button fill                                            |
| `font`                         | The app's body font stack, with system fallbacks               |

When the app has only one brand color, derive the accent family by mixing it
with `paper` (soft around 12%, line around 25%, border around 45%) and darken
it for `accent-ink`.

## Check before the Brand gate

- `ink` on `paper`, `muted` on `paper`, and `accent-ink` on `accent-soft` each
  reach a 4.5:1 contrast ratio.
- The logo reads at 25 pixels and as a favicon.
- The wordmark matches how the app writes its name, including case and any
  trailing punctuation.
- Dark-only apps: quire ships a light theme. Propose a light palette derived from
  the brand, or flag a dark theme as a template change at the gate.
