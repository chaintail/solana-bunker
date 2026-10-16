#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s11. Stills of s11-cnn.html at the given scene times (comma list) -> out/stills/still-<t>.png (1280x720)
# and out/stills/s-<t>.png (426x240). No grade.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s11; mkdir -p out/stills
for i in 1 2 3; do node film/scripts/capture.mjs s11-cnn --settle=4 --still="$1" --out=out/stills > out/stills.log 2>&1 && break; done; tail -1 out/stills.log
for t in ${1//,/ }; do ffmpeg -nostdin -v error -y -i out/stills/still-$t.png -vf scale=426:240:flags=bicubic -frames:v 1 out/stills/s-$t.png; done
