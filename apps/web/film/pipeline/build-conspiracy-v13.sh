#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. v13 (Liam, 2026-10-18): x12b with two script cuts (conspiracy-v13-edit.py: "they were quick to
# point out that" and p8b "At least that's what crypto Twitter kept repeating."), 1773 -> 1660 frames (59.100 -> 55.333 s).
# usage: build-conspiracy-v13.sh dialogue | picture | mux
#   dialogue  x12b's method on the v13 cut list (film-v13/data/conspiracy-audio.filter): take-dn.wav -> cut list mix -> atempo=1.2 (pitch kept)
#             -> two-pass loudnorm -16 LUFS -> brown-noise bed generated at the new length (not spliced) -> out/consp-v13/audio-final.wav
#   picture   PiP rebuilt from the v13 cut list with v4's cell recipe (cells whose source span and length are the x12b ones are reused from
#             out/consp-x12b/cells), PiP frame k = v13 PiP frame round(1.2k); overlay times = x12b's mapped through the cuts / 1.2 ->
#             out/conspiracy-v13-pic.mp4 (crf 14, dialogue-only audio) and -pic-phone.mp4 (960x540 crf 26)
#   mux       out/consp-v13/v13-final.wav (the m4c treatment, made on do-box) on the v13 pictures, picture stream-copied, aac 192k both ->
#             out/conspiracy-v13.mp4, out/conspiracy-v13-phone.mp4; video md5 pic vs final
# Needs out/consp-v13/seg/*.mp4 + list.txt (capture-consp-v13.sh: 175 + 1485 = 1660 frames), render-consp-x12/hat/ (38 frames),
# out/consp4/take-dn.wav, out/consp4/conspiracy-edl.json (the v4 cut list x12b's cells came from), ~/video-work/bunker/matte-full-{comp,alpha}.mp4.
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; O=out/consp-v13; mkdir -p $O; FFV="ffmpeg -nostdin -v error -y"; SPEED=1.2; M=1660
XT=$(python3 -c "print(round($M/30,4))"); s() { python3 -c "print(round($1/$SPEED,4))"; }
CUT=4.52   # seconds removed at 1x before every overlay time after the second cut (the PiP and hat end, 57.7 / 57.45 s in x12b)
case "${1:-}" in
dialogue)
  cp film-v13/data/conspiracy-audio.filter $O/
  $FFV -i out/consp4/take-dn.wav -/filter_complex $O/conspiracy-audio.filter -map '[mix]' -ac 1 -ar 48000 $O/mix-1x.wav
  $FFV -i $O/mix-1x.wav -af "atempo=$SPEED,apad=whole_dur=$XT,atrim=0:$XT,asetpts=PTS-STARTPTS" -ac 1 -ar 48000 $O/mix.wav
  M1=$(ffmpeg -nostdin -hide_banner -i $O/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g() { echo "$M1" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
  $FFV -i $O/mix.wav -f lavfi -i "anoisesrc=d=$XT:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=$(python3 -c "print(round($XT-0.6,4))"):d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[o]" -map '[o]' -ac 1 -ar 48000 $O/audio-final.wav
  ffmpeg -nostdin -hide_banner -i $O/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak"
  ffprobe -v error -show_entries format=duration -of csv=p=0 $O/audio-final.wav
  ;;
picture)
  [ "$(grep -c . $O/seg/list.txt)" -eq 28 ] || { echo "$O/seg/list.txt does not list 28 chunks"; exit 1; }
  [ "$(find render-consp-x12/hat -name 'f*.png' | wc -l)" -eq 38 ] || { echo "hat frames missing"; exit 1; }
  [ -s $O/audio-final.wav ] || { echo "run the dialogue step first"; exit 1; }
  mkdir -p $O/cells
  python3 - <<'PY'
import json, subprocess, os
B = os.path.expanduser('~/video-work/bunker')
def cells(path, total=None):
    e = json.load(open(path)); edl = e['edl']; total = round((total or e['total']) * 30)
    starts = [0] + [round(x['out_in'] * 30) for x in edl[1:]]; ends = starts[1:] + [total]
    return [(x['src_in'], x['src_out'] - x['src_in'], b - a, round(x['out_in'] * 30) if i == 0 else 0) for i, (x, a, b) in enumerate(zip(edl, starts, ends))]
old = cells('out/consp4/conspiracy-edl.json'); new = cells('film-v13/data/conspiracy-edl.json')
lst = []
for i, c in enumerate(new):
    src_in, seg, n, pre = c
    reuse = f'out/consp-x12b/cells/c{i:02d}.mov'
    if i < len(old) and old[i] == c and os.path.exists(reuse):
        f = reuse; print(f'cell {i:02d}: x12b cell reused ({n} frames)')
    else:
        f = f'out/consp-v13/cells/c{i:02d}.mov'
        fc = ("[0:v]despill=type=green:mix=0.6:expand=0.2,format=rgb24[c];[1:v]format=gray[a];[c][a]alphamerge,crop=918:1224:130:150,scale=216:288:flags=lanczos,fps=30,format=rgba,"
              + ("tpad=start_mode=clone:start=%d," % pre if i == 0 else "") + "tpad=stop_mode=clone:stop=%d,trim=end_frame=%d,setpts=PTS-STARTPTS" % (n, n))
        cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(src_in), "-t", str(seg), "-i", B + "/matte-full-comp.mp4", "-ss", str(src_in), "-t", str(seg),
               "-i", B + "/matte-full-alpha.mp4", "-filter_complex", fc, "-c:v", "png", "-pix_fmt", "rgba", "-r", "30", f]
        subprocess.run(cmd, check=True); print(f'cell {i:02d}: built, src {src_in:.4f} +{seg:.4f} s, {n} frames')
    lst.append("file '%s/%s'" % (os.getcwd(), f))
open('out/consp-v13/cells.txt', 'w').write('\n'.join(lst) + '\n')
PY
  $FFV -f concat -safe 0 -i $O/cells.txt -c copy $O/pip.mov
  PF=$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 $O/pip.mov)
  echo "v13 PiP: $PF frames"; [ "$PF" -ge $(python3 -c "print(round((57.7-$CUT)*30)+1)") ] || { echo "PiP too short"; exit 1; }
  # x12b overlay times (v4 1x): PiP 9.7-57.7 s, fade in 9.75 d 0.15, fade out 57.45 d 0.15, hat from 28.85 s shown 28.8-57.7; after the cuts the ends move 4.52 s
  PI=$(s 9.7); PO=$(s "(57.7-$CUT)"); FI=$(s 9.75); FO=$(s "(57.45-$CUT)"); FD=$(s 0.15); HS=$(s 28.85); HI=$(s 28.8)
  $FFV -f concat -safe 0 -i $O/seg/list.txt -i $O/pip.mov -i $O/audio-final.wav -framerate 30 -i render-consp-x12/hat/f%05d.png \
    -filter_complex "[0:v]format=yuv420p,setpts=PTS-STARTPTS[base];[1:v]select='eq(n\,round(round(n/$SPEED)*$SPEED))',setpts=N/30/TB,format=rgba,rotate=-2*PI/180:ow='rotw(-2*PI/180)':oh='roth(-2*PI/180)':c=none,fade=t=in:st=$FI:d=$FD:alpha=1,fade=t=out:st=$FO:d=$FD:alpha=1[pip];[3:v]format=rgba,tpad=stop_mode=clone:stop=900,setpts=PTS+$HS/TB,fade=t=out:st=$FO:d=$FD:alpha=1[hat];[base][pip]overlay=x=1124-w/2:y=492-h/2:enable='between(t,$PI,$PO)':format=auto[b2];[b2][hat]overlay=enable='between(t,$HI,$PO)':format=auto,format=yuv420p[v]" \
    -map '[v]' -map 2:a -r 30 -frames:v $M -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart out/conspiracy-v13-pic.mp4
  $FFV -i out/conspiracy-v13-pic.mp4 -vf scale=960:540 -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart out/conspiracy-v13-pic-phone.mp4
  for v in conspiracy-v13-pic conspiracy-v13-pic-phone; do ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,width,height -of compact out/$v.mp4; done
  [ "$(ffprobe -v error -select_streams v -show_entries stream=nb_frames -of csv=p=0 out/conspiracy-v13-pic.mp4)" = $M ] || { echo "out/conspiracy-v13-pic.mp4 is not $M frames"; exit 1; }
  ;;
mux)
  [ -s $O/v13-final.wav ] || { echo "$O/v13-final.wav missing"; exit 1; }
  $FFV -i out/conspiracy-v13-pic.mp4 -i $O/v13-final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart out/conspiracy-v13.mp4
  $FFV -i out/conspiracy-v13-pic-phone.mp4 -i $O/v13-final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart out/conspiracy-v13-phone.mp4
  for f in conspiracy-v13-pic conspiracy-v13 conspiracy-v13-pic-phone conspiracy-v13-phone; do
    echo "$f $(ffmpeg -nostdin -v error -i out/$f.mp4 -map 0:v -c copy -f md5 -) $(ffprobe -v error -show_entries stream=codec_type,width,height,nb_frames,duration,bit_rate -of compact=p=0 out/$f.mp4 | tr "\n" " ")"
  done
  ;;
*) echo "usage: $0 dialogue|picture|mux"; exit 2 ;;
esac
