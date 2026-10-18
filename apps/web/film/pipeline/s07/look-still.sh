#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s07. Draft still of the slide 7 seminar look: the alley window image is slide 6 v3's graded end frame
# (../s06/out/s06-v3.mp4 at 29.95 s); capture s07-look.html at t=0.5, then a warm projector grade (lifted blacks, warm tint, light grain, vignette).
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s07; mkdir -p out film/assets
ffmpeg -nostdin -v error -y -ss 29.95 -i ../s06/out/s06-v3.mp4 -frames:v 1 -vf scale=640:360:flags=lanczos film/assets/s07-alley-freeze.png
node film/scripts/capture.mjs s07-look --still=0.5 --out=out/look > out/look.log 2>&1; tail -1 out/look.log
ffmpeg -nostdin -v error -y -i out/look/still-0.5.png \
  -vf "format=yuv444p,curves=r='0/0.04 1/1':g='0/0.03 1/0.98':b='0/0.02 1/0.92',noise=c0s=14:c0f=u,vignette=angle=PI/4.6,format=rgb24" -frames:v 1 out/s07-look-draft.png
