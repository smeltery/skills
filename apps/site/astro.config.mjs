import { defineConfig } from "astro/config";
import react from "@astrojs/react";

export default defineConfig({
  site: process.env.SITE_URL || "https://smeltery-skills.vercel.app",
  output: "static",
  trailingSlash: "always",
  integrations: [
    react(),
    {
      name: "isolated-development-cache",
      hooks: {
        "astro:config:setup": ({ command, updateConfig }) => {
          // Builds must not invalidate lazy Mermaid modules in an open preview.
          updateConfig({ vite: { cacheDir: `node_modules/.vite-${command}` } });
        },
      },
    },
  ],
  devToolbar: { enabled: false },
});
