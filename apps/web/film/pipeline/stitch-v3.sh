#!/usr/bin/env bash
# Solana Bunker film master v3: stitch the ten scene masters into one film.
# Runs on dev-mac (ffmpeg-full 9.x). Usage: stitch-v3.sh [step...]   steps: audio master encode measure (default: all)
#   audio   decode each scene's audio, fit it to frames x 1600 samples (48 kHz / 30 fps), concatenate sample-exactly
#   master  measure the whole film, apply ONE linear gain to -16.0 LUFS, then a 4x-oversampled lookahead limiter
#           (alimiter, latency compensated) at LIMIT_DB so the encoded files measure <= -1.0 dBTP; no per-scene normalisation
#   encode  decode all ten pictures once, concat (hard cuts), encode master (crf 18 slow) and phone (960x540 crf 26)
#           from the same decode, both muxed with the mastered audio as AAC 192k (at 128k the Arcade square-wave
#           score overshoots to -0.86 dBTP)
#   measure frame counts, loudness / true peak of both outputs, per-scene loudness before and after mastering
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
ROOT=${ROOT:-$HOME/video-work/solana-bunker}
W=${W:-$ROOT/film/master-v3}
TARGET_LUFS=${TARGET_LUFS:--16.0}
LIMIT_DB=${LIMIT_DB:--1.3}   # PCM ceiling; AAC 192k adds up to +0.12 dB, so the encoded files measure <= -1.0 dBTP
OUT=${OUT:-solana-bunker-film-v3}
SCENES=(out/opening-m3.mp4 out/conspiracy-v13.mp4 out/s04-m2.mp4 out/s05-m3.mp4 s06/out/s06-m3.mp4
        s07/out/s07-m3.mp4 s08/out/s08-v8-x12.mp4 s09/out/s09-m2.mp4 s10/out/s10-m3.mp4 s11/out/s11-v11.mp4)
SPF=1600   # audio samples per video frame
mkdir -p "$W/aud" "$W/rep"; cd "$W"
ff() { ffmpeg -nostdin -hide_banner -v error -y "$@"; }
frames() { ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$1"; }
samples() { ffprobe -v error -count_packets -select_streams a:0 -show_entries stream=duration_ts -of csv=p=0 "$1"; }
steps=${*:-audio master encode measure}

if [[ $steps == *audio* ]]; then
  : > rep/scenes.tsv; : > aud/list.txt; start=0
  for i in "${!SCENES[@]}"; do
    s=$ROOT/${SCENES[$i]}; n=$(printf %02d $((i+1)))
    fr=$(frames "$s"); want=$((fr * SPF))
    ff -i "$s" -map 0:a:0 -c:a pcm_f32le -ar 48000 -ac 1 aud/$n-raw.wav
    got=$(samples aud/$n-raw.wav)
    diff=$((got - want)); (( ${diff#-} <= 48 )) || { echo "scene $n audio off by $diff samples (> 1 ms)"; exit 1; }
    ff -i aud/$n-raw.wav -af "apad=whole_len=$want,atrim=end_sample=$want" -c:a pcm_f32le aud/$n.wav
    [[ $(samples aud/$n.wav) == "$want" ]] || { echo "scene $n fit failed"; exit 1; }
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$n" "${SCENES[$i]}" "$fr" "$start" "$got" "$diff" >> rep/scenes.tsv
    echo "file '$n.wav'" >> aud/list.txt; start=$((start + fr))
  done
  echo "total_frames $start" > rep/total.txt
  ff -f concat -safe 0 -i aud/list.txt -c:a pcm_f32le aud/film-pre.wav
  [[ $(samples aud/film-pre.wav) == $((start * SPF)) ]] || { echo "concat sample count mismatch"; exit 1; }
fi

loud() { ffmpeg -nostdin -hide_banner -i "$@" -af ebur128=peak=true -f null - 2>&1 | sed -n '/Summary:/,$p'; }
if [[ $steps == *master* ]]; then
  loud aud/film-pre.wav > rep/loud-pre.txt
  ffmpeg -nostdin -hide_banner -i aud/film-pre.wav -af loudnorm=print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p' > rep/loudnorm-pre.json
  I=$(awk -F'"' '/"input_i"/ {print $4}' rep/loudnorm-pre.json)   # two decimals; ebur128 prints one
  G=$(awk -v t="$TARGET_LUFS" -v i="$I" 'BEGIN {printf "%.2f", t - i}')
  L=$(awk -v d="$LIMIT_DB" 'BEGIN {printf "%.6f", 10^(d/20)}')
  echo "pre_I $I gain_dB $G limit_dB $LIMIT_DB limit_lin $L" > rep/gain.txt
  ff -i aud/film-pre.wav -af "volume=${G}dB:precision=double" -c:a pcm_f32le aud/film-gain.wav
  ff -i aud/film-gain.wav -af "aresample=192000:resampler=soxr:precision=28,alimiter=limit=$L:attack=5:release=50:level=0:asc=0:latency=1,aresample=48000:resampler=soxr:precision=28" \
     -c:a pcm_f32le aud/film-master.wav
  [[ $(samples aud/film-master.wav) == $(samples aud/film-pre.wav) ]] || { echo "limiter changed the length"; exit 1; }
  loud aud/film-master.wav > rep/loud-master-wav.txt
  ffmpeg -nostdin -hide_banner -i aud/film-master.wav -af loudnorm=print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p' > rep/loudnorm-master-wav.json
fi

if [[ $steps == *encode* ]]; then
  args=(); fc=""; cat=""
  for i in "${!SCENES[@]}"; do args+=(-i "$ROOT/${SCENES[$i]}"); fc+="[$i:v:0]setsar=1[v$i];"; cat+="[v$i]"; done
  fc+="${cat}concat=n=${#SCENES[@]}:v=1:a=0,split[vm][vp0];[vp0]scale=960:540[vp]"
  A=${#SCENES[@]}
  ff "${args[@]}" -i aud/film-master.wav -filter_complex "$fc" \
     -map '[vm]' -map $A:a -r 30 -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart "$OUT.mp4" \
     -map '[vp]' -map $A:a -r 30 -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart "$OUT-phone.mp4"
fi

if [[ $steps == *measure* ]]; then
  for f in "$OUT.mp4" "$OUT-phone.mp4"; do
    ff -i "$f" -map 0:a -c:a pcm_f32le aud/check.wav
    { echo "== $f"; ffprobe -v error -count_frames -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_read_frames,duration,sample_rate,channels -show_entries format=duration,size -of compact "$f"
      echo "decoded_audio_samples $(samples aud/check.wav)"; echo "sha256 $(shasum -a 256 "$f" | cut -d' ' -f1)"; loud "$f"
      ffmpeg -nostdin -hide_banner -i "$f" -af loudnorm=print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p'; } > "rep/out-$f.txt"
  done
  rm -f aud/check.wav
  : > rep/per-scene.tsv
  while IFS=$'\t' read -r n name fr st got diff; do
    a=$((st * SPF)); b=$(((st + fr) * SPF))
    for src in film-pre film-master; do
      log=rep/ebur-$src-$n.txt
      ffmpeg -nostdin -hide_banner -i aud/$src.wav -af "atrim=start_sample=$a:end_sample=$b,ebur128=peak=true:framelog=info" -f null - > "$log" 2>&1
      sv=$(grep -o 'S: *-\{0,1\}[0-9.]*' "$log" | awk '{print $2}' | awk '$1 > -70' | sort -n)
      c=$(echo "$sv" | wc -l | tr -d ' ')
      printf '%s\t%s\tI=%s\tS_max=%s\tS_median=%s\tTP=%s\n' "$n" "$src" \
        "$(sed -n '/Summary:/,$p' "$log" | awk '/ I:/ {print $2; exit}')" "$(echo "$sv" | tail -1)" \
        "$(echo "$sv" | sed -n "$(((c + 1) / 2))p")" "$(sed -n '/True peak:/,$p' "$log" | awk '/Peak:/ {print $2; exit}')" >> rep/per-scene.tsv
    done
  done < rep/scenes.tsv
fi
echo "stitch-v3: done ($steps)"
