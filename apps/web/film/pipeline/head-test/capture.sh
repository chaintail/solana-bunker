#!/bin/bash
# Runs ON dev-mac from ~/video-work/head-test/film. Back and front layers in parallel, PNG frames to ../render/.
export PATH=/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/head-test/film; R=../render
node scripts/capture.mjs s-head-test --layer=back --out=$R/back > ../cap-back.log 2>&1 &
node scripts/capture.mjs s-head-test --layer=front --out=$R/front > ../cap-front.log 2>&1
wait; tail -1 ../cap-back.log ../cap-front.log
