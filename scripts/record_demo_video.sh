#!/usr/bin/env sh
# Filmy do README z testów przeglądarkowych (Playwright, zwolnione tempo) + konwersja ffmpeg.
# Wymaga: Python z zależnościami backendu w PATH, node_modules frontendu, ffmpeg.
# Użycie:
#   sh scripts/record_demo_video.sh                → docs/video/sciezka-rekrutera.mp4 (ścieżka rekrutera)
#   sh scripts/record_demo_video.sh automatyzacje  → docs/video/automatyzacje.mp4 + docs/screenshots/automatyzacje.gif
# Ten sam test biegnie w CI przy każdym PR (workflow „E2E — ścieżka rekrutera”, wideo w artefaktach),
# więc nagranie zawsze pokazuje aktualny stan — wystarczy je odświeżyć tym skryptem.
set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd)
WHAT="${1:-rekruter}"
case "$WHAT" in
  rekruter) GREP="rekruter"; OUT="sciezka-rekrutera" ;;
  automatyzacje) GREP="ekran Automatyzacje w demo"; OUT="automatyzacje" ;;
  *) echo "nieznane nagranie: $WHAT (rekruter | automatyzacje)"; exit 2 ;;
esac
cd "$ROOT/frontend"
rm -rf test-results-demo
PW_SLOWMO="${PW_SLOWMO:-700}" npx playwright test -c playwright.demo.config.ts --project=desktop -g "$GREP"
SRC=$(find test-results-demo -name video.webm | head -1)
mkdir -p "$ROOT/docs/video"
ffmpeg -y -loglevel error -i "$SRC" -vf "scale=1280:-2,fps=24" -c:v libx264 -pix_fmt yuv420p -crf 30 \
  -movflags +faststart "$ROOT/docs/video/$OUT.mp4"
echo "gotowe: docs/video/$OUT.mp4 ($(du -h "$ROOT/docs/video/$OUT.mp4" | cut -f1))"
if [ "$WHAT" = "automatyzacje" ]; then
  # GIF do README (GitHub odtwarza GIF w treści, MP4 tylko jako link): 960 px, 8 kl./s, wspólna paleta
  ffmpeg -y -loglevel error -i "$SRC" -vf "fps=8,scale=960:-2:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" \
    "$ROOT/docs/screenshots/automatyzacje.gif"
  echo "gotowe: docs/screenshots/automatyzacje.gif ($(du -h "$ROOT/docs/screenshots/automatyzacje.gif" | cut -f1))"
fi
