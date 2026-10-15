#!/bin/bash
# Runs ON do-box: copies the slide-5 scene tree to dev-mac (film/ + the scene's data) and runs the stills/captures there.
set -e
cd "$(dirname "$0")/.."
rsync -a --delete --exclude heads --exclude assets/bodies --exclude 's0[0-4]*' --exclude 's-head*' --exclude pipeline ./ dev-mac:video-work/solana-bunker/s05/film/
rsync -a pipeline/ dev-mac:video-work/solana-bunker/s05/film/pipeline/
