#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s08. Stills of s08-txsize.html at the given scene times (comma list) -> out/stills/still-<t>.png,
# each with the post grade (as build.sh) -> out/stills/g-<t>.png and a 426x240 downscale -> out/stills/s-<t>.png
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s08; mkdir -p out/stills
node film/scripts/capture.mjs s08-txsize --settle=6 --still="$1" --out=out/stills > out/stills.log 2>&1; tail -1 out/stills.log
for t in ${1//,/ }; do
  ffmpeg -nostdin -v error -y -i out/stills/still-$t.png -vf "format=yuv444p,noise=c0s=7:c0f=u,vignette=angle=PI/4.6,format=rgb24" -frames:v 1 out/stills/g-$t.png
  ffmpeg -nostdin -v error -y -i out/stills/g-$t.png -vf scale=426:240:flags=bicubic -frames:v 1 out/stills/s-$t.png
done
