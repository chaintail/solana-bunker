#!/bin/bash
# Runs ON dev-mac. Revision 4 frame capture into render-v4/ (the v2/v3 frames in render/ stay untouched).
export PATH=/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/film; R=../render-v4; mkdir -p $R
(for s in s00-intro s00b-advisory; do node scripts/capture.mjs $s --out=$R/$s; done; node scripts/capture.mjs s02-news --layer=back --still=0 --out=$R/s02-news-back) > ../out/cap-v4-a.log 2>&1 &
node scripts/capture.mjs s02-news --layer=front --out=$R/s02-news-front > ../out/cap-v4-b.log 2>&1
wait; echo ALLDONE >> ../out/cap-v4-b.log
