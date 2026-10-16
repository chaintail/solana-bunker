#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. Revision 8 = v7 picture + audio rebuilt:
#  1 desk voice denoised ONCE before cutting (afftdn nr=18:nf=-48:nt=w, noise profile from the silent clip 6.5-7.2 s = raw 14.66-15.36 s), mono downmix first
#  2 cut list as v7 (clip 0-9.5433 | 14.79-42.5) with 20 ms fades, desk fade-out at 37.0333, two-pass loudnorm -16 LUFS / TP -1.5 (linear) on the desk
#  3 mix with advisory + sponsor vo (untouched), brown-noise bed (lowpass 220, volume 0.05) under the whole opening, news sting + "A special report." over the wipe,
#    limiter 0.80 without auto-level (scene 9)
#  4 picture: v7 segments (seg-v7) + the last desk frame (wipe fully covering) held 63 frames = 2.1 s
# needs out/seg-v7/*.mp4, out/s00b-v7/vo-final.wav, out/s00a-v5/vo-final.wav, out/s8/special-report.wav, ~/audio-work/solana-bunker/out/audition/news-close-2-horn-stabs.mp3
# audio-v8.filter inputs: 0 picture, 1 advisory vo, 2 sponsor vo, 3 sting, 4 announcer, 5 bed source, 6 desk-final. Sting starts at the covering time 19.9+37.8333=57.7333, line 0.75 s later (+5 dB, sting -4 dB = peak -12.1 dBFS).
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; O=out/s8; S=out/seg-v7; mkdir -p $O
FFV="ffmpeg -nostdin -v error -y"; RAW=~/video-work/bunker-raw.mov
# --- 1 denoise once (clip time 0 = raw 8.16 s; the silent stretch is clip 6.5-7.2)
$FFV -ss 8.16 -t 44 -i $RAW -vn -af "pan=mono|c0=0.5*c0+0.5*c1,aresample=48000" -c:a pcm_s16le $O/desk-raw.wav
printf '6.50 afftdn sn start;\n7.20 afftdn sn stop;\n' > $O/sn.txt
$FFV -i $O/desk-raw.wav -af "asendcmd=f=$O/sn.txt,afftdn=nr=18:nf=-48:nt=w:om=o" -c:a pcm_s16le $O/desk-dn.wav
# --- 2 cut (20 ms fades) -> two-pass loudnorm
$FFV -i $O/desk-dn.wav -filter_complex "[0:a]asplit=2[l1][l2];[l1]atrim=0:9.5433,asetpts=PTS-STARTPTS,afade=t=out:st=9.5233:d=0.02[la];[l2]atrim=14.79:42.5,asetpts=PTS-STARTPTS,afade=t=in:d=0.02[lb];[la][lb]concat=n=2:v=0:a=1,afade=t=out:st=37.0333:d=0.2[o]" -map '[o]' -ar 48000 -c:a pcm_s16le $O/desk-cut.wav
M=$(ffmpeg -nostdin -hide_banner -i $O/desk-cut.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
$FFV -i $O/desk-cut.wav -af "loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" -ac 1 -ar 48000 -c:a pcm_s16le $O/desk-final.wav
echo "desk loudnorm pass1: I=$(g input_i) TP=$(g input_tp) LRA=$(g input_lra) offset=$(g target_offset)"
# --- 3 picture: v7 segments + held covering frame
enc() { $FFV "$@" -r 30 -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p; }
mkdir -p $O/seg
$FFV -i $S/s02-news.mp4 -vf "select=eq(n\,1134)" -frames:v 1 $O/last.png
enc -loop 1 -framerate 30 -i $O/last.png -frames:v 63 $O/seg/hold.mp4
for f in s00-intro s00b-advisory s00c-breaking s02-news; do cp $S/$f.mp4 $O/seg/; done
printf "file '%s'\n" s00-intro.mp4 s00b-advisory.mp4 s00c-breaking.mp4 s02-news.mp4 hold.mp4 | sed "s#^file '#file '$PWD/$O/seg/#" > $O/list.txt
# --- 4 mix + mux
$FFV -f concat -safe 0 -i $O/list.txt -i out/s00b-v7/vo-final.wav -i out/s00a-v5/vo-final.wav -i ~/audio-work/solana-bunker/out/audition/news-close-2-horn-stabs.mp3 -i $O/special-report.wav -f lavfi -i "anoisesrc=d=59.8333:c=brown:a=0.3:r=48000:s=1" -i $O/desk-final.wav \
  -/filter_complex pipeline/audio-v8.filter -map 0:v -map '[aout]' -c:v copy -c:a aac -b:a 192k -movflags +faststart -t 59.8333 out/opening-v8.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames -of compact out/opening-v8.mp4
$FFV -i out/opening-v8.mp4 -vf scale=960:540:flags=lanczos -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart out/opening-v8-phone.mp4
ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height -of compact out/opening-v8-phone.mp4
