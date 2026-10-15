#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s06.  usage: build.sh audio | build.sh video
#  audio: denoise the take once (afftdn nr=18, noise profile from the take's silent 0.10-0.70 s) -> out/take-dn.wav; s06-timing.py (edit list + cut filter);
#         cut (20 ms fades) -> mix.wav -> two-pass loudnorm -16 LUFS + brown-noise room-tone bed under the whole scene (same chain/level as conspiracy v4) -> out/audio-final.wav
#  video: the captured chunks (out/chunk-a.mkv, out/chunk-b.mkv, lossless, from capture.sh) -> grade (lifted-black S-curve, luma-only temporal grain mixed in
#         from 2.3 s over 0.4 s, vignette) + audio -> out/s06-$V.mp4 (crf 14) and out/s06-$V-phone.mp4 (960x540 crf 26)
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker/s06; FFV="ffmpeg -nostdin -v error -y"; V=${2:-v1}   # output version: build.sh video v2 -> out/s06-v2.mp4
if [ "$1" = audio ]; then
  printf '0.10 afftdn sn start;\n0.70 afftdn sn stop;\n' > out/sn.txt
  $FFV -i ../audio/bunker-take.wav -af "asendcmd=f=out/sn.txt,afftdn=nr=18:nf=-48:nt=w:om=o" -c:a pcm_s16le out/take-dn.wav
  /usr/bin/python3 pipeline/s06-timing.py   # numpy lives in the system python
  T=$(python3 -c "import json;print(json.load(open('out/s06-edl.json'))['total'])")
  $FFV -i out/take-dn.wav -/filter_complex out/s06-audio.filter -map '[mix]' -ac 1 -ar 48000 out/mix.wav
  M=$(ffmpeg -nostdin -hide_banner -i out/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g() { echo "$M" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
  $FFV -i out/mix.wav -f lavfi -i "anoisesrc=d=$T:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$(python3 -c "print($T-0.6)"):d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[o]" -map '[o]' -ac 1 -ar 48000 out/audio-final.wav
  ffmpeg -nostdin -hide_banner -i out/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak"
fi
if [ "$1" = video ]; then
  T=$(python3 -c "import json;print(json.load(open('out/s06-edl.json'))['total'])")
  printf "file '%s/out/chunk-a.mkv'\nfile '%s/out/chunk-b.mkv'\n" "$PWD" "$PWD" > out/chunks.txt
  $FFV -f concat -safe 0 -i out/chunks.txt -i out/audio-final.wav -filter_complex \
    "[0:v]format=yuv444p,curves=all='0/0.035 0.25/0.21 0.75/0.82 1/1',split[c][g0];[g0]noise=c0s=30:c0f=t+u[g];[c][g]blend=c0_expr='A+(B-A)*clip((T-2.3)/0.4,0,1)':c1_expr='A':c2_expr='A',vignette=angle=PI/4.2,format=yuv420p,setsar=1[v]" \
    -map '[v]' -map 1:a -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -t $T out/s06-$V.mp4
  $FFV -i out/s06-$V.mp4 -vf scale=960:540 -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/s06-$V-phone.mp4
  ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames,width,height -of compact out/s06-$V.mp4
  ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of compact out/s06-$V-phone.mp4
fi
