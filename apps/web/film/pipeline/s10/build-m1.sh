#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. Sign-off m1 (music + the wipe's jingle) on the locked v8 x12 picture: the picture is stream-copied
# from s10/out/s10-v8-x12.mp4 / -phone.mp4; the audio is v8 x12's delivered mix (s10/out/v8-x12/audio-final.wav, unchanged) plus the news bed and jingle A
# (s10-m1.json, music-m1.py), two-pass loudnorm to -16 LUFS and the scene's limiter (alimiter limit=0.80 level=0, as build-x12.sh; latency=1 so the
# dialogue keeps its timing) (finish-m1.py). P = the directory holding these pipeline files on dev-mac (default music-m1/s10/pipeline).
# Jingle A gain: as the opening (build-opening-v10.sh step 2): event loudness (ebur128 I, 1 s of silence each side) matched to x11's horn as it was mixed.
# Outputs: s10/out/s10-m1.mp4 (aac 192k), s10/out/s10-m1-phone.mp4 (aac 128k), stems s10/out/s10-m1-{dialogue,music,sfx}.wav (24-bit, times the loudnorm
# gain, before the limiter; the music stem runs 0.30 s past the picture with the stab's ring), verification in s10/out/m1/verify (verify-m1.py).
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; P=${P:-music-m1/s10/pipeline}; O=s10/out/m1; mkdir -p $O
PY=~/speech-lab/.venv/bin/python3; FFV="ffmpeg -nostdin -v error -y"; AU=~/audio-work/solana-bunker/out
ev() { ffmpeg -nostdin -hide_banner -i "$1" -af "$2,adelay=1000:all=1,apad=pad_dur=1,ebur128" -f null - 2>&1 | grep -A3 Summary | sed -n 's/.*I: *\(-*[0-9.]*\) LUFS/\1/p'; }
IH=$(ev $AU/audition/news-close-2-horn-stabs.mp3 "aresample=48000,pan=mono|c0=0.5*c0+0.5*c1,volume=-4dB,afade=t=out:st=1.2:d=0.13")
IA=$(ev $AU/work/news-open-1-mini-jingle.wav "pan=mono|c0=0.5*c0+0.5*c1")
GA=$(python3 -c "print(round($IH - $IA, 2))")
echo "event loudness: horn as mixed in x11 $IH LUFS; jingle A at 0 dB $IA LUFS -> gain $GA dB"
sed "s/\"JINGLE_GAIN\"/$GA/" $P/s10-m1.json > $O/s10-m1.json
$PY $P/music-m1.py $O/s10-m1.json $O/m1
$PY $P/finish-m1.py $O/m1 "alimiter=limit=0.80:level=0:latency=1" $O/m1-final.wav s10/out/s10-m1
$FFV -i s10/out/s10-v8-x12.mp4 -i $O/m1-final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart s10/out/s10-m1.mp4
$FFV -i s10/out/s10-v8-x12-phone.mp4 -i $O/m1-final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 128k -movflags +faststart s10/out/s10-m1-phone.mp4
$PY $P/verify-m1.py $O/s10-m1.json $O/m1 $O/verify
