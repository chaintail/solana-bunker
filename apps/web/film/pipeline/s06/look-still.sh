#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s06. Draft still of the slide 6 noir look:
# capture s06-look.html at t=0.5 (headless Chrome), then the post grade every s06 frame will get: luma-only grain (door keeps its red),
# a gentle S-curve and a vignette. Output out/s06-look-draft.png.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s06
node film/scripts/capture.mjs s06-look --still=0.5 --out=out/look > out/look.log 2>&1; tail -1 out/look.log
ffmpeg -nostdin -v error -y -i out/look/still-0.5.png \
  -vf "format=yuv444p,curves=all='0/0.035 0.25/0.21 0.75/0.82 1/1',noise=c0s=30:c0f=u,vignette=angle=PI/4.2,format=rgb24" -frames:v 1 out/s06-look-draft.png
