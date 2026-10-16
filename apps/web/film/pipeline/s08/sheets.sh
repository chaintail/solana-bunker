#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s08. 2x2 contact sheets of graded stills (out/stills/g-<t>.png) for review: sheets.sh <name> t1,t2,t3,t4 [...]
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker/s08/out/stills; N=$1; shift
L=(${1//,/ }); n=0
for ((i=0;i<${#L[@]};i+=4)); do a=(); for j in 0 1 2 3; do x=${L[$((i+j))]:-}; if [ -n "$x" ]; then a+=(-i g-$x.png); else a+=(-f lavfi -i color=black:s=1280x720:d=1); fi; done
  ffmpeg -nostdin -v error -y "${a[@]}" -filter_complex "[0:v]scale=640:360[a];[1:v]scale=640:360[b];[2:v]scale=640:360[c];[3:v]scale=640:360[d];[a][b][c][d]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0" -frames:v 1 $N-$n.png; n=$((n+1)); done
