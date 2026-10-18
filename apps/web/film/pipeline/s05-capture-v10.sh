#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s05. s05 v10 capture: v9's chunked x12 capture (out/x12v9/s05-capture-v9.sh = s05-capture-x12.sh with its own
# directories) with the scene ending 0.53 s after the last word: s05-hash.html data-duration 89.4333 -> 2683 scene frames -> ceil(2683/1.2) = 2236 output frames
# (v9: 91.45 s, 2744 -> 2287). Output frame k shows the page at t = k/30 * 1.2; the last output frame is pinned to the scene's last frame (2682/30 = 89.40 s, which
# is also 2235 * 1.2 / 30). ONE capture at a time, in 300-frame chunks (capture.mjs discards a warm-up shot before each chunk's first frame): each chunk renders
# into render/x12v10, is encoded to out/x12v10/seg/cNN.mp4 (crf 12) and its PNGs are deleted. A chunk whose Chrome stalls (no new PNG for 120 s) is killed and
# retried (3 tries). Leaves out/x12v10/seg/c00..c07.mp4 + list.txt for the mux (build-s05-v10.sh).
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s05; D=x12v10; mkdir -p out/$D/seg render/$D
SPEED=1.2; M=2236; CH=300   # v10: 89.4333 s scene = 2683 frames -> ceil(2683/1.2) = 2236 (v8/v9: 2287)
find render/$D -name 'f*.png' -delete
chunk() { # n first_frame count
  local n=$1 a=$2 c=$3 try pid last cnt idle
  for try in 1 2 3; do
    ( cd film && exec node scripts/capture.mjs s05-hash --speed=$SPEED --from=$(python3 -c "print($a/30)") --to=$(python3 -c "print(($a+$c)/30)") --out=../render/$D ) > out/$D/cap-$n.log 2>&1 &
    pid=$!; last=-1; idle=0
    while kill -0 $pid 2>/dev/null; do
      sleep 10; cnt=$(find render/$D -name 'f*.png' | wc -l)
      if [ "$cnt" -eq "$last" ]; then idle=$((idle+10)); else idle=0; last=$cnt; fi
      if [ $idle -ge 120 ]; then echo "chunk $n try $try: stalled at $cnt PNGs, killing"; kill -TERM $pid; sleep 3; kill -KILL $pid 2>/dev/null; fi
    done
    wait $pid; cnt=$(find render/$D -name 'f*.png' | wc -l)
    if [ "$cnt" -eq "$c" ]; then
      ffmpeg -nostdin -v error -y -framerate 30 -start_number $a -i render/$D/f%05d.png -frames:v $c -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p -r 30 out/$D/seg/c$n.mp4 \
        && find render/$D -name 'f*.png' -delete && echo "chunk $n ($a..$((a+c-1))) done" && return 0
    fi
    echo "chunk $n try $try: $cnt/$c PNGs, retrying"; find render/$D -name 'f*.png' -delete
  done
  echo "chunk $n FAILED"; return 1
}
: > out/$D/seg/list.txt
for ((i=0; i*CH<M; i++)); do
  a=$((i*CH)); c=$(( M-a < CH ? M-a : CH )); n=$(printf '%02d' $i)
  if [ -s out/$D/seg/c$n.mp4 ] && [ "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 out/$D/seg/c$n.mp4)" = "$c" ]; then echo "chunk $n kept"; else chunk $n $a $c || exit 1; fi
  echo "file '$PWD/out/$D/seg/c$n.mp4'" >> out/$D/seg/list.txt
done
echo ALLDONE
