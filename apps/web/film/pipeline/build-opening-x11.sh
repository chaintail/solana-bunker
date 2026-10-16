#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. x11 build mode (Liam 16583): opening v8 with Liam's desk speech at 1.1x. Only the desk segment (news desk + tweet,
# s02-news, Liam's voice) is sped; the sponsor card, the advisory card, the breaking card (TTS voices) and the 2.1 s hold with "A special report." stay at 1.0.
# Needs opening-x11/out/seg/c*.mkv + list.txt and opening-x11/render/back/still-0.png (capture-opening-x11.sh: desk front layer at 1.1x, 1032 frames),
# out/s8/desk-dn.wav + special-report.wav (build-opening-v8.sh), out/seg-v7/s00-intro|s00b-advisory|s00c-breaking.mp4, the two TTS vo-final.wavs, the sting mp3.
#  1 desk voice: v8's cut (0-9.5433 | 14.79-42.5, 20 ms fades, fade-out at 37.0333) -> atempo=1.1 (pitch kept) -> two-pass loudnorm -16 LUFS / TP -1.5 -> desk-final.wav
#  2 desk picture: desk-x11.filter = desk-v7.filter with the matted anchor (comp + alpha merged, after the 286|444 cut) time-scaled as one picture: output frame k
#    = v7 anchor frame round(1.1 k) (select; same as setpts=PTS/1.1 on the footage and its matte), backdrop, front layer at 1.1x on top -> 1032 frames = 34.4 s
#  3 timeline: 0a 4.9 | 0b 13 | 0c 2 (v7 segments, unscaled) | desk 34.4 (was 37.8333) | hold of the last desk frame 2.1 s = 56.4 s (was 59.8333)
#  4 audio-x11.filter: sponsor at 0, advisory at 5.5, desk at 19.9 (unchanged), the sting on the covering frame (start of the hold, 54.3 s; v8 57.7333), the announcer
#    0.75 s later (55.05 s), brown-noise bed over the new 56.4 s, limiter 0.80 level=0 -> out/opening-x11.mp4, out/opening-x11-phone.mp4 (960x540 crf 26)
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; X=opening-x11; O=opening-x11/out; mkdir -p $O/final
FFV="ffmpeg -nostdin -v error -y"; SPEED=1.1; DM=1032; XT=56.4; B=~/video-work/bunker
cp $X/film/pipeline/desk-x11.filter $O/desk-x11.filter
cp $X/film/pipeline/audio-x11.filter $O/audio-x11.filter
# --- 1 desk voice
$FFV -i out/s8/desk-dn.wav -filter_complex "[0:a]asplit=2[l1][l2];[l1]atrim=0:9.5433,asetpts=PTS-STARTPTS,afade=t=out:st=9.5233:d=0.02[la];[l2]atrim=14.79:42.5,asetpts=PTS-STARTPTS,afade=t=in:d=0.02[lb];[la][lb]concat=n=2:v=0:a=1,afade=t=out:st=37.0333:d=0.2[o]" -map '[o]' -ar 48000 -c:a pcm_s16le $O/desk-cut-1x.wav
$FFV -i $O/desk-cut-1x.wav -af "atempo=$SPEED" -ar 48000 -c:a pcm_s16le $O/desk-cut.wav
M=$(ffmpeg -nostdin -hide_banner -i $O/desk-cut.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
$FFV -i $O/desk-cut.wav -af "loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" -ac 1 -ar 48000 -c:a pcm_s16le $O/desk-final.wav
echo "desk loudnorm pass1: I=$(g input_i) TP=$(g input_tp) LRA=$(g input_lra) offset=$(g target_offset)"
# --- 2 desk picture
$FFV -loop 1 -framerate 30 -t 35.4 -i $X/render/back/still-0.png -ss 8.16 -t 44 -i $B/matte-full-comp.mp4 -ss 8.16 -t 44 -i $B/matte-full-alpha.mp4 \
  -f concat -safe 0 -i $X/out/seg/list.txt -/filter_complex $O/desk-x11.filter -map '[desk]' -frames:v $DM -r 30 -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p $O/final/s02-news.mp4
[ "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 $O/final/s02-news.mp4)" = $DM ] || { echo "desk segment frame count wrong"; exit 1; }
# --- 3 hold + concat
$FFV -i $O/final/s02-news.mp4 -vf "select=eq(n\,$((DM-1)))" -frames:v 1 $O/final/last.png
$FFV -loop 1 -framerate 30 -i $O/final/last.png -frames:v 63 -r 30 -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p $O/final/hold.mp4
printf "file '%s'\n" $PWD/out/seg-v7/s00-intro.mp4 $PWD/out/seg-v7/s00b-advisory.mp4 $PWD/out/seg-v7/s00c-breaking.mp4 $PWD/$O/final/s02-news.mp4 $PWD/$O/final/hold.mp4 > $O/final/list.txt
# --- 4 mix + mux
$FFV -f concat -safe 0 -i $O/final/list.txt -i out/s00b-v7/vo-final.wav -i out/s00a-v5/vo-final.wav -i ~/audio-work/solana-bunker/out/audition/news-close-2-horn-stabs.mp3 -i out/s8/special-report.wav -f lavfi -i "anoisesrc=d=$XT:c=brown:a=0.3:r=48000:s=1" -i $O/desk-final.wav \
  -/filter_complex $O/audio-x11.filter -map 0:v -map '[aout]' -c:v copy -c:a aac -b:a 192k -movflags +faststart -t $XT out/opening-x11.mp4
ffmpeg -nostdin -hide_banner -i out/opening-x11.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -A20 Summary | grep -E "I:|Peak:"
$FFV -i out/opening-x11.mp4 -vf scale=960:540:flags=lanczos -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart out/opening-x11-phone.mp4
for v in opening-x11 opening-x11-phone; do ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,width,height -of compact out/$v.mp4; done
