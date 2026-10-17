#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s06. Captures slide 6 (s06-signature, 29.5 s, v7 timing) for the x12 cut into lossless chunks; build-x12.sh grades and muxes.
# x12 build mode (Liam 16583, "1.2 on all"): capture.mjs --speed=1.2, output frame k shows the page at t = k/30 * 1.2, so every animation, anchor and lip-synced head runs 1.2x in
# step with the atempo=1.2 voice. 885 scene frames -> ceil(885/1.2) = 738 output frames (capture.mjs computes the same); frame 0 is the baked slide-5 end frame, the last output
# frame is the scene's last frame. The live whiteboard lab coat takes over at page 0.30 s = between output frames 7 (page 0.28) and 8 (page 0.32).
# capture.mjs takes two discarded warm-up shots after each page load, so no chunk starts on a stale frame-0 paint.
# ONE capture at a time, 300-frame chunks: each chunk renders into render/x12, is encoded to $SEG/cNN.mkv (lossless FFV1) and its PNGs deleted. A chunk whose Chrome stalls
# (no new PNG for 120 s) is killed and retried (3 tries). Chunks already encoded with the right frame count are kept on a re-run. Leaves $SEG/list.txt.
# V=<tag> (default v10) writes the chunks to out/x12/seg-<tag>, so an earlier build's chunks are never reused.
# v10: the output frame count comes from out/s06-edl.json's total (v9 29.5 s -> 738 frames; v10 26.5 s -> ceil(795/1.2) = 663 frames).
# FROM_EARLY=<n>:<k> captures chunk n from k frames before its first frame (a chunk that paints a stale frame-0 early) and drops those k frames at the encode.
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
V=${V:-v10}; SEG=out/x12/seg-$V
cd ~/video-work/solana-bunker/s06; mkdir -p $SEG render/x12
SPEED=1.2; CH=300
M=$(python3 -c "import json,math;N=round(json.load(open('out/s06-edl.json'))['total']*30);print(math.ceil(N/$SPEED-1e-9))"); echo "output frames $M"
find render/x12 -name 'f*.png' -delete
chunk() { # n first_frame count
  local n=$1 a=$2 c=$3 try pid last cnt idle e=0
  [ "${FROM_EARLY%%:*}" = "$n" ] && e=${FROM_EARLY#*:}
  for try in 1 2 3; do
    ( cd film && exec node scripts/capture.mjs s06-signature  --speed=$SPEED --from=$(python3 -c "print(($a-$e)/30)") --to=$(python3 -c "print(($a+$c)/30)") --out=../render/x12 ) > $SEG/cap-$n.log 2>&1 &
    pid=$!; last=-1; idle=0
    while kill -0 $pid 2>/dev/null; do
      sleep 10; cnt=$(find render/x12 -name 'f*.png' | wc -l)
      if [ "$cnt" -eq "$last" ]; then idle=$((idle+10)); else idle=0; last=$cnt; fi
      if [ $idle -ge 120 ]; then echo "chunk $n try $try: stalled at $cnt PNGs, killing"; kill -TERM $pid; sleep 3; kill -KILL $pid 2>/dev/null; fi
    done
    wait $pid; cnt=$(find render/x12 -name 'f*.png' | wc -l)
    if [ "$cnt" -eq "$((c+e))" ]; then
      ffmpeg -nostdin -v error -y -framerate 30 -start_number $a -i render/x12/f%05d.png -frames:v $c -c:v ffv1 -level 3 -pix_fmt bgr0 -r 30 $SEG/c$n.mkv \
        && find render/x12 -name 'f*.png' -delete && echo "chunk $n ($a..$((a+c-1))) done" && return 0
    fi
    echo "chunk $n try $try: $cnt/$((c+e)) PNGs, retrying"; find render/x12 -name 'f*.png' -delete
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
