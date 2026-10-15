#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s06. Captures s06-signature.html (843 frames, 30 fps) in two chunks (plan R11): each chunk's PNG frames
# are packed into a lossless FFV1 file (out/chunk-a.mkv, out/chunk-b.mkv) and the frame folder is deleted before the next chunk starts.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s06
node film/scripts/capture.mjs s06-signature --from=0 --to=14.0667 --out=render/a > out/cap-a.log 2>&1; tail -1 out/cap-a.log
ls render/a | wc -l
ffmpeg -nostdin -v error -y -framerate 30 -start_number 0 -i render/a/f%05d.png -c:v ffv1 -level 3 -pix_fmt bgr0 out/chunk-a.mkv
find render/a -name 'f*.png' -delete
node film/scripts/capture.mjs s06-signature --from=14.0667 --out=render/b > out/cap-b.log 2>&1; tail -1 out/cap-b.log
ls render/b | wc -l
ffmpeg -nostdin -v error -y -framerate 30 -start_number 422 -i render/b/f%05d.png -c:v ffv1 -level 3 -pix_fmt bgr0 out/chunk-b.mkv
find render/b -name 'f*.png' -delete
for c in a b; do ffprobe -v error -count_frames -show_entries stream=nb_read_frames -of csv=p=0 out/chunk-$c.mkv; done
