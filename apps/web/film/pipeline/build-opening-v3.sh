#!/bin/bash
# Runs ON dev-mac. v3 = v2 video (out/seg untouched, beat 0a stays 4 s) + sponsor voice (render-sponsor.sh) mixed over the room tone.
# Beat 0a needed no extension: line ends ~3.4 s, card fades out 3.65-4.0 s, so later segments do not shift.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:$PATH
cd ~/video-work/solana-bunker
ffmpeg -nostdin -v error -y -f concat -safe 0 -i out/seg/list.txt -ss 8.16 -i ~/video-work/bunker-raw.mov -i out/s00b-v2/vo-final.wav -i out/s00a-v3/sponsor-bf_emma.wav \
  -/filter_complex pipeline/audio-v3.filter -map 0:v -map '[aout]' -c:v copy -c:a aac -b:a 192k -movflags +faststart -t 64 out/opening-v3.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames -of compact out/opening-v3.mp4
