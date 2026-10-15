#!/bin/bash
# do-box side: usage s04-fetch.sh <dest-dir> <t> ... ; renders stills on dev-mac and copies them back.
D=$1; shift; mkdir -p $D
ssh dev-mac "bash ~/video-work/solana-bunker/film/pipeline/s04-stills.sh $*" >/dev/null && for t in "$@"; do scp -q dev-mac:video-work/solana-bunker/out/s04/stills/still-$t.png $D/; done
