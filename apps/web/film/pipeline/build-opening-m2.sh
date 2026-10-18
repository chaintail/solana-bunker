#!/bin/bash
# Opening m2: v11's audio with the music treatment locked on conspiracy m4c (+9, word-speed ducking, high cut), picture unchanged (video stream-copied
# from out/opening-v11.mp4 / -phone.mp4). The mix runs on do-box (ffmpeg audio only, /home/claude/venvs/manim); only the mux and the video md5 check run
# on dev-mac in ~/video-work/solana-bunker.
# usage: build-opening-m2.sh <work root on do-box> <outbox dir>
#   1. inputs in <work root>/in (v11's stems at its final gain: dialogue-sfx, stings, music (reference); work/voice-final (the sidechain key); the two
#      cues); fetched from dev-mac when missing
#   2. music-m2-opening.py -> finish-m3.py (-16 LUFS, true peak <= -1.3 dBTP, limiter latency-compensated) -> opening-m2-final.wav and 24-bit stems
#   3. dev-mac: out/opening-m2/opening-m2-final.wav, stems out/opening-m2-{dialogue,music,sfx}.wav (dialogue = voices and the brown-noise bed, sfx = jingles
#      A and C); mux out/opening-m2.mp4 and -phone.mp4 (video copied from v11 / v11-phone, aac 192k both), video md5 v11 vs m2; mp4s copied to <outbox>
#   4. verify-m2.py (sync, placement, onsets, guard, levels, highs, loudness of the decoded mp4 audio), plot-levels-m2.py -> <outbox>/opening-m2-levels.png
set -euo pipefail
ROOT=$1; OB=$2; P=$(cd "$(dirname "$0")" && pwd); PY=/home/claude/venvs/manim/bin/python; N=opening-m2; W=$ROOT/opening
mkdir -p "$ROOT/in/opening" "$ROOT/in/cues/1-sponsor" "$ROOT/in/cues/2-news" "$W"
if [ ! -f "$ROOT/in/opening/work-voice-final.wav" ]; then
  for k in dialogue-sfx music stings; do scp -q "dev-mac:video-work/solana-bunker/opening-v11/out/stems/$k.wav" "$ROOT/in/opening/"; done
  scp -q dev-mac:video-work/solana-bunker/opening-v11/out/work/voice-final.wav "$ROOT/in/opening/work-voice-final.wav"
fi
[ -f "$ROOT/in/cues/1-sponsor/suno-1-reassuring-groove-a.wav" ] || scp -q dev-mac:audio-work/solana-bunker/music/suno/1-sponsor/suno-1-reassuring-groove-a.wav "$ROOT/in/cues/1-sponsor/"
[ -f "$ROOT/in/cues/2-news/suno-2-breaking-news-a.wav" ] || scp -q dev-mac:audio-work/solana-bunker/music/suno/2-news/suno-2-breaking-news-a.wav "$ROOT/in/cues/2-news/"
cd "$ROOT"
$PY "$P/music-m2-opening.py" "$P/opening-m2.json" "$ROOT" "opening/$N" | tee opening/build.log
$PY "$P/finish-m3.py" "opening/$N" "opening/$N-final.wav" "opening/$N" | tee -a opening/build.log
ssh dev-mac "mkdir -p ~/video-work/solana-bunker/out/$N"
scp -q "opening/$N-final.wav" "dev-mac:video-work/solana-bunker/out/$N/"
for k in dialogue music sfx; do scp -q "opening/$N-$k.wav" "dev-mac:video-work/solana-bunker/out/"; done
ssh dev-mac bash -s "$N" <<'REMOTE' | tee opening/mux.log
set -euo pipefail
N=$1
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH; cd ~/video-work/solana-bunker
FFV="ffmpeg -nostdin -v error -y"; XT=54.5667
$FFV -i out/opening-v11.mp4 -i "out/$N/$N-final.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart -t $XT "out/$N.mp4"
$FFV -i out/opening-v11-phone.mp4 -i "out/$N/$N-final.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart -t $XT "out/$N-phone.mp4"
for f in opening-v11 "$N" opening-v11-phone "$N-phone"; do
  echo "$f $(ffmpeg -nostdin -v error -i out/$f.mp4 -map 0:v -c copy -f md5 -) $(ffprobe -v error -show_entries stream=codec_type,width,height,nb_frames,duration,bit_rate,channels -of compact=p=0 out/$f.mp4 | tr "\n" " ")"
done
REMOTE
scp -q "dev-mac:video-work/solana-bunker/out/$N.mp4" "dev-mac:video-work/solana-bunker/out/$N-phone.mp4" "$OB/"
$PY "$P/verify-m2.py" "opening/$N" "opening/$N" "opening/$N-final.wav" opening/verify "$OB/$N.mp4" "$OB/$N-phone.mp4" | tee opening/verify.log
$PY "$P/plot-levels-m2.py" "$OB/$N-levels.png" opening/verify/levels.npz Opening
