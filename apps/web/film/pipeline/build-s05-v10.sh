#!/bin/bash
# s05 (whiteboard) v10: the scene ends 0.53 s after the last word (2236 frames, 74.533 s; v9/m3 2287, 76.233 s). Picture: s05-capture-v10.sh on dev-mac
# (out/x12v10/seg). Audio: the m3 pipeline (build-s05-m3.sh) on m3-s05-v10.json: the same render cut at the new scene end with a 0.25 s fade, the dialogue cut
# there with the same fade (bed only), SFX unchanged. Python mixing/plotting run on do-box; all ffmpeg work runs on dev-mac.
# usage: build-s05-v10.sh <work root on do-box> <outbox dir>
#   1. inputs in <work root>/in as build-s05-m3.sh, plus m3's render in/m3/s04-s05-m3-music-unsplit.wav (the v10 render must equal it up to the end fade)
#   2. music-m3-workshop.py m3-s05-v10.json -> finish-m3.py (s05 -> s05-v10-final.wav + stems; s04 -> check only, PCM bit-identical to m2's s04-m2-audio.wav),
#      continuity-m3.py (finish, continuity, and verification on dev-mac; no local ffmpeg)
#   3. dev-mac: out/s05-v10-audio.wav, stems out/s05-v10-{dialogue,music,sfx}.wav, out/s04-s05-v10-music-unsplit.wav; mux out/s05-v10.mp4 (video stream-copied
#      from s05/out/x12v10/seg, aac mono 192k, -shortest) and out/s05-v10-phone.mp4 (960x540 lanczos crf 26, aac mono 192k); both copied to <outbox>
#   4. verify-m3.py, plot-levels-m3.py -> <outbox>/s05-v10-levels.png
set -euo pipefail
ROOT=$1; OB=$2; P=$(cd "$(dirname "$0")" && pwd); PY=/home/claude/venvs/manim/bin/python; WS=ws; T=v10
mkdir -p "$ROOT/in/s04" "$ROOT/in/s05" "$ROOT/in/sfx" "$ROOT/in/m1" "$ROOT/in/m2" "$ROOT/in/m3" "$ROOT/in/cues/4-workshop" "$ROOT/$WS" "$OB"
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
[ -f in/m3/s04-s05-m3-music-unsplit.wav ] || scp -q dev-mac:video-work/solana-bunker/out/s04-s05-m3-music-unsplit.wav in/m3/
# Keep every ffmpeg/ffprobe invocation on dev-mac, including audio decode and metering.
REMOTE_ROOT=video-work/solana-bunker/s05/out/x12v10/audio-work
ssh dev-mac 'bash -ls' <<'REMOTE'
mkdir -p ~/video-work/solana-bunker/s05/out/x12v10/audio-work/pipeline
REMOTE
$PY "$P/music-m3-workshop.py" "$P/m3-s05-v10.json" "$ROOT" "$WS" | tee "$WS/python-mix.log"
scp -qr in "$WS" "dev-mac:$REMOTE_ROOT/"
scp -q "$P/"{music-m3-workshop.py,music-m2-workshop.py,music-m4.py,finish-m3.py,continuity-m3.py,verify-m3.py,m3-s05-v10.json} "dev-mac:$REMOTE_ROOT/pipeline/"
ssh dev-mac 'bash -ls' <<'REMOTE' | tee "$WS/build.log"
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker/s05/out/x12v10/audio-work
PY=~/venvs/audio/bin/python
for s in s04 s05; do $PY pipeline/finish-m3.py "ws/$s-v10" "ws/$s-v10-final.wav" "ws/$s-v10"; done
$PY - <<'CHECK'
import json
import numpy as np
from scipy.io import wavfile
for previous in ('m2', 'm3'):
    assert json.load(open(f'ws/s04-s05-v10-vs-{previous}.json'))['s04_part_bit_identical_float32']
sr, a = wavfile.read('ws/s04-v10-final.wav')
sr2, b = wavfile.read('in/m2/s04-m2-audio.wav')
assert sr == sr2 and np.array_equal(a, b)
print('s04 final PCM bit-identical to m2; WAV encoder metadata may differ')
CHECK
$PY pipeline/continuity-m3.py ws/s04-s05-v10-music-unsplit.wav ws/s04-v10 ws/s05-v10 ws/s04-s05-v10-continuity.json
cp ws/s05-v10-final.wav ~/video-work/solana-bunker/out/s05-v10-audio.wav
for k in dialogue music sfx; do cp "ws/s05-v10-$k.wav" ~/video-work/solana-bunker/out/; done
cp ws/s04-s05-v10-music-unsplit.wav ~/video-work/solana-bunker/out/
REMOTE
ssh dev-mac 'bash -ls' <<'REMOTE' | tee $WS/mux.log
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH; cd ~/video-work/solana-bunker
deadline=$((SECONDS + 1800))
while ! grep -q ALLDONE s05/out/x12v10/capture-v10.log; do
  if grep -q 'FAILED' s05/out/x12v10/capture-v10.log || [ "$SECONDS" -ge "$deadline" ]; then
    echo "capture failed or timed out"; exit 1
  fi
  sleep 10
done
grep -q ALLDONE s05/out/x12v10/capture-v10.log || { echo "capture not finished"; exit 1; }
[ "$(wc -l < s05/out/x12v10/seg/list.txt | tr -d ' ')" = 8 ] || { echo "seg list incomplete"; exit 1; }
FFV="ffmpeg -nostdin -v error -y"; A=out/s05-v10-audio.wav
nf() { ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "$1"; }
$FFV -f concat -safe 0 -i s05/out/x12v10/seg/list.txt -i $A -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ac 1 -movflags +faststart -shortest out/s05-v10.mp4
$FFV -i out/s05-v10.mp4 -i $A -map 0:v -map 1:a -vf scale=960:540:flags=lanczos -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 192k -ac 1 -movflags +faststart -shortest out/s05-v10-phone.mp4
for f in s05-m3 s05-v10 s05-m3-phone s05-v10-phone; do
  echo "$f frames=$(nf out/$f.mp4) $(ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,nb_frames,duration,bit_rate,channels,sample_rate -of compact=p=0 out/$f.mp4 | tr '\n' ' ')"
done
REMOTE
scp -q dev-mac:video-work/solana-bunker/out/s05-$T.mp4 dev-mac:video-work/solana-bunker/out/s05-$T-phone.mp4 "$OB/"
ssh dev-mac 'bash -ls' <<'REMOTE' | tee "$WS/verify-s05.log"
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker/s05/out/x12v10/audio-work
~/venvs/audio/bin/python pipeline/verify-m3.py ws/s05-v10 ws/s05-v10 ws/s05-v10-final.wav ws/verify-s05 ~/video-work/solana-bunker/out/s05-v10.mp4 ~/video-work/solana-bunker/out/s05-v10-phone.mp4
REMOTE
scp -qr "dev-mac:$REMOTE_ROOT/ws/." "$WS/"
$PY "$P/plot-levels-m3.py" "$OB/s05-$T-levels.png" "$WS/verify-s05/levels.npz" "s05 whiteboard v10"
