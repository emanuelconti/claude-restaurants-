#!/usr/bin/env bash
# One command, nothing to install by hand: puts three.js in a cache folder,
# checks ffmpeg, Python numpy and Playwright, and installs what is missing.
# Usage: bash social-cloud-backup/videokit3d/setup.sh [/tmp/vk3]
set -euo pipefail
CACHE="${1:-/tmp/vk3}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$CACHE"
cp "$HERE"/*.js "$HERE"/*.sh "$HERE"/examples/* "$CACHE"/ 2>/dev/null || true
cd "$CACHE"
[ -f package.json ] || npm init -y >/dev/null
[ -d node_modules/three ] || npm i --silent three@0.170.0
if ! node -e "require('playwright')" 2>/dev/null; then
  if [ -d "$(npm root -g)/playwright" ]; then ln -sfn "$(npm root -g)/playwright" node_modules/playwright; else npm i --silent playwright@1.48.2 && npx playwright install chromium; fi
fi
command -v ffmpeg >/dev/null || (apt-get install -y ffmpeg >/dev/null 2>&1 || pip install -q imageio-ffmpeg)
python3 -c "import numpy" 2>/dev/null || pip install -q numpy
mkdir -p assets
echo "videokit3d ready in $CACHE"
