#!/bin/bash
# do-box helper: sync, take stills on dev-mac at the comma list $1, copy them to $2
cd "$(dirname "$0")/.." && ./pipeline/s05-sync.sh && ssh dev-mac "rm -rf ~/video-work/solana-bunker/s05/out/stills; ~/video-work/solana-bunker/s05/film/pipeline/s05-still.sh $1 2>&1 | tail -2" && rm -rf $2 && mkdir -p $2 && rsync -a dev-mac:video-work/solana-bunker/s05/out/stills/ $2/
