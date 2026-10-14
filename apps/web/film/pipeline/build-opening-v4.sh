#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. Needs render-v4/<scene>/ frames (capture-v4.sh), out/s00a-v4/vo-final.wav (sponsor) and
# out/s00b-v4/vo-final.wav (advisory), both from render-vo-v4.py. Beat 0c (breaking slam) is unchanged and reused from out/seg.
# Timeline: 0a 4.3 s | 0b 12 s (VO at +0.6) | 0c 2 s | desk 44.4 s  = 62.7 s
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:$PATH
cd ~/video-work/solana-bunker; B=~/video-work/bunker; O=out/seg-v4; mkdir -p $O
enc() { ffmpeg -nostdin -v error -y "$@" -r 30 -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p; }
seg() { enc -framerate 30 -i render-v4/$1/f%05d.png -frames:v $2 $O/$1.mp4; }
seg s00-intro 129; seg s00b-advisory 360
cp out/seg/s00c-breaking.mp4 $O/s00c-breaking.mp4
enc -loop 1 -framerate 30 -t 44.4 -i render-v4/s02-news-back/still-0.png \
  -ss 8.16 -t 44.4 -i $B/matte-full-comp.mp4 -ss 8.16 -t 44.4 -i $B/matte-full-alpha.mp4 \
  -framerate 30 -i render-v4/s02-news-front/f%05d.png \
  -/filter_complex pipeline/desk-v4.filter -map '[desk]' -frames:v 1332 $O/s02-news.mp4
for f in s00-intro s00b-advisory s00c-breaking s02-news; do echo "$f frames: $(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 $O/$f.mp4)"; done
printf "file '%s'\n" s00-intro.mp4 s00b-advisory.mp4 s00c-breaking.mp4 s02-news.mp4 | sed "s#^file '#file '$PWD/$O/#" > $O/list.txt
ffmpeg -nostdin -v error -y -f concat -safe 0 -i $O/list.txt -ss 8.16 -i ~/video-work/bunker-raw.mov -i out/s00b-v4/vo-final.wav -i out/s00a-v4/vo-final.wav \
  -/filter_complex pipeline/audio-v4.filter -map 0:v -map '[aout]' -c:v copy -c:a aac -b:a 192k -movflags +faststart -t 62.7 out/opening-v4.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames -of compact out/opening-v4.mp4
