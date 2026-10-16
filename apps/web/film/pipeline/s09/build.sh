#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s09.  usage: build.sh assets | build.sh audio | build.sh video [v1]
#  assets: scene 8 v1's graded last frame -> film/assets/s09-s08-last.png (beat 0); bodies.py -> film/assets/s09/ (oval erased; the lab coat's hand layer)
#  audio:  denoise the take once (afftdn nr=18, noise profile from the take's silent 0.10-0.70 s) -> out/take-dn.wav; s09-timing.py (edit list, beat times,
#          SFX markers, cut filter); cut (20 ms fades) -> mix.wav -> two-pass loudnorm -16 LUFS + brown-noise bed under the whole scene, limiter at 0.80 without auto-level (alimiter level=0) so the true peak stays under -1.5 dBTP -> out/audio-final.wav
#  video:  the captured chunks (out/chunk-a/b.mkv, lossless, capture.sh) -> light luma grain (c0s=7) before the colour snap only + vignette PI/4.6
#          + audio -> out/s09-<v>.mp4 (crf 14) and out/s09-<v>-phone.mp4 (960x540 crf 26)
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker/s09; FFV="ffmpeg -nostdin -v error -y"; V=${2:-v1}
mkdir -p out film/assets film/heads film/data
if [ "$1" = assets ]; then
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 ../s08/out/s08-v1.mp4)
  $FFV -ss "$(python3 -c "print($D-0.05)")" -i ../s08/out/s08-v1.mp4 -frames:v 1 -update 1 film/assets/s09-s08-last.png
  (cd film && /usr/bin/python3 pipeline/s09/bodies.py)
fi
if [ "$1" = audio ]; then
  printf '0.10 afftdn sn start;\n0.70 afftdn sn stop;\n' > out/sn.txt
  $FFV -i ../audio/bunker-take.wav -af "asendcmd=f=out/sn.txt,afftdn=nr=18:nf=-48:nt=w:om=o" -c:a pcm_s16le out/take-dn.wav
  /usr/bin/python3 film/pipeline/s09/s09-timing.py
  T=$(python3 -c "import json;print(json.load(open('out/s09-edl.json'))['total'])")
  $FFV -i out/take-dn.wav -/filter_complex out/s09-audio.filter -map '[mix]' -ac 1 -ar 48000 out/mix.wav
  M=$(ffmpeg -nostdin -hide_banner -i out/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g() { echo "$M" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
  $FFV -i out/mix.wav -f lavfi -i "anoisesrc=d=$T:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$(python3 -c "print($T-0.6)"):d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.80:level=0[o]" -map '[o]' -ac 1 -ar 48000 out/audio-final.wav
  ffmpeg -nostdin -hide_banner -i out/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A20 Summary | grep -E "I:|Peak:"
fi
if [ "$1" = video ]; then
  T=$(python3 -c "import json;print(json.load(open('out/s09-edl.json'))['total'])")
  SNAP=$(python3 -c "import json;print(json.load(open('out/s09-edl.json'))['T']['snap'])")
  printf "file '%s/out/chunk-a.mkv'\nfile '%s/out/chunk-b.mkv'\n" "$PWD" "$PWD" > out/chunks.txt
  $FFV -f concat -safe 0 -i out/chunks.txt -i out/audio-final.wav -filter_complex \
    "[0:v]format=yuv444p,noise=c0s=7:c0f=t+u:enable='lt(t,$SNAP)',vignette=angle=PI/4.6,format=yuv420p,setsar=1[v]" \
    -map '[v]' -map 1:a -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -t $T out/s09-$V.mp4
  $FFV -i out/s09-$V.mp4 -vf scale=960:540:flags=lanczos -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/s09-$V-phone.mp4
  ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames,width,height -of compact out/s09-$V.mp4
  ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of compact out/s09-$V-phone.mp4
fi
