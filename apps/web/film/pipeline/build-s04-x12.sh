#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. x12 build mode (Liam 16583): build-s04.sh with Liam's voice at 1.2x.
# Needs out/s04/x12/seg/c*.mp4 + list.txt (capture-s04-x12.sh, 1395 frames = 46.50 s), out/s04/take-dn.wav (build-s04.sh) and film/data/s04-audio.filter.
# audio: the v6 cut list -> mix -> atempo=1.2 (pitch kept; a phrase at t lands at t/1.2, in step with the --speed=1.2 picture) -> two-pass loudnorm -16 LUFS
#   -> brown-noise bed re-generated at the new length -> out/s04/x12/audio-final.wav
# video: chunks concatenated (stream copy) + audio -> out/s04-v7-x12.mp4, 960x540 crf 26 phone cut out/s04-v7-x12-phone.mp4
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; O=out/s04/x12; mkdir -p $O
FFV="ffmpeg -nostdin -v error -y"; SPEED=1.2; M=1395
XT=$(python3 -c "print(round($M/30,4))")
[ -f out/s04/take-dn.wav ] || { echo "out/s04/take-dn.wav missing (run build-s04.sh once)"; exit 1; }
cp film/data/s04-audio.filter $O/s04-audio.filter
$FFV -i out/s04/take-dn.wav -/filter_complex $O/s04-audio.filter -map '[mix]' -ac 1 -ar 48000 $O/mix-1x.wav
$FFV -i $O/mix-1x.wav -af "atempo=$SPEED,apad=whole_dur=$XT,atrim=0:$XT,asetpts=PTS-STARTPTS" -ac 1 -ar 48000 $O/mix.wav
M1=$(ffmpeg -nostdin -hide_banner -i $O/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M1" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
FADE=$(python3 -c "print(round($XT-0.6,2))")
$FFV -i $O/mix.wav -f lavfi -i "anoisesrc=d=$XT:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$FADE:d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[o]" -map '[o]' -ac 1 -ar 48000 $O/audio-final.wav
ffmpeg -nostdin -hide_banner -i $O/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak"
$FFV -f concat -safe 0 -i $O/seg/list.txt -i $O/audio-final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart -t $XT out/s04-v7-x12.mp4
$FFV -i out/s04-v7-x12.mp4 -vf scale=960:540 -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/s04-v7-x12-phone.mp4
for v in s04-v7-x12 s04-v7-x12-phone; do ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,width,height -of compact out/$v.mp4; done
