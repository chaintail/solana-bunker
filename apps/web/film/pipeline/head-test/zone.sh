#!/bin/bash
# Runs ON dev-mac. Static "below the chin, outside the jaw" zone mask (1080x1440 gray): 255 where the shirt key may act.
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/head-test
ffmpeg -nostdin -v error -y -f lavfi -i color=c=black:s=1080x1440,format=gray \
  -vf "geq=lum='255*max(clip((hypot((X-630)/235,(Y-870)/200)-1)*6,0,1)*clip((Y-925)/40,0,1),clip((abs(X-625)-150)/20,0,1)*clip((Y-955)/15,0,1))'" -frames:v 1 zone.png
# hard-kill mask: everything below the jaw that is outside the neck column (shoulders / sleeve folds whose highlights beat the luma key)
ffmpeg -nostdin -v error -y -f lavfi -i color=c=black:s=1080x1440,format=gray \
  -vf "geq=lum='255*clip((abs(X-625)-172)/18,0,1)*clip((Y-950)/12,0,1)'" -frames:v 1 kill.png
