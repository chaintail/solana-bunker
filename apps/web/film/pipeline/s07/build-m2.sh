#!/bin/bash
# Scene m2: the conspiracy m4c music treatment (film/conspiracy 70fecfa) on the scene's m1 music plan; audio-only remix on the locked picture.
# The mix runs on do-box (ffmpeg audio only, -vn; /home/claude/venvs/manim); only the mux (picture stream-copied from the scene's master and
# phone cut, as its m1 build did; AAC 192k on both) and the video md5 check run on dev-mac in ~/video-work/solana-bunker. Stems stay on do-box.
# usage: build-m2.sh <scene> <work root on do-box> <outbox dir>        (spec: <scene>-m2.json next to this script)
#   1. inputs in <work root>/in (the scene's delivered mix, the cue, the effect files, m1's delivered stems in in/m1), fetched from dev-mac
#      (read only) when missing: spec.fetch
#   2. music-m2.py -> finish-m3.py (-16 LUFS, true peak <= -1.3 dBTP, alimiter latency=1) -> w/<scene>-m2-final.wav and 24-bit stems
#   3. dev-mac: <mux.work>/<scene>-m2-final.wav; mux <mux.dst>.mp4 and -phone.mp4; video md5 source vs m2; mp4s copied back to <outbox>
#   4. verify-m2.py (sync, onsets, highs, dialogue - music, levels, loudness of the decoded mp4 audio); plot-levels-m2.py -> <outbox>/<scene>-m2-levels.png
set -euo pipefail
SC=$1; W=$2; OB=$3; P=$(cd "$(dirname "$0")" && pwd); PY=/home/claude/venvs/manim/bin/python; SPEC=$P/$SC-m2.json; N=$SC-m2
mkdir -p "$W/in/sfx" "$W/in/m1" "$W/w"
$PY -c 'import json,sys; [print(a, b) for a, b in json.load(open(sys.argv[1]))["fetch"]]' "$SPEC" | while read -r src dst; do
  [ -f "$W/$dst$(basename "$src")" ] || scp -q "dev-mac:$src" "$W/$dst"
done
MW=$($PY -c 'import json,sys; m=json.load(open(sys.argv[1]))["mux"]; print(m["work"], m["master"], m["phone"], m["dst"], sep="\n")' "$SPEC")
MWORK=$(sed -n 1p <<<"$MW"); MSRC=$(sed -n 2p <<<"$MW"); MPH=$(sed -n 3p <<<"$MW"); MDST=$(sed -n 4p <<<"$MW")
MARGS=$($PY -c 'import json,sys; print(json.load(open(sys.argv[1]))["mux"]["args"])' "$SPEC")
cd "$W"
$PY "$P/music-m2.py" "$SPEC" "$W" "w/$N" | tee w/build.log
$PY "$P/finish-m3.py" "w/$N" "w/$N-final.wav" "w/$N" | tee -a w/build.log
ssh dev-mac "mkdir -p ~/video-work/solana-bunker/$MWORK"
scp -q "w/$N-final.wav" "dev-mac:video-work/solana-bunker/$MWORK/"
ssh dev-mac "bash -s $(printf '%q ' "$MWORK/$N-final.wav" "$MSRC" "$MPH" "$MDST" "$MARGS")" <<'REMOTE' | tee w/mux.log
set -euo pipefail
FIN=$1; SRC=$2; PH=$3; DST=$4; ARGS=$5
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH; cd ~/video-work/solana-bunker
FFV="ffmpeg -nostdin -v error -y"
$FFV -i "$SRC" -i "$FIN" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k $ARGS "$DST.mp4"
$FFV -i "$PH" -i "$FIN" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k $ARGS "$DST-phone.mp4"
for f in "$SRC" "$DST.mp4" "$PH" "$DST-phone.mp4"; do
  echo "$f $(ffmpeg -nostdin -v error -i "$f" -map 0:v -c copy -f md5 -) $(ffprobe -v error -show_entries stream=codec_type,width,height,nb_frames,duration,bit_rate -of compact=p=0 "$f" | tr "\n" " ")"
done
REMOTE
scp -q "dev-mac:video-work/solana-bunker/$MDST.mp4" "dev-mac:video-work/solana-bunker/$MDST-phone.mp4" "$OB/"
$PY "$P/verify-m2.py" "$SPEC" "w/$N" "w/$N" "w/$N-final.wav" w/verify "$OB/$(basename "$MDST").mp4" "$OB/$(basename "$MDST")-phone.mp4" | tee w/verify.log
$PY "$P/plot-levels-m2.py" "$OB/$N-levels.png" w/verify/levels.npz "$SC"
