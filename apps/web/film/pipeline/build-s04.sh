#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. Needs render-s04/f%05d.png (capture-s04.sh), audio/bunker-take.wav (Liam's take),
# out/s04/s04-audio.filter + s04-edl.json (pipeline/s04-timing.py, synced by sync-s04.sh).
# 1 audio: same chain as conspiracy v4: denoise the take once (afftdn nr=18, noise profile from the silent 0.10-0.70 s of the take) -> cut list (20 ms fades)
#   -> two-pass loudnorm -16 LUFS + constant brown-noise room-tone bed (-52.5 dBFS RMS) -> audio-final.wav
# 2 frames + audio -> out/s04-bunker-v1.mp4 (1280x720, 30 fps, crf 14); phone re-encode 960x540 crf 26 next to it
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; O=out/s04; mkdir -p $O
FFV="ffmpeg -nostdin -v error -y"
TOTAL=$(python3 -c "import json;print(json.load(open('$O/s04-edl.json'))['total'])")
printf '0.10 afftdn sn start;\n0.70 afftdn sn stop;\n' > $O/sn.txt
$FFV -i audio/bunker-take.wav -af "asendcmd=f=$O/sn.txt,afftdn=nr=18:nf=-48:nt=w:om=o" -c:a pcm_s16le $O/take-dn.wav
$FFV -i $O/take-dn.wav -/filter_complex $O/s04-audio.filter -map '[mix]' -ac 1 -ar 48000 $O/mix.wav
M=$(ffmpeg -nostdin -hide_banner -i $O/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
FADE=$(python3 -c "print(round($TOTAL-0.6,2))")
$FFV -i $O/mix.wav -f lavfi -i "anoisesrc=d=$TOTAL:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$FADE:d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[o]" -map '[o]' -ac 1 -ar 48000 $O/audio-final.wav
ffmpeg -nostdin -hide_banner -i $O/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak"
$FFV -framerate 30 -i render-s04/f%05d.png -i $O/audio-final.wav -map 0:v -map 1:a -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -t "$TOTAL" out/s04-bunker-v1.mp4
$FFV -i out/s04-bunker-v1.mp4 -vf scale=960:540 -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/s04-bunker-v1-phone.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames,width,height -of compact out/s04-bunker-v1.mp4
