#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FIXTURE="$SKILL_DIR/fixtures/portability"
WORK_DIR="$(mktemp -d /tmp/ui-studio-portability.XXXXXX)"

cleanup() {
  case "$WORK_DIR" in
    /tmp/ui-studio-portability.*)
      find "$WORK_DIR" -depth -delete 2>/dev/null || true
      ;;
    *) echo "Refusing to clean unexpected path: $WORK_DIR" >&2 ;;
  esac
}
trap cleanup EXIT INT TERM

python3 "$SKILL_DIR/scripts/check-portability.py"
cp -R "$FIXTURE/." "$WORK_DIR/"
cd "$WORK_DIR"
npm ci --ignore-scripts --no-audit --no-fund
npm run build

for consumer in react vue svelte web-components; do
  if [ ! -f "$WORK_DIR/$consumer/dist/index.html" ]; then
    echo "Missing production build for $consumer" >&2
    exit 1
  fi
done

echo "UI Studio framework portability dogfood passed."
