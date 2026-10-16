#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. Opening v9 (Liam 2026-10-16), four changes on the locked x11; everything else is x11's.
#  1 sponsor and advisory reads at 1.2x from the existing renders (render-vo-v9.py: atempo, pitch kept; advisory per phrase to an effective 1.2), cards shortened
#    to match (capture-v9.sh): sponsor 4.9 -> 4.1 s (123 frames), advisory 13 -> 11.5667 s (347 frames)
#  2 the BREAKING NEWS band is replaced by the Chaintail News Network ident with BREAKING NEWS (s00c-ident.html, port of s11's ident), 2.2 s (66 frames, was 2.0)
#  3 jingle A: first big hit on the ident's slam landing (ident 1.40 s), runs under the desk entry, ducked -12 dB (100 ms) at Liam's first word and faded over 1.0 s
#  4 jingle C replaces the horn stabs: last hit on the SPECIAL REPORT slam frame (desk frame 1031, the first frame with the card at rest), gain matched to the horn's
#    event loudness in x11, rings under "A special report." to the end of the scene
# Desk picture, desk voice (x11's desk-final.wav: denoised once, the jump cut, 1.1x, two-pass loudnorm), the hold, the announcer (+5 dB, 0.75 s after the hold
# starts), the brown-noise bed and the limiter are x11's.
# Timeline (frames at 30 fps): sponsor 0-122 | advisory 123-469 | ident 470-535 | desk 536-1567 | hold 1568-1630 = 1631 frames = 54.3667 s (x11 1692 = 56.4 s)
# Needs: opening-v9/out/cap/<scene>/list.txt (capture-v9.sh), opening-v9/out/vo/{sponsor-vo,adv-vo}.wav (render-vo-v9.py),
#        opening-x11/out/final/{s02-news,hold}.mp4 + opening-x11/out/desk-final.wav (build-opening-x11.sh), out/s8/special-report.wav, the cue files below.
# DUCK_C (dB, default 8): C's duck under the announcer's voiced span. Unducked, the voice-over-C margin was 4.7-12.8 dB in the voiced 100 ms windows (6.1 and
# 4.7 dB on "special"); 8 dB puts every voiced window at 12.7 dB or more. C is not shortened.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; X=opening-v9; O=$X/out; mkdir -p $O/final $O/jingles
FFV="ffmpeg -nostdin -v error -y"; PY=~/speech-lab/.venv/bin/python3; AU=~/audio-work/solana-bunker/out
XT=54.3667   # 1631 frames; the ident starts at frame 470, the desk at 536, the hold at 1568
A_HIT=$(python3 -c "print(round((470 + 42) / 30, 4))")            # ident frame 42 (1.40 s): BREAKING NEWS lands (end of the 0.25 s slam, the frame shake)
WORD=$(python3 -c "print(round(536 / 30 + 0.28, 4))")          # Liam's first word: 0.28 s into desk-final.wav (10 ms RMS rises out of the floor)
C_HIT=$(python3 -c "print(round((536 + 1031) / 30, 4))")      # desk frame 1031: SPECIAL REPORT at rest (frame 1030 is < 1 px off, 1031 = the held frame)
ANN=$(python3 -c "print(round(1568 / 30 + 0.75, 4))")
nfr() { ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "$1"; }
# --- 1 picture: card segments from the lossless chunks, then x11's desk and hold
for s in s00-intro:123 s00b-advisory-v9:347 s00c-ident:66; do
  sc=${s%:*}; n=${s#*:}
  $FFV -f concat -safe 0 -i $O/cap/$sc/list.txt -frames:v $n -r 30 -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p $O/final/$sc.mp4
  [ "$(nfr $O/final/$sc.mp4)" = $n ] || { echo "$sc frame count wrong"; exit 1; }
done
printf "file '%s'\n" $PWD/$O/final/s00-intro.mp4 $PWD/$O/final/s00b-advisory-v9.mp4 $PWD/$O/final/s00c-ident.mp4 $PWD/opening-x11/out/final/s02-news.mp4 $PWD/opening-x11/out/final/hold.mp4 > $O/final/list.txt
# --- 2 jingle gains: event loudness (ebur128 I, 1 s of silence each side) matched to x11's horn as it was mixed (mono fold, -4 dB, fade at 1.2 s)
ev() { ffmpeg -nostdin -hide_banner -i "$1" -af "$2,adelay=1000:all=1,apad=pad_dur=1,ebur128" -f null - 2>&1 | grep -A3 Summary | sed -n 's/.*I: *\(-*[0-9.]*\) LUFS/\1/p'; }
IH=$(ev $AU/audition/news-close-2-horn-stabs.mp3 "aresample=48000,pan=mono|c0=0.5*c0+0.5*c1,volume=-4dB,afade=t=out:st=1.2:d=0.13")
IA=$(ev $AU/work/news-open-1-mini-jingle.wav "pan=mono|c0=0.5*c0+0.5*c1")
IC=$(ev $AU/work/news-open-3-da-da-da-daaa.wav "pan=mono|c0=0.5*c0+0.5*c1")
GA=$(python3 -c "print(round($IH - $IA, 2))"); GC=$(python3 -c "print(round($IH - $IC, 2))")
echo "event loudness: horn as mixed in x11 $IH LUFS; A at 0 dB $IA -> gain $GA dB; C at 0 dB $IC -> gain $GC dB"
# --- 3 jingle stems
$PY $X/film/pipeline/jingles-v9.py $AU/work/news-open-1-mini-jingle.wav $AU/work/news-open-3-da-da-da-daaa.wav $O/jingles $XT $A_HIT $GA $WORD $C_HIT $GC out/s8/special-report.wav $ANN 5 ${DUCK_C:-8}
# --- 4 mix + mux. Inputs: 0 picture, 1 advisory vo, 2 sponsor vo, 3 jingle C, 4 announcer, 5 bed source, 6 desk voice, 7 jingle A
$FFV -f concat -safe 0 -i $O/final/list.txt -i $O/vo/adv-vo.wav -i $O/vo/sponsor-vo.wav -i $O/jingles/jingle-c.wav -i out/s8/special-report.wav \
  -f lavfi -i "anoisesrc=d=$XT:c=brown:a=0.3:r=48000:s=1" -i opening-x11/out/desk-final.wav -i $O/jingles/jingle-a.wav \
  -/filter_complex $X/film/pipeline/audio-v9.filter -map 0:v -map '[aout]' -c:v copy -c:a aac -b:a 192k -movflags +faststart -t $XT out/opening-v9.mp4
ffmpeg -nostdin -hide_banner -i out/opening-v9.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -A20 Summary | grep -E "I:|LRA:|Peak:"
$FFV -i out/opening-v9.mp4 -vf scale=960:540:flags=lanczos -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart out/opening-v9-phone.mp4
# --- 5 the card excerpt: the last 12 s (Liam's sign-off line, the SPECIAL REPORT wipe from 50.72 s, jingle C, "A special report.", the end)
$FFV -ss $(python3 -c "print(round($XT - 12, 4))") -i out/opening-v9.mp4 -vn -t 12 -c:a libmp3lame -b:a 192k out/opening-v9-card-excerpt.mp3
for v in opening-v9 opening-v9-phone; do ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,width,height -of compact out/$v.mp4; done
echo "A_HIT $A_HIT WORD $WORD C_HIT $C_HIT ANN $ANN"
