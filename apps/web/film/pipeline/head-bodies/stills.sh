#!/bin/bash
# Runs ON dev-mac from ~/video-work/head-test/h2. Extracts the full frames of poses A/B/C from head-bodies-test.mp4 (t=1.5, 4.5, 7.5) and crops each of the six figures
# (fig-<n>-<pose>.png, 2x) plus a 4x head-and-collar crop (head-<n>-<pose>.png) for inspection.
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/head-test/h2; mkdir -p stills
CX=(100 308 516 724 932 1140); P=(A B C); T=(1.5 4.5 7.5)
for j in 0 1 2; do
  ffmpeg -nostdin -v error -y -ss ${T[$j]} -i head-bodies-test.mp4 -frames:v 1 stills/full-${P[$j]}.png
  for i in 0 1 2 3 4 5; do
    x=$(( ${CX[$i]} - 105 )); [ $x -lt 0 ] && x=0; [ $x -gt 1070 ] && x=1070
    ffmpeg -nostdin -v error -y -i stills/full-${P[$j]}.png -vf "crop=210:650:$x:30,scale=420:1300:flags=lanczos" -frames:v 1 stills/fig-$((i+1))-${P[$j]}.png
    hx=$(( ${CX[$i]} - 40 )); [ $hx -lt 0 ] && hx=0
    ffmpeg -nostdin -v error -y -i stills/full-${P[$j]}.png -vf "crop=80:100:$hx:130,scale=400:500:flags=neighbor" -frames:v 1 stills/head-$((i+1))-${P[$j]}.png
  done
done
