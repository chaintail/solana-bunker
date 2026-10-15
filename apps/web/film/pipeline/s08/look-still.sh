#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s08 (film/ = rsync of apps/web/film). Draft still of the scene 8 arcade look (film-plan-s08.md section 7):
# 1 bodies.py -> film/assets/s08/ (engineer body with the oval cut out, hard hat kept); 2 one keyed head frame of Liam at 463.15 s (the pause after "damn it",
# mouth closed) with slide 6's look-head.sh (same key as pipeline/head-test/key.sh); 3 capture s08-look.html at t=0.1 (GAME OVER on);
# 4 post: vignette + light luma grain (the CRT itself is in-scene). Output out/s08-look-draft.png.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s08; mkdir -p out film/heads
(cd film && /usr/bin/python3 pipeline/s08/bodies.py)
bash film/pipeline/s06/look-head.sh 463.15 film/heads/s08-look-head.png
node film/scripts/capture.mjs s08-look --still=0.1 --out=out/look > out/look.log 2>&1; tail -1 out/look.log
ffmpeg -nostdin -v error -y -i out/look/still-0.1.png \
  -vf "format=yuv444p,noise=c0s=7:c0f=u,vignette=angle=PI/4.6,format=rgb24" -frames:v 1 out/s08-look-draft.png
