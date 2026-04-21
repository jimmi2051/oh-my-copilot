#!/usr/bin/env bash
set -euo pipefail

#!/usr/bin/env bash
set -euo pipefail

# Minimal helper to initialize a node adapter folder for optional Node/TS bridge
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ADAPTER_DIR="$REPO_ROOT/bridge"

mkdir -p "$ADAPTER_DIR"
cd "$ADAPTER_DIR"

if [ ! -f package.json ]; then
  cat > package.json <<'JSON'
{
  "name": "omc-copilot-bridge",
  "version": "0.0.0",
  "private": true,
  "type": "module",
  "dependencies": {}
}
JSON
fi

if command -v npm >/dev/null 2>&1; then
  npm init -y >/dev/null 2>&1 || true
fi

cat > bridge-notify.mjs <<'JS'
export async function sendNotify(url, payload) {
  // TODO: implement adapter that mirrors omc-copilot notify format
  console.log('bridge sendNotify placeholder', url, payload);
}
JS

echo "Node adapter scaffolded under bridge/ — implement bridge-notify.mjs to reuse TypeScript logic"