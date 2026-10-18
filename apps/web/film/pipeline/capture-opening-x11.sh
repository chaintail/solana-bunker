#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/opening-x11 (film/ = rsync of film/opening-v8 apps/web/film, its own copy: the shared ~/video-work/solana-bunker/film
# holds other scenes). Captures the desk front layer (s02-news ?layer=front, transparent, 37.8333 s) for the opening x11 cut; the sponsor, advisory and breaking
# cards are not sped and are reused from out/seg-v7. Chunk 0 (output 0..299, which holds the PiP zoom, v7 frames 175..251 = output 159..229) is captured with
# --fresh as v7 did; every PNG is forced to RGBA before its chunk is encoded (the wipe goes opaque and Chrome then writes RGB PNGs, capture-v6.sh).
# Also writes the backdrop still render/back/still-0.png.
# x11 build mode (Liam 16583): capture.mjs --speed=1.1, output frame k shows the page at t = k/30 * 1.1, so every animation, anchor and lip-synced head runs 1.1x in
# step with the atempo=1.1 voice. 1135 scene frames -> ceil(1135/1.1) = 1032 output frames; the last output frame is the scene's last frame (hand-off unchanged).
# ONE capture at a time, 300-frame chunks: each chunk renders into render, is encoded to out/seg/cNN.mkv (lossless FFV1) and its PNGs deleted. A chunk whose Chrome stalls
# (no new PNG for 120 s) is killed and retried (3 tries). Chunks already encoded with the right frame count are kept on a re-run. Leaves out/seg/list.txt.
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/opening-x11; mkdir -p out/seg render
SPEED=1.1; M=1032; CH=300
find render -name 'f*.png' -delete
chunk() { # n first_frame count
  local n=$1 a=$2 c=$3 try pid last cnt idle
  local FRESH=''; [ $a -eq 0 ] && FRESH=--fresh
  for try in 1 2 3; do
    ( cd film && exec node scripts/capture.mjs s02-news --layer=front $FRESH --speed=$SPEED --from=$(python3 -c "print($a/30)") --to=$(python3 -c "print(($a+$c)/30)") --out=../render ) > out/seg/cap-$n.log 2>&1 &
    pid=$!; last=-1; idle=0
    while kill -0 $pid 2>/dev/null; do
      sleep 10; cnt=$(find render -name 'f*.png' | wc -l)
      if [ "$cnt" -eq "$last" ]; then idle=$((idle+10)); else idle=0; last=$cnt; fi
      if [ $idle -ge 120 ]; then echo "chunk $n try $try: stalled at $cnt PNGs, killing"; kill -TERM $pid; sleep 3; kill -KILL $pid 2>/dev/null; fi
    done
    wait $pid; cnt=$(find render -name 'f*.png' | wc -l)
    if [ "$cnt" -eq "$c" ]; then
      ~/speech-lab/.venv/bin/python3 -c "import glob;from PIL import Image
for p in glob.glob('render/f*.png'):
  im=Image.open(p)
  if im.mode!='RGBA': im.convert('RGBA').save(p)" || return 1
      ffmpeg -nostdin -v error -y -framerate 30 -start_number $a -i render/f%05d.png -frames:v $c -c:v ffv1 -level 3 -pix_fmt bgra -r 30 out/seg/c$n.mkv \
        && find render -name 'f*.png' -delete && echo "chunk $n ($a..$((a+c-1))) done" && return 0
    fi
    echo "chunk $n try $try: $cnt/$c PNGs, retrying"; find render -name 'f*.png' -delete
  done
  echo "chunk $n FAILED"; return 1
}
: > out/seg/list.txt
for ((i=0; i*CH<M; i++)); do
  a=$((i*CH)); c=$(( M-a < CH ? M-a : CH )); n=$(printf '%02d' $i)
  if [ -s out/seg/c$n.mkv ] && [ "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 out/seg/c$n.mkv)" = "$c" ]; then echo "chunk $n kept"; else chunk $n $a $c || exit 1; fi
  echo "file '$PWD/out/seg/c$n.mkv'" >> out/seg/list.txt
done
[ -s render/back/still-0.png ] || ( cd film && node scripts/capture.mjs s02-news --layer=back --still=0 --out=../render/back ) > out/seg/cap-back.log 2>&1
ls -la render/back/still-0.png && echo ALLDONE
