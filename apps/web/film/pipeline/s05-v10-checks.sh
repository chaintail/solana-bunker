#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker after build-s05-v10.sh: glitch-scan v2 (master + phone, chunk starts every 300 frames, ref frame 0),
# the hand-off frame (v10 last frame vs v9's last frame, s06-m3's frame 0 and s06's baked assets/s06/s05-end-full.png), per-frame PSNR v9 vs v10 over the
# common frames (same page times), and out/s05-v10-end-compare.png (v10 last frame | s06-m3 frame 0).
# usage: s05-v10-checks.sh <glitch-scan-v2.py>
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; GS=$1; C=s05/out/x12v10/chk; mkdir -p $C; FFV="ffmpeg -nostdin -v error -y"
psnr() { ffmpeg -nostdin -hide_banner -i "$1" -i "$2" -lavfi "[0:v]format=yuv420p[a];[1:v]format=yuv420p[b];[a][b]psnr" -f null - 2>&1 | grep -o 'PSNR y:.*'; }
echo "glitch-scan v2 (md5 $(md5 -q $GS)) on dev-mac ~/video-work/solana-bunker/out, $(TZ=America/New_York date '+%Y-%m-%d %H:%M %Z')"
for v in s05-v10 s05-v10-phone; do
  echo; echo "=== $v.mp4  --chunk-size 300 --ref 0"; ~/venvs/audio/bin/python $GS out/$v.mp4 --chunk-size 300 --ref 0; echo "exit $?"
done
L=$(( $(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 out/s05-v10.mp4) - 1 ))
$FFV -i out/s05-v10.mp4 -vf "select=eq(n\,$L)" -frames:v 1 $C/v10-last.png
$FFV -i out/s05-v9.mp4 -vf "select=eq(n\,2286)" -frames:v 1 $C/v9-last.png
$FFV -i s06/out/s06-m3.mp4 -vf "select=eq(n\,0)" -frames:v 1 $C/s06-m3-f0.png
$FFV -i out/s05-v10.mp4 -vf "select=eq(n\,0)" -frames:v 1 $C/v10-f0.png
echo; echo "hand-off frame: v10 frame $L"
echo "  v10 f$L vs v9 f2286:            $(psnr $C/v10-last.png $C/v9-last.png)"
echo "  v10 f$L vs s06-m3 f0:           $(psnr $C/v10-last.png $C/s06-m3-f0.png)"
echo "  v9 f2286 vs s06-m3 f0:          $(psnr $C/v9-last.png $C/s06-m3-f0.png)"
echo "  v10 f$L vs s06 s05-end-full.png: $(psnr $C/v10-last.png s06/film/assets/s06/s05-end-full.png)"
echo "  v9 f2286 vs s06 s05-end-full.png: $(psnr $C/v9-last.png s06/film/assets/s06/s05-end-full.png)"
ffmpeg -nostdin -v error -i out/s05-v9.mp4 -i out/s05-v10.mp4 -lavfi "[0:v]trim=end_frame=$L[a];[1:v]trim=end_frame=$L[b];[a][b]psnr=stats_file=$C/psnr-v9-v10.txt" -f null -
awk -v L=$L '{for(i=1;i<=NF;i++) if($i ~ /^psnr_avg:/){split($i,a,":"); v=a[2]; n++; if(v=="inf"){inf++} else if(v+0<40){lo++; low=low" "$1"="v} else if (v+0<45) mid++}} END {printf "v9 vs v10 frames 0-%d (same page times): %d frames, identical %d, 40-45 dB %d, < 40 dB %d%s\n", L-1, n, inf, mid, lo, low}' $C/psnr-v9-v10.txt
F="fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=8:x=16:y=16"
$FFV -i $C/v10-last.png -i $C/s06-m3-f0.png -filter_complex "[0:v]drawtext=$F:text='s05 v10 last frame ($L)'[a];[1:v]drawtext=$F:text='s06 m3 frame 0'[b];[a][b]hstack=inputs=2" -frames:v 1 out/s05-v10-end-compare.png && echo "-> out/s05-v10-end-compare.png"

# Prove the drawn state at the shortened end equals v9's old end, before encoding.
(
  cd s05/film
  export CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  node scripts/capture.mjs s05-hash --still=89.4,91.43333333333334 --out=../out/x12v10/chk/source-end
)
A=$(ffmpeg -nostdin -v error -i "$C/source-end/still-89.4.png" -pix_fmt rgba -f hash -hash sha256 -)
B=$(ffmpeg -nostdin -v error -i "$C/source-end/still-91.43333333333334.png" -pix_fmt rgba -f hash -hash sha256 -)
[ "$A" = "$B" ] || { echo "Source end-state pixels differ: $A vs $B"; exit 1; }
echo "Source end-state pixels identical: $A"
