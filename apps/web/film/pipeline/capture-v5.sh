#!/bin/bash
# Runs ON dev-mac. Revision 5 frame capture into render-v5/ (v2-v4 frames stay untouched). Beat 0c (breaking) is reused from out/seg.
export PATH=/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/film; R=../render-v5; mkdir -p $R
(for s in s00-intro s00b-advisory; do node scripts/capture.mjs $s --out=$R/$s; done; node scripts/capture.mjs s02-news --layer=back --still=0 --out=$R/s02-news-back) > ../out/cap-v5-a.log 2>&1 &
node scripts/capture.mjs s02-news --layer=front --out=$R/s02-news-front > ../out/cap-v5-b.log 2>&1
wait; echo ALLDONE >> ../out/cap-v5-b.log
