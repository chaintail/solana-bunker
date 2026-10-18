#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/opening-v9 (film/ = rsync of film/opening-v8 apps/web/film, its own copy). Opening v9 (Liam 2026-10-16) captures
# only the three cards in front of the desk; the desk segment and the hold are x11's (opening-x11/out/final), unchanged.
#   s00-intro          sponsor card at --speed=1.2 (its animations are fixed times, the read is atempo 1.2): 147 scene frames -> 123
#   s00b-advisory-v9   advisory card re-timed to the 1.2x read (data/s00b-words-v9.js): 347 frames
#   s00c-ident         the Chaintail News Network ident with BREAKING NEWS (port of s11-cnn.html C0/C1): 66 frames
# 60-frame chunks (dev-mac's internal disk is nearly full: Chrome's profile goes to tmp/chrome on the shared volume via TMPDIR). Every chunk is a fresh Chrome,
# and capture.mjs shoots two warm-up frames per load (stale frame-0 paint at chunk starts). A chunk with no new PNG for 120 s is killed and retried (3 tries).
# Each chunk -> out/cap/<scene>/cNN.mkv (FFV1), PNGs deleted; chunks already encoded with the right count are kept on a re-run. Leaves out/cap/<scene>/list.txt.
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/opening-v9; mkdir -p tmp/chrome render out/cap; export TMPDIR=$PWD/tmp/chrome
CH=60
nfr() { ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "$1"; }
chunk() { # scene speed n first count
  local sc=$1 sp=$2 n=$3 a=$4 c=$5 try pid last cnt idle
  for try in 1 2 3; do
    find render -name 'f*.png' -delete
    ( cd film && exec node scripts/capture.mjs $sc --speed=$sp --from=$(python3 -c "print($a/30)") --to=$(python3 -c "print(($a+$c)/30)") --out=../render ) > out/cap/$sc/cap-$n.log 2>&1 &
    pid=$!; last=-1; idle=0
    while kill -0 $pid 2>/dev/null; do
      sleep 5; cnt=$(find render -name 'f*.png' | wc -l)
      if [ "$cnt" -eq "$last" ]; then idle=$((idle+5)); else idle=0; last=$cnt; fi
      if [ $idle -ge 120 ]; then echo "$sc chunk $n try $try: stalled at $cnt PNGs, killing pid $pid"; kill -TERM $pid; sleep 3; kill -KILL $pid 2>/dev/null; fi
    done
    wait $pid; cnt=$(find render -name 'f*.png' | wc -l)
    if [ "$cnt" -eq "$c" ]; then
      ffmpeg -nostdin -v error -y -framerate 30 -start_number $a -i render/f%05d.png -frames:v $c -c:v ffv1 -level 3 -pix_fmt bgr0 -r 30 out/cap/$sc/c$n.mkv \
        && find render -name 'f*.png' -delete && echo "$sc chunk $n ($a..$((a+c-1))) done" && return 0
    fi
    echo "$sc chunk $n try $try: $cnt/$c PNGs, retrying"
  done
  echo "$sc chunk $n FAILED"; return 1
}
scene() { # scene speed frames
  local sc=$1 sp=$2 M=$3 i a c n; mkdir -p out/cap/$sc; : > out/cap/$sc/list.txt
  for ((i=0; i*CH<M; i++)); do
    a=$((i*CH)); c=$(( M-a < CH ? M-a : CH )); n=$(printf '%02d' $i)
    if [ -s out/cap/$sc/c$n.mkv ] && [ "$(nfr out/cap/$sc/c$n.mkv)" = "$c" ]; then echo "$sc chunk $n kept"; else chunk $sc $sp $n $a $c || return 1; fi
    echo "file '$PWD/out/cap/$sc/c$n.mkv'" >> out/cap/$sc/list.txt
  done
}
scene s00c-ident 1 66 || exit 1
scene s00-intro 1.2 123 || exit 1
scene s00b-advisory-v9 1 347 || exit 1
echo ALLDONE
