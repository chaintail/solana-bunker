#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s11 (film/ = rsync of film/s11's apps/web/film). usage: build.sh assets | audio | video [v1]
#  assets: scene 10's last frame (S10V, default v2; v3 once scene 10 is re-encoded with scene 9 v3: the last frame does not change) -> film/assets/s11-s10-last.png (under the bars, 0-0.35 s)
#  audio:  v3/v4: the generated outro read (v4: outro-v4.wav) -> out/take-dn.wav (v1/v2: the denoised take); s11-timing.py; cut (20 ms fades) -> mix.wav;
#          two-pass loudnorm -16 LUFS + brown-noise bed, limiter 0.80 without auto-level -> out/audio-final.wav. The bed fades out with the picture.
#          v7: the voice alone is gained to -16 LUFS (as the v1-v6 loudnorm), the jingles (-20 LUFS) and the groove (-26 LUFS) are mixed on
#          (out/s11-mix.filter), then the same bed and limiter. No gain on the whole mix: 23 s of groove 10 dB under the voice lowers the gated integrated
#          reading, and lifting the scene back to -16 integrated would put the voice about 3.5 dB above scene 10 and into heavy limiting.
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
  # v4: the locked read, film/pipeline/voices/outro/outro-v4.wav (outro-voice-01-stitch-B.mp3, en-US-Studio-O, decoded to 48 kHz mono on dev-mac);
  # v3 used outro.wav (en-GB-Studio-C, 24 kHz); v1/v2 used Liam's take 583.62-586.00
  # v7: jingle A, jingle B and the sponsor groove (dev-mac ~/audio-work/solana-bunker; cue rows news-open-1-mini-jingle and
  # news-open-2-minimalist-transition in film/sfx audio/sfx/cues.tsv) mixed onto the voice (out/s11-mix.filter, s11-timing.py); levels as the header.
  AW=~/audio-work/solana-bunker
  cp film/pipeline/voices/outro/outro-v4.wav out/take-dn.wav
  /usr/bin/python3 film/pipeline/s11/s11-timing.py
  T=$(python3 -c "import json;print(json.load(open('out/s11-edl.json'))['total'])")
  lufs() { ffmpeg -nostdin -hide_banner -i "$1" -af ebur128 -f null - 2>&1 | grep -A3 'Integrated loudness' | sed -n 's/ *I: *\(-*[0-9.]*\) LUFS/\1/p'; }
  $FFV -i out/take-dn.wav -/filter_complex out/s11-audio.filter -map '[mix]' -ac 1 -ar 48000 out/voice.wav
  VG=$(python3 -c "print(round(-16-($(lufs out/voice.wav)),2))"); sed "s/VOICE_GAIN/$VG/" out/s11-mix.filter > out/s11-mix.run.filter
  IN="-i out/voice.wav -i $AW/out/work/news-open-1-mini-jingle.wav -i $AW/out/work/news-open-2-minimalist-transition.wav -i $AW/music/suno/1-sponsor/suno-1-reassuring-groove-a.wav"
  $FFV $IN -/filter_complex out/s11-mix.run.filter -map '[mix]' -ac 1 -ar 48000 -c:a pcm_f32le out/mix.wav
  sed 's/;\[v\]\[ja\]\[jb\]\[g\]amix.*//' out/s11-mix.run.filter > out/s11-stems.filter   # the four placed layers, for the onset checks
  $FFV $IN -/filter_complex out/s11-stems.filter -map '[v]' -c:a pcm_f32le out/stem-v.wav -map '[ja]' -c:a pcm_f32le out/stem-ja.wav \
    -map '[jb]' -c:a pcm_f32le out/stem-jb.wav -map '[g]' -c:a pcm_f32le out/stem-g.wav
  echo "voice gain $VG dB (the voice alone at -16 LUFS); mix $(lufs out/mix.wav) LUFS integrated"
  $FFV -i out/mix.wav -f lavfi -i "anoisesrc=d=$T:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$(python3 -c "print($T-1.0)"):d=1.0[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.80:level=0[o]" -map '[o]' -ac 1 -ar 48000 out/audio-final.wav
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
