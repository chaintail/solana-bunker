#!/bin/bash
# Runs ON dev-mac. back frames + head-and-neck clip (bob = 4*sin(2*pi*t/2.2), same as the scene) + front frames, with Liam's audio from the same stretch.
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/head-test; S=${S:-23}
ffmpeg -nostdin -v error -y -framerate 30 -i render/back/f%05d.png -i head-key.mov -framerate 30 -i render/front/f%05d.png -ss $S -t 10 -i ~/video-work/bunker-raw.mov \
 -filter_complex "[1:v]fps=30,scale=304:440:flags=lanczos,format=rgba,setpts=PTS-STARTPTS[h];
 [0:v]format=rgba[b];[b][h]overlay=x=238:y='34+4*sin(2*PI*t/2.2)':format=auto:shortest=1[bh];
 [bh][2:v]overlay=format=auto,format=yuv420p,setsar=1[v]" -map '[v]' -map 3:a \
 -r 30 -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -c:a aac -b:a 192k -frames:v 300 -t 10 -movflags +faststart floating-head-test.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames -of compact floating-head-test.mp4
