#!/bin/bash
# Runs ON dev-mac. Conspiracy v3 frames into render-consp3/: s01 (210), s03 (2044, three parallel ranges), hat layer (45 transparent frames, held by build-conspiracy-v3.sh).
export PATH=/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/film; R=../render-consp3; mkdir -p $R ../out
node scripts/capture.mjs s01-title --out=$R/s01-title > ../out/cap-c3-1.log 2>&1 &
node scripts/capture.mjs s03b-hat --layer=front --from=0 --to=1.5 --out=$R/hat > ../out/cap-c3-hat.log 2>&1 &
node scripts/capture.mjs s03-conspiracy --from=0    --to=23 --out=$R/s03-conspiracy > ../out/cap-c3-2.log 2>&1 &
node scripts/capture.mjs s03-conspiracy --from=23   --to=46 --out=$R/s03-conspiracy > ../out/cap-c3-3.log 2>&1 &
node scripts/capture.mjs s03-conspiracy --from=46   --out=$R/s03-conspiracy > ../out/cap-c3-4.log 2>&1 &
wait; echo ALLDONE > ../out/cap-c3-done.log
