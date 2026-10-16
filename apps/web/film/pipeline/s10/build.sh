#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker/s10 (film/ = rsync of film/s10's apps/web/film). usage: build.sh assets | audio | video [v1]
#  assets: scene 9's last frame -> film/assets/s10-s09-last.png (under the wipe, 0-0.55 s). S09V picks the scene 9 render (default v2 until s09-v3 exists:
#          then re-run with S09V=v3 and rebuild video; one line). Also the backdrop still (s10-news ?layer=back) -> out/back.png.
#  audio:  denoise the take once (afftdn nr=18, profile from 0.10-0.70 s, as scenes 5-9) -> out/take-dn.wav; s10-timing.py; cut (20 ms fades) -> mix.wav;
#          two-pass loudnorm -16 LUFS + brown-noise bed, limiter 0.80 without auto-level (as scene 9) -> out/audio-final.wav
#  video:  composite as the opening (desk-v7.filter): backdrop, the matted anchor (B1 frames 0-400 at take = t + 531.75, 525x700 at 377,-20;
#          B2 frames 401-1001 at take = t + 550.20, same 525x700 at 377,-20: v4 has no punch-in, the cut is hidden by a 2-frame white flash in the front layer), scene 9's last frame under the wipe (t < 0.55),
#          the front layer (out/front-a/b.mkv, FFV1 bgra from capture.sh; v4: retimed to 1/30 with settb,setpts=N, since the mkv millisecond timestamps made the overlay take the previous front frame on about a third of frames) -> out/s10-<v>.mp4 (crf 14) and out/s10-<v>-phone.mp4 (960x540 crf 26)
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cd ~/video-work/solana-bunker/s10; FFV="ffmpeg -nostdin -v error -y"; V=${2:-v1}; B=~/video-work/bunker; S09V=${S09V:-v2}
mkdir -p out film/assets
if [ "$1" = assets ]; then
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 ../s09/out/s09-$S09V.mp4)
  $FFV -ss "$(python3 -c "print($D-0.05)")" -i ../s09/out/s09-$S09V.mp4 -frames:v 1 -update 1 film/assets/s10-s09-last.png
  node film/scripts/capture.mjs s10-news --layer=back --still=0 --out=out/backcap > out/cap-back.log 2>&1; cp out/backcap/still-0.png out/back.png
fi
if [ "$1" = audio ]; then
  printf '0.10 afftdn sn start;\n0.70 afftdn sn stop;\n' > out/sn.txt
  $FFV -i ../audio/bunker-take.wav -af "asendcmd=f=out/sn.txt,afftdn=nr=18:nf=-48:nt=w:om=o" -c:a pcm_s16le out/take-dn.wav
  /usr/bin/python3 film/pipeline/s10/s10-timing.py
  T=$(python3 -c "import json;print(json.load(open('out/s10-edl.json'))['total'])")
  $FFV -i out/take-dn.wav -/filter_complex out/s10-audio.filter -map '[mix]' -ac 1 -ar 48000 out/mix.wav
  M=$(ffmpeg -nostdin -hide_banner -i out/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g() { echo "$M" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
  $FFV -i out/mix.wav -f lavfi -i "anoisesrc=d=$T:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$(python3 -c "print($T-0.6)"):d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.80:level=0[o]" -map '[o]' -ac 1 -ar 48000 out/audio-final.wav
  ffmpeg -nostdin -hide_banner -i out/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A20 Summary | grep -E "I:|Peak:"
fi
if [ "$1" = video ]; then
  T=$(python3 -c "import json;print(json.load(open('out/s10-edl.json'))['total'])")
  printf "file '%s/out/front-a.mkv'\nfile '%s/out/front-b.mkv'\n" "$PWD" "$PWD" > out/fronts.txt
  $FFV -loop 1 -framerate 30 -t $T -i out/back.png -ss 531.75 -t 13.6 -i $B/matte-full-comp.mp4 -ss 531.75 -t 13.6 -i $B/matte-full-alpha.mp4 \
    -ss 563.5667 -t 20.3 -i $B/matte-full-comp.mp4 -ss 563.5667 -t 20.3 -i $B/matte-full-alpha.mp4 -loop 1 -framerate 30 -t $T -i film/assets/s10-s09-last.png \
    -f concat -safe 0 -i out/fronts.txt -i out/audio-final.wav -filter_complex \
    "[1:v]fps=30,trim=end_frame=401,setpts=PTS-STARTPTS,scale=525:700:flags=lanczos,despill=type=green:mix=0.6:expand=0.2,format=rgb24[c1];
     [2:v]fps=30,trim=end_frame=401,setpts=PTS-STARTPTS,scale=525:700:flags=lanczos,format=gray[a1];[c1][a1]alphamerge[l1];
     [3:v]fps=30,trim=end_frame=601,setpts=PTS-STARTPTS+401/30/TB,scale=525:700:flags=lanczos,despill=type=green:mix=0.6:expand=0.2,format=rgb24[c2];
     [4:v]fps=30,trim=end_frame=601,setpts=PTS-STARTPTS+401/30/TB,scale=525:700:flags=lanczos,format=gray[a2];[c2][a2]alphamerge[l2];
     [0:v]format=rgb24,setpts=PTS-STARTPTS[bg];[bg][l1]overlay=x=377:y=-20:eof_action=pass:format=auto[b1];[b1][l2]overlay=x=377:y=-20:eof_action=pass:format=auto[b2];
     [5:v]format=rgb24,setpts=PTS-STARTPTS[s9];[b2][s9]overlay=0:0:enable='lt(t,0.55)'[b3];
     [6:v]settb=1/30,setpts=N,format=rgba[fr];[b3][fr]overlay=format=auto,format=yuv420p,setsar=1[v]" \
    -map '[v]' -map 7:a -r 30 -frames:v $(python3 -c "print(round($T*30))") -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart out/s10-$V.mp4
  $FFV -i out/s10-$V.mp4 -vf scale=960:540:flags=lanczos -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/s10-$V-phone.mp4
  ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames,width,height -of compact out/s10-$V.mp4
  ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of compact out/s10-$V-phone.mp4
fi
