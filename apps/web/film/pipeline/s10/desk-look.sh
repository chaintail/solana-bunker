#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/ending (film-s10/ = rsync of film/s10's apps/web/film). Look draft B of film-plan-ending.md:
# the opening's desk backdrop (s02-news.html ?layer=back, unchanged), the matted anchor from the take at T (default 539.30 s, "like us", just after
# "crypto nerd"), and s10-desk-look.html ?layer=front (CRYPTOGRAPHY NERD lower third, bugs, chyron), composited as pipeline/desk-v7.filter
# (comp scaled 525x700, despill, alpha from matte-full-alpha, overlay at 377,-20) -> out/ending-look-B.png (1280x720) and out/ending-look-B-240.png.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/ending; B=~/video-work/bunker; T=${1:-539.30}; mkdir -p out
cap() { for i in 1 2 3; do node film-s10/scripts/capture.mjs "$@" >> out/look-b.log 2>&1 && return 0; echo "capture retry $i: $*" >> out/look-b.log; done; return 1; }   # headless Chrome sometimes misses the 12 s CDP window
: > out/look-b.log
cap s02-news --layer=back --still=0 --out=out/look-b-back
cap s10-desk-look --layer=front --settle=4 --still=0.5 --out=out/look-b-front; tail -1 out/look-b.log
# the two stills are looped and every stream starts at PTS 0, so the single output frame has all three layers
ffmpeg -nostdin -v error -y -loop 1 -i out/look-b-back/still-0.png -ss $T -i $B/matte-full-comp.mp4 -ss $T -i $B/matte-full-alpha.mp4 -loop 1 -i out/look-b-front/still-0.5.png -filter_complex \
 "[1:v]setpts=PTS-STARTPTS,scale=525:700:flags=lanczos,despill=type=green:mix=0.6:expand=0.2,format=rgb24[c];[2:v]setpts=PTS-STARTPTS,scale=525:700:flags=lanczos,format=gray[a];[c][a]alphamerge[liam];
  [0:v]setpts=PTS-STARTPTS,format=rgb24[bg];[bg][liam]overlay=x=377:y=-20:format=auto[bgl];[3:v]setpts=PTS-STARTPTS,format=rgba[fr];[bgl][fr]overlay=format=auto,format=rgb24[o]" \
 -map '[o]' -frames:v 1 out/ending-look-B.png
ffmpeg -nostdin -v error -y -i out/ending-look-B.png -vf scale=426:240:flags=bicubic -frames:v 1 out/ending-look-B-240.png
