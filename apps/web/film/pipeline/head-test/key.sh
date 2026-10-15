#!/bin/bash
# Runs ON dev-mac. Head-and-neck alpha clip: RVM alpha minus a luma key of the black shirt, restricted to the zone below the chin.
# (two separate decodes of the comp: format=gray shares the luma plane with its source frame and lut edits it in place, which corrupted the colour branch)
# usage: key.sh <start_s> <dur_s> <out.mov>
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/head-test; B=~/video-work/bunker
LO=${LO:-28}; HI=${HI:-58}
ffmpeg -nostdin -v error -y -ss $1 -t $2 -i $B/matte-full-comp.mp4 -ss $1 -t $2 -i $B/matte-full-alpha.mp4 -loop 1 -framerate 30 -i zone.png -loop 1 -framerate 30 -i kill.png -ss $1 -t $2 -i $B/matte-full-comp.mp4 \
 -filter_complex "
 [0:v]fps=30,format=gray,gblur=sigma=1.5,lut=y='clip((${HI}-val)*255/(${HI}-${LO}),0,255)'[s];
 [2:v]format=gray[z];
 [3:v]format=gray[kl];
 [s][z]blend=all_mode=multiply,dilation,dilation[sd];
 [sd][kl]blend=all_mode=lighten,negate,gblur=sigma=1.2[k];
 [1:v]fps=30,format=gray[a];
 [a][k]blend=all_mode=multiply,gblur=sigma=0.8[am];
 [4:v]fps=30,format=rgb24,despill=type=green:mix=0.6:expand=0.2,format=gbrp[rgb];
 [rgb][am]alphamerge,crop=760:1100:250:150,format=argb[o]" -map "[o]" -frames:v $((${2}*30)) -c:v qtrle $3
