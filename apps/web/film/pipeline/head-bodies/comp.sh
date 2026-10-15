#!/bin/bash
# Runs ON dev-mac. Builds head-bodies-test.mp4 (12 s, 30 fps, silent) from the 3 captured pose frames + the small head clip.
# Poses: A 0-3 s, B 3-6 s, C 6-9 s, A 9-12 s (hard cuts). Head clip loops (10 s clip, 12 s scene) with a 1 px bob per figure (2 px peak to peak), phase offset per figure.
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/head-test/h2; C=cap
CX=(100 308 516 724 932 1140); TY=140.5; HX=26.2
FC="[0:v][1:v][2:v][0:v]concat=n=4:v=1:a=0,format=rgba[bk];[3:v][4:v][5:v][3:v]concat=n=4:v=1:a=0,format=rgba[fr];"
FC+="[6:v]fps=30,format=rgba,split=6[h0][h1][h2][h3][h4][h5];"
prev=bk
for i in 0 1 2 3 4 5; do
  FC+="[$prev][h$i]overlay=x=$(python3 -c "print(${CX[$i]}-$HX)"):y='$TY+1*sin(2*PI*t/2.2+$i*1.1)':format=auto:shortest=0[o$i];"; prev=o$i
done
FC+="[$prev][fr]overlay=format=auto,format=yuv420p,setsar=1[v]"
ffmpeg -nostdin -v error -y \
  -loop 1 -framerate 30 -t 3 -i $C/back/still-1.5.png -loop 1 -framerate 30 -t 3 -i $C/back/still-4.5.png -loop 1 -framerate 30 -t 3 -i $C/back/still-7.5.png \
  -loop 1 -framerate 30 -t 3 -i $C/front/still-1.5.png -loop 1 -framerate 30 -t 3 -i $C/front/still-4.5.png -loop 1 -framerate 30 -t 3 -i $C/front/still-7.5.png \
  -stream_loop -1 -i head-small.mov \
  -filter_complex "$FC" -map '[v]' -r 30 -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -frames:v 360 -t 12 -an -movflags +faststart head-bodies-test.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames,width,height -of compact head-bodies-test.mp4
