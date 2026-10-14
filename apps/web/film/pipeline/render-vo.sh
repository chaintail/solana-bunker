#!/bin/bash
# Runs ON dev-mac. usage: render-vo.sh <dir> <voice-1x-file> ; dir holds s00b-tempo.cmd
# 1) tempo-ramp the 1x render with rubberband driven by asendcmd (pitch preserved, no chunking)
# 2) two-pass loudnorm to -16 LUFS, 48 kHz mono wav, then lead-in pad (0.8 s) -> vo-final.wav
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:$PATH
D="$1"; IN="$2"; cd "$D"
cat > stretch.filter <<'F'
[0:a]aresample=48000,asendcmd=f=s00b-tempo.cmd,rubberband@rb=tempo=1.0:pitch=1:transients=smooth:window=long:pitchq=quality[a]
F
ffmpeg -nostdin -v error -y -i "$IN" -/filter_complex stretch.filter -map '[a]' -ac 1 vo-stretched.wav
M=$(ffmpeg -nostdin -hide_banner -i vo-stretched.wav -af loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
cat > norm.filter <<F
[0:a]loudnorm=I=-16:TP=-1.5:LRA=7:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,adelay=800,aresample=48000[a]
F
ffmpeg -nostdin -v error -y -i vo-stretched.wav -/filter_complex norm.filter -map '[a]' -ac 1 -ar 48000 vo-final.wav
ffmpeg -nostdin -hide_banner -i vo-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak"
ffprobe -v error -show_entries format=duration -of csv=p=0 vo-final.wav
