#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s06. x11 build mode (Liam 16583): build.sh audio + video with Liam's voice at 1.1x.
# Needs out/take-dn.wav and out/s06-audio.filter (build.sh audio, v7 timing, 29.5 s) and out/x11/seg/c*.mkv + list.txt (capture-x11.sh, 805 frames = 26.833 s).
#  audio: v7 cut list -> mix -> atempo=1.1 (pitch kept; a line at t lands at t/1.1, in step with the --speed=1.1 picture) -> two-pass loudnorm -16 LUFS
#         -> brown-noise bed re-generated at the new length -> out/x11/audio-final.wav
#  video: build.sh's grade with its times scaled by 1/1.1 (grain in from 2.3/1.1 s over 0.4/1.1 s, grade blended in over 0.3/1.1-1.2/1.1 s) -> out/s06-x11.mp4 (crf 14),
#         out/s06-x11-phone.mp4 (960x540 crf 26). The SFX_SLOT_SLAM marker is not in the mix (as in v7); its scaled time is 27.72/1.1 = 25.20 s.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker/s06; O=out/x11; FFV="ffmpeg -nostdin -v error -y"; SPEED=1.1; M=805
XT=$(python3 -c "print(round($M/30,4))")
[ "$(python3 -c "import json;print(json.load(open('out/s06-edl.json'))['total'])")" = 29.5 ] || { echo "out/s06-edl.json is not the v7 timing"; exit 1; }
cp out/s06-audio.filter $O/s06-audio.filter
$FFV -i out/take-dn.wav -/filter_complex $O/s06-audio.filter -map '[mix]' -ac 1 -ar 48000 $O/mix-1x.wav
$FFV -i $O/mix-1x.wav -af "atempo=$SPEED,apad=whole_dur=$XT,atrim=0:$XT,asetpts=PTS-STARTPTS" -ac 1 -ar 48000 $O/mix.wav
M1=$(ffmpeg -nostdin -hide_banner -i $O/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M1" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
$FFV -i $O/mix.wav -f lavfi -i "anoisesrc=d=$XT:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$(python3 -c "print($XT-0.6)"):d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[o]" -map '[o]' -ac 1 -ar 48000 $O/audio-final.wav
ffmpeg -nostdin -hide_banner -i $O/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak"
G0=$(python3 -c "print(round(2.3/$SPEED,4))"); GD=$(python3 -c "print(round(0.4/$SPEED,4))"); B0=$(python3 -c "print(round(0.3/$SPEED,4))"); BD=$(python3 -c "print(round(0.9/$SPEED,4))")
$FFV -f concat -safe 0 -i $O/seg/list.txt -i $O/audio-final.wav -filter_complex \
  "[0:v]format=yuv444p,split[raw][x];[x]curves=all='0/0.035 0.25/0.21 0.75/0.82 1/1',split[c][g0];[g0]noise=c0s=30:c0f=t+u[g];[c][g]blend=c0_expr='A+(B-A)*clip((T-$G0)/$GD,0,1)':c1_expr='A':c2_expr='A',vignette=angle=PI/4.2[gv];[raw][gv]blend=all_expr='A+(B-A)*clip((T-$B0)/$BD,0,1)',format=yuv420p,setsar=1[v]" \
  -map '[v]' -map 1:a -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -t $XT out/s06-x11.mp4
$FFV -i out/s06-x11.mp4 -vf scale=960:540 -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/s06-x11-phone.mp4
for v in s06-x11 s06-x11-phone; do ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,width,height -of compact out/$v.mp4; done
