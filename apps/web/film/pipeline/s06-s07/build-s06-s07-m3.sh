#!/bin/bash
# s06 (speakeasy) + s07 (seminar + alley) m3: one noir cue rendered across both scenes and split at the cut sample; the lecture at -4 dB, back up on
# the alley cut. Audio-only remix on the locked pictures (video stream-copied from the m2 sources). Same directory on film/s06 and film/s07.
# The mix runs on do-box (ffmpeg audio only, -vn; /home/claude/venvs/manim); only the mux and the video md5 check run on dev-mac in
# ~/video-work/solana-bunker. Stems stay on do-box.
# usage: build-s06-s07-m3.sh <work root on do-box> <outbox dir> [<m2 work root with s06/w and s07/w>]
#   1. inputs in <work root>/in: both scenes' delivered mixes, the noir cue and analysis.json, the effect files (fetched from dev-mac when missing,
#      m3-noir.json fetch), m2's delivered stems and loudness reports in in/m2 (copied from the m2 work root when missing; the sfx null and the
#      m2 comparison)
#   2. music-m3-noir.py (one render, split at the cut) -> finish-m3.py per scene (-16 LUFS, true peak <= -1.3 dBTP, limiter latency=1); the join
#      compensation (s06 gain - s07 gain) is fed back into the render until the scene gains repeat
#   3. continuity-m3.py: split == render, no level step and no click at the cut (delivered music and the concatenated final wavs), the loop
#   4. dev-mac: mux <scene>/out/<scene>-m3.mp4 and -phone.mp4 (video copied, AAC 192k mono, -shortest), video md5 source vs m3; copied to <outbox>
#   5. verify-m2.py per scene (ref = m2), plot-levels-m3.py -> <outbox>/s06-s07-m3-levels.png and the section level report
set -euo pipefail
W=$1; OB=$2; M2=${3:-}; P=$(cd "$(dirname "$0")" && pwd); PY=/home/claude/venvs/manim/bin/python; SPEC=$P/m3-noir.json
mkdir -p "$W/in/s06" "$W/in/s07" "$W/in/cue" "$W/in/sfx" "$W/in/m2" "$W/w"
$PY -c 'import json,sys; [print(a, b) for a, b in json.load(open(sys.argv[1]))["fetch"]]' "$SPEC" | while read -r src dst; do
  [ -f "$W/$dst$(basename "$src")" ] || scp -q "dev-mac:$src" "$W/$dst"
done
for s in s06 s07; do for f in $s-m2-dialogue.wav $s-m2-music.wav $s-m2-sfx.wav $s-m2-loudness.json; do
  [ -f "$W/in/m2/$f" ] || cp -p "$M2/$s/w/$f" "$W/in/m2/"
done; done
cd "$W"
gain() { $PY -c 'import json,sys; print(round(json.load(open(sys.argv[1]))["linear_gain_db"], 3))' "w/$1-m3-loudness.json"; }
COMP=0
for pass in 1 2 3 4; do
  $PY "$P/music-m3-noir.py" "$SPEC" "$W" w "$COMP" | tee w/build.log
  for s in s06 s07; do $PY "$P/finish-m3.py" "w/$s-m3" "w/$s-m3-final.wav" "w/$s-m3" | tee -a w/build.log; done
  NEXT=$($PY -c 'import sys; print(round(float(sys.argv[1]) - float(sys.argv[2]), 3))' "$(gain s06)" "$(gain s07)")
  echo "pass $pass: join compensation $COMP dB, scene gains s06 $(gain s06) / s07 $(gain s07) -> $NEXT" | tee -a w/build.log
  if $PY -c 'import sys; sys.exit(0 if abs(float(sys.argv[1]) - float(sys.argv[2])) < 0.005 else 1)' "$COMP" "$NEXT"; then break; fi
  [ "$pass" = 4 ] && { echo "join compensation did not settle" >&2; exit 1; }
  COMP=$NEXT
done
$PY "$P/continuity-m3.py" "$SPEC" "$W" w w/s06-s07-m3-continuity.json | tee w/continuity.log
for s in s06 s07; do
  MW=$($PY -c 'import json,sys; m=[x for x in json.load(open(sys.argv[1]))["scenes"] if x["name"]==sys.argv[2]][0]["mux"]; print(m["work"], m["master"], m["phone"], m["dst"], m["args"], sep="\n")' "$SPEC" "$s")
  MWORK=$(sed -n 1p <<<"$MW"); MSRC=$(sed -n 2p <<<"$MW"); MPH=$(sed -n 3p <<<"$MW"); MDST=$(sed -n 4p <<<"$MW"); MARGS=$(sed -n 5p <<<"$MW")
  ssh dev-mac "mkdir -p ~/video-work/solana-bunker/$MWORK"
  scp -q "w/$s-m3-final.wav" "dev-mac:video-work/solana-bunker/$MWORK/"
  ssh dev-mac "bash -s $(printf '%q ' "$MWORK/$s-m3-final.wav" "$MSRC" "$MPH" "$MDST" "$MARGS")" <<'REMOTE' | tee "w/mux-$s.log"
set -euo pipefail
FIN=$1; SRC=$2; PH=$3; DST=$4; ARGS=$5
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH; cd ~/video-work/solana-bunker
FFV="ffmpeg -nostdin -v error -y"
$FFV -i "$SRC" -i "$FIN" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k $ARGS "$DST.mp4"
$FFV -i "$PH" -i "$FIN" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k $ARGS "$DST-phone.mp4"
for f in "$SRC" "$DST.mp4" "$PH" "$DST-phone.mp4"; do
  echo "$f $(ffmpeg -nostdin -v error -i "$f" -map 0:v -c copy -f md5 -) $(ffprobe -v error -show_entries stream=codec_type,width,height,nb_frames,duration,bit_rate,channels -of compact=p=0 "$f" | tr "\n" " ")"
done
REMOTE
  scp -q "dev-mac:video-work/solana-bunker/$MDST.mp4" "dev-mac:video-work/solana-bunker/$MDST-phone.mp4" "$OB/"
  $PY "$P/verify-m2.py" "w/$s-m3-spec.json" "w/$s-m3" "w/$s-m3" "w/$s-m3-final.wav" "w/verify-$s" "$OB/$(basename "$MDST").mp4" "$OB/$(basename "$MDST")-phone.mp4" | tee "w/verify-$s.log"
done
$PY "$P/plot-levels-m3.py" "$SPEC" "$W" w "$OB/s06-s07-m3-levels.png" w/s06-s07-m3-levels.json | tee w/levels.log
