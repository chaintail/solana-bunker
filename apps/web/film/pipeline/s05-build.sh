#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s05. Needs out/seg/seg0..3.mp4 (s05-capture.sh), out/take-dn.wav (the take denoised once: afftdn nr=18 noise profile from the
# silent 0.10-0.70 s, same as conspiracy v3a), data/s05-audio.filter (s05-timing.py, 20 ms cut fades) and ../audio/bunker-take.wav.
# audio: cut list -> mix.wav -> two-pass loudnorm -16 LUFS + constant brown-noise bed (lowpass 220 Hz, volume 0.05) under the whole scene -> audio-final.wav
# video: four near-lossless segments concatenated, muxed with the audio -> ../out/s05-v2.mp4 and the 960x540 crf 26 phone re-encode ../out/s05-v2-phone.mp4
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker/s05; O=out; mkdir -p ../out
FFV="ffmpeg -nostdin -v error -y"
TOTAL=$(python3 -c "import json;print(json.load(open('$O/s05-edl.json'))['total'])")
[ -f $O/take-dn.wav ] || { printf '0.10 afftdn sn start;\n0.70 afftdn sn stop;\n' > $O/sn.txt; $FFV -i ../audio/bunker-take.wav -af "asendcmd=f=$O/sn.txt,afftdn=nr=18:nf=-48:nt=w:om=o" -c:a pcm_s16le $O/take-dn.wav; }
cp film/data/s05-audio.filter $O/s05-audio.filter
$FFV -i $O/take-dn.wav -/filter_complex $O/s05-audio.filter -map '[mix]' -ac 1 -ar 48000 $O/mix.wav
M=$(ffmpeg -nostdin -hide_banner -i $O/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
ST=$(python3 -c "print(round($TOTAL-0.6,2))")
$FFV -i $O/mix.wav -f lavfi -i "anoisesrc=d=$TOTAL:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$ST:d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[o]" -map '[o]' -ac 1 -ar 48000 $O/audio-final.wav
ffmpeg -nostdin -hide_banner -i $O/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak"
printf "file '%s'\n" $PWD/$O/seg/seg0.mp4 $PWD/$O/seg/seg1.mp4 $PWD/$O/seg/seg2.mp4 $PWD/$O/seg/seg3.mp4 > $O/seg/list.txt
$FFV -f concat -safe 0 -i $O/seg/list.txt -i $O/audio-final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart -t $TOTAL ../out/s05-v2.mp4
$FFV -i ../out/s05-v2.mp4 -vf scale=960:540:flags=lanczos -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart ../out/s05-v2-phone.mp4
for v in s05-v2 s05-v2-phone; do ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,width,height -of compact ../out/$v.mp4; done
