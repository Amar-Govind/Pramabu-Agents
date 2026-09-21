#!/usr/bin/env bash
set -euo pipefail

# Idempotent bootstrap for the Parambu Agents monorepo:
#   1. Python multi-agent CLI (pramabu_agents) in a local virtualenv
#   2. Next.js storefront under storefront/
#
# Safe to run repeatedly and against cached/partially-prepared state.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# --- System dependency: python venv support (missing from the base image) ---
if ! python3 -c "import ensurepip" >/dev/null 2>&1; then
  echo "[install] Installing python3-venv system package..."
  sudo apt-get update -qq
  sudo apt-get install -y -qq python3-venv
fi

# --- Python virtualenv + dependencies ---
if [ ! -x ".venv/bin/python" ]; then
  echo "[install] Creating virtualenv at .venv..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install -e . -q
deactivate

# --- Storefront (Next.js) dependencies ---
cd "$REPO_ROOT/storefront"
if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi

echo "[install] Environment bootstrap complete."
