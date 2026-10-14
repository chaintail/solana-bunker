#!/bin/bash
# usage: sync-and-still.sh <scene> <t,t,...> [layer]   (renders stills on dev-mac, copies them back to /tmp/pr/st/<scene>)
cd "$(dirname "$0")/../.." || exit 1
rsync -a film/ dev-mac:video-work/solana-bunker/film/ --exclude pipeline
L=""; [ -n "$3" ] && L="--layer=$3"
ssh dev-mac "export PATH=/opt/homebrew/bin:\$PATH CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'; cd ~/video-work/solana-bunker/film && node scripts/capture.mjs $1 --still=$2 $L --out=../out/stills/$1${3:+-$3}" | tail -1
mkdir -p /tmp/pr/st/$1${3:+-$3}; scp -q "dev-mac:video-work/solana-bunker/out/stills/$1${3:+-$3}/*" /tmp/pr/st/$1${3:+-$3}/
