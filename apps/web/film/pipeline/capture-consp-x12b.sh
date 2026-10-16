#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. x12b (Liam, voice 2026-10-16): x12 with the end trimmed (conspiracy-x12b-edit.py + s03 close retimed;
# s03 data-duration 68.13 -> 63.9 s). capture.mjs --speed=1.2 samples output frame k at page time k/30 * 1.2 whatever the scene length (only the last
# frame is pinned to the scene end), and nothing in s03 changes before page time 61.78 s (the corkboard fade, output frame 1544.5), so:
#   s01-title       175 frames: x12 chunks c00-c02 kept (copied)
#   s03-conspiracy 1917 -> 1598 frames: x12 chunks c00-c24 (output frames 0-1499) kept (copied); c25 (1500-1559) and c26 (1560-1597, 38 frames) captured
#   hat: render-consp-x12/hat is reused by the build (unchanged, ends at 57.7 s)
# Same method as x12: two discarded warm-up shots per page load, ONE capture at a time, 60-frame chunks, stall watchdog with 3 tries.
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker; mkdir -p out/consp-x12b/seg render-consp-x12b/frames
SPEED=1.2; CH=60; HATN=38
find render-consp-x12b/frames -name 'f*.png' -delete
run() { # log out from to extra...   one capture with the stall watchdog; 0 when it wrote the expected number of PNGs into out
  local log=$1 out=$2 a=$3 b=$4; shift 4; local pid last=-1 cnt idle=0
  ( cd film && exec node scripts/capture.mjs "$@" --speed=$SPEED --from=$(python3 -c "print($a/30)") --to=$(python3 -c "print($b/30)") --out=../$out ) > $log 2>&1 &
  pid=$!
  while kill -0 $pid 2>/dev/null; do
    sleep 10; cnt=$(find $out -name 'f*.png' | wc -l)
    if [ "$cnt" -eq "$last" ]; then idle=$((idle+10)); else idle=0; last=$cnt; fi
    if [ $idle -ge 120 ]; then echo "$log: stalled at $cnt PNGs, killing"; kill -TERM $pid; sleep 3; kill -KILL $pid 2>/dev/null; fi
  done
  wait $pid; [ "$(find $out -name 'f*.png' | wc -l)" -eq $((b-a)) ]
}
chunk() { # scene n first count
  local s=$1 n=$2 a=$3 c=$4 try
  for try in 1 2 3; do
    if run out/consp-x12b/seg/cap-$s-$n.log render-consp-x12b/frames $a $((a+c)) $s; then
      ffmpeg -nostdin -v error -y -framerate 30 -start_number $a -i render-consp-x12b/frames/f%05d.png -frames:v $c -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p -r 30 out/consp-x12b/seg/$s-c$n.mp4 \
        && find render-consp-x12b/frames -name 'f*.png' -delete && echo "$s chunk $n ($a..$((a+c-1))) done" && return 0
    fi
    echo "$s chunk $n try $try failed, retrying"; find render-consp-x12b/frames -name 'f*.png' -delete
  done
  echo "$s chunk $n FAILED"; return 1
}
# seed the unchanged chunks from x12 (copies, so x12 stays rebuildable)
for n in 00 01 02; do [ -s out/consp-x12b/seg/s01-title-c$n.mp4 ] || cp out/consp-x12/seg/s01-title-c$n.mp4 out/consp-x12b/seg/; done
for ((i=0; i<=24; i++)); do n=$(printf '%02d' $i); [ -s out/consp-x12b/seg/s03-conspiracy-c$n.mp4 ] || cp out/consp-x12/seg/s03-conspiracy-c$n.mp4 out/consp-x12b/seg/; done
: > out/consp-x12b/seg/list.txt
for spec in s01-title:175 s03-conspiracy:1598; do
  s=${spec%%:*}; M=${spec##*:}
  for ((i=0; i*CH<M; i++)); do
    a=$((i*CH)); c=$(( M-a < CH ? M-a : CH )); n=$(printf '%02d' $i)
    if [ -s out/consp-x12b/seg/$s-c$n.mp4 ] && [ "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 out/consp-x12b/seg/$s-c$n.mp4)" = "$c" ]; then echo "$s chunk $n kept"; else chunk $s $n $a $c || exit 1; fi
    echo "file '$PWD/out/consp-x12b/seg/$s-c$n.mp4'" >> out/consp-x12b/seg/list.txt
  done
done
[ "$(find render-consp-x12/hat -name 'f*.png' | wc -l)" -eq $HATN ] || { echo "render-consp-x12/hat is not $HATN frames"; exit 1; }
echo ALLDONE
