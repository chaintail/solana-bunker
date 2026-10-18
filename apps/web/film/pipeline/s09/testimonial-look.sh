#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/ending (film-s09/ = rsync of film/s09's apps/web/film). Look draft A of film-plan-ending.md:
# 1 bodies.py (now with professor-point) -> film-s09/assets/s09/; 2 one keyed head frame of the lab coat on "rotation" (528.45 s): the key of
# pipeline/head-test/key.sh / s06 look-head.sh, but with the zone / kill masks recentred on the jaw (the composer's chin patch for heads.py,
# chin-s09-heads.diff: zone.png / kill.png are centred on x 625 and cut a notch out of the left jaw). JX 545 = the median jaw-span centre,
# rows 930-1080 of matte-full-alpha, at eight times across 518.9-532.5 s (541-549); 3 capture s09-testimonial-look.html; 4 post as the colour half of scene 9 (vignette only);
# 5 out/ending-look-A.png (1280x720) and out/ending-look-A-240.png (426x240).
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/ending; mkdir -p out film-s09/heads
(cd film-s09 && /usr/bin/python3 pipeline/s09/bodies.py > /dev/null)
JX=545; LO=28; HI=58; B=~/video-work/bunker; T=528.45
ffmpeg -nostdin -v error -y -f lavfi -i color=c=black:s=1080x1440,format=gray -vf "geq=lum='255*max(clip((hypot((X-$JX)/255,(Y-870)/245)-1)*12,0,1)*clip((Y-925)/40,0,1),clip((abs(X-$JX)-200)/20,0,1)*clip((Y-955)/15,0,1))'" -frames:v 1 out/zone-jaw.png
ffmpeg -nostdin -v error -y -f lavfi -i color=c=black:s=1080x1440,format=gray -vf "geq=lum='255*clip((abs(X-$JX)-265)/18,0,1)*clip((Y-950)/12,0,1)'" -frames:v 1 out/kill-jaw.png
ffmpeg -nostdin -v error -y -ss $T -i $B/matte-full-comp.mp4 -ss $T -i $B/matte-full-alpha.mp4 -loop 1 -i out/zone-jaw.png -loop 1 -i out/kill-jaw.png -ss $T -i $B/matte-full-comp.mp4 \
 -filter_complex "[0:v]format=gray,gblur=sigma=1.5,lut=y='clip(($HI-val)*255/($HI-$LO),0,255)'[s];[2:v]format=gray[z];[3:v]format=gray[kl];
 [s][z]blend=all_mode=multiply,dilation,dilation[sd];[sd][kl]blend=all_mode=lighten,negate,gblur=sigma=1.2[k];
 [1:v]format=gray[a];[a][k]blend=all_mode=multiply,gblur=sigma=0.8[am];
 [4:v]format=rgb24,despill=type=green:mix=0.6:expand=0.2,format=gbrp[rgb];[rgb][am]alphamerge,crop=760:1100:250:150,format=rgba[o]" -map "[o]" -frames:v 1 film-s09/heads/s09-look-lab.png
node film-s09/scripts/capture.mjs s09-testimonial-look --settle=4 --still=0.5 --out=out/look-a > out/look-a.log 2>&1; tail -1 out/look-a.log
ffmpeg -nostdin -v error -y -i out/look-a/still-0.5.png -vf "format=yuv444p,vignette=angle=PI/4.6,format=rgb24" -frames:v 1 out/ending-look-A.png
ffmpeg -nostdin -v error -y -i out/ending-look-A.png -vf scale=426:240:flags=bicubic -frames:v 1 out/ending-look-A-240.png
