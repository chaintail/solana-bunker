#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. Re-pulls slide 6's opening frames from slide 5's last frame (s05/film = film/s05 tree) -> s06/out/s05-end/:
#   full.png  = s05-hash.html at its last frame time (N-1)/30, N = round(total*30) (the x12 capture's last output frame shows the same page time)
#   plate.png = full.png with the lab coat replaced by a render of the same time with #figL hidden (what is behind him once the live s06 figure takes over)
# The plate is a composite, not a second plain render: headless Chrome sometimes rasterises with 4-level edge anti-aliasing and sometimes with smooth anti-aliasing,
# so two renders can differ on every edge of the board; outside the coat silhouette the plate is taken from full.png byte for byte, so the board does not change at
# the takeover. Check: full.png pushed through the master's chunk encode (x264 crf 12 yuv420p) is compared with the s05 master's last frame (42 dB on the board when it is
# the master's raster mode, about 37.6 dB in the other one); the full render is retried until it passes. Which mode Chrome
# picks is not under our control (2026-10-16: one pass at 42.0 dB, then four renders in a row at 37.5-37.6 dB), so FULL=<png> uses an existing full frame
# (e.g. the committed film/assets/s06/s05-end-full.png) instead of rendering one, still runs the check, and builds the plate from it. Copy full.png / plate.png to film/assets/s06/s05-end-{full,plate}.png after the check.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker; O=s06/out/s05-end; MASTER=${MASTER:-out/s05-v7-x12.mp4}; mkdir -p $O
T=$(python3 -c "import json;d=json.load(open('s05/film/data/s05-edl.json'));print(repr((round(d['total']*30)-1)/30))")
echo "s05 last frame time $T"
sed "s#</head>#<style>\#figL{visibility:hidden !important}</style></head>#" s05/film/s05-hash.html > s05/film/s05-nocoat-tmp.html
ffmpeg -nostdin -v error -y -sseof -0.2 -i $MASTER -update 1 $O/master-last.png
for try in 1 2 3 4; do   # full.png must be in the master's raster mode (board PSNR after the round trip > 40 dB), else re-render
  if [ -n "${FULL:-}" ]; then cp "$FULL" $O/full.png; else
  ( cd s05/film && node scripts/capture.mjs s05-hash --still=$T --out=../../$O/a ) > /dev/null; mv $O/a/still-$T.png $O/full.png; rmdir $O/a; fi
  ffmpeg -nostdin -v error -y -i $O/full.png -frames:v 1 -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p $O/rt.mp4
  ffmpeg -nostdin -v error -y -i $O/rt.mp4 -frames:v 1 $O/rt.png
  P=$(ffmpeg -nostdin -i $O/rt.png -i $O/master-last.png -lavfi '[0:v]crop=928:720:352:0,format=rgb24[a];[1:v]crop=928:720:352:0,format=rgb24[b];[a][b]psnr' -f null - 2>&1 | grep -o 'average:[0-9.]*' | cut -d: -f2)
  echo "full render try $try: board PSNR vs master last frame $P dB"; python3 -c "import sys; sys.exit(0 if float('$P') > 40 else 1)" && break
  [ -n "${FULL:-}" ] || [ $try = 4 ] && { echo "full.png never matched the master's raster mode"; rm -f s05/film/s05-nocoat-tmp.html; exit 1; }
done
( cd s05/film && node scripts/capture.mjs s05-nocoat-tmp --still=$T --out=../../$O/b ) > /dev/null; mv $O/b/still-$T.png $O/nocoat.png; rmdir $O/b
rm -f s05/film/s05-nocoat-tmp.html
/usr/bin/python3 - $O <<'PY'   # system python: has numpy/scipy/PIL (Homebrew python3 does not)
import sys, numpy as np; from PIL import Image; from scipy import ndimage as ndi
o = sys.argv[1]; L = lambda p: np.array(Image.open(p).convert('RGB')).astype(int)
n, p = L(o + '/full.png'), L(o + '/nocoat.png')
m = np.abs(n - p).max(2) > 4; reg = np.zeros_like(m); reg[150:715, 0:360] = True; m &= reg          # the coat stands in x < 360, y 150-715
m = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=3)); lab, k = ndi.label(m)
m = lab == (np.argmax(ndi.sum(m, lab, range(1, k + 1))) + 1); m = ndi.binary_dilation(m, iterations=4)  # largest component = the coat, 4 px margin
Image.fromarray(np.where(m[..., None], p, n).astype(np.uint8)).save(o + '/plate.png', optimize=True)
ring = ndi.binary_dilation(m, iterations=2) & ~m; print('coat mask %d px, seam ring max |full-nocoat| %d' % (m.sum(), np.abs(n - p).max(2)[ring].max()))
PY
