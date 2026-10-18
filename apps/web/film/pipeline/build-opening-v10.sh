#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. Opening v10 (Liam, voice 2026-10-17), two changes on v9; everything else is v9's.
#  1 sponsor read: everything through "by" stays at 1.2x (v9's atempo file), "Chaintail Labs" and the end tail are the original 1.0 render (render-vo-v10.py:
#    joined at a zero crossing in the silence 10 ms before "Chaintail", no added pause). The read is 3.766 -> 3.952 s, so the sponsor card holds 6 frames
#    longer (s00-intro-v10.html, capture-v10.sh): 123 -> 129 frames (4.1 -> 4.3 s). Every later part moves 6 frames (0.2 s) later.
#  2 jingle A starts 0.45 s earlier than v9's placement (v9: its big hit, 0.660 s into the file, on the ident's slam landing) and its 2 ms fade-in is removed
#    (jingles-v10.py). The duck at Liam's first word and the 1.0 s fade-out are v9's.
# Advisory picture and voice, ident, jingle C on the SPECIAL REPORT slam, desk, hold, announcer, bed and limiter are v9's (the advisory and ident segments are
# v9's encodes, opening-v9/out/final).
# Timeline (frames at 30 fps): sponsor 0-128 | advisory 129-475 | ident 476-541 | desk 542-1573 | hold 1574-1636 = 1637 frames = 54.5667 s (v9 1631 = 54.3667 s)
# Needs: opening-v10/out/cap/s00-intro-v10/list.txt (capture-v10.sh), opening-v9/out/{final/s00b-advisory-v9.mp4,final/s00c-ident.mp4,vo/adv-vo.wav,vo/sponsor-vo.wav},
#        out/s00a-v5/vo-final.wav, opening-x11/out/final/{s02-news,hold}.mp4, opening-x11/out/desk-final.wav, out/s8/special-report.wav, the cue files below.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; X=opening-v10; O=$X/out; P9=opening-v9/out; mkdir -p $O/final $O/jingles $O/vo
FFV="ffmpeg -nostdin -v error -y"; PY=~/speech-lab/.venv/bin/python3; AU=~/audio-work/solana-bunker/out
XT=54.5667   # 1637 frames; the advisory starts at frame 129, the ident at 476, the desk at 542, the hold at 1574
A_HIT=$(python3 -c "print(round((476 + 42) / 30, 4))")            # ident frame 42 (1.40 s): BREAKING NEWS lands (v9's anchor for A; v10 starts A 0.45 s earlier)
WORD=$(python3 -c "print(round(542 / 30 + 0.28, 4))")           # Liam's first word: 0.28 s into desk-final.wav
C_HIT=$(python3 -c "print(round((542 + 1031) / 30, 4))")       # desk frame 1031: SPECIAL REPORT at rest
ANN=$(python3 -c "print(round(1574 / 30 + 0.75, 4))")
nfr() { ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "$1"; }
# --- 0 the sponsor read
$PY $X/film/pipeline/render-vo-v10.py out/s00a-v5/vo-final.wav $P9/vo/sponsor-vo.wav $O/vo/sponsor-vo.wav
# --- 1 picture: the new sponsor card from its lossless chunks, then v9's advisory and ident, x11's desk and hold
$FFV -f concat -safe 0 -i $O/cap/s00-intro-v10/list.txt -frames:v 129 -r 30 -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p $O/final/s00-intro-v10.mp4
[ "$(nfr $O/final/s00-intro-v10.mp4)" = 129 ] || { echo "s00-intro-v10 frame count wrong"; exit 1; }
printf "file '%s'\n" $PWD/$O/final/s00-intro-v10.mp4 $PWD/$P9/final/s00b-advisory-v9.mp4 $PWD/$P9/final/s00c-ident.mp4 $PWD/opening-x11/out/final/s02-news.mp4 $PWD/opening-x11/out/final/hold.mp4 > $O/final/list.txt
# --- 2 jingle gains, as v9: event loudness (ebur128 I, 1 s of silence each side) matched to x11's horn as it was mixed
ev() { ffmpeg -nostdin -hide_banner -i "$1" -af "$2,adelay=1000:all=1,apad=pad_dur=1,ebur128" -f null - 2>&1 | grep -A3 Summary | sed -n 's/.*I: *\(-*[0-9.]*\) LUFS/\1/p'; }
IH=$(ev $AU/audition/news-close-2-horn-stabs.mp3 "aresample=48000,pan=mono|c0=0.5*c0+0.5*c1,volume=-4dB,afade=t=out:st=1.2:d=0.13")
IA=$(ev $AU/work/news-open-1-mini-jingle.wav "pan=mono|c0=0.5*c0+0.5*c1")
IC=$(ev $AU/work/news-open-3-da-da-da-daaa.wav "pan=mono|c0=0.5*c0+0.5*c1")
GA=$(python3 -c "print(round($IH - $IA, 2))"); GC=$(python3 -c "print(round($IH - $IC, 2))")
echo "event loudness: horn as mixed in x11 $IH LUFS; A at 0 dB $IA -> gain $GA dB; C at 0 dB $IC -> gain $GC dB"
# --- 3 jingle stems (A 0.45 s earlier, fade-in removed via the pre-master)
$PY $X/film/pipeline/jingles-v10.py $AU/work/news-open-1-mini-jingle.wav $AU/work/news-open-3-da-da-da-daaa.wav $O/jingles $XT $A_HIT $GA $WORD $C_HIT $GC \
  out/s8/special-report.wav $ANN 5 ${DUCK_C:-8} 0.45 $AU/work/news-open-1-mini-jingle.pre.wav
# --- 4 mix + mux. Inputs: 0 picture, 1 advisory vo, 2 sponsor vo, 3 jingle C, 4 announcer, 5 bed source, 6 desk voice, 7 jingle A
$FFV -f concat -safe 0 -i $O/final/list.txt -i $P9/vo/adv-vo.wav -i $O/vo/sponsor-vo.wav -i $O/jingles/jingle-c.wav -i out/s8/special-report.wav \
  -f lavfi -i "anoisesrc=d=$XT:c=brown:a=0.3:r=48000:s=1" -i opening-x11/out/desk-final.wav -i $O/jingles/jingle-a.wav \
  -/filter_complex $X/film/pipeline/audio-v10.filter -map 0:v -map '[aout]' -c:v copy -c:a aac -b:a 192k -movflags +faststart -t $XT out/opening-v10.mp4
ffmpeg -nostdin -hide_banner -i out/opening-v10.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -A20 Summary | grep -E "I:|LRA:|Peak:"
$FFV -i out/opening-v10.mp4 -vf scale=960:540:flags=lanczos -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart out/opening-v10-phone.mp4
# --- 5 excerpts: the sponsor card's audio (frames 0-128, 0-4.3 s), and the ident from 1 s before its first frame to 2 s into the desk (14.8667-20.0667 s)
$FFV -i out/opening-v10.mp4 -vn -t 4.3 -c:a libmp3lame -b:a 192k out/opening-v10-sponsor-excerpt.mp3
$FFV -ss 14.8667 -i out/opening-v10.mp4 -vn -t 5.2 -c:a libmp3lame -b:a 192k out/opening-v10-ident-excerpt.mp3
for v in opening-v10 opening-v10-phone; do ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,width,height -of compact out/$v.mp4; done
echo "A_HIT $A_HIT WORD $WORD C_HIT $C_HIT ANN $ANN"
