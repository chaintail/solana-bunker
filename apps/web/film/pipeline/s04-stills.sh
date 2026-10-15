#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. usage: s04-stills.sh <t> <t> ...  -> out/s04/stills/still-<t>.png (scene stills, no encode)
export PATH=/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/film; mkdir -p ../out/s04/stills
node scripts/capture.mjs s04-bunker --still=$(IFS=,; echo "$*") --out=../out/s04/stills 2>&1 | tail -3
