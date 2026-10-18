#!/bin/bash
# Conspiracy m2: audio-only remix of m1 on the locked x12b picture. The mix runs on do-box (ffmpeg audio only, /home/claude/venvs/manim); only
# the mux (picture stream-copied from out/conspiracy-x12b.mp4 / -phone.mp4) and the video md5 check run on dev-mac in ~/video-work/solana-bunker.
# usage: build-conspiracy-m2.sh <work dir on do-box> <outbox dir>
#   1. fetch m1's inputs from dev-mac into <work>/in (x12b's delivered mix, the cue, the stamp files) and m1's work stems into <work>/in/m1;
#      the folder-close file comes from the composer outbox (sfx/folder-close-2-doc-folder.mp3)
#   2. music-m2.py -> finish-m2.py (-16 LUFS, true peak <= -1.3 dBTP) -> m2-final.wav and 24-bit stems
#   3. dev-mac: out/consp-m2/m2-final.wav, stems out/conspiracy-m2-{dialogue,music,sfx}.wav; mux out/conspiracy-m2.mp4 and -phone.mp4 (aac 192k
#      both), video md5 source vs m2; copy the mp4s back to <outbox>
#   4. verify-m2.py (sync, onsets, guard, levels, loudness of the decoded mp4 audio) and plot-levels-m2.py -> <outbox>/conspiracy-m2-levels.png
set -euo pipefail
W=$1; OB=$2; P=$(cd "$(dirname "$0")" && pwd); PY=/home/claude/venvs/manim/bin/python
mkdir -p "$W/in/sfx" "$W/in/m1" "$W/w"
for f in out/consp-x12b/audio-final.wav; do scp -q "dev-mac:video-work/solana-bunker/$f" "$W/in/"; done
scp -q dev-mac:audio-work/solana-bunker/music/suno/3-conspiracy/suno-3-the-clock-ticks-twice-a.wav "$W/in/"
for f in stamp-thump-1-traditional-stamp stamp-thump-2-stamp-bright-shelved; do scp -q "dev-mac:audio-work/solana-bunker/out/work/$f.wav" "$W/in/sfx/"; done
for f in m1-dialogue.wav m1-music.wav m1-sfx.wav m1-loudness.json; do scp -q "dev-mac:video-work/solana-bunker/out/consp-m1/$f" "$W/in/m1/"; done
cp "$OB/sfx/folder-close-2-doc-folder.mp3" "$W/in/sfx/"
cd "$W"
$PY "$P/music-m2.py" "$P/conspiracy-m2.json" "$W" w/m2 | tee w/build.log
$PY "$P/finish-m2.py" w/m2 w/m2-final.wav w/conspiracy-m2 | tee -a w/build.log
ssh dev-mac 'mkdir -p ~/video-work/solana-bunker/out/consp-m2'
scp -q w/m2-final.wav dev-mac:video-work/solana-bunker/out/consp-m2/
for k in dialogue music sfx; do scp -q "w/conspiracy-m2-$k.wav" "dev-mac:video-work/solana-bunker/out/"; done
ssh dev-mac 'bash -s' <<'REMOTE' | tee w/mux.log
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH; cd ~/video-work/solana-bunker
FFV="ffmpeg -nostdin -v error -y"
$FFV -i out/conspiracy-x12b.mp4 -i out/consp-m2/m2-final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart out/conspiracy-m2.mp4
$FFV -i out/conspiracy-x12b-phone.mp4 -i out/consp-m2/m2-final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart out/conspiracy-m2-phone.mp4
for f in conspiracy-x12b conspiracy-m2 conspiracy-x12b-phone conspiracy-m2-phone; do
  echo "$f $(ffmpeg -nostdin -v error -i out/$f.mp4 -map 0:v -c copy -f md5 -) $(ffprobe -v error -show_entries stream=codec_type,width,height,nb_frames,duration,bit_rate -of compact=p=0 out/$f.mp4 | tr "\n" " ")"
done
REMOTE
scp -q dev-mac:video-work/solana-bunker/out/conspiracy-m2.mp4 dev-mac:video-work/solana-bunker/out/conspiracy-m2-phone.mp4 "$OB/"
$PY "$P/verify-m2.py" "$P/conspiracy-m2.json" w/m2 w/conspiracy-m2 w/m2-final.wav in/m1 w/verify "$OB/conspiracy-m2.mp4" "$OB/conspiracy-m2-phone.mp4" | tee w/verify.log
$PY "$P/plot-levels-m2.py" w/verify/levels.npz "$OB/conspiracy-m2-levels.png"
