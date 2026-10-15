#!/bin/bash
# usage: still-consp.sh <scene> <t,t,...>   Captures stills on dev-mac into render-consp/stills/<scene>/ and copies them to the local scratch dir $STILLS.
set -e
S=$1; T=$2
ssh dev-mac "export PATH=/opt/homebrew/bin:\$PATH CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'; cd ~/video-work/solana-bunker/film && node scripts/capture.mjs $S --still=$T --out=../render-consp/stills/$S" | tail -2
mkdir -p "$STILLS/$S"; rsync -a dev-mac:video-work/solana-bunker/render-consp/stills/$S/ "$STILLS/$S/"
