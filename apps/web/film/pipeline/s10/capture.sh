#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s10. Captures s10-news.html ?layer=front (transparent PNGs, 30 fps, 1002 frames) in two chunks:
# each chunk is packed into lossless FFV1 with alpha (bgra, out/front-a/b.mkv) and its frame folder emptied (literal paths) before the next chunk.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s10; mkdir -p out
cap() { for i in 1 2 3; do node film/scripts/capture.mjs "$@" && return 0; echo "capture retry $i" >&2; done; return 1; }
cap s10-news --layer=front --settle=4 --from=0 --to=17 --out=render/a > out/cap-a.log 2>&1; tail -1 out/cap-a.log
ffmpeg -nostdin -v error -y -framerate 30 -start_number 0 -i render/a/f%05d.png -c:v ffv1 -level 3 -pix_fmt bgra out/front-a.mkv
find render/a -name 'f*.png' -delete
cap s10-news --layer=front --settle=4 --from=17 --out=render/b > out/cap-b.log 2>&1; tail -1 out/cap-b.log
ffmpeg -nostdin -v error -y -framerate 30 -start_number 510 -i render/b/f%05d.png -c:v ffv1 -level 3 -pix_fmt bgra out/front-b.mkv
find render/b -name 'f*.png' -delete
find render -type d -empty -delete
for c in a b; do ffprobe -v error -count_frames -show_entries stream=nb_read_frames -of csv=p=0 out/front-$c.mkv; done
