#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s08. x11 build mode (Liam 16583): build.sh audio + video with Liam's voice at 1.1x and the score re-rendered
# from the scaled EDL. Needs out/take-dn.wav and out/s08-audio.filter (build.sh audio, v5 timing, 52.32 s), film/data/s08-edl-x11.js (pipeline/s08/edl-x11.py:
# every scene time / 1.1, total 47.6 s) and out/x11/seg/c*.mkv + list.txt (capture-x11.sh, 1428 frames).
#  audio: v5 cut list -> mix -> atempo=1.1 (pitch kept) -> two-pass loudnorm -16 LUFS -> out/x11/voice-ln.wav; score.py --edl data/s08-edl-x11.js (tempo map and
#         stings from the scaled markers, dialogue guard on the sped voice) -> out/x11/score.wav; mixed as build.sh (score after the loudnorm, brown bed at the new
#         length, limiter) -> out/x11/audio-final.wav; score-check.py on the x11 files -> out/x11/score-check.log
#  video: build.sh's grade (grain c0s=7, vignette PI/4.6) -> out/<name>.mp4 (crf 14), out/<name>-phone.mp4 (960x540 lanczos crf 26); usage: build-x11.sh [name] (default s08-x11)
#  [seg dir] (default out/x11/seg). v7: lengths come from the EDLs (out/s08-edl.json scene frames N, the x11 copy's total = ceil(N/1.1)/30) instead of v5/v6's fixed 52.32 s / 1428.
#  v7: the grain is run GOFF = 1428 - M frames ahead (tpad clone, trimmed after the grade), so the last frame (scene 9's hand-off, pixel-identical to v6's in the
#  capture) also gets v6's last-frame grain; the noise is per frame number, so the offset changes nothing else. GOFF = 0 for a 1428-frame cut (v6 unchanged).
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker/s08; O=out/x11; FFV="ffmpeg -nostdin -v error -y"; SPEED=1.1; EDLX=film/data/s08-edl-x11.js; V=${1:-s08-x11}; SEG=${2:-out/x11/seg}
M=$(python3 -c "import json,math;print(math.ceil(round(json.load(open('out/s08-edl.json'))['total']*30)/$SPEED-1e-9))"); XT=$(python3 -c "print(round($M/30,4))")
GOFF=$(( M < 1428 ? 1428 - M : 0 ))
[ "$(python3 -c "import json;s=open('$EDLX').read();print(json.loads(s[s.index('{'):s.rindex('}')+1])['total'])")" = "$XT" ] || { echo "$EDLX total is not $XT"; exit 1; }
cp out/s08-audio.filter $O/s08-audio.filter
$FFV -i out/take-dn.wav -/filter_complex $O/s08-audio.filter -map '[mix]' -ac 1 -ar 48000 $O/mix-1x.wav
$FFV -i $O/mix-1x.wav -af "atempo=$SPEED,apad=whole_dur=$XT,atrim=0:$XT,asetpts=PTS-STARTPTS" -ac 1 -ar 48000 $O/mix.wav
M1=$(ffmpeg -nostdin -hide_banner -i $O/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M1" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
LN="loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000"
$FFV -i $O/mix.wav -af "$LN" -ac 1 -c:a pcm_s16le $O/voice-ln.wav
/usr/bin/python3 film/pipeline/s08/score.py --edl $EDLX --voice $O/voice-ln.wav --out $O/score.wav --events $O/score-events.json --table > $O/score-table.md
$FFV -i $O/mix.wav -f lavfi -i "anoisesrc=d=$XT:c=brown:a=0.3:r=48000:s=1" -i $O/score.wav -filter_complex "[2:a]aresample=48000,apad=whole_dur=$XT,atrim=0:$XT[sfx];[0:a]$LN[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$(python3 -c "print($XT-0.6)"):d=0.6[bed];[v][bed][sfx]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.95[o]" -map '[o]' -ac 1 -ar 48000 $O/audio-final.wav
ffmpeg -nostdin -hide_banner -i $O/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A16 Summary | grep -E "I:|Peak"
/usr/bin/python3 film/pipeline/s08/score-check.py --edl $EDLX --score $O/score.wav --voice $O/voice-ln.wav --events $O/score-events.json --final $O/audio-final.wav | tee $O/score-check.log || true
$FFV -f concat -safe 0 -i $SEG/list.txt -i $O/audio-final.wav -filter_complex \
  "[0:v]tpad=start=$GOFF:start_mode=clone,format=yuv444p,noise=c0s=7:c0f=t+u,vignette=angle=PI/4.6,format=yuv420p,setsar=1,trim=start_frame=$GOFF,setpts=PTS-STARTPTS[v]" \
  -map '[v]' -map 1:a -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -t $XT out/$V.mp4
$FFV -i out/$V.mp4 -vf scale=960:540:flags=lanczos -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/$V-phone.mp4
for v in $V $V-phone; do ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,width,height -of compact out/$v.mp4; done
