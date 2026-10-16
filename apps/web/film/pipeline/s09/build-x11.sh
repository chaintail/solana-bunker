#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s09. x11 build mode (Liam 16583): build.sh audio + video with Liam's voice at 1.1x.
# usage: build-x11.sh [name]  (default s09-x11; v9: build-x11.sh s09-v9-x11) -> out/<name>.mp4 and out/<name>-phone.mp4
# Needs out/take-dn.wav, out/s09-audio.filter, out/s09-edl.json (build.sh audio, v9 timing, 43.54 s; v1-v8: 45.58 s) and out/x11/seg/c*.mkv + list.txt (capture-x11.sh, 1188 frames = 39.6 s).
#  audio: v6 cut list -> mix -> atempo=1.1 (pitch kept; a line at t lands at t/1.1, in step with the --speed=1.1 picture) -> two-pass loudnorm -16 LUFS
#         -> brown-noise bed re-generated at the new length, limiter 0.80 without auto-level (as build.sh) -> out/x11/audio-final.wav
#  video: build.sh's grade, the grain's end at the colour snap scaled by 1/1.1 (T.snap/1.1) -> out/<name>.mp4 (crf 14), out/<name>-phone.mp4 (960x540 crf 26)
#  The five SFX markers are not in the mix (as v6); their x11 times are the v6 times / 1.1.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker/s09; O=out/x11; FFV="ffmpeg -nostdin -v error -y"; SPEED=1.1; M=1188; V=${1:-s09-x11}
XT=$(python3 -c "print(round($M/30,4))")
[ "$(python3 -c "import json;print(json.load(open('out/s09-edl.json'))['total'])")" = 43.54 ] || { echo "out/s09-edl.json is not the v9 timing"; exit 1; }
SNAP=$(python3 -c "import json;print(round(json.load(open('out/s09-edl.json'))['T']['snap']/$SPEED,4))")
cp out/s09-audio.filter $O/s09-audio.filter
$FFV -i out/take-dn.wav -/filter_complex $O/s09-audio.filter -map '[mix]' -ac 1 -ar 48000 $O/mix-1x.wav
$FFV -i $O/mix-1x.wav -af "atempo=$SPEED,apad=whole_dur=$XT,atrim=0:$XT,asetpts=PTS-STARTPTS" -ac 1 -ar 48000 $O/mix.wav
M1=$(ffmpeg -nostdin -hide_banner -i $O/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M1" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
$FFV -i $O/mix.wav -f lavfi -i "anoisesrc=d=$XT:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$(python3 -c "print($XT-0.6)"):d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.80:level=0[o]" -map '[o]' -ac 1 -ar 48000 $O/audio-final.wav
ffmpeg -nostdin -hide_banner -i $O/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A20 Summary | grep -E "I:|Peak:"
$FFV -f concat -safe 0 -i $O/seg/list.txt -i $O/audio-final.wav -filter_complex \
  "[0:v]format=yuv444p,noise=c0s=7:c0f=t+u:enable='lt(t,$SNAP)',vignette=angle=PI/4.6,format=yuv420p,setsar=1[v]" \
  -map '[v]' -map 1:a -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -t $XT out/$V.mp4
$FFV -i out/$V.mp4 -vf scale=960:540:flags=lanczos -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/$V-phone.mp4
for v in $V $V-phone; do ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,width,height -of compact out/$v.mp4; done
