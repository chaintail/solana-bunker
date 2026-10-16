#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s08. Captures scene 8 (s08-txsize, 52.32 s, v4/v5 picture, --settle=6 as capture.sh) for the x11 cut into lossless chunks.
# x11 build mode (Liam 16583): capture.mjs --speed=1.1, output frame k shows the page at t = k/30 * 1.1, so every animation, anchor and lip-synced head runs 1.1x in
# step with the atempo=1.1 voice. 1570 scene frames -> ceil(1570/1.1) = 1428 output frames; the last output frame is the scene's last frame (hand-off unchanged).
# ONE capture at a time, 300-frame chunks: each chunk renders into render/x11, is encoded to out/x11/seg/cNN.mkv (lossless FFV1) and its PNGs deleted. A chunk whose Chrome stalls
# (no new PNG for 120 s) is killed and retried (3 tries). Chunks already encoded with the right frame count are kept on a re-run. Leaves <seg>/list.txt.
# v7: usage capture-x11.sh [seg dir, default out/x11/seg]; the frame count M = ceil(scene frames / 1.1) is read from film/data/s08-edl-x11.js (v6: 1428, v7: 1155).
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s08; SEG=${1:-out/x11/seg}; mkdir -p $SEG render/x11
SPEED=1.1; CH=300; M=$(python3 -c "import json;s=open('film/data/s08-edl-x11.js').read();print(round(json.loads(s[s.index('{'):s.rindex('}')+1])['total']*30))")
echo "capturing $M frames into $SEG"
find render/x11 -name 'f*.png' -delete
chunk() { # n first_frame count
  local n=$1 a=$2 c=$3 try pid last cnt idle
  for try in 1 2 3; do
    ( cd film && exec node scripts/capture.mjs s08-txsize --settle=6 --speed=$SPEED --from=$(python3 -c "print($a/30)") --to=$(python3 -c "print(($a+$c)/30)") --out=../render/x11 ) > $SEG/cap-$n.log 2>&1 &
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
