#!/bin/bash
# Runs ON dev-mac. Conspiracy v4 frames into render-consp4/: s01 (210), s03 (2044, three parallel ranges), hat layer (45 transparent frames, held by build-conspiracy-v3.sh).
export PATH=/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/film; R=../render-consp4; mkdir -p $R ../out
node scripts/capture.mjs s01-title --out=$R/s01-title > ../out/cap-c4-1.log 2>&1 &
node scripts/capture.mjs s03b-hat --layer=front --from=0 --to=1.5 --out=$R/hat > ../out/cap-c4-hat.log 2>&1 &
node scripts/capture.mjs s03-conspiracy --from=0    --to=23 --out=$R/s03-conspiracy > ../out/cap-c4-2.log 2>&1 &
node scripts/capture.mjs s03-conspiracy --from=23   --to=46 --out=$R/s03-conspiracy > ../out/cap-c4-3.log 2>&1 &
node scripts/capture.mjs s03-conspiracy --from=46   --out=$R/s03-conspiracy > ../out/cap-c4-4.log 2>&1 &
wait; echo ALLDONE > ../out/cap-c4-done.log
