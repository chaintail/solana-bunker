#!/bin/bash
# s05 (whiteboard) m3: the workshop cue continues from the freeze through the robbery to the scene end (m3-s05-workshop.json); picture unchanged (video
# stream-copied from out/s05-v9.mp4 and out/s05-v9-phone.mp4). The mix runs on do-box (ffmpeg audio only, /home/claude/venvs/manim); only the mux and the
# video md5 check run on dev-mac in ~/video-work/solana-bunker.
# usage: build-s05-m3.sh <work root on do-box> <outbox dir>
#   1. inputs in <work root>/in: m2's (build-s04-s05-m2.sh) plus m2's delivered s04/s05 audio, music stems and unsplit render in in/m2; fetched from
#      dev-mac when missing
#   2. music-m3-workshop.py (one render across both scenes, split at 46.5 s; the s04 part must equal m2's) -> finish-m3.py: s05 -> s05-m3-final.wav and
#      24-bit stems; s04 -> s04-m3-final.wav as a check only, which must be byte-identical to m2's delivered out/s04-m2-audio.wav (s04 is not re-delivered);
#      continuity-m3.py (stems / scene gains concatenate to the render)
#   3. dev-mac: out/s05-m3-audio.wav, stems out/s05-m3-{dialogue,music,sfx}.wav, out/s04-s05-m3-music-unsplit.wav; mux out/s05-m3.mp4 and -phone.mp4
#      (video copied from s05-v9 / s05-v9-phone, aac mono 192k, -shortest), video md5 v9 vs m3; mp4s copied to <outbox>
#   4. verify-m3.py, plot-levels-m3.py -> <outbox>/s05-m3-levels.png
set -euo pipefail
ROOT=$1; OB=$2; P=$(cd "$(dirname "$0")" && pwd); PY=/home/claude/venvs/manim/bin/python; WS=ws
mkdir -p "$ROOT/in/s04" "$ROOT/in/s05" "$ROOT/in/sfx" "$ROOT/in/m1" "$ROOT/in/m2" "$ROOT/in/cues/4-workshop" "$ROOT/$WS"
cd "$ROOT"
[ -f in/s04/audio-final.wav ] || scp -q dev-mac:video-work/solana-bunker/out/s04/v8x12/audio-final.wav in/s04/
[ -f in/s05/audio-final.wav ] || scp -q dev-mac:video-work/solana-bunker/s05/out/x12/audio-final.wav in/s05/
for f in suno-4-mechanical-curiosity-a.wav analysis.json; do [ -f "in/cues/4-workshop/$f" ] || scp -q "dev-mac:audio-work/solana-bunker/music/suno/4-workshop/$f" in/cues/4-workshop/; done
for f in stamp-thump-2-stamp-bright-shelved glass-shatter-2-glass-panel cash-register-1-purchase confetti-pop-1-party-popper camera-shutter-2-yn500-single; do
  [ -f "in/sfx/$f.wav" ] || scp -q "dev-mac:audio-work/solana-bunker/out/work/$f.wav" in/sfx/
done
[ -f in/m1/s04-s05-m1-report.json ] || scp -q dev-mac:video-work/solana-bunker/out/s04-s05-m1-report.json in/m1/
for f in s04-m2-audio s05-m2-audio s04-m2-music s05-m2-music s04-s05-m2-music-unsplit; do
  [ -f "in/m2/$f.wav" ] || scp -q "dev-mac:video-work/solana-bunker/out/$f.wav" in/m2/
done
$PY "$P/music-m3-workshop.py" "$P/m3-s05-workshop.json" "$ROOT" "$WS" | tee $WS/build.log
for s in s04 s05; do $PY "$P/finish-m3.py" "$WS/$s-m3" "$WS/$s-m3-final.wav" "$WS/$s-m3" | tee -a $WS/build.log; done
python3 -c "import json,sys; v=json.load(open('$WS/s04-s05-m3-vs-m2.json')); sys.exit(0 if v['s04_part_bit_identical_float32'] else 's04 music differs from m2')"
cmp "$WS/s04-m3-final.wav" in/m2/s04-m2-audio.wav || { echo "s04 check FAILED: s04-m3-final.wav differs from m2's s04-m2-audio.wav"; exit 1; }
echo "s04 check: s04-m3-final.wav is byte-identical to m2's s04-m2-audio.wav ($(md5sum < in/m2/s04-m2-audio.wav | cut -c1-32))" | tee -a $WS/build.log
$PY "$P/continuity-m3.py" "$WS/s04-s05-m3-music-unsplit.wav" "$WS/s04-m3" "$WS/s05-m3" "$WS/s04-s05-m3-continuity.json" | tee -a $WS/build.log
scp -q "$WS/s05-m3-final.wav" "dev-mac:video-work/solana-bunker/out/s05-m3-audio.wav"
for k in dialogue music sfx; do scp -q "$WS/s05-m3-$k.wav" "dev-mac:video-work/solana-bunker/out/"; done
scp -q "$WS/s04-s05-m3-music-unsplit.wav" dev-mac:video-work/solana-bunker/out/
LOCAL_MD5="$(md5sum < "$WS/s05-m3-final.wav" | cut -c1-32) $(md5sum < in/m2/s04-m2-audio.wav | cut -c1-32)"
ssh dev-mac bash -s -- $LOCAL_MD5 <<'REMOTE' | tee $WS/mux.log
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH; cd ~/video-work/solana-bunker
[ "$(md5 -q out/s05-m3-audio.wav)" = "$1" ] || { echo "s05-m3-audio.wav md5 mismatch after copy"; exit 1; }
echo "s04 m2 audio on dev-mac: $(md5 -q out/s04-m2-audio.wav) (do-box check copy $2)"
FFV="ffmpeg -nostdin -v error -y"
$FFV -i out/s05-v9.mp4 -i out/s05-m3-audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ac 1 -movflags +faststart -shortest out/s05-m3.mp4
$FFV -i out/s05-v9-phone.mp4 -i out/s05-m3-audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ac 1 -movflags +faststart -shortest out/s05-m3-phone.mp4
for f in s05-v9 s05-m3 s05-v9-phone s05-m3-phone; do
  echo "$f $(ffmpeg -nostdin -v error -i out/$f.mp4 -map 0:v -c copy -f md5 -) $(ffprobe -v error -show_entries stream=codec_type,width,height,nb_frames,duration,bit_rate,channels -of compact=p=0 out/$f.mp4 | tr "\n" " ")"
done
REMOTE
scp -q dev-mac:video-work/solana-bunker/out/s05-m3.mp4 dev-mac:video-work/solana-bunker/out/s05-m3-phone.mp4 "$OB/"
$PY "$P/verify-m3.py" "$WS/s05-m3" "$WS/s05-m3" "$WS/s05-m3-final.wav" "$WS/verify-s05" "$OB/s05-m3.mp4" "$OB/s05-m3-phone.mp4" | tee "$WS/verify-s05.log"
$PY "$P/plot-levels-m3.py" "$OB/s05-m3-levels.png" "$WS/verify-s05/levels.npz" "s05 whiteboard"
