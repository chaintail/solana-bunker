#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s09. Captures scene 9 (s09-seed, v11: 38.83 s, --settle=4 as capture.sh) for the x13 cut into lossless chunks; build-x13.sh grades and muxes.
# x13 build mode (v11, Liam "speeding this up to 1.3x"): capture.mjs --speed=1.3 (with its warm-up shot before the first frame after each page load), output frame k shows the page at
# t = k/30 * 1.3, so every animation, anchor and lip-synced head runs 1.3x in step with the atempo=1.3 voice. 1165 scene frames -> ceil(1165/1.3) = 897 output frames
# (x12 v10: 1306 -> 1089); the last output frame is the scene's last frame (hand-off unchanged).
# ONE capture at a time, 300-frame chunks: each chunk renders into render/x13, is encoded to out/x13/seg/cNN.mkv (lossless FFV1) and its PNGs deleted. A chunk whose Chrome stalls
# (no new PNG for 120 s) is killed and retried (3 tries). Chunks already encoded with the right frame count are kept on a re-run:
# after any page change delete out/x13/seg/c*.mkv first, or stale chunks of the old page are reused. Leaves out/x13/seg/list.txt.
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s09; mkdir -p out/x13/seg render/x13
SPEED=1.3; M=897; CH=300
find render/x13 -name 'f*.png' -delete
chunk() { # n first_frame count
  local n=$1 a=$2 c=$3 try pid last cnt idle
  for try in 1 2 3; do
    ( cd film && exec node scripts/capture.mjs s09-seed --settle=4 --speed=$SPEED --from=$(python3 -c "print($a/30)") --to=$(python3 -c "print(($a+$c)/30)") --out=../render/x13 ) > out/x13/seg/cap-$n.log 2>&1 &
    pid=$!; last=-1; idle=0
    while kill -0 $pid 2>/dev/null; do
      sleep 10; cnt=$(find render/x13 -name 'f*.png' | wc -l)
      if [ "$cnt" -eq "$last" ]; then idle=$((idle+10)); else idle=0; last=$cnt; fi
      if [ $idle -ge 120 ]; then echo "chunk $n try $try: stalled at $cnt PNGs, killing"; kill -TERM $pid; sleep 3; kill -KILL $pid 2>/dev/null; fi
    done
    wait $pid; cnt=$(find render/x13 -name 'f*.png' | wc -l)
    if [ "$cnt" -eq "$c" ]; then
      ffmpeg -nostdin -v error -y -framerate 30 -start_number $a -i render/x13/f%05d.png -frames:v $c -c:v ffv1 -level 3 -pix_fmt bgr0 -r 30 out/x13/seg/c$n.mkv \
        && find render/x13 -name 'f*.png' -delete && echo "chunk $n ($a..$((a+c-1))) done" && return 0
    fi
    echo "chunk $n try $try: $cnt/$c PNGs, retrying"; find render/x13 -name 'f*.png' -delete
  done
  echo "chunk $n FAILED"; return 1
}
: > out/x13/seg/list.txt
for ((i=0; i*CH<M; i++)); do
  a=$((i*CH)); c=$(( M-a < CH ? M-a : CH )); n=$(printf '%02d' $i)
  if [ -s out/x13/seg/c$n.mkv ] && [ "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 out/x13/seg/c$n.mkv)" = "$c" ]; then echo "chunk $n kept"; else chunk $n $a $c || exit 1; fi
  echo "file '$PWD/out/x13/seg/c$n.mkv'" >> out/x13/seg/list.txt
done
echo ALLDONE
