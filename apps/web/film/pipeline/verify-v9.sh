#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker after build-opening-v9.sh. Opening v9 checks:
#  1 glitch-scan v2 (apps/web/film/scripts/glitch-scan.py on film/conspiracy, copied to opening-v9/tools/glitch-scan-v2.py) on master and phone: explicit chunk starts (the card captures' 60-frame chunks, x11's 300-frame desk chunks, the hold), stale-copy refs at
#    each part's frame 0 (sponsor 0, advisory 123, ident 470, desk 536)
#  2 the mix as wav (48 kHz for onsets, 16 kHz for whisper on do-box)
#  3 onsets in the mix: jingle A around the ident landing (17.0667), jingle C around the SPECIAL REPORT slam (52.2333); the same on the jingle stems alone
#  4 stills from the master, and the ident compare sheet (v9 master frames beside s11-v6 master frames at the same beats)
set -uo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; X=opening-v9; V=$X/verify; mkdir -p $V/stills; PY=~/speech-lab/.venv/bin/python3
CS=0,60,120,123,183,243,303,363,423,470,530,536,836,1136,1436,1568
for v in opening-v9 opening-v9-phone; do echo "== glitch scan $v"; ~/venvs/audio/bin/python $X/tools/glitch-scan-v2.py out/$v.mp4 --chunk-starts $CS --ref 0 --ref 123 --ref 470 --ref 536; echo "exit $?"; done
ffmpeg -nostdin -v error -y -i out/opening-v9.mp4 -vn -ac 1 -ar 48000 -c:a pcm_s16le $V/mix48.wav
ffmpeg -nostdin -v error -y -i out/opening-v9.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le $V/mix16.wav
echo "== onsets, mix, jingle A window"; $PY $X/film/pipeline/onsets-fine.py $V/mix48.wav 16.2 17.6
echo "== onsets, jingle A stem"; $PY $X/film/pipeline/onsets-fine.py $X/out/jingles/jingle-a.wav 16.2 17.6
echo "== onsets, mix, jingle C window"; $PY $X/film/pipeline/onsets-fine.py $V/mix48.wav 51.6 52.6
echo "== onsets, jingle C stem"; $PY $X/film/pipeline/onsets-fine.py $X/out/jingles/jingle-c.wav 51.6 52.6
# stills (frame numbers in the final film)
st() { ffmpeg -nostdin -v error -y -i out/opening-v9.mp4 -vf "select=eq(n\,$1)" -frames:v 1 $V/stills/$2.png; }
st 30 sponsor-1.0s; st 110 sponsor-3.67s; st 250 advisory-4.2s; st 440 advisory-10.6s; st 469 advisory-last
st 470 ident-f0; st 480 ident-0.33s; st 488 ident-0.6s; st 500 ident-1.0s; st 506 ident-1.2s; st 512 ident-slam-1.4s; st 520 ident-1.67s; st 535 ident-last
st 536 desk-f0; st 545 desk-0.3s; st 566 desk-1.0s; st 1500 wipe-50.0s; st 1530 wipe-51.0s; st 1567 special-report-slam; st 1600 special-report-hold
for p in 470 471 512 513 535 536 537; do st $p f$p; done
# compare: s11-v6 ident beats (scene t: lemur mid-spin 0.75, lines in 1.5, CNN landed 2.05, streak 2.4) beside v9 at the same beats (0.75, 1.1, 1.4, 1.73)
s11() { ffmpeg -nostdin -v error -y -ss $1 -i s11/out/s11-v6.mp4 -frames:v 1 $V/stills/s11-$1.png; }
s11 0.75; s11 1.5; s11 2.05; s11 2.4
st 492 cmp-0.75; st 503 cmp-1.1; st 512 cmp-1.4; st 522 cmp-1.73
$PY $X/film/pipeline/contact-sheet.py out/opening-v9-ident-compare.png 2 800 450 $V/stills/s11-0.75.png:"closing card (s11 v6) 0.75 s: lemur spin" $V/stills/cmp-0.75.png:"opening v9 ident 0.75 s: lemur spin" \
  $V/stills/s11-1.5.png:"closing 1.50 s: network lines" $V/stills/cmp-1.1.png:"opening 1.10 s: network lines" \
  $V/stills/s11-2.05.png:"closing 2.05 s: CNN slam lands" $V/stills/cmp-1.4.png:"opening 1.40 s: CNN + BREAKING NEWS slam lands" \
  $V/stills/s11-2.4.png:"closing 2.40 s: streak" $V/stills/cmp-1.73.png:"opening 1.73 s: streak"
ls -la out/opening-v9-ident-compare.png
