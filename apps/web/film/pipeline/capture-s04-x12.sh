#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. Captures slide 4 (s04-bunker, 55.77 s) for the x12 cut; build-s04-x12.sh muxes it.
# x12 build mode (Liam 16583): capture.mjs --speed=1.2, output frame k shows the page at t = k/30 * 1.2, so every animation, anchor and lip-synced head runs 1.2x in
# step with the atempo=1.2 voice. 1673 scene frames -> ceil(1673/1.2) = 1395 output frames; the last output frame is the scene's last frame (hand-off unchanged).
# ONE capture at a time, 300-frame chunks: each chunk renders into render-s04-v8x12, is encoded to out/s04/v8x12/seg/cNN.mp4 (crf 12) and its PNGs deleted. A chunk whose Chrome stalls
# (no new PNG for 120 s) is killed and retried (3 tries). Chunks already encoded with the right frame count are kept on a re-run. Leaves out/s04/v8x12/seg/list.txt.
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker; mkdir -p out/s04/v8x12/seg render-s04-v8x12
SPEED=1.2; M=1395; CH=300
find render-s04-v8x12 -name 'f*.png' -delete
chunk() { # n first_frame count
  local n=$1 a=$2 c=$3 try pid last cnt idle
  for try in 1 2 3; do
    ( cd film && exec node scripts/capture.mjs s04-bunker  --speed=$SPEED --from=$(python3 -c "print($a/30)") --to=$(python3 -c "print(($a+$c)/30)") --out=../render-s04-v8x12 ) > out/s04/v8x12/seg/cap-$n.log 2>&1 &
    pid=$!; last=-1; idle=0
    while kill -0 $pid 2>/dev/null; do
      sleep 10; cnt=$(find render-s04-v8x12 -name 'f*.png' | wc -l)
      if [ "$cnt" -eq "$last" ]; then idle=$((idle+10)); else idle=0; last=$cnt; fi
      if [ $idle -ge 120 ]; then echo "chunk $n try $try: stalled at $cnt PNGs, killing"; kill -TERM $pid; sleep 3; kill -KILL $pid 2>/dev/null; fi
    done
    wait $pid; cnt=$(find render-s04-v8x12 -name 'f*.png' | wc -l)
    if [ "$cnt" -eq "$c" ]; then
      ffmpeg -nostdin -v error -y -framerate 30 -start_number $a -i render-s04-v8x12/f%05d.png -frames:v $c -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p -r 30 out/s04/v8x12/seg/c$n.mp4 \
        && find render-s04-v8x12 -name 'f*.png' -delete && echo "chunk $n ($a..$((a+c-1))) done" && return 0
    fi
    echo "chunk $n try $try: $cnt/$c PNGs, retrying"; find render-s04-v8x12 -name 'f*.png' -delete
  done
  echo "chunk $n FAILED"; return 1
}
: > out/s04/v8x12/seg/list.txt
for ((i=0; i*CH<M; i++)); do
  a=$((i*CH)); c=$(( M-a < CH ? M-a : CH )); n=$(printf '%02d' $i)
  if [ -s out/s04/v8x12/seg/c$n.mp4 ] && [ "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 out/s04/v8x12/seg/c$n.mp4)" = "$c" ]; then echo "chunk $n kept"; else chunk $n $a $c || exit 1; fi
  echo "file '$PWD/out/s04/v8x12/seg/c$n.mp4'" >> out/s04/v8x12/seg/list.txt
done
echo ALLDONE
