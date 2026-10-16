#!/usr/bin/env sh
# Film „ścieżka rekrutera” do README: przeklikanie demo w zwolnionym tempie (Playwright) i konwersja
# nagrania do MP4 (ffmpeg). Wymaga: Python z zależnościami backendu w PATH, node_modules frontendu, ffmpeg.
# Użycie: sh scripts/record_demo_video.sh   → docs/video/sciezka-rekrutera.mp4
set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT/frontend"
rm -rf test-results-demo
PW_SLOWMO="${PW_SLOWMO:-700}" npx playwright test -c playwright.demo.config.ts --project=desktop -g "rekruter"
SRC=$(find test-results-demo -name video.webm | head -1)
mkdir -p "$ROOT/docs/video"
ffmpeg -y -loglevel error -i "$SRC" -vf "scale=1280:-2,fps=24" -c:v libx264 -pix_fmt yuv420p -crf 30 \
  -movflags +faststart "$ROOT/docs/video/sciezka-rekrutera.mp4"
echo "gotowe: docs/video/sciezka-rekrutera.mp4 ($(du -h "$ROOT/docs/video/sciezka-rekrutera.mp4" | cut -f1))"
