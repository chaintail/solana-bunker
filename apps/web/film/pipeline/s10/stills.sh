#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s10. Stills of scene 10 at the given scene times (comma list), composited exactly as build.sh video does
# (backdrop, matte at the mapped take time with the B2 punch-in, scene 9's last frame under the wipe, front layer) -> out/stills/g-<t>.png (1280x720)
# and out/stills/s-<t>.png (426x240). Needs out/back.png (build.sh assets) and data/s10-edl.js (build.sh audio).
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s10; B=~/video-work/bunker; mkdir -p out/stills
for i in 1 2 3; do node film/scripts/capture.mjs s10-news --layer=front --settle=4 --still="$1" --out=out/stills > out/stills.log 2>&1 && break; done; tail -1 out/stills.log
for t in ${1//,/ }; do
  read SRC SC X Y S9 <<< "$(python3 -c "
t=$t; k=round(t*30)
print(*( (round(k/30+531.75,4),'525:700',377,-20) if k<401 else (round(k/30+550.20,4),'567:756',356,-44) ), 1 if t<0.55 else 0)")"
  ffmpeg -nostdin -v error -y -loop 1 -i out/back.png -ss $SRC -i $B/matte-full-comp.mp4 -ss $SRC -i $B/matte-full-alpha.mp4 -loop 1 -i film/assets/s10-s09-last.png -loop 1 -i out/stills/still-$t.png -filter_complex \
   "[1:v]setpts=PTS-STARTPTS,scale=$SC:flags=lanczos,despill=type=green:mix=0.6:expand=0.2,format=rgb24[c];[2:v]setpts=PTS-STARTPTS,scale=$SC:flags=lanczos,format=gray[a];[c][a]alphamerge[l];
    [0:v]setpts=PTS-STARTPTS,format=rgb24[bg];[bg][l]overlay=x=$X:y=$Y:format=auto[b1];[3:v]setpts=PTS-STARTPTS,format=rgb24[s9];[b1][s9]overlay=0:0:enable='gt($S9,0.5)'[b2];
    [4:v]setpts=PTS-STARTPTS,format=rgba[fr];[b2][fr]overlay=format=auto,format=rgb24[o]" -map '[o]' -frames:v 1 out/stills/g-$t.png
  ffmpeg -nostdin -v error -y -i out/stills/g-$t.png -vf scale=426:240:flags=bicubic -frames:v 1 out/stills/s-$t.png
done
