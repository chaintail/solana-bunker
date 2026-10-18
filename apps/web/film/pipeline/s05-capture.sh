#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s05. Captures the 96.42 s scene (2893 frames) in four parallel ranges, one frame folder per segment; each segment is
# encoded to a near-lossless H.264 file as soon as its frames are done and its frame folder is deleted (nothing is kept but out/seg/segN.mp4).
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s05; mkdir -p out/seg render
one() { # n from to frames
  R=render/seg$1; rm -rf $R; mkdir -p $R
  if [ -n "$3" ]; then ( cd film && node scripts/capture.mjs s05-hash --from=$2 --to=$3 --out=../$R ) > out/cap-s05-$1.log 2>&1
  else ( cd film && node scripts/capture.mjs s05-hash --from=$2 --out=../$R ) > out/cap-s05-$1.log 2>&1; fi
  ffmpeg -nostdin -v error -y -framerate 30 -start_number $4 -i $R/f%05d.png -frames:v $5 -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p -r 30 out/seg/seg$1.mp4 && find render/seg$1 -name 'f*.png' -delete && echo "seg$1 done"
}
one 0 0  24 0    720 &
one 1 24 48 720  720 &
one 2 48 72 1440 720 &
one 3 72 "" 2160 733 &
wait; echo ALLDONE > out/cap-s05-done.log
