#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d ".venv" ]]; then
    python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

pip install -q -r requirements-build.txt

pyinstaller --clean --noconfirm totem.spec

echo ""
echo "Build concluído."
if [[ "$(uname)" == "Darwin" ]]; then
    echo "Executável: dist/FilaflowTotem.app"
else
    echo "Executável: dist/FilaflowTotem/FilaflowTotem"
fi
