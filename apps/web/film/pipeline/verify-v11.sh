#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker after build-opening-v11.sh. Opening v11 checks:
#  1 the video stream of opening-v11.mp4 against v10's (stream md5), loudness of master and phone (ebur128, true peak)
#  2 the master's audio as wav (48 kHz for onsets and levels, 16 kHz for whisper on do-box) and the sponsor card's audio
#  3 onsets: jingle A (first note, slam hit) in the mix and the stings stem; groove in/out and bed in/out in the music stem (and the mix where audible)
#  4 verify-v11.py: dialogue guard on the final stems, music levels, the music's offset in the master, envelopes for the level plot
#  5 sponsor-check-v10.py: "Chaintail Labs" in the mix against the 1.0 render
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; X=opening-v11; O=$X/out; V=$X/verify; mkdir -p $V; PY=~/speech-lab/.venv/bin/python3; F=$X/film/pipeline/onsets-fine.py
for f in opening-v10 opening-v11; do echo "video md5 $f $(ffmpeg -nostdin -v error -i out/$f.mp4 -map 0:v -c copy -f md5 -)"; done
for f in opening-v11 opening-v11-phone; do echo "== loudness $f"; ffmpeg -nostdin -hide_banner -i out/$f.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -A20 Summary | grep -E "I:|LRA:|Peak:"; done
ffmpeg -nostdin -v error -y -i out/opening-v11.mp4 -vn -ac 1 -ar 48000 -c:a pcm_f32le $V/mix48.wav
ffmpeg -nostdin -v error -y -i out/opening-v11.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le $V/mix16.wav
ffmpeg -nostdin -v error -y -i out/opening-v11.mp4 -vn -t 4.3 -ac 1 -ar 16000 -c:a pcm_s16le $V/sponsor16.wav
echo "== jingle A, mix 15.6-17.8"; $PY $F $V/mix48.wav 15.6 17.8
echo "== jingle A, stings stem 15.6-17.8"; $PY $F $O/stems/stings.wav 15.6 17.8
echo "== groove in, music stem 0.1-0.6"; $PY $F $O/stems/music.wav 0.1 0.6
echo "== groove out, music stem 4.1-4.5"; $PY $F $O/stems/music.wav 4.1 4.5
echo "== groove out, mix 4.1-4.5"; $PY $F $V/mix48.wav 4.1 4.5
echo "== bed in, music stem 17.6-18.1"; $PY $F $O/stems/music.wav 17.6 18.1
echo "== bed out, music stem 52.2-52.6"; $PY $F $O/stems/music.wav 52.2 52.6
echo "== music stem last sound above -60 dBFS (10 ms)"; $PY -c "
import numpy as np, soundfile as sf; x, sr = sf.read('$O/stems/music.wav'); w = 480; e = 20*np.log10(np.sqrt(np.mean(x[:len(x)//w*w].reshape(-1, w)**2, 1))+1e-12)
on = np.nonzero(e > -60)[0]; b = np.nonzero(np.diff(on) > 1)[0]; print('music spans (s):', [(round(on[i]*0.01,2), round((on[j]+1)*0.01,2)) for i, j in zip(np.r_[0, b+1], np.r_[b, len(on)-1])])"
echo "== levels"; $PY $X/film/pipeline/verify-v11.py $O/work/voice-final.wav $O/stems/music.wav $O/stems/stings.wav $V/mix48.wav $V/levels.csv
echo "== sponsor"; ffmpeg -nostdin -v error -y -i $V/mix48.wav -c:a pcm_s16le $V/mix48s16.wav; $PY $X/film/pipeline/sponsor-check-v10.py $V/mix48s16.wav out/s00a-v5/vo-final.wav 3.2946
