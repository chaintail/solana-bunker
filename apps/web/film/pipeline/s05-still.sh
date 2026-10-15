#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s05: stills of the slide-5 scene at the given times (comma list) into out/stills/.
export PATH=/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s05/film && mkdir -p ../out/stills && node scripts/capture.mjs s05-hash --still=$1 --out=../out/stills
