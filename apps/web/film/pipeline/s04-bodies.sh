#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. Exports the stand-in bodies (s04-bodies.html, six assets) to film/assets/bodies/<asset>.png (body, no head)
# and <asset>-front.png (collar layer), both cropped 640x720+320+0 (figure centre x = 320 in the crop, floor y = 700, scale per asset in anchors.js).
export PATH=/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/film; T=../out/s04/bodies-tmp; mkdir -p $T assets/bodies
node scripts/capture.mjs s04-bodies --layer=back --still=0,1,2,3,4,5 --out=$T/back > ../out/s04/cap-bodies-back.log 2>&1 &
node scripts/capture.mjs s04-bodies --layer=front --still=0,1,2,3,4,5 --out=$T/front > ../out/s04/cap-bodies-front.log 2>&1
wait
i=0; for n in physicist-point joe-rest joe-up eng-walk1 eng-walk2 eng-point; do
  magick $T/back/still-$i.png -crop 640x720+320+0 +repage assets/bodies/$n.png
  magick $T/front/still-$i.png -crop 640x720+320+0 +repage assets/bodies/$n-front.png; i=$((i+1)); done
ls -la assets/bodies
