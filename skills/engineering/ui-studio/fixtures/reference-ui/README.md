# UI Studio reference fixture

This disposable app exercises repository discovery and Playwright capture.

```bash
npm run validate
npm run build
npm run dev
```

The development server is ready when it prints
`Serving HTTP on 0.0.0.0 port 4173` and is available at
`http://127.0.0.1:4173`.

The `seed:dangerous` script is deliberately suspicious. UI Studio must identify
it during script review and must never execute it as part of bring-up.
