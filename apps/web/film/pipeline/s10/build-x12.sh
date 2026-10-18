#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s10. x12 build mode (Liam 16583, "1.2 on all"): build.sh audio + video with Liam's voice at 1.2x. v8 content, unchanged.
# Needs out/take-dn.wav, out/s10-audio.filter, out/s10-edl.json (build.sh audio, v7 timing, 33.40 s), out/back.png, film/assets/s10-s09-last.png (build.sh assets)
# and out/$TAG/seg/c*.mkv + list.txt (capture-x12.sh: the front layer at --speed=1.2, 835 frames = 27.833 s).
# The scene's audio is Liam's take only (two cut segments, no generated speech, stings or sound effects), so the whole mix goes through atempo.
#  audio: v7 cut list on the denoised take -> mix -> atempo=1.2 (pitch kept) -> two-pass loudnorm -16 LUFS -> brown-noise bed at the new length, limiter 0.80 level=0 (as build.sh)
#         -> out/$TAG/audio-final.wav
#  video: build.sh's v7 background composite, unchanged (backdrop, the matted anchor B1/B2 with comp and alpha matte merged, the 4-frame anchor crossfade at 399-402,
#         scene 9's last frame under the wipe), then time-scaled as one picture: output frame k = v7 frame round(1.2 k) (select; the same as setpts=PTS/1.2 on the
#         footage and on its alpha matte, nearest-frame, and the two can never drift apart). Last output frame 834 = v7 frame 1001 (hand-off unchanged).
#         The front layer (captured at 1.2x) goes on top -> out/s10-$TAG.mp4 (crf 14), out/s10-$TAG-phone.mp4 (960x540 crf 26), and the last frame -> out/s10-$TAG-last.png
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
TAG=${TAG:-v8-x12}; cd ~/video-work/solana-bunker/s10; O=out/$TAG; FFV="ffmpeg -nostdin -v error -y"; SPEED=1.2; M=835; B=~/video-work/bunker
XT=$(python3 -c "print(round($M/30,4))")
T=$(python3 -c "import json;print(json.load(open('out/s10-edl.json'))['total'])"); [ "$T" = 33.4 ] || { echo "out/s10-edl.json is not the v7 timing"; exit 1; }
cp out/s10-audio.filter $O/s10-audio.filter
$FFV -i out/take-dn.wav -/filter_complex $O/s10-audio.filter -map '[mix]' -ac 1 -ar 48000 $O/mix-1x.wav
$FFV -i $O/mix-1x.wav -af "atempo=$SPEED,apad=whole_dur=$XT,atrim=0:$XT,asetpts=PTS-STARTPTS" -ac 1 -ar 48000 $O/mix.wav
M1=$(ffmpeg -nostdin -hide_banner -i $O/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M1" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
$FFV -i $O/mix.wav -f lavfi -i "anoisesrc=d=$XT:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$(python3 -c "print($XT-0.6)"):d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.80:level=0[o]" -map '[o]' -ac 1 -ar 48000 $O/audio-final.wav
ffmpeg -nostdin -hide_banner -i $O/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A20 Summary | grep -E "I:|Peak:"
$FFV -loop 1 -framerate 30 -t $T -i out/back.png -ss 531.75 -t 13.6 -i $B/matte-full-comp.mp4 -ss 531.75 -t 13.6 -i $B/matte-full-alpha.mp4 \
  -ss 563.5 -t 20.4 -i $B/matte-full-comp.mp4 -ss 563.5 -t 20.4 -i $B/matte-full-alpha.mp4 -loop 1 -framerate 30 -t $T -i film/assets/s10-s09-last.png \
  -f concat -safe 0 -i $O/seg/list.txt -i $O/audio-final.wav -filter_complex \
  "[1:v]fps=30,trim=end_frame=403,setpts=PTS-STARTPTS,scale=525:700:flags=lanczos,despill=type=green:mix=0.6:expand=0.2,format=rgb24[c1];
   [2:v]fps=30,trim=end_frame=403,setpts=PTS-STARTPTS,scale=525:700:flags=lanczos,format=gray[a1];[c1][a1]alphamerge[l1];
   [3:v]fps=30,trim=end_frame=603,setpts=PTS-STARTPTS+399/30/TB,scale=525:700:flags=lanczos,despill=type=green:mix=0.6:expand=0.2,format=rgb24[c2];
   [4:v]fps=30,trim=end_frame=603,setpts=PTS-STARTPTS+399/30/TB,scale=525:700:flags=lanczos,format=gray[a2];[c2][a2]alphamerge[l2];
   [0:v]format=rgb24,setpts=PTS-STARTPTS,split[bga][bgb];[bga][l1]overlay=x=377:y=-20:eof_action=pass:format=auto,format=gbrp[ba];[bgb][l2]overlay=x=377:y=-20:eof_action=pass:format=auto,format=gbrp[bb];
   [ba][bb]blend=all_expr='A*(1-clip((N-398)/5\,0\,1))+B*clip((N-398)/5\,0\,1)',format=rgb24[b2];
   [5:v]format=rgb24,setpts=PTS-STARTPTS[s9];[b2][s9]overlay=0:0:enable='lt(t,0.55)'[b3];
   [b3]select='eq(n\,round(round(n/$SPEED)*$SPEED))',setpts=N/30/TB[b4];
   [6:v]settb=1/30,setpts=N,format=rgba[fr];[b4][fr]overlay=format=auto,format=yuv420p,setsar=1[v]" \
  -map '[v]' -map 7:a -r 30 -frames:v $M -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart out/s10-$TAG.mp4
$FFV -i out/s10-$TAG.mp4 -vf scale=960:540:flags=lanczos -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/s10-$TAG-phone.mp4
for v in s10-$TAG s10-$TAG-phone; do ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,width,height -of compact out/$v.mp4; done
[ "$(ffprobe -v error -select_streams v -show_entries stream=nb_frames -of csv=p=0 out/s10-$TAG.mp4)" = $M ] || { echo "out/s10-$TAG.mp4 is not $M frames"; exit 1; }
$FFV -i out/s10-$TAG.mp4 -vf "select='eq(n\,$((M-1)))'" -frames:v 1 -update 1 out/s10-$TAG-last.png
