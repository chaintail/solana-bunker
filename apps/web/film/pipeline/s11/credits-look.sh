#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/ending (film-s11/ = rsync of film/s11's apps/web/film). Look draft C of film-plan-ending.md:
# s11-credits-look.html at t (default 8.1 s: the roll 4.5 s in, the CAST block in the window) -> out/ending-look-C.png (1280x720)
# and out/ending-look-C-240.png (426x240). No post grade (the credits are graphics; the scene gets none).
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/ending; T=${1:-8.1}; mkdir -p out; : > out/look-c.log
cap() { for i in 1 2 3; do node film-s11/scripts/capture.mjs "$@" >> out/look-c.log 2>&1 && return 0; echo "capture retry $i: $*" >> out/look-c.log; done; return 1; }   # headless Chrome sometimes misses the 12 s CDP window
cap s11-credits-look --settle=4 --still=$T --out=out/look-c; tail -1 out/look-c.log
cp out/look-c/still-$T.png out/ending-look-C.png
ffmpeg -nostdin -v error -y -i out/ending-look-C.png -vf scale=426:240:flags=bicubic -frames:v 1 out/ending-look-C-240.png
