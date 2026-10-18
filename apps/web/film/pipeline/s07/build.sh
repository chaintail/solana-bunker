#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s07.  usage: build.sh assets | build.sh audio | build.sh video [v1]
#  assets: slide 6 v3's graded end frame -> film/assets/s07-s06-end.png (beat 0, full frame) and film/assets/s07-alley-freeze.png (the corner window);
#          slide 6's red devil head -> film/heads/s06-devil.png
#  audio:  denoise the take once (afftdn nr=18, noise profile from the take's silent 0.10-0.70 s) -> out/take-dn.wav; s07-timing.py (edit list + cut filter);
#          cut (20 ms fades) -> mix.wav -> two-pass loudnorm -16 LUFS + brown-noise room-tone bed under the whole scene -> out/audio-final.wav
#  video:  the captured chunks (out/chunk-a/b/c.mkv, lossless, capture.sh) -> two grades joined at the 33.0 s hard cut:
#          seminar 0-33.0 s: warm curves, light luma grain (c0s=14), vignette PI/4.6;  alley 33.0 s-end: slide 6's noir grade (lifted-black S-curve, c0s=30, PI/4.2)
#          + audio -> out/s07-<v>.mp4 (crf 14) and out/s07-<v>-phone.mp4 (960x540 crf 26)
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker/s07; FFV="ffmpeg -nostdin -v error -y"; V=${2:-v1}; CUT=33.0
mkdir -p out film/assets film/heads film/data
if [ "$1" = assets ]; then
  $FFV -ss 29.95 -i ../s06/out/s06-v3.mp4 -frames:v 1 film/assets/s07-s06-end.png
  $FFV -ss 29.95 -i ../s06/out/s06-v3.mp4 -frames:v 1 -vf scale=640:360:flags=lanczos film/assets/s07-alley-freeze.png
  cp ../s06/film/heads/s06-devil.png film/heads/s06-devil.png
fi
if [ "$1" = audio ]; then
  printf '0.10 afftdn sn start;\n0.70 afftdn sn stop;\n' > out/sn.txt
  $FFV -i ../audio/bunker-take.wav -af "asendcmd=f=out/sn.txt,afftdn=nr=18:nf=-48:nt=w:om=o" -c:a pcm_s16le out/take-dn.wav
  /usr/bin/python3 pipeline/s07-timing.py
  T=$(python3 -c "import json;print(json.load(open('out/s07-edl.json'))['total'])")
  $FFV -i out/take-dn.wav -/filter_complex out/s07-audio.filter -map '[mix]' -ac 1 -ar 48000 out/mix.wav
  M=$(ffmpeg -nostdin -hide_banner -i out/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g() { echo "$M" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
  $FFV -i out/mix.wav -f lavfi -i "anoisesrc=d=$T:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$(python3 -c "print($T-0.6)"):d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[o]" -map '[o]' -ac 1 -ar 48000 out/audio-final.wav
  ffmpeg -nostdin -hide_banner -i out/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak"
fi
if [ "$1" = video ]; then
  T=$(python3 -c "import json;print(json.load(open('out/s07-edl.json'))['total'])")
  printf "file '%s/out/chunk-a.mkv'\nfile '%s/out/chunk-b.mkv'\nfile '%s/out/chunk-c.mkv'\n" "$PWD" "$PWD" "$PWD" > out/chunks.txt
  $FFV -f concat -safe 0 -i out/chunks.txt -i out/audio-final.wav -filter_complex \
    "[0:v]format=yuv444p,split[s][a];
     [s]trim=end=$CUT,setpts=PTS-STARTPTS,curves=r='0/0.04 1/1':g='0/0.03 1/0.98':b='0/0.02 1/0.92',noise=c0s=14:c0f=t+u,vignette=angle=PI/4.6[sv];
     [a]trim=start=$CUT,setpts=PTS-STARTPTS,curves=all='0/0.035 0.25/0.21 0.75/0.82 1/1',noise=c0s=30:c0f=t+u,vignette=angle=PI/4.2[av];
     [sv][av]concat=n=2:v=1:a=0,format=yuv420p,setsar=1[v]" \
    -map '[v]' -map 1:a -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -t $T out/s07-$V.mp4
  $FFV -i out/s07-$V.mp4 -vf scale=960:540 -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/s07-$V-phone.mp4
  ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames,width,height -of compact out/s07-$V.mp4
  ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of compact out/s07-$V-phone.mp4
fi
