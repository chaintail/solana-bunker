#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. x12 build mode (Liam 16583, "1.2 on all"): the approved x11 cut (v4 choreography, lamp flicker removed) captured with
# capture.mjs --speed=1.2 (output frame k shows the page at t = k/30 * 1.2, so every animation and word anchor runs 1.2x in step with the atempo=1.2 voice; each scene's
# last output frame is its last frame; capture.mjs computes the output count as ceil(scene frames / 1.2)):
#   s01-title       210 frames -> 175 (Liam speaks from 0.4 s, so the title is sped too)
#   s03-conspiracy 2044 frames -> 1704
#   s03b-hat (--layer=front) output frames 0..37 (page 0-1.48 s; the hat settles at 1.3 s, so frame 37 is the settled hat, held by the build), PNGs kept for the build
# capture.mjs takes two discarded warm-up shots after each page load, so no chunk starts on a stale frame-0 paint.
# ONE capture at a time, 60-frame chunks (dev-mac disk is shared and near full): each chunk renders into render-consp-x12/frames, is encoded to
# out/consp-x12/seg/<scene>-cNN.mp4 (crf 12) and its PNGs deleted; a chunk whose Chrome stalls (no new PNG for 120 s) is killed and retried (3 tries); chunks already
# encoded with the right frame count are kept on a re-run (delete them by literal path first if the scene changed).
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker; mkdir -p out/consp-x12/seg render-consp-x12/frames render-consp-x12/hat
SPEED=1.2; CH=60; HATN=38
find render-consp-x12/frames -name 'f*.png' -delete
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
    if run out/consp-x12/seg/cap-$s-$n.log render-consp-x12/frames $a $((a+c)) $s; then
      ffmpeg -nostdin -v error -y -framerate 30 -start_number $a -i render-consp-x12/frames/f%05d.png -frames:v $c -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p -r 30 out/consp-x12/seg/$s-c$n.mp4 \
        && find render-consp-x12/frames -name 'f*.png' -delete && echo "$s chunk $n ($a..$((a+c-1))) done" && return 0
    fi
    echo "$s chunk $n try $try failed, retrying"; find render-consp-x12/frames -name 'f*.png' -delete
  done
  echo "$s chunk $n FAILED"; return 1
}
: > out/consp-x12/seg/list.txt
for spec in s01-title:175 s03-conspiracy:1704; do
  s=${spec%%:*}; M=${spec##*:}
  for ((i=0; i*CH<M; i++)); do
    a=$((i*CH)); c=$(( M-a < CH ? M-a : CH )); n=$(printf '%02d' $i)
    if [ -s out/consp-x12/seg/$s-c$n.mp4 ] && [ "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 out/consp-x12/seg/$s-c$n.mp4)" = "$c" ]; then echo "$s chunk $n kept"; else chunk $s $n $a $c || exit 1; fi
    echo "file '$PWD/out/consp-x12/seg/$s-c$n.mp4'" >> out/consp-x12/seg/list.txt
  done
done
if [ "$(find render-consp-x12/hat -name 'f*.png' | wc -l)" -ne $HATN ]; then
  for try in 1 2 3; do
    find render-consp-x12/hat -name 'f*.png' -delete
    run out/consp-x12/seg/cap-hat.log render-consp-x12/hat 0 $HATN s03b-hat --layer=front && { echo "hat done"; break; }
    echo "hat try $try failed"; [ $try = 3 ] && exit 1
  done
fi
echo ALLDONE
