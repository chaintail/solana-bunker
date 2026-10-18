#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker after build-opening-v10.sh. Opening v10 checks:
#  1 glitch-scan v2 (copied to opening-v10/tools/glitch-scan-v2.py) on master and phone: chunk starts (the new sponsor card's 60-frame chunks, v9's advisory and
#    ident chunks and x11's desk chunks moved 6 frames, the hold), stale-copy refs at each part's frame 0 (sponsor 0, advisory 129, ident 476, desk 542)
#  2 the mix as wav (48 kHz for onsets, 16 kHz for whisper on do-box), and the sponsor stem
#  3 onsets: jingle A from before the ident's first frame (15.8667) past the slam landing (17.2667), in the mix and the stem; jingle C at the SPECIAL REPORT
#    slam (52.4333)
#  4 stills: the sponsor card at its reveals and its last frame, the ident's first frames and slam, the desk's first frame
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; X=opening-v10; V=$X/verify; mkdir -p $V/stills; PY=~/speech-lab/.venv/bin/python3
CS=0,60,120,129,189,249,309,369,429,476,536,542,842,1142,1442,1574
for v in opening-v10 opening-v10-phone; do echo "== glitch scan $v"; ~/venvs/audio/bin/python $X/tools/glitch-scan-v2.py out/$v.mp4 --chunk-starts $CS --ref 0 --ref 129 --ref 476 --ref 542; echo "exit $?"; done
ffmpeg -nostdin -v error -y -i out/opening-v10.mp4 -vn -ac 1 -ar 48000 -c:a pcm_s16le $V/mix48.wav
ffmpeg -nostdin -v error -y -i out/opening-v10.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le $V/mix16.wav
ffmpeg -nostdin -v error -y -i out/opening-v10.mp4 -vn -t 4.3 -ac 1 -ar 16000 -c:a pcm_s16le $V/sponsor16.wav
echo "== onsets, mix, jingle A window"; $PY $X/film/pipeline/onsets-fine.py $V/mix48.wav 15.6 17.8
echo "== onsets, jingle A stem"; $PY $X/film/pipeline/onsets-fine.py $X/out/jingles/jingle-a.wav 15.6 17.8
echo "== onsets, mix, jingle C window"; $PY $X/film/pipeline/onsets-fine.py $V/mix48.wav 51.8 52.8
echo "== onsets, jingle C stem"; $PY $X/film/pipeline/onsets-fine.py $X/out/jingles/jingle-c.wav 51.8 52.8
st() { ffmpeg -nostdin -v error -y -i out/opening-v10.mp4 -vf "select=eq(n\,$1)" -frames:v 1 $V/stills/$2.png; }
st 0 sponsor-f0; st 15 sponsor-text-mid; st 30 sponsor-text-in; st 83 sponsor-chaintail-onset; st 90 sponsor-brand-mid; st 97 sponsor-brand-in
st 113 sponsor-v9-fade-start; st 119 sponsor-hold-end; st 124 sponsor-fade-mid; st 128 sponsor-last; st 129 advisory-f0
st 475 advisory-last; st 476 ident-f0; st 477 ident-f1; st 486 ident-0.33s; st 504 ident-0.95s; st 518 ident-slam-1.4s; st 541 ident-last; st 542 desk-f0
st 1573 special-report-slam
