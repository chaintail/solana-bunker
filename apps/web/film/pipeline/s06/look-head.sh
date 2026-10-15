#!/bin/bash
# Runs ON dev-mac. One head-and-neck still (RGBA PNG, 760x1100 key crop) from Liam's take for the s06 look draft.
# Same key as pipeline/head-test/key.sh (RVM alpha minus a luma key of the black shirt below the chin, zone.png / kill.png).
# usage: look-head.sh <t_s> <out.png>
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
B=~/video-work/bunker; HT=~/video-work/head-test; LO=28; HI=58
ffmpeg -nostdin -v error -y -ss $1 -i $B/matte-full-comp.mp4 -ss $1 -i $B/matte-full-alpha.mp4 -loop 1 -i $HT/zone.png -loop 1 -i $HT/kill.png -ss $1 -i $B/matte-full-comp.mp4 \
 -filter_complex "
 [0:v]format=gray,gblur=sigma=1.5,lut=y='clip((${HI}-val)*255/(${HI}-${LO}),0,255)'[s];
 [2:v]format=gray[z];[3:v]format=gray[kl];
 [s][z]blend=all_mode=multiply,dilation,dilation[sd];
 [sd][kl]blend=all_mode=lighten,negate,gblur=sigma=1.2[k];
 [1:v]format=gray[a];[a][k]blend=all_mode=multiply,gblur=sigma=0.8[am];
 [4:v]format=rgb24,despill=type=green:mix=0.6:expand=0.2,format=gbrp[rgb];
 [rgb][am]alphamerge,crop=760:1100:250:150,format=rgba[o]" -map "[o]" -frames:v 1 "$2"
