#!/usr/bin/env bash
# Scene to MP4 in one command, using every core.
#   bash make.sh <scene.html> <seconds> <music.wav> <out.mp4> [width height]
set -euo pipefail
SCENE="$1"; SECS="$2"; WAV="$3"; OUT="$4"; W="${5:-1080}"; H="${6:-1920}"
cd "$(dirname "$0")"
(python3 -m http.server 8765 >/dev/null 2>&1 &) ; sleep 1
TOTAL=$(python3 -c "print(round($SECS*30))"); P=$(nproc); STEP=$(( (TOTAL + P - 1) / P ))
rm -rf frames
for i in $(seq 0 $((P-1))); do A=$((i*STEP)); B=$(( (i+1)*STEP < TOTAL ? (i+1)*STEP : TOTAL )); node render.js "$SCENE" "$SECS" "$W" "$H" "$A" "$B" frames & done; wait
ffmpeg -y -loglevel error -framerate 30 -i frames/f%05d.jpg -i "$WAV" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT"
echo "written $OUT"
