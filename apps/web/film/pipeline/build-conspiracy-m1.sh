#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. Conspiracy m1 (music + sound effects) on the locked x12b picture: the picture is stream-copied from
# out/conspiracy-x12b.mp4 / -phone.mp4; the audio is x12b's delivered mix (out/consp-x12b/audio-final.wav, unchanged) plus the conspiracy cue and seven
# sound effects (conspiracy-m1.json, music-m1.py), two-pass loudnorm to -16 LUFS and x12b's limiter (alimiter limit=0.95; latency=1 so the dialogue keeps x12b's timing) (finish-m1.py).
# P = the directory holding these pipeline files on dev-mac (default music-m1/consp/pipeline).
# Outputs: out/conspiracy-m1.mp4 (aac 192k), out/conspiracy-m1-phone.mp4 (aac 128k), stems out/conspiracy-m1-{dialogue,music,sfx}.wav (24-bit, times the
# loudnorm gain, before the limiter), verification in out/consp-m1/verify (verify-m1.py).
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; P=${P:-music-m1/consp/pipeline}; O=out/consp-m1; mkdir -p $O
PY=~/speech-lab/.venv/bin/python3; FFV="ffmpeg -nostdin -v error -y"
$PY $P/music-m1.py $P/conspiracy-m1.json $O/m1
$PY $P/finish-m1.py $O/m1 "alimiter=limit=0.95:latency=1" $O/m1-final.wav out/conspiracy-m1
$FFV -i out/conspiracy-x12b.mp4 -i $O/m1-final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart out/conspiracy-m1.mp4
$FFV -i out/conspiracy-x12b-phone.mp4 -i $O/m1-final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 128k -movflags +faststart out/conspiracy-m1-phone.mp4
$PY $P/verify-m1.py $P/conspiracy-m1.json $O/m1 $O/verify
