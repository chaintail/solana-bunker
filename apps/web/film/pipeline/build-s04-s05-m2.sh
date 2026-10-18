#!/bin/bash
# s04 (bunker) + s05 (whiteboard) m2: m1's audio with the music treatment locked on conspiracy m4c (+9, word-speed ducking, high cut), pictures unchanged
# (video stream-copied from out/s04-v8-x12.mp4, s05-v8-x12.mp4 and their -phone files). Same file on film/s04 and film/s05. The mix runs on do-box
# (ffmpeg audio only, /home/claude/venvs/manim); only the mux and the video md5 check run on dev-mac in ~/video-work/solana-bunker.
# usage: build-s04-s05-m2.sh <work root on do-box> <outbox dir>
#   1. inputs in <work root>/in (the delivered audio-final.wav of both scenes, the workshop cue and its analysis.json, the five effect files, m1's stems and
#      report); fetched from dev-mac when missing
#   2. music-m2-workshop.py (one render across both scenes, split at 46.5 s) -> finish-m3.py per scene (-16 LUFS, true peak <= -1.3 dBTP, limiter
#      latency-compensated) -> <scene>-m2-final.wav and 24-bit stems; continuity-m2.py (stems / scene gains concatenate to the render)
#   3. dev-mac: out/<scene>-m2-audio.wav, stems out/<scene>-m2-{dialogue,music,sfx}.wav, out/s04-s05-m2-music-unsplit.wav; mux out/<scene>-m2.mp4 and
#      -phone.mp4 (as m1: video copied, aac mono, -shortest; 192k both), video md5 source vs m2; mp4s copied to <outbox>
#   4. verify-m2.py per scene, plot-levels-m2.py -> <outbox>/<scene>-m2-levels.png
set -euo pipefail
ROOT=$1; OB=$2; P=$(cd "$(dirname "$0")" && pwd); PY=/home/claude/venvs/manim/bin/python; WS=ws
mkdir -p "$ROOT/in/s04" "$ROOT/in/s05" "$ROOT/in/sfx" "$ROOT/in/m1" "$ROOT/in/cues/4-workshop" "$ROOT/$WS"
cd "$ROOT"
[ -f in/s04/audio-final.wav ] || scp -q dev-mac:video-work/solana-bunker/out/s04/v8x12/audio-final.wav in/s04/
[ -f in/s05/audio-final.wav ] || scp -q dev-mac:video-work/solana-bunker/s05/out/x12/audio-final.wav in/s05/
for f in suno-4-mechanical-curiosity-a.wav analysis.json; do [ -f "in/cues/4-workshop/$f" ] || scp -q "dev-mac:audio-work/solana-bunker/music/suno/4-workshop/$f" in/cues/4-workshop/; done
for f in stamp-thump-2-stamp-bright-shelved glass-shatter-2-glass-panel cash-register-1-purchase confetti-pop-1-party-popper camera-shutter-2-yn500-single; do
  [ -f "in/sfx/$f.wav" ] || scp -q "dev-mac:audio-work/solana-bunker/out/work/$f.wav" in/sfx/
done
[ -f in/m1/s04-s05-m1-report.json ] || scp -q dev-mac:video-work/solana-bunker/out/s04-s05-m1-report.json in/m1/
for s in s04 s05; do for k in dialogue music sfx; do [ -f "in/m1/$s-m1-$k.wav" ] || scp -q "dev-mac:video-work/solana-bunker/out/$s-m1-$k.wav" in/m1/; done; done
$PY "$P/music-m2-workshop.py" "$P/m2-workshop.json" "$ROOT" "$WS" | tee $WS/build.log
for s in s04 s05; do $PY "$P/finish-m3.py" "$WS/$s-m2" "$WS/$s-m2-final.wav" "$WS/$s-m2" | tee -a $WS/build.log; done
$PY "$P/continuity-m2.py" "$WS/s04-s05-m2-music-unsplit.wav" "$WS/s04-m2" "$WS/s05-m2" | tee -a $WS/build.log
for s in s04 s05; do
  scp -q "$WS/$s-m2-final.wav" "dev-mac:video-work/solana-bunker/out/$s-m2-audio.wav"
  for k in dialogue music sfx; do scp -q "$WS/$s-m2-$k.wav" "dev-mac:video-work/solana-bunker/out/"; done
done
scp -q "$WS/s04-s05-m2-music-unsplit.wav" dev-mac:video-work/solana-bunker/out/
ssh dev-mac bash -s <<'REMOTE' | tee $WS/mux.log
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH; cd ~/video-work/solana-bunker
FFV="ffmpeg -nostdin -v error -y"
for s in s04 s05; do
  $FFV -i "out/$s-v8-x12.mp4" -i "out/$s-m2-audio.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ac 1 -movflags +faststart -shortest "out/$s-m2.mp4"
  $FFV -i "out/$s-v8-x12-phone.mp4" -i "out/$s-m2-audio.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ac 1 -movflags +faststart -shortest "out/$s-m2-phone.mp4"
  for f in "$s-v8-x12" "$s-m2" "$s-v8-x12-phone" "$s-m2-phone"; do
    echo "$f $(ffmpeg -nostdin -v error -i out/$f.mp4 -map 0:v -c copy -f md5 -) $(ffprobe -v error -show_entries stream=codec_type,width,height,nb_frames,duration,bit_rate,channels -of compact=p=0 out/$f.mp4 | tr "\n" " ")"
  done
done
REMOTE
for s in s04 s05; do
  scp -q "dev-mac:video-work/solana-bunker/out/$s-m2.mp4" "dev-mac:video-work/solana-bunker/out/$s-m2-phone.mp4" "$OB/"
  $PY "$P/verify-m2.py" "$WS/$s-m2" "$WS/$s-m2" "$WS/$s-m2-final.wav" "$WS/verify-$s" "$OB/$s-m2.mp4" "$OB/$s-m2-phone.mp4" | tee "$WS/verify-$s.log"
done
$PY "$P/plot-levels-m2.py" "$OB/s04-m2-levels.png" "$WS/verify-s04/levels.npz" "s04 bunker"
$PY "$P/plot-levels-m2.py" "$OB/s05-m2-levels.png" "$WS/verify-s05/levels.npz" "s05 whiteboard"
