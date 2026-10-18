#!/bin/bash
# Conspiracy m4 (m2 with the music from frame 0, intro levelled, tick highs cut; m4c +9 dB, m4d +12 dB over m2 under speech): audio-only remix
# on the locked x12b picture. The mix runs on do-box (ffmpeg audio only, /home/claude/venvs/manim); only the mux (picture stream-copied from
# out/conspiracy-x12b.mp4 / -phone.mp4) and the video md5 check run on dev-mac in ~/video-work/solana-bunker.
# usage: build-conspiracy-m4.sh <work root on do-box> <outbox dir> <variant>...      (variants: c d -> conspiracy-m4c.json, conspiracy-m4d.json)
#   per variant, in <work root>/m4<v>:
#   1. inputs in in/ (x12b's delivered mix, the cue, the effect files, m2's delivered stems in in/m2); fetched from dev-mac when missing;
#      the folder-close file comes from the composer outbox (sfx/folder-close-2-doc-folder.mp3)
#   2. music-m4.py -> finish-m3.py (unchanged: -16 LUFS, true peak <= -1.3 dBTP) -> m4<v>-final.wav and 24-bit stems
#   3. dev-mac: out/consp-m4<v>/m4<v>-final.wav, stems out/conspiracy-m4<v>-{dialogue,music,sfx}.wav; mux out/conspiracy-m4<v>.mp4 and -phone.mp4
#      (aac 192k both), video md5 source vs m4<v>; copy the mp4s back to <outbox>
#   4. verify-m4.py (sync, onsets, start, highs, guard, levels, loudness of the decoded mp4 audio)
#   then plot-levels-m4.py -> <outbox>/conspiracy-m4-levels.png (all variants against m2)
set -euo pipefail
ROOT=$1; OB=$2; shift 2; P=$(cd "$(dirname "$0")" && pwd); PY=/home/claude/venvs/manim/bin/python
PLOTS=()
for v in "$@"; do
N=m4$v; W=$ROOT/$N
mkdir -p "$W/in/sfx" "$W/in/m2" "$W/w"
if [ ! -f "$W/in/audio-final.wav" ]; then
  scp -q dev-mac:video-work/solana-bunker/out/consp-x12b/audio-final.wav "$W/in/"
  scp -q dev-mac:audio-work/solana-bunker/music/suno/3-conspiracy/suno-3-the-clock-ticks-twice-a.wav "$W/in/"
  for f in stamp-thump-1-traditional-stamp stamp-thump-2-stamp-bright-shelved; do scp -q "dev-mac:audio-work/solana-bunker/out/work/$f.wav" "$W/in/sfx/"; done
fi
if [ ! -f "$W/in/m2/conspiracy-m2-music.wav" ]; then
  for k in dialogue music sfx; do scp -q "dev-mac:video-work/solana-bunker/out/conspiracy-m2-$k.wav" "$W/in/m2/"; done
fi
cp "$OB/sfx/folder-close-2-doc-folder.mp3" "$W/in/sfx/"
(
cd "$W"
$PY "$P/music-m4.py" "$P/conspiracy-$N.json" "$W" "w/$N" | tee w/build.log
$PY "$P/finish-m3.py" "w/$N" "w/$N-final.wav" "w/conspiracy-$N" | tee -a w/build.log
ssh dev-mac "mkdir -p ~/video-work/solana-bunker/out/consp-$N"
scp -q "w/$N-final.wav" "dev-mac:video-work/solana-bunker/out/consp-$N/"
for k in dialogue music sfx; do scp -q "w/conspiracy-$N-$k.wav" "dev-mac:video-work/solana-bunker/out/"; done
ssh dev-mac bash -s "$N" <<'REMOTE' | tee w/mux.log
set -euo pipefail
N=$1
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH; cd ~/video-work/solana-bunker
FFV="ffmpeg -nostdin -v error -y"
$FFV -i out/conspiracy-x12b.mp4 -i "out/consp-$N/$N-final.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart "out/conspiracy-$N.mp4"
$FFV -i out/conspiracy-x12b-phone.mp4 -i "out/consp-$N/$N-final.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart "out/conspiracy-$N-phone.mp4"
for f in conspiracy-x12b "conspiracy-$N" conspiracy-x12b-phone "conspiracy-$N-phone"; do
  echo "$f $(ffmpeg -nostdin -v error -i out/$f.mp4 -map 0:v -c copy -f md5 -) $(ffprobe -v error -show_entries stream=codec_type,width,height,nb_frames,duration,bit_rate -of compact=p=0 out/$f.mp4 | tr "\n" " ")"
done
REMOTE
scp -q "dev-mac:video-work/solana-bunker/out/conspiracy-$N.mp4" "dev-mac:video-work/solana-bunker/out/conspiracy-$N-phone.mp4" "$OB/"
$PY "$P/verify-m4.py" "$P/conspiracy-$N.json" "w/$N" "w/conspiracy-$N" "w/$N-final.wav" w/verify "$OB/conspiracy-$N.mp4" "$OB/conspiracy-$N-phone.mp4" | tee w/verify.log
)
PLOTS+=("$N=$W/w/verify/levels.npz")
done
$PY "$P/plot-levels-m4.py" "$OB/conspiracy-m4-levels.png" "${PLOTS[@]}"
