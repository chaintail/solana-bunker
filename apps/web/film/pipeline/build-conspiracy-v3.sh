#!/bin/bash
# Runs ON dev-mac from ~/video-work/solana-bunker. Needs render-consp3/{s01-title,s03-conspiracy}/ frames (capture-consp.sh),
# audio/bunker-take.wav (Liam's take), out/consp/conspiracy-audio.filter + conspiracy-edl.json (conspiracy-timing.py).
# 1 audio: denoise take once (afftdn nr=18, noise profile learned from the silent 0.10-0.70 s of the take) -> cut list (20 ms fades) -> mix.wav
#   -> two-pass loudnorm -16 LUFS + constant brown-noise room-tone bed (same chain/level as opening-v6, -52.5 dBFS RMS) -> audio-final.wav
# 2 Liam picture-in-picture: one lossless PNG-in-MOV cell per audio segment (matte comp+alpha cut with the same in/out), last frame held through pauses
# 3 base (s01 + s03 frames) + rotated PiP over the Polaroid + tin foil hat layer (render-consp3/hat, held, fades with the PiP) + audio -> out/conspiracy-v3.mp4
set -euo pipefail
export PATH=/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:$PATH
cd ~/video-work/solana-bunker; O=out/consp3; mkdir -p $O; cp film/data/conspiracy-audio.filter $O/; cp film/data/conspiracy-edl.json $O/; B=~/video-work/bunker; mkdir -p $O/cells
FFV="ffmpeg -nostdin -v error -y"
# --- 1 audio
printf '0.10 afftdn sn start;\n0.70 afftdn sn stop;\n' > $O/sn.txt
$FFV -i audio/bunker-take.wav -af "asendcmd=f=$O/sn.txt,afftdn=nr=18:nf=-48:nt=w:om=o" -c:a pcm_s16le $O/take-dn.wav
$FFV -i $O/take-dn.wav -/filter_complex $O/conspiracy-audio.filter -map '[mix]' -ac 1 -ar 48000 $O/mix.wav
M=$(ffmpeg -nostdin -hide_banner -i $O/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | sed -n "s/.*\"$1\" *: *\"\\(.*\\)\".*/\\1/p"; }
$FFV -i $O/mix.wav -f lavfi -i "anoisesrc=d=75.13:c=brown:a=0.3:r=48000:s=1" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[v];[1:a]lowpass=f=220,volume=0.05,afade=t=in:d=0.3,afade=t=out:st=74.53:d=0.6[bed];[v][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[o]" -map '[o]' -ac 1 -ar 48000 $O/audio-final.wav
ffmpeg -nostdin -hide_banner -i $O/audio-final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak"
# --- 2 PiP cells
python3 - <<'PY'
import json,subprocess,os
e=json.load(open('out/consp3/conspiracy-edl.json')); B=os.path.expanduser('~/video-work/bunker')
edl=e['edl']; total=round(e['total']*30)
starts=[0]+[round(x['out_in']*30) for x in edl[1:]]; ends=starts[1:]+[total]
lst=[]
for i,(x,a,b) in enumerate(zip(edl,starts,ends)):
    n=b-a; seg=x['src_out']-x['src_in']; 
    f=f"out/consp3/cells/c{i:02d}.mov"
    pre="tpad=start_mode=clone:start=%d,"%round(x['out_in']*30) if i==0 else ""
    fc="[0:v]despill=type=green:mix=0.6:expand=0.2,format=rgb24[c];[1:v]format=gray[a];[c][a]alphamerge,crop=918:1224:130:150,scale=216:288:flags=lanczos,fps=30,format=rgba,"+pre+"tpad=stop_mode=clone:stop=%d,trim=end_frame=%d,setpts=PTS-STARTPTS"%(n,n)
    cmd=["ffmpeg","-nostdin","-v","error","-y","-ss",str(x['src_in']),"-t",str(seg),"-i",B+"/matte-full-comp.mp4","-ss",str(x['src_in']),"-t",str(seg),"-i",B+"/matte-full-alpha.mp4","-filter_complex",fc,"-c:v","png","-pix_fmt","rgba","-r","30",f]
    subprocess.run(cmd,check=True); lst.append("file '%s/%s'"%(os.getcwd(),f))
    print(x['id'],a,b,n)
open('out/consp3/cells.txt','w').write('\n'.join(lst)+'\n')
PY
$FFV -f concat -safe 0 -i $O/cells.txt -c copy $O/pip.mov
# --- 3 composite
$FFV -framerate 30 -i render-consp3/s01-title/f%05d.png -framerate 30 -i render-consp3/s03-conspiracy/f%05d.png -i $O/pip.mov -i $O/audio-final.wav -framerate 30 -i render-consp3/hat/f%05d.png \
  -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0,format=yuv420p[base];[2:v]format=rgba,rotate=-2*PI/180:ow='rotw(-2*PI/180)':oh='roth(-2*PI/180)':c=none,fade=t=in:st=9.75:d=0.15:alpha=1,fade=t=out:st=57.45:d=0.15:alpha=1[pip];[4:v]format=rgba,tpad=stop_mode=clone:stop=900,setpts=PTS+28.85/TB,fade=t=out:st=57.45:d=0.15:alpha=1[hat];[base][pip]overlay=x=1124-w/2:y=492-h/2:enable='between(t,9.7,57.7)':format=auto[b2];[b2][hat]overlay=enable='between(t,28.8,57.7)':format=auto,format=yuv420p[v]" \
  -map '[v]' -map 3:a -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -t "$(python3 -c "import json;print(json.load(open('$O/conspiracy-edl.json'))['total'])")" out/conspiracy-v3a.mp4
ffmpeg -nostdin -v error -y -i out/conspiracy-v3a.mp4 -vf scale=960:540 -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/conspiracy-v3a-phone.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames,width,height -of compact out/conspiracy-v3a.mp4
