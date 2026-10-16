#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s07. Captures slide 7 (s07-xmss, 39.9634 s, v7) for the x11 cut into lossless chunks; build-x11.sh grades and muxes.
# x11 build mode (Liam 16583): capture.mjs --speed=1.1, output frame k shows the page at t = k/30 * 1.1, so every animation, anchor and lip-synced head runs 1.1x in
# step with the atempo=1.1 voice. 1198.9 scene frames (v7) -> ceil(39.9634/1.1*30) = 1090 output frames; the last output frame is the scene's last frame (hand-off unchanged).
# ONE capture at a time, 300-frame chunks: each chunk renders into render/x11, is encoded to $SEG/cNN.mkv (lossless FFV1) and its PNGs deleted. A chunk whose Chrome stalls
# (no new PNG for 120 s) is killed and retried (3 tries). Chunks already encoded with the right frame count are kept on a re-run. Leaves $SEG/list.txt.
# V=<tag> (e.g. V=v5) writes the chunks to out/x11/seg-<tag> instead, so an earlier build's chunks are never reused.
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
V=${V:-}; SEG=out/x11/seg${V:+-$V}
cd ~/video-work/solana-bunker/s07; mkdir -p $SEG render/x11
SPEED=1.1; M=1090; CH=300
find render/x11 -name 'f*.png' -delete
chunk() { # n first_frame count
  local n=$1 a=$2 c=$3 try pid last cnt idle
  for try in 1 2 3; do
    ( cd film && exec node scripts/capture.mjs s07-xmss  --speed=$SPEED --from=$(python3 -c "print($a/30)") --to=$(python3 -c "print(($a+$c)/30)") --out=../render/x11 ) > $SEG/cap-$n.log 2>&1 &
    pid=$!; last=-1; idle=0
    while kill -0 $pid 2>/dev/null; do
      sleep 10; cnt=$(find render/x11 -name 'f*.png' | wc -l)
      if [ "$cnt" -eq "$last" ]; then idle=$((idle+10)); else idle=0; last=$cnt; fi
      if [ $idle -ge 120 ]; then echo "chunk $n try $try: stalled at $cnt PNGs, killing"; kill -TERM $pid; sleep 3; kill -KILL $pid 2>/dev/null; fi
    done
    wait $pid; cnt=$(find render/x11 -name 'f*.png' | wc -l)
    if [ "$cnt" -eq "$c" ]; then
      ffmpeg -nostdin -v error -y -framerate 30 -start_number $a -i render/x11/f%05d.png -frames:v $c -c:v ffv1 -level 3 -pix_fmt bgr0 -r 30 $SEG/c$n.mkv \
        && find render/x11 -name 'f*.png' -delete && echo "chunk $n ($a..$((a+c-1))) done" && return 0
    fi
    echo "chunk $n try $try: $cnt/$c PNGs, retrying"; find render/x11 -name 'f*.png' -delete
  done
  echo "chunk $n FAILED"; return 1
}
: > $SEG/list.txt
for ((i=0; i*CH<M; i++)); do
  a=$((i*CH)); c=$(( M-a < CH ? M-a : CH )); n=$(printf '%02d' $i)
  if [ -s $SEG/c$n.mkv ] && [ "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 $SEG/c$n.mkv)" = "$c" ]; then echo "chunk $n kept"; else chunk $n $a $c || exit 1; fi
  echo "file '$PWD/$SEG/c$n.mkv'" >> $SEG/list.txt
done
echo ALLDONE
