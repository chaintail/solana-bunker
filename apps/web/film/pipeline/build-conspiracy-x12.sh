#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. x12 build mode (Liam 16583, "1.2 on all"): build-conspiracy-v4.sh (x11 cut, lamp flicker removed) with Liam's voice at 1.2x.
# Needs out/consp-x12/seg/*.mp4 + list.txt and render-consp-x12/hat/ (capture-consp-x12.sh: 175 + 1704 = 1879 frames = 62.633 s), out/consp4/take-dn.wav and
# out/consp4/pip.mov (build-conspiracy-v4.sh, 2244 frames), film/data/conspiracy-audio.filter (v4 cut list).
# The scene's audio is Liam's take only (no generated speech or sound effects), so the whole mix goes through atempo.
# 1 audio: take-dn.wav (v4's white-noise cleanup: afftdn nr=18 with the noise profile learned from the silent 0.10-0.70 s) -> v4 cut list -> mix -> atempo=1.2
#   (pitch kept; a word at t lands at t/1.2) -> two-pass loudnorm -16 LUFS -> brown-noise bed re-generated at the new length -> audio-final.wav
# 2 PiP: v4's pip.mov (matte comp + alpha already merged per segment) time-scaled as one picture: output frame k = v4 PiP frame round(1.2 k) (select; the same as
#   setpts=PTS/1.2 on the footage and its alpha matte, nearest-frame, the two locked together)
# 3 base (x12 chunks) + rotated PiP + hat layer (x12 hat frames, last one held), every v4 overlay time / 1.2 -> out/conspiracy-x12.mp4 (crf 14), -phone.mp4 (960x540 crf 26)
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; O=out/consp-x12; mkdir -p $O; FFV="ffmpeg -nostdin -v error -y"; SPEED=1.2; M=1879
XT=$(python3 -c "print(round($M/30,4))"); s() { python3 -c "print(round($1/$SPEED,4))"; }
PF=$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 out/consp4/pip.mov)   # v4's PiP: 2244 frames (74.8 s)
[ "$PF" -ge 1731 ] || { echo "out/consp4/pip.mov ($PF frames) does not cover the PiP window (to 57.7 s)"; exit 1; }
[ "$(find render-consp-x12/hat -name 'f*.png' | wc -l)" -eq 38 ] || { echo "hat frames missing"; exit 1; }
[ "$(grep -c . $O/seg/list.txt)" -eq 32 ] || { echo "$O/seg/list.txt does not list 32 chunks"; exit 1; }
# --- 1 audio
cp film/data/conspiracy-audio.filter $O/
$FFV -i out/consp4/take-dn.wav -/filter_complex $O/conspiracy-audio.filter -map '[mix]' -ac 1 -ar 48000 $O/mix-1x.wav
$FFV -i $O/mix-1x.wav -af "atempo=$SPEED,apad=whole_dur=$XT,atrim=0:$XT,asetpts=PTS-STARTPTS" -ac 1 -ar 48000 $O/mix.wav
M1=$(ffmpeg -nostdin -hide_banner -i $O/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M1" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
$FFV -i $O/mix.wav -f lavfi -i "anoisesrc=d=$XT:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$(python3 -c "print(round($XT-0.6,4))"):d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[o]" -map '[o]' -ac 1 -ar 48000 $O/audio-final.wav
ffmpeg -nostdin -hide_banner -i $O/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak"
# --- 3 composite (v4 times: PiP 9.7-57.7 s, fade in 9.75 d 0.15, fade out 57.45 d 0.15; hat from 28.85 s, shown 28.8-57.7 s)
PI=$(s 9.7); PO=$(s 57.7); FI=$(s 9.75); FO=$(s 57.45); FD=$(s 0.15); HS=$(s 28.85); HI=$(s 28.8)
$FFV -f concat -safe 0 -i $O/seg/list.txt -i out/consp4/pip.mov -i $O/audio-final.wav -framerate 30 -i render-consp-x12/hat/f%05d.png \
  -filter_complex "[0:v]format=yuv420p,setpts=PTS-STARTPTS[base];[1:v]select='eq(n\,round(round(n/$SPEED)*$SPEED))',setpts=N/30/TB,format=rgba,rotate=-2*PI/180:ow='rotw(-2*PI/180)':oh='roth(-2*PI/180)':c=none,fade=t=in:st=$FI:d=$FD:alpha=1,fade=t=out:st=$FO:d=$FD:alpha=1[pip];[3:v]format=rgba,tpad=stop_mode=clone:stop=900,setpts=PTS+$HS/TB,fade=t=out:st=$FO:d=$FD:alpha=1[hat];[base][pip]overlay=x=1124-w/2:y=492-h/2:enable='between(t,$PI,$PO)':format=auto[b2];[b2][hat]overlay=enable='between(t,$HI,$PO)':format=auto,format=yuv420p[v]" \
  -map '[v]' -map 2:a -r 30 -frames:v $M -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart out/conspiracy-x12.mp4
$FFV -i out/conspiracy-x12.mp4 -vf scale=960:540 -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/conspiracy-x12-phone.mp4
for v in conspiracy-x12 conspiracy-x12-phone; do ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,width,height -of compact out/$v.mp4; done
[ "$(ffprobe -v error -select_streams v -show_entries stream=nb_frames -of csv=p=0 out/conspiracy-x12.mp4)" = $M ] || { echo "out/conspiracy-x12.mp4 is not $M frames"; exit 1; }
