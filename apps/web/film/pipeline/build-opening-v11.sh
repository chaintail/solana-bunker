#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. Opening v11 = v10's picture (video stream copied, no capture) with two audio changes (Liam, 2026-10-17):
#  1 jingle A starts at 15.778 s: its first note (8 ms into the file) lands 81 ms before the ident's first frame (15.867 s) and its 1.489 s hit on the slam
#    (17.267 s). jingles-v10.py with a_lead 0.829 (= 1.489 - 0.660: v9's anchor was the 0.660 s hit). No fade-in; duck and 1.0 s fade at Liam's first word as v10.
#    Jingle C is unchanged (the same script and arguments as v10).
#  2 music (music-plan.md, Opening) via music-v11.py: the sponsor groove under the sponsor read with a downbeat end on the WARNING card cut (4.300 s), the
#    advisory dry, and the news bed from bar 1 under jingle A with a downbeat end (bar 18) on the SPECIAL REPORT slam (52.433 s), under jingle C.
#    The plan's opening times are x11 scene times; v11 anchors to v10's picture events, not to plan time + 0.2 s.
# Mix: v10's graph as three stems (stems-v11.filter): dialogue + existing sound (brown-noise bed, advisory, sponsor, desk, announcer), the voices alone (for the
# guard), the stings (jingles A and C). Then dialogue + music + stings, v10's limiter (0.80, no auto-level), two-pass loudnorm (linear) to -16 LUFS as ebur128 reads it.
# Stems for the final stitch are written pre-limiter at the final (loudnorm) gain, 24-bit 48 kHz mono, in opening-v11/out/stems.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; X=opening-v11; O=$X/out; P9=opening-v9/out; P10=opening-v10/out; mkdir -p $O/jingles $O/stems $O/work
FFV="ffmpeg -nostdin -v error -y"; PY=~/speech-lab/.venv/bin/python3; AU=~/audio-work/solana-bunker/out; MU=~/audio-work/solana-bunker/music/suno
XT=54.5667; CUT=4.3; A_HIT=17.2667; WORD=18.3467; C_HIT=52.4333; ANN=53.2167   # frames 129, 518, 542 + 0.28 s, 1573, 1574 + 0.75 s
# --- 1 jingle stems (v10's gains, measured as v10 does)
ev() { ffmpeg -nostdin -hide_banner -i "$1" -af "$2,adelay=1000:all=1,apad=pad_dur=1,ebur128" -f null - 2>&1 | grep -A3 Summary | sed -n 's/.*I: *\(-*[0-9.]*\) LUFS/\1/p'; }
IH=$(ev $AU/audition/news-close-2-horn-stabs.mp3 "aresample=48000,pan=mono|c0=0.5*c0+0.5*c1,volume=-4dB,afade=t=out:st=1.2:d=0.13")
IA=$(ev $AU/work/news-open-1-mini-jingle.wav "pan=mono|c0=0.5*c0+0.5*c1"); IC=$(ev $AU/work/news-open-3-da-da-da-daaa.wav "pan=mono|c0=0.5*c0+0.5*c1")
GA=$(python3 -c "print(round($IH - $IA, 2))"); GC=$(python3 -c "print(round($IH - $IC, 2))"); echo "jingle gains: A $GA dB, C $GC dB"
$PY $X/film/pipeline/jingles-v10.py $AU/work/news-open-1-mini-jingle.wav $AU/work/news-open-3-da-da-da-daaa.wav $O/jingles $XT $A_HIT $GA $WORD $C_HIT $GC \
  out/s8/special-report.wav $ANN 5 8 0.829 $AU/work/news-open-1-mini-jingle.pre.wav
python3 -c "s=$A_HIT-0.660-0.829; print(f'A (v11): starts {s:.4f}, first note {s+0.008:.4f} (ident first frame 15.8667), 1.489 s hit {s+1.489:.4f} (slam $A_HIT)')"
cmp -s $O/jingles/jingle-c.wav $P10/jingles/jingle-c.wav && echo "jingle C stem identical to v10's" || echo "jingle C stem DIFFERS from v10's"
# --- 2 stems from v10's graph. Inputs: 0 advisory vo, 1 sponsor vo, 2 jingle C, 3 announcer, 4 brown noise, 5 desk voice, 6 jingle A
$FFV -i $P9/vo/adv-vo.wav -i $P10/vo/sponsor-vo.wav -i $O/jingles/jingle-c.wav -i out/s8/special-report.wav -f lavfi -i "anoisesrc=d=$XT:c=brown:a=0.3:r=48000:s=1" \
  -i opening-x11/out/desk-final.wav -i $O/jingles/jingle-a.wav -/filter_complex $X/film/pipeline/stems-v11.filter \
  -map '[dx]' -c:a pcm_f32le $O/work/dx.wav -map '[voice]' -c:a pcm_f32le $O/work/voice.wav -map '[st]' -c:a pcm_f32le $O/work/stings.wav
# --- 3 music: each cue referenced to -16 LUFS over its span (folded to mono, 180 Hz high-pass), then music-v11.py
lu() { ffmpeg -nostdin -hide_banner -ss $2 -t $3 -i "$1" -af "pan=mono|c0=0.5*c0+0.5*c1,highpass=f=180,ebur128" -f null - 2>&1 | grep -A3 Summary | sed -n 's/.*I: *\(-*[0-9.]*\) LUFS/\1/p'; }
LG=$(lu $MU/1-sponsor/suno-1-reassuring-groove-a.wav 1.273 4.539); LN=$(lu $MU/2-news/suno-2-breaking-news-a.wav 0.112 35.085)
GR=$(python3 -c "print(round(-16 - $LG, 2))"); NR=$(python3 -c "print(round(-16 - $LN, 2))"); echo "cue loudness (mono, HP 180): groove $LG, news $LN LUFS"
$PY $X/film/pipeline/music-v11.py $O/work/voice.wav $MU/1-sponsor/suno-1-reassuring-groove-a.wav $MU/2-news/suno-2-breaking-news-a.wav $O/work $XT $CUT $C_HIT $GR $NR
# --- 4 mix, limiter, two-pass loudnorm
MIX="[0:a][1:a][2:a]amix=inputs=3:normalize=0:duration=longest,atrim=0:$XT,asetpts=PTS-STARTPTS,alimiter=limit=0.80:level=0"
J=$(ffmpeg -nostdin -hide_banner -i $O/work/dx.wav -i $O/work/music.wav -i $O/work/stings.wav -filter_complex "$MIX,loudnorm=I=-16:TP=-1:LRA=20:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
mi=$(echo "$J" | sed -n 's/.*"input_i" : "\(.*\)".*/\1/p'); mt=$(echo "$J" | sed -n 's/.*"input_tp" : "\(.*\)".*/\1/p')
ml=$(echo "$J" | sed -n 's/.*"input_lra" : "\(.*\)".*/\1/p'); mh=$(echo "$J" | sed -n 's/.*"input_thresh" : "\(.*\)".*/\1/p'); of=$(echo "$J" | sed -n 's/.*"target_offset" : "\(.*\)".*/\1/p')
LE=$(ffmpeg -nostdin -hide_banner -i $O/work/dx.wav -i $O/work/music.wav -i $O/work/stings.wav -filter_complex "$MIX,ebur128" -f null - 2>&1 | grep -A3 Summary | sed -n 's/.*I: *\(-*[0-9.]*\) LUFS/\1/p')
TI=$(python3 -c "print(round(-16 + $mi - $LE, 2))")   # loudnorm's own meter (192 kHz) reads this mix lower than ebur128; the pass-2 target corrects it so ebur128 reads -16.0
echo "loudnorm pass 1: I $mi LUFS (ebur128 $LE), TP $mt dBTP, LRA $ml LU, thresh $mh, offset $of; pass-2 target $TI"
ffmpeg -nostdin -hide_banner -y -i $O/work/dx.wav -i $O/work/music.wav -i $O/work/stings.wav \
  -filter_complex "$MIX,loudnorm=I=$TI:TP=-1:LRA=20:measured_I=$mi:measured_TP=$mt:measured_LRA=$ml:measured_thresh=$mh:offset=$of:linear=true:print_format=json,aresample=48000" \
  -c:a pcm_f32le $O/work/mix.wav 2>&1 | grep -E '"normalization_type"|"output_i"|"output_tp"'
GAIN=$(python3 -c "print(round(-16 - $LE, 2))"); echo "final gain (linear loudnorm) $GAIN dB"
for s in dx music stings; do $FFV -i $O/work/$s.wav -af volume=${GAIN}dB -c:a pcm_s24le $O/stems/$s.wav; done
$FFV -i $O/work/voice.wav -af volume=${GAIN}dB -c:a pcm_f32le $O/work/voice-final.wav
mv $O/stems/dx.wav $O/stems/dialogue-sfx.wav
# --- 5 mux on v10's video stream (copied), phone file
$FFV -i out/opening-v10.mp4 -i $O/work/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart -t $XT out/opening-v11.mp4
$FFV -i out/opening-v11.mp4 -vf scale=960:540:flags=lanczos -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart out/opening-v11-phone.mp4
for v in opening-v11 opening-v11-phone; do ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,width,height,channels -of compact out/$v.mp4; done
