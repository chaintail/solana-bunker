#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s08. Captures s08-txsize.html (30 fps) in three chunks: each chunk's PNG frames are packed into a lossless
# FFV1 file (out/chunk-a/b/c.mkv) and its frame folder is emptied (literal paths) before the next chunk starts.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s08
node film/scripts/capture.mjs s08-txsize --settle=6 --from=0 --to=18 --out=render/a > out/cap-a.log 2>&1; tail -1 out/cap-a.log
ffmpeg -nostdin -v error -y -framerate 30 -start_number 0 -i render/a/f%05d.png -c:v ffv1 -level 3 -pix_fmt bgr0 out/chunk-a.mkv
find render/a -name 'f*.png' -delete
node film/scripts/capture.mjs s08-txsize --settle=6 --from=18 --to=36 --out=render/b > out/cap-b.log 2>&1; tail -1 out/cap-b.log
ffmpeg -nostdin -v error -y -framerate 30 -start_number 540 -i render/b/f%05d.png -c:v ffv1 -level 3 -pix_fmt bgr0 out/chunk-b.mkv
find render/b -name 'f*.png' -delete
node film/scripts/capture.mjs s08-txsize --settle=6 --from=36 --out=render/c > out/cap-c.log 2>&1; tail -1 out/cap-c.log
ffmpeg -nostdin -v error -y -framerate 30 -start_number 1080 -i render/c/f%05d.png -c:v ffv1 -level 3 -pix_fmt bgr0 out/chunk-c.mkv
find render/c -name 'f*.png' -delete
find render -type d -empty -delete
for c in a b c; do ffprobe -v error -count_frames -show_entries stream=nb_read_frames -of csv=p=0 out/chunk-$c.mkv; done
