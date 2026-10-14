#!/bin/bash
# Runs ON dev-mac. Renders the beat-0a sponsor line with kokoro (speech-lab server, :8899) in two British female voices,
# keeps both, and normalises each to -16 LUFS / 48 kHz mono with a 0.1 s lead-in (absolute t=0 is the start of the film).
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:$PATH
D=~/video-work/solana-bunker/out/s00a-v3; mkdir -p "$D"; cd "$D"
T="The following program is brought to you by Chaintail Labs."
for v in bf_emma bf_isabella; do
  curl -sf -m120 localhost:8899/v1/audio/speech -H "Content-Type: application/json" \
    -d "{\"model\":\"mlx-community/Kokoro-82M-bf16\",\"input\":\"$T\",\"voice\":\"$v\",\"speed\":0.9,\"response_format\":\"wav\"}" -o raw_$v.wav
  M=$(ffmpeg -nostdin -hide_banner -i raw_$v.wav -af loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g() { echo "$M" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
  ffmpeg -nostdin -v error -y -i raw_$v.wav -af "aresample=48000,loudnorm=I=-16:TP=-1.5:LRA=7:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000,adelay=100" -ac 1 -ar 48000 sponsor-$v.wav
  echo $v; ffmpeg -nostdin -hide_banner -i sponsor-$v.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak"
  ffprobe -v error -show_entries format=duration -of csv=p=0 sponsor-$v.wav
done
