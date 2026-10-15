#!/bin/bash
# Runs ON dev-mac. Scales the r1 head key (760x1100) to the r2 size: head hair-top-to-chin = 1/7 of a 473 px figure -> scale 0.0819 -> 62x90.
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/head-test
ffmpeg -nostdin -v error -y -i head-key.mov -vf "scale=62:90:flags=lanczos,format=argb" -c:v qtrle h2/head-small.mov
