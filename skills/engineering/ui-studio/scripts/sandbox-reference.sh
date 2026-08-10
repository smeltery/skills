#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: sandbox-reference.sh --repo PATH --image IMAGE [options] -- COMMAND...

Options:
  --runtime docker|podman  Select an installed container runtime.
  --network MODE           Container network mode; defaults to none.
  --allow-network          Required when network mode is not none.

The image must already exist locally. The repository is mounted read-only,
copied inside a disposable writable mount, and never executed from the host
worktree.
EOF
}

REPO=""
IMAGE=""
RUNTIME=""
NETWORK_MODE="none"
ALLOW_NETWORK="0"
COMMAND=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo) REPO="${2:-}"; shift 2 ;;
    --image) IMAGE="${2:-}"; shift 2 ;;
    --runtime) RUNTIME="${2:-}"; shift 2 ;;
    --network) NETWORK_MODE="${2:-}"; shift 2 ;;
    --allow-network) ALLOW_NETWORK="1"; shift ;;
    --help|-h) usage; exit 0 ;;
    --) shift; COMMAND=("$@"); break ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$REPO" ] || [ -z "$IMAGE" ] || [ "${#COMMAND[@]}" -eq 0 ]; then
  usage >&2
  exit 2
fi
if [ "$NETWORK_MODE" != "none" ] && [ "$ALLOW_NETWORK" != "1" ]; then
  echo "Non-isolated networking requires --allow-network." >&2
  exit 2
fi
if [ ! -d "$REPO" ]; then
  echo "Repository directory does not exist: $REPO" >&2
  exit 2
fi
REPO_PATH="$(cd "$REPO" && pwd -P)"

if [ -z "$RUNTIME" ]; then
  if command -v podman >/dev/null 2>&1; then
    RUNTIME="podman"
  elif command -v docker >/dev/null 2>&1; then
    RUNTIME="docker"
  else
    echo "No podman or docker runtime found." >&2
    exit 1
  fi
fi
case "$RUNTIME" in
  docker|podman) ;;
  *) echo "Unsupported runtime: $RUNTIME" >&2; exit 2 ;;
esac
if ! command -v "$RUNTIME" >/dev/null 2>&1; then
  echo "Container runtime is unavailable: $RUNTIME" >&2
  exit 1
fi
if ! "$RUNTIME" image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "Image is not available locally: $IMAGE" >&2
  echo "Review and pull it separately before retrying." >&2
  exit 1
fi

WORK_DIR="$(mktemp -d /tmp/ui-studio-reference.XXXXXX)"
cleanup() {
  case "$WORK_DIR" in
    /tmp/ui-studio-reference.*)
      find "$WORK_DIR" -depth -delete 2>/dev/null || true
      ;;
    *) echo "Refusing to clean unexpected path: $WORK_DIR" >&2 ;;
  esac
}
trap cleanup EXIT INT TERM

"$RUNTIME" run --rm \
  --read-only \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --network "$NETWORK_MODE" \
  --tmpfs /tmp:rw,nosuid,nodev \
  --volume "$REPO_PATH:/reference:ro" \
  --volume "$WORK_DIR:/work:rw" \
  --workdir /work \
  "$IMAGE" \
  sh -c 'cp -R /reference/. /work/reference && cd /work/reference && exec "$@"' \
  ui-studio-sandbox "${COMMAND[@]}"
