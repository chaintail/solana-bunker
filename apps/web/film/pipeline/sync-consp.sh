#!/bin/bash
# Runs on do-box. Copies only the conspiracy scene files to dev-mac (no --delete, and film.js/capture.mjs are left alone:
# the opening builder shares that tree).
cd "$(dirname "$0")/.."
F=$(ls dossier.css s01-title.html s03-conspiracy.html 2>/dev/null)
rsync -a $F dev-mac:video-work/solana-bunker/film/
rsync -a lib/dossier.js dev-mac:video-work/solana-bunker/film/lib/
rsync -a data/conspiracy-timing.js data/conspiracy-edl.json dev-mac:video-work/solana-bunker/film/data/
