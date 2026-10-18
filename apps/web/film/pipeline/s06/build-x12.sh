#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s06. x12 build mode (Liam 16583, "1.2 on all"): build.sh audio + video with Liam's voice at 1.2x.
# Needs out/take-dn.wav and out/s06-audio.filter (build.sh audio, v7 timing, 29.5 s) and out/x12/seg-$V/c*.mkv + list.txt (capture-x12.sh, 738 frames = 24.6 s).
# The scene's audio is Liam's take only: the devil's whisper is the on-screen "psst" (no generated speech) and SFX_SLOT_SLAM is a marker, not in the mix,
# so the whole mix goes through atempo (the marker's x12 time would be 27.72/1.2 = 23.10 s).
#  audio: v7 cut list -> mix -> atempo=1.2 (pitch kept; a line at t lands at t/1.2, in step with the --speed=1.2 picture) -> two-pass loudnorm -16 LUFS
#         -> brown-noise bed re-generated at the new length -> out/x12/audio-final.wav
#  video: build.sh's grade with its times scaled by 1/1.2 (grain in from 2.3/1.2 s over 0.4/1.2 s, grade blended in over 0.3/1.2-1.2/1.2 s, so frame 0 is slide 5's
#         ungraded last frame) -> out/s06-$V-x12.mp4 (crf 14), out/s06-$V-x12-phone.mp4 (960x540 crf 26)
# V=<tag> (default v10) reads out/x12/seg-<tag>/list.txt. v10: the frame count comes from out/s06-edl.json's total (26.5 s -> 663 frames, 22.1 s).
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker/s06; O=out/x12; mkdir -p $O; FFV="ffmpeg -nostdin -v error -y"; SPEED=1.2
M=$(python3 -c "import json,math;N=round(json.load(open('out/s06-edl.json'))['total']*30);print(math.ceil(N/$SPEED-1e-9))")
V=${V:-v10}; SEG=$O/seg-$V; N=s06-$V-x12
XT=$(python3 -c "print(round($M/30,4))")
NC=$(( (M + 299) / 300 )); [ "$(grep -c . $SEG/list.txt)" = $NC ] || { echo "$SEG/list.txt does not list $NC chunks"; exit 1; }
cp out/s06-audio.filter $O/s06-audio.filter
$FFV -i out/take-dn.wav -/filter_complex $O/s06-audio.filter -map '[mix]' -ac 1 -ar 48000 $O/mix-1x.wav
$FFV -i $O/mix-1x.wav -af "atempo=$SPEED,apad=whole_dur=$XT,atrim=0:$XT,asetpts=PTS-STARTPTS" -ac 1 -ar 48000 $O/mix.wav
M1=$(ffmpeg -nostdin -hide_banner -i $O/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M1" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
FADE=$(python3 -c "print(round($XT-0.6,2))")
$FFV -i $O/mix.wav -f lavfi -i "anoisesrc=d=$XT:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$FADE:d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[o]" -map '[o]' -ac 1 -ar 48000 $O/audio-final.wav
ffmpeg -nostdin -hide_banner -i $O/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|LRA:|Peak"
G0=$(python3 -c "print(round(2.3/$SPEED,4))"); GD=$(python3 -c "print(round(0.4/$SPEED,4))"); B0=$(python3 -c "print(round(0.3/$SPEED,4))"); BD=$(python3 -c "print(round(0.9/$SPEED,4))")
$FFV -f concat -safe 0 -i $SEG/list.txt -i $O/audio-final.wav -filter_complex \
  "[0:v]format=yuv444p,split[raw][x];[x]curves=all='0/0.035 0.25/0.21 0.75/0.82 1/1',split[c][g0];[g0]noise=c0s=30:c0f=t+u[g];[c][g]blend=c0_expr='A+(B-A)*clip((T-$G0)/$GD,0,1)':c1_expr='A':c2_expr='A',vignette=angle=PI/4.2[gv];[raw][gv]blend=all_expr='A+(B-A)*clip((T-$B0)/$BD,0,1)',format=yuv420p,setsar=1[v]" \
  -map '[v]' -map 1:a -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -t $XT out/$N.mp4
$FFV -i out/$N.mp4 -vf scale=960:540 -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/$N-phone.mp4
for v in $N $N-phone; do ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,width,height -of compact out/$v.mp4; done
[ "$(ffprobe -v error -select_streams v -show_entries stream=nb_frames -of csv=p=0 out/$N.mp4)" = $M ] || { echo "out/$N.mp4 is not $M frames"; exit 1; }
