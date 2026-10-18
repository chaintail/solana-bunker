#!/bin/bash
# Runs ON dev-mac. Captures the 1673 frames of s04-bunker into render-s04/ in four parallel ranges.
export PATH=/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/film; R=../render-s04; mkdir -p $R ../out/s04
node scripts/capture.mjs s04-bunker --from=0    --to=14   --out=$R > ../out/s04/cap-1.log 2>&1 &
node scripts/capture.mjs s04-bunker --from=14   --to=28   --out=$R > ../out/s04/cap-2.log 2>&1 &
node scripts/capture.mjs s04-bunker --from=28   --to=42   --out=$R > ../out/s04/cap-3.log 2>&1 &
node scripts/capture.mjs s04-bunker --from=42             --out=$R > ../out/s04/cap-4.log 2>&1 &
wait; echo ALLDONE > ../out/s04/cap-done.log
