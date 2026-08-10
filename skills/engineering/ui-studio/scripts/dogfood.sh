#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FIXTURE="$SKILL_DIR/fixtures/reference-ui"
DOGFOOD="$SKILL_DIR/fixtures/dogfood"
WORK_DIR="$(mktemp -d /tmp/ui-studio-dogfood.XXXXXX)"
SERVER_PID=""

cleanup() {
  if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  case "$WORK_DIR" in
    /tmp/ui-studio-dogfood.*) find "$WORK_DIR" -depth -delete 2>/dev/null || true ;;
    *) echo "Refusing to clean unexpected path: $WORK_DIR" >&2 ;;
  esac
}
trap cleanup EXIT INT TERM

python3 "$SKILL_DIR/scripts/validate-kit.py" --check-files "$FIXTURE"
python3 "$SKILL_DIR/scripts/doctor.py" --root "$FIXTURE" --json >"$WORK_DIR/doctor.json"
python3 - "$WORK_DIR/doctor.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert any(
    item["name"] == "UI Studio Fixture" and item["schemaValid"]
    for item in report["kits"]
)
assert any("dev" in item["uiScripts"] for item in report["packages"])
PY

cp -R "$FIXTURE/." "$WORK_DIR/"
cp "$DOGFOOD/playwright.config.ts" "$WORK_DIR/playwright.config.ts"
mkdir -p "$WORK_DIR/tests"
cp "$DOGFOOD/ui-studio.spec.ts" "$WORK_DIR/tests/ui-studio.spec.ts"
cd "$WORK_DIR"

npm run validate
npm run build

PLAYWRIGHT_VERSION="${UI_STUDIO_PLAYWRIGHT_VERSION:-}"
if [ -z "$PLAYWRIGHT_VERSION" ]; then
  PLAYWRIGHT_VERSION="$(npx --yes playwright --version | awk '{print $2}')"
fi
npm install --no-save --ignore-scripts "@playwright/test@$PLAYWRIGHT_VERSION"

if [ "${UI_STUDIO_SKIP_BROWSER_INSTALL:-0}" != "1" ]; then
  npx playwright install chromium
fi

git init -q
git config user.name "UI Studio Dogfood"
git config user.email "dogfood@example.invalid"
git add .
git commit -qm "fixture baseline"

npm run dev >server.log 2>&1 &
SERVER_PID="$!"
ready=0
for _ in $(seq 1 80); do
  if python3 - <<'PY' >/dev/null 2>&1
from urllib.request import urlopen
with urlopen("http://127.0.0.1:4173", timeout=0.25) as response:
    assert response.status == 200
PY
  then
    ready=1
    break
  fi
  sleep 0.25
done
if [ "$ready" != "1" ]; then
  echo "Reference fixture did not become ready." >&2
  sed -n '1,120p' server.log >&2
  exit 1
fi

if ! npx playwright test --workers=1 --trace=on; then
  echo "Playwright dogfood failed. If host libraries are missing, run the" >&2
  echo "reported 'playwright install-deps chromium' command only in an" >&2
  echo "authorized environment." >&2
  exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
  echo "Dogfood changed tracked fixture files:" >&2
  git status --short >&2
  exit 1
fi

echo "UI Studio dogfood passed; temporary artifacts will be removed."
