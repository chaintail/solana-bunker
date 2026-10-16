#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s05. x12 build mode (Liam 16763), same chain as s05-capture-x12.sh at --speed=1.2: output frame k shows the page at
# t = k/30 * 1.2 (heads, anchors, pokes all run 1.2x, in step with the atempo=1.2 voice). v6 scene (96.78 s, 0.36 s pause = 300 ms at 1.2x after 'if it matches'): 2903 scene frames
# -> ceil(2903/1.2) = 2420 output frames; the last output frame is the scene's last frame (hand-off to s06 unchanged). ONE capture at a time, in 300-frame chunks
# (capture.mjs warms up before each chunk's first shot): each chunk renders into render/x12, is encoded to out/x12/seg/cNN.mp4 (crf 12) and its PNGs are deleted.
# A chunk whose Chrome stalls (no new PNG for 120 s) is killed and retried (3 tries). Leaves out/x12/seg/c00..c08.mp4 + out/x12/seg/list.txt for s05-build-x12.sh.
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s05; mkdir -p out/x12/seg render/x12
SPEED=1.2; M=2420; CH=300
find render/x12 -name 'f*.png' -delete
chunk() { # n first_frame count
  local n=$1 a=$2 c=$3 try pid last cnt idle
  for try in 1 2 3; do
    ( cd film && exec node scripts/capture.mjs s05-hash --speed=$SPEED --from=$(python3 -c "print($a/30)") --to=$(python3 -c "print(($a+$c)/30)") --out=../render/x12 ) > out/x12/cap-$n.log 2>&1 &
    pid=$!; last=-1; idle=0
    while kill -0 $pid 2>/dev/null; do
      sleep 10; cnt=$(find render/x12 -name 'f*.png' | wc -l)
      if [ "$cnt" -eq "$last" ]; then idle=$((idle+10)); else idle=0; last=$cnt; fi
      if [ $idle -ge 120 ]; then echo "chunk $n try $try: stalled at $cnt PNGs, killing"; kill -TERM $pid; sleep 3; kill -KILL $pid 2>/dev/null; fi
    done
    wait $pid; cnt=$(find render/x12 -name 'f*.png' | wc -l)
    if [ "$cnt" -eq "$c" ]; then
      ffmpeg -nostdin -v error -y -framerate 30 -start_number $a -i render/x12/f%05d.png -frames:v $c -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p -r 30 out/x12/seg/c$n.mp4 \
        && find render/x12 -name 'f*.png' -delete && echo "chunk $n ($a..$((a+c-1))) done" && return 0
    fi
    echo "chunk $n try $try: $cnt/$c PNGs, retrying"; find render/x12 -name 'f*.png' -delete
  done
  echo "chunk $n FAILED"; return 1
}
: > out/x12/seg/list.txt
for ((i=0; i*CH<M; i++)); do
  a=$((i*CH)); c=$(( M-a < CH ? M-a : CH )); n=$(printf '%02d' $i)
  if [ -s out/x12/seg/c$n.mp4 ] && [ "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 out/x12/seg/c$n.mp4)" = "$c" ]; then echo "chunk $n kept"; else chunk $n $a $c || exit 1; fi
  echo "file '$PWD/out/x12/seg/c$n.mp4'" >> out/x12/seg/list.txt
done
echo ALLDONE
