#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. Needs render-consp/{s01-title,s03-conspiracy}/ frames (capture-consp.sh),
# audio/bunker-take.wav (Liam's take), out/consp/conspiracy-audio.filter + conspiracy-edl.json (conspiracy-timing.py).
# 1 audio: cut list -> mix.wav -> two-pass loudnorm -16 LUFS -> audio-final.wav
# 2 Liam picture-in-picture: one lossless PNG-in-MOV cell per audio segment (matte comp+alpha cut with the same in/out), last frame held through pauses
# 3 base (s01 + s03 frames) + rotated PiP over the Polaroid + audio -> out/conspiracy-v2.mp4
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; O=out/consp2; mkdir -p $O; cp film/data/conspiracy-audio.filter $O/; cp film/data/conspiracy-edl.json $O/; B=~/video-work/bunker; mkdir -p $O/cells
FFV="ffmpeg -nostdin -v error -y"
# --- 1 audio
$FFV -i audio/bunker-take.wav -/filter_complex $O/conspiracy-audio.filter -map '[mix]' -ac 1 -ar 48000 $O/mix.wav
M=$(ffmpeg -nostdin -hide_banner -i $O/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
$FFV -i $O/mix.wav -af "loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000,alimiter=limit=0.95" -ac 1 -ar 48000 $O/audio-final.wav
ffmpeg -nostdin -hide_banner -i $O/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak"
# --- 2 PiP cells
python3 - <<'PY'
import json,subprocess,os
e=json.load(open('out/consp2/conspiracy-edl.json')); B=os.path.expanduser('~/video-work/bunker')
edl=e['edl']; total=round(e['total']*30)
starts=[0]+[round(x['out_in']*30) for x in edl[1:]]; ends=starts[1:]+[total]
lst=[]
for i,(x,a,b) in enumerate(zip(edl,starts,ends)):
    n=b-a; seg=x['src_out']-x['src_in']; 
    f=f"out/consp2/cells/c{i:02d}.mov"
    pre="tpad=start_mode=clone:start=%d,"%round(x['out_in']*30) if i==0 else ""
    fc="[0:v]despill=type=green:mix=0.6:expand=0.2,format=rgb24[c];[1:v]format=gray[a];[c][a]alphamerge,crop=918:1224:130:150,scale=216:288:flags=lanczos,fps=30,format=rgba,"+pre+"tpad=stop_mode=clone:stop=%d,trim=end_frame=%d,setpts=PTS-STARTPTS"%(n,n)
    cmd=["ffmpeg","-nostdin","-v","error","-y","-ss",str(x['src_in']),"-t",str(seg),"-i",B+"/matte-full-comp.mp4","-ss",str(x['src_in']),"-t",str(seg),"-i",B+"/matte-full-alpha.mp4","-filter_complex",fc,"-c:v","png","-pix_fmt","rgba","-r","30",f]
    subprocess.run(cmd,check=True); lst.append("file '%s/%s'"%(os.getcwd(),f))
    print(x['id'],a,b,n)
open('out/consp2/cells.txt','w').write('\n'.join(lst)+'\n')
PY
$FFV -f concat -safe 0 -i $O/cells.txt -c copy $O/pip.mov
# --- 3 composite
$FFV -framerate 30 -i render-consp/s01-title/f%05d.png -framerate 30 -i render-consp/s03-conspiracy/f%05d.png -i $O/pip.mov -i $O/audio-final.wav \
  -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0,format=yuv420p[base];[2:v]format=rgba,rotate=-2*PI/180:ow='rotw(-2*PI/180)':oh='roth(-2*PI/180)':c=none,fade=t=in:st=9.75:d=0.15:alpha=1,fade=t=out:st=57.45:d=0.15:alpha=1[pip];[base][pip]overlay=x=1124-w/2:y=492-h/2:enable='between(t,9.7,57.7)':format=auto,format=yuv420p[v]" \
  -map '[v]' -map 3:a -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -t "$(python3 -c "import json;print(json.load(open('$O/conspiracy-edl.json'))['total'])")" out/conspiracy-v2.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames,width,height -of compact out/conspiracy-v2.mp4
