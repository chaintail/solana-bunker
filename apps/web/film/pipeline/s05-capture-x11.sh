#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s05. x11 build mode (Liam 16583): the slide-5 scene captured with capture.mjs --speed=1.1, i.e. output frame k shows
# the page at t = k/30 * 1.1 (heads, anchors, pokes all run 1.1x, in step with the atempo=1.1 voice). 2893 scene frames -> ceil(2893/1.1) = 2630 output frames; the last
# output frame is the scene's last frame (hand-off to s06 unchanged). ONE capture at a time, in 300-frame chunks: each chunk renders into render/x11, is encoded to
# out/x11/seg/cNN.mp4 (crf 12) and its PNGs are deleted. A chunk whose Chrome stalls (no new PNG for 120 s) is killed and retried (3 tries).
# Leaves out/x11/seg/c00..c08.mp4 + out/x11/seg/list.txt for s05-build-x11.sh.
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s05; mkdir -p out/x11/seg render/x11
SPEED=1.1; M=2630; CH=300
find render/x11 -name 'f*.png' -delete
chunk() { # n first_frame count
  local n=$1 a=$2 c=$3 try pid last cnt idle
  for try in 1 2 3; do
    ( cd film && exec node scripts/capture.mjs s05-hash --speed=$SPEED --from=$(python3 -c "print($a/30)") --to=$(python3 -c "print(($a+$c)/30)") --out=../render/x11 ) > out/x11/cap-$n.log 2>&1 &
    pid=$!; last=-1; idle=0
    while kill -0 $pid 2>/dev/null; do
      sleep 10; cnt=$(find render/x11 -name 'f*.png' | wc -l)
      if [ "$cnt" -eq "$last" ]; then idle=$((idle+10)); else idle=0; last=$cnt; fi
      if [ $idle -ge 120 ]; then echo "chunk $n try $try: stalled at $cnt PNGs, killing"; kill -TERM $pid; sleep 3; kill -KILL $pid 2>/dev/null; fi
    done
    wait $pid; cnt=$(find render/x11 -name 'f*.png' | wc -l)
    if [ "$cnt" -eq "$c" ]; then
      ffmpeg -nostdin -v error -y -framerate 30 -start_number $a -i render/x11/f%05d.png -frames:v $c -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p -r 30 out/x11/seg/c$n.mp4 \
        && find render/x11 -name 'f*.png' -delete && echo "chunk $n ($a..$((a+c-1))) done" && return 0
    fi
    echo "chunk $n try $try: $cnt/$c PNGs, retrying"; find render/x11 -name 'f*.png' -delete
  done
  echo "chunk $n FAILED"; return 1
}
: > out/x11/seg/list.txt
for ((i=0; i*CH<M; i++)); do
  a=$((i*CH)); c=$(( M-a < CH ? M-a : CH )); n=$(printf '%02d' $i)
  if [ -s out/x11/seg/c$n.mp4 ] && [ "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 out/x11/seg/c$n.mp4)" = "$c" ]; then echo "chunk $n kept"; else chunk $n $a $c || exit 1; fi
  echo "file '$PWD/out/x11/seg/c$n.mp4'" >> out/x11/seg/list.txt
done
echo ALLDONE
