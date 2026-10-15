#!/bin/bash
# Runs ON dev-mac. usage: stills.sh t1 t2 ... -> stills/t<T>.png from the finished clip
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:$PATH; cd ~/video-work/head-test; mkdir -p stills
for t in "$@"; do ffmpeg -nostdin -v error -y -ss $t -i floating-head-test.mp4 -frames:v 1 stills/comp-$t.png; done
