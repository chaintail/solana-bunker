#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s08.  usage: capture.sh [vN]   Captures s08-txsize.html (30 fps) in three chunks (retrying Chrome hangs, up to 5 times each);
# each chunk's PNG frames are packed into a lossless FFV1 file (out/chunk-a/b/c.mkv) and its frame folder is emptied (literal paths) before the next chunk; then build.sh video.
# Chunk edges are 18 s / 36 s (frames 540 / 1080).
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s08
cap() { for i in 1 2 3 4 5; do node film/scripts/capture.mjs s08-txsize --settle=6 --from=$2 ${3:+--to=$3} --out=render/$1 > out/cap-$1.log 2>&1 && return 0; sleep 5; done; return 1; }
cap a 0 18 && ffmpeg -nostdin -v error -y -framerate 30 -start_number 0 -i render/a/f%05d.png -c:v ffv1 -level 3 -pix_fmt bgr0 out/chunk-a.mkv && find render/a -name 'f*.png' -delete
cap b 18 36 && ffmpeg -nostdin -v error -y -framerate 30 -start_number 540 -i render/b/f%05d.png -c:v ffv1 -level 3 -pix_fmt bgr0 out/chunk-b.mkv && find render/b -name 'f*.png' -delete
cap c 36 && ffmpeg -nostdin -v error -y -framerate 30 -start_number 1080 -i render/c/f%05d.png -c:v ffv1 -level 3 -pix_fmt bgr0 out/chunk-c.mkv && find render/c -name 'f*.png' -delete
for c in a b c; do ffprobe -v error -count_frames -show_entries stream=nb_read_frames -of csv=p=0 out/chunk-$c.mkv; done
bash film/pipeline/s08/build.sh video ${1:-v4}
echo DONE
