#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s06. Stills of s06-signature.html at the given scene times (comma list) -> out/stills/still-<t>.png
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s06
node film/scripts/capture.mjs s06-signature --still="$1" --out=out/stills > out/stills.log 2>&1; tail -1 out/stills.log
