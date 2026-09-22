#!/bin/bash
# Loads the interface in a headless Chromium (Playwright container) and prints console output,
# failed requests, router state and DOM markers. Usage: tools/probe.sh [url]
set -euo pipefail
cd "$(dirname "$0")"
URL="${1:-http://localhost:8100/}"
docker run --rm --network host -v "$PWD:/probe" -w /probe mcr.microsoft.com/playwright:v1.58.0-noble \
  sh -c "npm install --silent --no-audit --no-fund playwright@1.58.0 >/dev/null 2>&1; node probe.mjs $URL"
