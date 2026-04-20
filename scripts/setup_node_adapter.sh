#!/usr/bin/env bash
set -euo pipefail

# Minimal setup helper for the Node.js interoperability adapter.
# - verifies node and npm are available
# - creates a package.json in omc_copilot/adapters if missing

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ADAPTER_DIR="$REPO_ROOT/omc_copilot/adapters"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is not installed on PATH. Install Node.js (v16+ recommended): https://nodejs.org/"
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is not installed or not on PATH. Install Node.js which includes npm: https://nodejs.org/"
  exit 1
fi

echo "Node found: $(node --version)"
echo "npm found: $(npm --version)"

mkdir -p "$ADAPTER_DIR"
cd "$ADAPTER_DIR"

if [ ! -f package.json ]; then
  echo "Initializing npm in $ADAPTER_DIR"
  npm init -y >/dev/null
else
  echo "package.json already exists in $ADAPTER_DIR"
fi

cat <<'EOF'
Setup complete.
To add runtime dependencies used by your JS skills, run:
  cd omc_copilot/adapters
  npm install <package>

Run tests with:
  pytest -q
EOF
