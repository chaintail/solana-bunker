#!/bin/bash
# Runs ON dev-mac from ~/video-work/head-test/film. The bodies are stop-frame (poses hold for 3 s), so only one frame per pose is captured: t = 1.5 (A), 4.5 (B), 7.5 (C).
export PATH=/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/head-test/film; R=../h2/cap
node scripts/capture.mjs s-head-bodies --layer=back --still=1.5,4.5,7.5 --out=$R/back > ../h2/cap-back.log 2>&1 &
node scripts/capture.mjs s-head-bodies --layer=front --still=1.5,4.5,7.5 --out=$R/front > ../h2/cap-front.log 2>&1
wait; tail -1 ../h2/cap-back.log ../h2/cap-front.log
