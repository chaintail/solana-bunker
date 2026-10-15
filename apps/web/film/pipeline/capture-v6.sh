#!/bin/bash
# Runs ON dev-mac. Revision 6 capture into render-v6/. Only the advisory (new voice timing) and the tail of the desk front layer (wipe 0.4 s earlier)
# change; desk frames 0..1079 are identical to v5 (wipe starts at 1084), so they are symlinked from render-v5 and only 1080..1134 are captured.
export PATH=/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/film; R=../render-v6; mkdir -p $R/s02-news-front
node scripts/capture.mjs s00b-advisory --out=$R/s00b-advisory > ../out/cap-v6-a.log 2>&1 &
for i in $(seq 0 1079); do ln -sf ../../render-v5/s02-news-front/$(printf 'f%05d.png' $i) $R/s02-news-front/$(printf 'f%05d.png' $i); done
node scripts/capture.mjs s02-news --layer=front --from=36.0 --out=$R/s02-news-front > ../out/cap-v6-b.log 2>&1
node scripts/capture.mjs s02-news --layer=back --still=0 --out=$R/s02-news-back >> ../out/cap-v6-b.log 2>&1
wait; echo ALLDONE >> ../out/cap-v6-b.log
# The wipe goes fully opaque from desk frame ~1117, and Chrome then writes RGB (no alpha) PNGs; ffmpeg's image2 demuxer drops the overlay for the
# frames at the format switch (two unwiped face frames seen in the first v6 encode). Force RGBA on every captured frame.
~/speech-lab/.venv/bin/python3 - <<'PY'
from PIL import Image
import os
d=os.path.expanduser('~/video-work/solana-bunker/render-v6/s02-news-front/')
for i in range(1080,1135):
    p=d+f'f{i:05d}.png'; im=Image.open(p)
    if im.mode!='RGBA': im.convert('RGBA').save(p)
PY
