#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. v13 (Liam, 2026-10-18: two script cuts, conspiracy-v13-edit.py): s03 data-duration 63.9 -> 59.38,
# 1598 -> 1485 frames at 1.2x (113 frames removed: x12b output frames 787-814 and 987-1071). The scene is captured from a private copy of the film
# tree, film-v13/ (base/fonts/dossier css, fonts, lib and capture.mjs copied from film/, s03-conspiracy.html and data/conspiracy-* from the v13
# commit), so film/ is left as x12b had it. capture.mjs --speed=1.2 samples output frame k at page time k/30 * 1.2; nothing before x12b global
# 31.4456 s (s03 output frame 611.1) changes, so:
#   s01-title       175 frames: x12b chunks c00-c02 kept (copied)
#   s03-conspiracy 1485 frames: x12b chunks c00-c08 (output frames 0-539) kept (copied); c09-c24 captured (c09 is unchanged picture and is
#                  compared with x12b's c09 as a check that the v13 page renders the uncut part identically)
#   hat: render-consp-x12/hat is reused by the build (unchanged, it starts before the first cut)
# Same method as x12b: two discarded warm-up shots per page load (capture.mjs), ONE capture at a time, 60-frame chunks, stall watchdog, 3 tries.
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker; O=out/consp-v13/seg; R=render-consp-v13/frames; mkdir -p $O $R
SPEED=1.2; CH=60; HATN=38
find $R -name 'f*.png' -delete
run() { # log out from to extra...   one capture with the stall watchdog; 0 when it wrote the expected number of PNGs into out
  local log=$1 out=$2 a=$3 b=$4; shift 4; local pid last=-1 cnt idle=0
  ( cd film-v13 && exec node scripts/capture.mjs "$@" --speed=$SPEED --from=$(python3 -c "print($a/30)") --to=$(python3 -c "print($b/30)") --out=../$out ) > $log 2>&1 &
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
    if run $O/cap-$s-$n.log $R $a $((a+c)) $s; then
      ffmpeg -nostdin -v error -y -framerate 30 -start_number $a -i $R/f%05d.png -frames:v $c -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p -r 30 $O/$s-c$n.mp4 \
        && find $R -name 'f*.png' -delete && echo "$s chunk $n ($a..$((a+c-1))) done $(date +%H:%M:%S)" && return 0
    fi
    echo "$s chunk $n try $try failed, retrying"; find $R -name 'f*.png' -delete
  done
  echo "$s chunk $n FAILED"; return 1
}
for n in 00 01 02; do [ -s $O/s01-title-c$n.mp4 ] || cp out/consp-x12b/seg/s01-title-c$n.mp4 $O/; done
for ((i=0; i<=8; i++)); do n=$(printf '%02d' $i); [ -s $O/s03-conspiracy-c$n.mp4 ] || cp out/consp-x12b/seg/s03-conspiracy-c$n.mp4 $O/; done
: > $O/list.txt
for spec in s01-title:175 s03-conspiracy:1485; do
  s=${spec%%:*}; M=${spec##*:}
  for ((i=0; i*CH<M; i++)); do
    a=$((i*CH)); c=$(( M-a < CH ? M-a : CH )); n=$(printf '%02d' $i)
    if [ -s $O/$s-c$n.mp4 ] && [ "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 $O/$s-c$n.mp4)" = "$c" ]; then echo "$s chunk $n kept"; else chunk $s $n $a $c || exit 1; fi
    echo "file '$PWD/$O/$s-c$n.mp4'" >> $O/list.txt
  done
done
# check: the recaptured c09 (unchanged picture) against x12b's c09, decoded frame md5s
a=$(ffmpeg -nostdin -v error -i out/consp-x12b/seg/s03-conspiracy-c09.mp4 -f framemd5 - | grep -v '^#' | md5 -q)
b=$(ffmpeg -nostdin -v error -i $O/s03-conspiracy-c09.mp4 -f framemd5 - | grep -v '^#' | md5 -q)
echo "c09 decoded frames v13 vs x12b: $([ "$a" = "$b" ] && echo identical || echo DIFFERENT) ($a / $b)"
[ "$(find render-consp-x12/hat -name 'f*.png' | wc -l)" -eq $HATN ] || { echo "render-consp-x12/hat is not $HATN frames"; exit 1; }
echo ALLDONE
