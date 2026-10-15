#!/bin/bash
# Runs ON dev-mac. Revision 7 capture into render-v7/. Changes vs v6: the advisory card (new audio timing) and the PiP outline (own layer, zoom driven from the seek hook),
# which only differs in the zoom (front frames ~179..246). Front frames are symlinks to render-v5 (identical outside the zoom), except:
#   - 175..251 (5.8333..8.4 s): recaptured with --fresh (a fresh page per frame; Chrome drops the outline paint on isolated frames after an incremental update, e.g. frame 202).
#     Every one of these frames was checked: the 5 px white outline is present on the right and top edge (see the ring check in the commit message / report).
#   - 1080..1134 (36.0 s on): the v6 tail (wipe), recaptured, forced to RGBA (see capture-v6.sh).
export PATH=/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/film; R=../render-v7; mkdir -p $R/s02-news-front $R/new-zoom $R/new-tail
node scripts/capture.mjs s00b-advisory --out=$R/s00b-advisory > ../out/cap-v7-a.log 2>&1 &
for i in $(seq 0 1134); do ln -sf ../../render-v5/s02-news-front/$(printf 'f%05d.png' $i) $R/s02-news-front/$(printf 'f%05d.png' $i); done
node scripts/capture.mjs s02-news --layer=front --fresh --from=5.8333 --to=8.4 --out=$R/new-zoom > ../out/cap-v7-b.log 2>&1
node scripts/capture.mjs s02-news --layer=front --from=36.0 --to=37.8333 --out=$R/new-tail >> ../out/cap-v7-b.log 2>&1
node scripts/capture.mjs s02-news --layer=back --still=0 --out=$R/s02-news-back >> ../out/cap-v7-b.log 2>&1
wait
# then: force RGBA on new-tail frames, mv new-tail/* and new-zoom/* over the symlinks (mv replaces the link, never writes through it).
