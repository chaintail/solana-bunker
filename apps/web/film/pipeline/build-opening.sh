#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. Needs render/<scene>/ frames (capture.mjs) and out/s00b-v2/vo-final.wav (render-vo.sh).
# Stage 1 encodes every beat to an exact-length intermediate (frame counts are checked), stage 2 joins them and mixes audio.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:$PATH
cd ~/video-work/solana-bunker; B=~/video-work/bunker; O=out/seg; mkdir -p $O
enc() { ffmpeg -nostdin -v error -y "$@" -r 30 -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p; }
seg() { enc -framerate 30 -i render/$1/f%05d.png -frames:v $2 $O/$1.mp4; }
seg s00-intro 120; seg s00b-advisory 360; seg s00c-breaking 60
# desk: backdrop + matted Liam (same -ss on video and audio) + transparent front layer
enc -loop 1 -framerate 30 -t 46 -i render/s02-news-back/still-0.png \
  -ss 8.16 -t 46 -i $B/matte-full-comp.mp4 -ss 8.16 -t 46 -i $B/matte-full-alpha.mp4 \
  -framerate 30 -i render/s02-news-front/f%05d.png \
  -/filter_complex pipeline/desk.filter -map '[desk]' -frames:v 1380 $O/s02-news.mp4
for f in s00-intro s00b-advisory s00c-breaking s02-news; do echo "$f frames: $(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 $O/$f.mp4)"; done
printf "file '%s'\n" s00-intro.mp4 s00b-advisory.mp4 s00c-breaking.mp4 s02-news.mp4 | sed "s#^file '#file '$PWD/$O/#" > $O/list.txt
ffmpeg -nostdin -v error -y -f concat -safe 0 -i $O/list.txt -ss 8.16 -i ~/video-work/bunker-raw.mov -i out/s00b-v2/vo-final.wav \
  -/filter_complex pipeline/audio.filter -map 0:v -map '[aout]' -c:v copy -c:a aac -b:a 192k -movflags +faststart -t 64 out/opening-v2.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames -of compact out/opening-v2.mp4
