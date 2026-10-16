#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s11 (film/ = rsync of film/s11's apps/web/film). usage: build.sh assets | audio | video [v1]
#  assets: scene 10's last frame (S10V, default v2; v3 once scene 10 is re-encoded with scene 9 v3: the last frame does not change) -> film/assets/s11-s10-last.png (under the bars, 0-0.35 s)
#  audio:  v3: the generated outro read -> out/take-dn.wav (v1/v2: the denoised take); s11-timing.py; cut (20 ms fades) -> mix.wav;
#          two-pass loudnorm -16 LUFS + brown-noise bed, limiter 0.80 without auto-level -> out/audio-final.wav. The bed fades out with the picture.
#  video:  the captured chunks (out/chunk-a/b.mkv, capture.sh) + audio -> out/s11-<v>.mp4 (crf 14) and out/s11-<v>-phone.mp4 (960x540 crf 26). No grade.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker/s11; FFV="ffmpeg -nostdin -v error -y"; V=${2:-v1}; S10V=${S10V:-v2}
mkdir -p out film/assets film/data
if [ "$1" = assets ]; then
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 ../s10/out/s10-$S10V.mp4)
  $FFV -ss "$(python3 -c "print($D-0.05)")" -i ../s10/out/s10-$S10V.mp4 -frames:v 1 -update 1 film/assets/s11-s10-last.png
fi
if [ "$1" = audio ]; then
  # v3: the voice is the generated outro read (film/pipeline/voices/outro/outro.wav, 24 kHz, no denoise needed); v1/v2 used Liam's take 583.62-586.00
  cp film/pipeline/voices/outro/outro.wav out/take-dn.wav
  /usr/bin/python3 film/pipeline/s11/s11-timing.py
  T=$(python3 -c "import json;print(json.load(open('out/s11-edl.json'))['total'])")
  $FFV -i out/take-dn.wav -/filter_complex out/s11-audio.filter -map '[mix]' -ac 1 -ar 48000 out/mix.wav
  M=$(ffmpeg -nostdin -hide_banner -i out/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g() { echo "$M" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
  $FFV -i out/mix.wav -f lavfi -i "anoisesrc=d=$T:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$(python3 -c "print($T-1.0)"):d=1.0[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.80:level=0[o]" -map '[o]' -ac 1 -ar 48000 out/audio-final.wav
  ffmpeg -nostdin -hide_banner -i out/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A20 Summary | grep -E "I:|Peak:"
fi
if [ "$1" = video ]; then
  T=$(python3 -c "import json;print(json.load(open('out/s11-edl.json'))['total'])")
  printf "file '%s/out/chunk-a.mkv'\nfile '%s/out/chunk-b.mkv'\n" "$PWD" "$PWD" > out/chunks.txt
  $FFV -f concat -safe 0 -i out/chunks.txt -i out/audio-final.wav -map 0:v -map 1:a -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -vf setsar=1 \
    -c:a aac -b:a 192k -movflags +faststart -t $T out/s11-$V.mp4
  $FFV -i out/s11-$V.mp4 -vf scale=960:540:flags=lanczos -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/s11-$V-phone.mp4
  ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames,width,height -of compact out/s11-$V.mp4
  ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of compact out/s11-$V-phone.mp4
fi
