#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s07. x12 build mode (Liam 16583, "1.2 on all"): build.sh audio + video with Liam's voice at 1.2x.
# Needs out/take-dn.wav and out/s07-audio.filter (s07-timing.py, v7 timing, 39.9634 s) and out/x12/seg/c*.mkv + list.txt (capture-x12.sh, 1000 frames = 33.33 s).
# The scene's audio is Liam's take only (no generated speech or sound effects), so the whole mix goes through atempo.
#  audio: v7 cut list -> mix -> atempo=1.2 (pitch kept; a line at t lands at t/1.2, in step with the --speed=1.2 picture) -> two-pass loudnorm -16 LUFS
#         -> brown-noise bed re-generated at the new length -> out/x12/audio-final.wav
#  video: build.sh's two grades, joined at the hard cut scaled by 1/1.2: the v7 cut at page time 30.9467 s falls between output frames 773 (page 30.92) and 774 (page 30.96),
#         so the alley starts on output frame 774 (25.8 s; CUT is a hair under it) -> out/$N.mp4 (crf 14), out/$N-phone.mp4 (960x540 crf 26)
# V=<tag> (e.g. V=v7) reads out/x12/seg-<tag>/list.txt and writes out/s07-<tag>-x12.mp4 / -phone.mp4.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker/s07; O=out/x12; mkdir -p $O; FFV="ffmpeg -nostdin -v error -y"; SPEED=1.2; M=1000; CUT=25.799
V=${V:-}; SEG=$O/seg${V:+-$V}; N=s07${V:+-$V}-x12
XT=$(python3 -c "print(round($M/30,4))")
[ "$(python3 -c "import json;print(json.load(open('out/s07-edl.json'))['total'])")" = 39.9634 ] || { echo "out/s07-edl.json is not the v7 timing"; exit 1; }
[ "$(grep -c . $SEG/list.txt)" = 4 ] || { echo "$SEG/list.txt does not list 4 chunks"; exit 1; }
cp out/s07-audio.filter $O/s07-audio.filter
$FFV -i out/take-dn.wav -/filter_complex $O/s07-audio.filter -map '[mix]' -ac 1 -ar 48000 $O/mix-1x.wav
$FFV -i $O/mix-1x.wav -af "atempo=$SPEED,apad=whole_dur=$XT,atrim=0:$XT,asetpts=PTS-STARTPTS" -ac 1 -ar 48000 $O/mix.wav
M1=$(ffmpeg -nostdin -hide_banner -i $O/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M1" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
FADE=$(python3 -c "print(round($XT-0.6,2))")
$FFV -i $O/mix.wav -f lavfi -i "anoisesrc=d=$XT:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$FADE:d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[o]" -map '[o]' -ac 1 -ar 48000 $O/audio-final.wav
ffmpeg -nostdin -hide_banner -i $O/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak"
$FFV -f concat -safe 0 -i $SEG/list.txt -i $O/audio-final.wav -filter_complex \
  "[0:v]format=yuv444p,split[s][a];
   [s]trim=end=$CUT,setpts=PTS-STARTPTS,curves=r='0/0.04 1/1':g='0/0.03 1/0.98':b='0/0.02 1/0.92',noise=c0s=14:c0f=t+u,vignette=angle=PI/4.6[sv];
   [a]trim=start=$CUT,setpts=PTS-STARTPTS,curves=all='0/0.035 0.25/0.21 0.75/0.82 1/1',noise=c0s=30:c0f=t+u,vignette=angle=PI/4.2[av];
   [sv][av]concat=n=2:v=1:a=0,format=yuv420p,setsar=1[v]" \
  -map '[v]' -map 1:a -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -t $XT out/$N.mp4
$FFV -i out/$N.mp4 -vf scale=960:540 -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/$N-phone.mp4
for v in $N $N-phone; do ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,width,height -of compact out/$v.mp4; done
[ "$(ffprobe -v error -select_streams v -show_entries stream=nb_frames -of csv=p=0 out/$N.mp4)" = $M ] || { echo "out/$N.mp4 is not $M frames"; exit 1; }
