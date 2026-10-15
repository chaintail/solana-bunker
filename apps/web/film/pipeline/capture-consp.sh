#!/bin/bash
# Runs ON dev-mac. Captures conspiracy frames into render-consp/ (s01: 210 frames; s03: 2044 frames in four parallel ranges).
export PATH=/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/film; R=../render-consp; mkdir -p $R ../out
node scripts/capture.mjs s01-title --out=$R/s01-title > ../out/cap-consp-1.log 2>&1 &
node scripts/capture.mjs s03-conspiracy --from=0    --to=17.1 --out=$R/s03-conspiracy > ../out/cap-consp-2.log 2>&1 &
node scripts/capture.mjs s03-conspiracy --from=17.1 --to=34.2 --out=$R/s03-conspiracy > ../out/cap-consp-3.log 2>&1 &
node scripts/capture.mjs s03-conspiracy --from=34.2 --to=51.2 --out=$R/s03-conspiracy > ../out/cap-consp-4.log 2>&1 &
node scripts/capture.mjs s03-conspiracy --from=51.2 --out=$R/s03-conspiracy > ../out/cap-consp-5.log 2>&1 &
wait; echo ALLDONE > ../out/cap-consp-done.log
