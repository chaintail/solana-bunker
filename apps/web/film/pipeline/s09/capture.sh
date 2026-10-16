#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s09. Captures s09-seed.html (30 fps, 1367 frames in v3) in three chunks: each chunk's PNG frames are packed
# into a lossless FFV1 file (out/chunk-a/b/c.mkv) and its frame folder is emptied (literal paths) before the next chunk starts.
# Chrome on dev-mac sometimes hangs at launch (film-plan-ending.md R-B1): capture.mjs gives up when it cannot reach Chrome, and each chunk is retried up to 3 times.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s09
cap() {   # cap <chunk> <from> <to|''>
  for try in 1 2 3; do
    if [ -n "$3" ]; then node film/scripts/capture.mjs s09-seed --settle=4 --from=$2 --to=$3 --out=render/$1 > out/cap-$1.log 2>&1 && break
    else node film/scripts/capture.mjs s09-seed --settle=4 --from=$2 --out=render/$1 > out/cap-$1.log 2>&1 && break; fi
    echo "chunk $1 try $try failed: $(tail -1 out/cap-$1.log)"; sleep 20
  done; tail -1 out/cap-$1.log; }
cap a 0 15
ffmpeg -nostdin -v error -y -framerate 30 -start_number 0 -i render/a/f%05d.png -c:v ffv1 -level 3 -pix_fmt bgr0 out/chunk-a.mkv
find render/a -name 'f*.png' -delete
cap b 15 30
ffmpeg -nostdin -v error -y -framerate 30 -start_number 450 -i render/b/f%05d.png -c:v ffv1 -level 3 -pix_fmt bgr0 out/chunk-b.mkv
find render/b -name 'f*.png' -delete
cap c 30 ''
ffmpeg -nostdin -v error -y -framerate 30 -start_number 900 -i render/c/f%05d.png -c:v ffv1 -level 3 -pix_fmt bgr0 out/chunk-c.mkv
find render/c -name 'f*.png' -delete
find render -type d -empty -delete
for c in a b c; do ffprobe -v error -count_frames -show_entries stream=nb_read_frames -of csv=p=0 out/chunk-$c.mkv; done
