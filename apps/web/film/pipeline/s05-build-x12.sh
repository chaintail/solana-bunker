#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s05. x12 build mode (Liam 16763): s05-build-x11.sh at 1.2x on the v6 cut list.
# audio: the v6 cut list (film/data/s05-audio.filter, 0.36 s pause (300 ms heard at 1.2x) after 'if it matches') -> mix.wav -> atempo=1.2 (pitch kept; every phrase start t lands at t/1.2,
#   in step with the --speed=1.2 picture) -> two-pass loudnorm -16 LUFS -> brown-noise bed re-generated at the new length -> out/x12/audio-final.wav
# video: out/x12/seg/c*.mp4 (s05-capture-x12.sh, 2287 frames = 76.233 s in v8) muxed -> ../out/s05-$V-x12.mp4 + the 960x540 crf 26 phone cut ../out/s05-$V-x12-phone.mp4 (V = cut version, default v8)
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker/s05; O=out/x12; mkdir -p $O ../out
FFV="ffmpeg -nostdin -v error -y"; SPEED=1.2; M=2287; V=${V:-v8}   # v8: 2287 frames = 76.233 s (v6/v7: 2420)
XT=$(python3 -c "print(round($M/30,4))")
[ -f out/take-dn.wav ] || { echo "out/take-dn.wav missing (run s05-build.sh once)"; exit 1; }
cp film/data/s05-audio.filter $O/s05-audio.filter
$FFV -i out/take-dn.wav -/filter_complex $O/s05-audio.filter -map '[mix]' -ac 1 -ar 48000 $O/mix-1x.wav
$FFV -i $O/mix-1x.wav -af "atempo=$SPEED,apad=whole_dur=$XT,atrim=0:$XT,asetpts=PTS-STARTPTS" -ac 1 -ar 48000 $O/mix.wav
M1=$(ffmpeg -nostdin -hide_banner -i $O/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M1" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
ST=$(python3 -c "print(round($XT-0.6,2))")
$FFV -i $O/mix.wav -f lavfi -i "anoisesrc=d=$XT:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$ST:d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[o]" -map '[o]' -ac 1 -ar 48000 $O/audio-final.wav
ffmpeg -nostdin -hide_banner -i $O/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak"
$FFV -f concat -safe 0 -i $O/seg/list.txt -i $O/audio-final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart -t $XT ../out/s05-$V-x12.mp4
$FFV -i ../out/s05-$V-x12.mp4 -vf scale=960:540:flags=lanczos -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart ../out/s05-$V-x12-phone.mp4
for v in s05-$V-x12 s05-$V-x12-phone; do ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,width,height -of compact ../out/$v.mp4; done
