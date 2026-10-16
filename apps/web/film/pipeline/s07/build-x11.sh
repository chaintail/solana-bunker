#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s07. x11 build mode (Liam 16583): build.sh audio + video with Liam's voice at 1.1x.
# Needs out/take-dn.wav and out/s07-audio.filter (build.sh audio, v4 timing, 42.0 s) and out/x11/seg/c*.mkv + list.txt (capture-x11.sh, 1146 frames = 38.20 s).
#  audio: v4 cut list -> mix -> atempo=1.1 (pitch kept; a line at t lands at t/1.1, in step with the --speed=1.1 picture) -> two-pass loudnorm -16 LUFS
#         -> brown-noise bed re-generated at the new length -> out/x11/audio-final.wav
#  video: build.sh's two grades, joined at the hard cut scaled by 1/1.1: page frame 990 (33.0 s) is output frame 900 (30.0 s) -> out/$N.mp4 (crf 14),
#         out/$N-phone.mp4 (960x540 crf 26)
# V=<tag> (e.g. V=v5) reads out/x11/seg-<tag>/list.txt and writes out/s07-<tag>-x11.mp4 / -phone.mp4.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker/s07; O=out/x11; FFV="ffmpeg -nostdin -v error -y"; SPEED=1.1; M=1146; CUT=30.0
V=${V:-}; SEG=$O/seg${V:+-$V}; N=s07${V:+-$V}-x11
XT=$(python3 -c "print(round($M/30,4))")
[ "$(python3 -c "import json;print(json.load(open('out/s07-edl.json'))['total'])")" = 42.0 ] || { echo "out/s07-edl.json is not the v4 timing"; exit 1; }
cp out/s07-audio.filter $O/s07-audio.filter
$FFV -i out/take-dn.wav -/filter_complex $O/s07-audio.filter -map '[mix]' -ac 1 -ar 48000 $O/mix-1x.wav
$FFV -i $O/mix-1x.wav -af "atempo=$SPEED,apad=whole_dur=$XT,atrim=0:$XT,asetpts=PTS-STARTPTS" -ac 1 -ar 48000 $O/mix.wav
M1=$(ffmpeg -nostdin -hide_banner -i $O/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M1" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
$FFV -i $O/mix.wav -f lavfi -i "anoisesrc=d=$XT:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$(python3 -c "print($XT-0.6)"):d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[o]" -map '[o]' -ac 1 -ar 48000 $O/audio-final.wav
ffmpeg -nostdin -hide_banner -i $O/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak"
$FFV -f concat -safe 0 -i $SEG/list.txt -i $O/audio-final.wav -filter_complex \
  "[0:v]format=yuv444p,split[s][a];
   [s]trim=end=$CUT,setpts=PTS-STARTPTS,curves=r='0/0.04 1/1':g='0/0.03 1/0.98':b='0/0.02 1/0.92',noise=c0s=14:c0f=t+u,vignette=angle=PI/4.6[sv];
   [a]trim=start=$CUT,setpts=PTS-STARTPTS,curves=all='0/0.035 0.25/0.21 0.75/0.82 1/1',noise=c0s=30:c0f=t+u,vignette=angle=PI/4.2[av];
   [sv][av]concat=n=2:v=1:a=0,format=yuv420p,setsar=1[v]" \
  -map '[v]' -map 1:a -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -t $XT out/$N.mp4
$FFV -i out/$N.mp4 -vf scale=960:540 -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/$N-phone.mp4
for v in $N $N-phone; do ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,width,height -of compact out/$v.mp4; done
