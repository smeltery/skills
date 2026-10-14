import { readFile, writeFile } from "node:fs/promises";
import sharp from "sharp";
const root = new URL("../public/", import.meta.url);
const mark = await readFile(new URL("mark.svg", root));
const markUri = `data:image/svg+xml;base64,${mark.toString("base64")}`;
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
<rect width="1200" height="630" fill="#f7f7f2"/>
<path d="M840 0v630M0 514h1200" stroke="#dcded3"/>
<image href="${markUri}" x="64" y="48" width="44" height="46"/>
<text x="123" y="80" font-family="Arial,sans-serif" font-size="27" font-weight="bold" fill="#292b25">smeltery <tspan font-weight="normal" fill="#697062">/ skills</tspan></text>
<text x="64" y="198" font-family="monospace" font-size="13" letter-spacing="3" fill="#526447">A LITTLE STRUCTURE. A LOT BETTER WORK.</text>
<text x="59" y="290" font-family="Arial,sans-serif" font-weight="bold" font-size="76" letter-spacing="-4" fill="#292b25">Good workflows.</text>
<text x="62" y="379" font-family="Georgia,serif" font-style="italic" font-size="82" letter-spacing="-3" fill="#526447">Written down.</text>
<text x="65" y="444" font-family="Arial,sans-serif" font-size="22" fill="#697062">Portable skills for thoughtful builders and their agents.</text>
<rect x="889" y="173" width="262" height="262" rx="36" fill="#e9eddf"/>
<image href="${markUri}" x="930" y="210" width="180" height="187"/>
<text x="65" y="573" font-family="monospace" font-size="19" fill="#292b25">npx skills add smeltery/skills</text>
<text x="1136" y="573" text-anchor="end" font-family="Arial,sans-serif" font-size="17" fill="#526447">Find your next workflow.</text>
</svg>`;
await writeFile(new URL("brand/og.svg", root), svg);
await sharp(Buffer.from(svg))
  .png()
  .toFile(new URL("brand/og.png", root).pathname);
await sharp(mark)
  .resize(180, 180, { fit: "contain", background: "#f7f7f2" })
  .png()
  .toFile(new URL("apple-touch-icon.png", root).pathname);
await sharp(mark)
  .resize(32, 32, {
    fit: "contain",
    background: { r: 0, g: 0, b: 0, alpha: 0 },
  })
  .png()
  .toFile(new URL("favicon.png", root).pathname);
