#!/bin/bash
# Runs ON dev-mac. usage: still-key.sh <clip.mov> <t_s> <out.png>  -- raw head key over a checkerboard
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/head-test
ffmpeg -nostdin -v error -y -f lavfi -i "color=c=gray:s=760x1100,format=gray,geq=lum='if(lt(mod(floor(X/20)+floor(Y/20),2),1),205,120)'" \
  -ss $2 -i $1 -filter_complex "[0:v]format=rgb24[bg];[bg][1:v]overlay=shortest=1:format=auto" -frames:v 1 $3
