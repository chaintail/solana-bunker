#!/usr/bin/env bash
# Run on dev-mac. v5 = 15 poster frames + unchanged v4 picture/PCM.
# Usage: stitch-v5.sh [audio encode cover measure] (default: all).
# Requires stitch-v4.sh's completed master/phone/PCM and rep/scenes.tsv.
set -euo pipefail
[[ $(uname -s) == Darwin ]] || { echo 'Run this script on dev-mac.' >&2; exit 1; }
export PATH=/opt/homebrew/bin:$PATH
SCRIPT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")
ROOT=${ROOT:-$HOME/video-work/solana-bunker}
V4=${V4:-$ROOT/film/master-v4}
W=${W:-$ROOT/film/master-v5}
POSTER=${POSTER:-$W/poster.jpg}
OUT=solana-bunker-film-v5
SPF=1600
HEAD_FRAMES=15
HEAD_SAMPLES=$((HEAD_FRAMES * SPF))
TOTAL_FRAMES=12636
TOTAL_SAMPLES=$((TOTAL_FRAMES * SPF))
steps=${*:-audio encode cover measure}
mkdir -p "$W/aud" "$W/rep"
cd "$W"
ff() { ffmpeg -nostdin -hide_banner -v warning -y "$@"; }
samples() { ffprobe -v error -select_streams a:0 -show_entries stream=duration_ts -of csv=p=0 "$1"; }
[[ -f $POSTER && -f $V4/aud/film-master.wav ]] || { echo 'Missing poster or v4 mastered PCM.' >&2; exit 1; }

# Fail before processing if the exact measured v4 inputs are absent or changed.
python3 - "$V4" <<'PYVALIDATE'
import hashlib, pathlib, subprocess, json, sys
v4=pathlib.Path(sys.argv[1])
expected={
 'solana-bunker-film-v4-nocover.mp4':'ac58bee6f67adb2a3a004715337390e36f10ca59eb62025e47a0cd78e25c52a3',
 'solana-bunker-film-v4-phone-nocover.mp4':'575e881a1a69c7a8d07d72f5cb73b4ee670ec03f5776f33b503bb9502ee206c6',
 'aud/film-master.wav':'cea5acd6315c70b46e5d5dffb7bdd0712ab0a8dcb2473097c2836657316537d8'}
for name,want in expected.items():
 path=v4/name
 with path.open('rb') as f: got=hashlib.file_digest(f,'sha256').hexdigest()
 assert got==want, f'v4 input changed: {name}: {got}'
 metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)]))
 if name.endswith('.mp4'):
  video=metadata['streams'][0]
  assert int(video['nb_frames'])==12621 and video['r_frame_rate']=='30/1' and video['duration']=='420.700000', name
 else:
  audio=metadata['streams'][0]
  assert int(audio['duration_ts'])==20193600 and audio['sample_rate']=='48000' and audio['channels']==1, name
print('Validated exact v4 SHA-256, video frames and PCM samples.')
PYVALIDATE

if [[ $steps == *audio* ]]; then
  [[ $(samples "$V4/aud/film-master.wav") == 20193600 ]] || { echo 'Unexpected v4 PCM length.' >&2; exit 1; }
  # Mastering is already complete: unchanged v4 whole-film +0.30 dB gain,
  # 4x oversampled latency-compensated alimiter at -1.3 dB; do not renormalize.
  ff -f lavfi -i anullsrc=r=48000:cl=mono -af "atrim=end_sample=$HEAD_SAMPLES" -c:a pcm_f32le aud/poster-silence.wav
  printf "file '%s'\nfile '%s'\n" "$W/aud/poster-silence.wav" "$V4/aud/film-master.wav" > aud/list.txt
  ff -f concat -safe 0 -i aud/list.txt -map 0:a:0 -c:a pcm_f32le aud/film-master.wav
  [[ $(samples aud/film-master.wav) == "$TOTAL_SAMPLES" ]] || { echo 'PCM sample count mismatch.' >&2; exit 1; }
fi

if [[ $steps == *encode* ]]; then
  for variant in master phone; do
    if [[ $variant == master ]]; then
      src=$V4/solana-bunker-film-v4-nocover.mp4; suffix=; size=1280:720; crf=18; preset=slow
    else
      src=$V4/solana-bunker-film-v4-phone-nocover.mp4; suffix=-phone; size=960:540; crf=26; preset=medium
    fi
    # Encode only the new poster; existing v4 H.264 pictures are stream copied.
    ff -loop 1 -framerate 30 -i "$POSTER" -an -vf "scale=$size:in_range=pc:out_range=tv,setsar=1" -frames:v "$HEAD_FRAMES" \
      -c:v libx264 -preset "$preset" -crf "$crf" -pix_fmt yuv420p -color_range tv -video_track_timescale 15360 "poster-$variant.mp4"
    ff -i "$src" -map 0:v:0 -c copy "v4-picture-$variant.mp4"
    printf "file '%s'\nduration 0.500000\nfile '%s'\n" "$W/poster-$variant.mp4" "$W/v4-picture-$variant.mp4" > "picture-$variant.txt"
    ff -f concat -safe 0 -i "picture-$variant.txt" -i aud/film-master.wav \
      -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 1 \
      -movflags +faststart "$OUT$suffix-nocover.mp4"
  done
fi

if [[ $steps == *cover* ]]; then
  for suffix in '' -phone; do
    ff -i "$OUT$suffix-nocover.mp4" -i "$POSTER" -map 0:v:0 -map 0:a:0 -map 1:v:0 \
      -c copy -disposition:v:0 default -disposition:v:1 attached_pic -movflags +faststart "$OUT$suffix.mp4"
  done
fi

if [[ $steps == *measure* ]]; then
  python3 - "$W" "$V4" "$POSTER" "$SCRIPT" "$ROOT" <<'PY'
import array, hashlib, json, math, pathlib, re, subprocess, sys
w, v4, poster, script, root = map(pathlib.Path, sys.argv[1:])
def run(*args):
    return subprocess.check_output([str(a) for a in args], stderr=subprocess.PIPE)
def probe(path, count=False):
    return json.loads(run('ffprobe','-v','error',*(['-count_frames'] if count else []),'-show_streams','-show_format','-of','json',path))
def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()
def streamhash(path):
    return run('ffmpeg','-nostdin','-v','error','-i',path,'-map','0:v:0','-map','0:a:0','-c','copy','-f','streamhash','-hash','md5','-').decode().strip()
def pcm(path, trim=None):
    return run('ffmpeg','-nostdin','-v','error','-i',path,'-map','0:a:0',*(['-af',trim] if trim else []),'-c:a','pcm_f32le','-f','f32le','-')
def framehashes(path, trim=False):
    raw = run('ffmpeg','-nostdin','-v','error','-i',path,'-map','0:v:0','-an',*(['-vf','trim=start_frame=15,setpts=PTS-STARTPTS'] if trim else []),'-f','framemd5','-').decode()
    return [line.split(',')[-1].strip() for line in raw.splitlines() if line and not line.startswith('#')]
def loud(path):
    p=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-i',str(path),'-map','0:a:0','-af','loudnorm=print_format=json','-f','null','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=True)
    return json.loads(p.stderr[p.stderr.rfind('{'):p.stderr.rfind('}')+1])
# Exact float PCM prefix/tail check; no silence threshold substitutes for zero.
prefix=pcm(w/'aud/film-master.wav','atrim=end_sample=24000')
assert len(prefix)==24000*4 and set(prefix)=={0}, 'PCM prefix is not digital silence'
v4pcm=pcm(v4/'aud/film-master.wav')
v5tail=pcm(w/'aud/film-master.wav','atrim=start_sample=24000')
assert v4pcm==v5tail, 'v4 PCM changed'
meta=probe(w/'aud/film-master.wav')
assert int(meta['streams'][0]['duration_ts'])==20217600
report=dict(environment=dict(host='dev-mac',ffmpeg=run('ffmpeg','-version').decode().splitlines()[0]),
    base_commit='41a909beb40a2a228c35aa2f8c80faa2e826aa0c',
    script_sha256=sha(script),
    poster_sha256=sha(poster), head_frames=15,head_seconds=0.5,head_pcm_zero_samples=24000,
    total_frames=12636,total_seconds=421.2,pcm_samples=20217600,
    unchanged_v4_pcm_tail_sha256=hashlib.sha256(v5tail).hexdigest(), outputs=[])
for suffix,size in [('',(1280,720)),('-phone',(960,540))]:
    final=w/f'solana-bunker-film-v5{suffix}.mp4'; before=w/f'solana-bunker-film-v5{suffix}-nocover.mp4'
    src=v4/f'solana-bunker-film-v4{suffix}-nocover.mp4'
    m=probe(final,True); video=m['streams'][0]; audio=m['streams'][1]; cover=m['streams'][2]
    assert video['codec_name']=='h264' and (video['width'],video['height'])==size and video['pix_fmt']=='yuv420p'
    assert int(video['nb_read_frames'])==12636 and video['r_frame_rate']=='30/1'
    assert abs(float(video['duration'])-421.2)<1e-6 and abs(float(audio['duration'])-421.2)<1e-6
    assert abs(float(m['format']['duration'])-421.2)<1e-6
    assert audio['codec_name']=='aac' and audio['sample_rate']=='48000' and audio['channels']==1
    assert cover['codec_name']=='mjpeg' and cover['disposition']['attached_pic']==1 and video['disposition']['attached_pic']==0
    old_hash,new_hash=streamhash(before),streamhash(final)
    assert old_hash==new_hash, 'cover remux changed media packets'
    oldframes,newframes=framehashes(src),framehashes(final,True)
    assert oldframes==newframes and len(newframes)==12621, 'v4 decoded pictures changed'
    # Compare RGB-converted decoded frame zero with poster scaled identically.
    p=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-i',str(final),'-i',str(poster),'-filter_complex',f'[0:v:0]select=eq(n\\,0),setpts=PTS-STARTPTS,format=yuv420p[a];[1:v:0]scale={size[0]}:{size[1]}:in_range=pc:out_range=tv,setsar=1,format=yuv420p[b];[a][b]psnr','-an','-frames:v','1','-f','null','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=True)
    psnr=float(re.findall(r'average:([0-9.]+)',p.stderr)[-1])
    if not suffix: assert psnr>40, psnr
    (w/f'rep/poster-psnr{suffix}.txt').write_text(p.stderr)
    decoded=pcm(final)
    # AAC packet padding is reported independently of exact MP4 duration/PCM.
    out=dict(file=str(final),bytes=final.stat().st_size,sha256=sha(final),video_frames=int(video['nb_read_frames']),video_duration=video['duration'],audio_duration=audio['duration'],container_duration=m['format']['duration'],decoded_aac_samples=len(decoded)//4,
        video_size=list(size),poster_frame0_psnr_db=psnr,cover_attached_pic=1,media_stream_md5_before_cover=old_hash,media_stream_md5_after_cover=new_hash,
        unchanged_v4_picture_frames=len(newframes),unchanged_v4_picture_framehashes_sha256=hashlib.sha256('\n'.join(newframes).encode()).hexdigest(),loudness=loud(final))
    report['outputs'].append(out)
    (w/f'rep/metadata{suffix}.json').write_text(json.dumps(m,indent=2)+'\n')
# Actual video stream durations, plus the fixed measured 15-frame lead-in.
scenes=[]; offset=.5
rows=(v4/'rep/scenes.tsv').read_text().splitlines()
names=['Opening','Conspiracy','Bunker','Whiteboard','Speakeasy','Seminar','Arcade','Infomercial','Sign-off','Closing card']
for name,row in zip(names,rows):
    n,rel,frames,oldstart,got,diff=row.split('\t')
    source=root/rel
    sm=probe(source); sv=next(s for s in sm['streams'] if s['codec_type']=='video' and not s['disposition']['attached_pic'])
    duration=float(sv['duration'])
    scenes.append(dict(name=name,source=rel,source_sha256=sha(source),frames=int(frames),duration_seconds=duration,start_seconds=round(offset,6),start_frame=int(oldstart)+15,v4_start_frame=int(oldstart)))
    offset+=duration
report['chapters']=scenes
report['measured_scene_duration_sum_plus_head_seconds']=round(offset,6)
(w/'rep/stitch-v5.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
PY
  shasum -a 256 "$SCRIPT" > rep/stitch-script.sha256
fi
printf 'stitch-v5: done (%s)\n' "$steps"
