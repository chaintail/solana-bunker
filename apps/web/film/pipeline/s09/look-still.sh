#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s09 (film/ = rsync of apps/web/film). Draft still of the scene 9 look (film-plan-s09.md section 7):
# 1 bodies.py -> film/assets/s09/; 2 two keyed head frames with slide 6's look-head.sh (same key as pipeline/head-test/key.sh): Joe at 501.85 s ("thousand"),
# the suit at 515.62 s ("we did that too"); 3 capture s09-look.html at t=0.5 (panel A, black and white) and t=1.5 (panel B, colour);
# 4 post as the scene will get it: A light luma grain + vignette, B vignette only (the grain goes with the colour snap);
# 5 the two 1280x720 frames side by side -> out/s09-look-draft.png (2560x720), and each frame at 426x240 side by side -> out/s09-look-draft-240.png (852x240).
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s09; mkdir -p out film/heads
(cd film && /usr/bin/python3 pipeline/s09/bodies.py)
bash film/pipeline/s06/look-head.sh 501.85 film/heads/s09-look-joe.png
bash film/pipeline/s06/look-head.sh 515.62 film/heads/s09-look-suit.png
node film/scripts/capture.mjs s09-look --settle=4 --still=0.5,1.5 --out=out/look > out/look.log 2>&1; tail -1 out/look.log
ffmpeg -nostdin -v error -y -i out/look/still-0.5.png -i out/look/still-1.5.png -filter_complex \
  "[0:v]format=yuv444p,noise=c0s=7:c0f=u,vignette=angle=PI/4.6,format=rgb24[a];[1:v]format=yuv444p,vignette=angle=PI/4.6,format=rgb24[b];[a][b]hstack=inputs=2[o]" \
  -map '[o]' -frames:v 1 out/s09-look-draft.png
ffmpeg -nostdin -v error -y -i out/s09-look-draft.png -filter_complex "[0:v]split[x][y];[x]crop=1280:720:0:0,scale=426:240:flags=bicubic[a];[y]crop=1280:720:1280:0,scale=426:240:flags=bicubic[b];[a][b]hstack=inputs=2[o]" \
  -map '[o]' -frames:v 1 out/s09-look-draft-240.png
for p in out/s09-look-draft.png out/s09-look-draft-240.png; do ffprobe -v error -show_entries stream=width,height -of csv=p=0 "$p"; done
