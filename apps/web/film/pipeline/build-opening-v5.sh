#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. Needs render-v5/<scene>/ frames (capture-v5.sh), out/s00a-v5/vo-final.wav (sponsor, Studio-C) and
# out/s00b-v5/vo-final.wav (advisory, Studio-Q), both from render-vo-v5.py. Beat 0c (breaking slam) is unchanged and reused from out/seg.
# Timeline: 0a 4.9 s | 0b 13 s (VO at +0.6) | 0c 2 s | desk 38.6333 s (1159 frames; mid-take cut: footage frames 286|444, end trimmed 0.5 s) = 58.5333 s
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:$PATH
cd ~/video-work/solana-bunker; B=~/video-work/bunker; O=out/seg-v5; mkdir -p $O
enc() { ffmpeg -nostdin -v error -y "$@" -r 30 -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p; }
seg() { enc -framerate 30 -i render-v5/$1/f%05d.png -frames:v $2 $O/$1.mp4; }
seg s00-intro 147; seg s00b-advisory 390
cp out/seg/s00c-breaking.mp4 $O/s00c-breaking.mp4
enc -loop 1 -framerate 30 -t 38.7 -i render-v5/s02-news-back/still-0.png \
  -ss 8.16 -t 44 -i $B/matte-full-comp.mp4 -ss 8.16 -t 44 -i $B/matte-full-alpha.mp4 \
  -framerate 30 -i render-v5/s02-news-front/f%05d.png \
  -/filter_complex pipeline/desk-v5.filter -map '[desk]' -frames:v 1159 $O/s02-news.mp4
for f in s00-intro s00b-advisory s00c-breaking s02-news; do echo "$f frames: $(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 $O/$f.mp4)"; done
printf "file '%s'\n" s00-intro.mp4 s00b-advisory.mp4 s00c-breaking.mp4 s02-news.mp4 | sed "s#^file '#file '$PWD/$O/#" > $O/list.txt
ffmpeg -nostdin -v error -y -f concat -safe 0 -i $O/list.txt -ss 8.16 -i ~/video-work/bunker-raw.mov -i out/s00b-v5/vo-final.wav -i out/s00a-v5/vo-final.wav \
  -/filter_complex pipeline/audio-v5.filter -map 0:v -map '[aout]' -c:v copy -c:a aac -b:a 192k -movflags +faststart -t 58.5333 out/opening-v5.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames -of compact out/opening-v5.mp4
