# UI Studio portability fixture

This workspace production-builds one framework-neutral public kit from React,
Vue, Svelte, and native web-component consumers. Versions are pinned solely to
make UI Studio's own dogfood reproducible; they are not defaults for generated
kits, which must use the destination repository's discovered stack.

Run through `../../scripts/dogfood-portability.sh`. The runner copies this
workspace to a disposable directory, uses the committed lockfile with `npm ci`,
verifies every production output, and deletes installed dependencies afterward.

When intentionally updating fixture dependencies, verify current stable releases
from their official registries, regenerate the lockfile, run all four builds,
and keep the public kit imports unchanged so the test continues to measure
portability rather than framework-specific source access.
