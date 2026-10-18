#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s05. Lip-synced head-and-neck sprites for slide 5 (lab coat Liam), cut with the audio edit list (out/s05-edl.json).
Same key as ~/video-work/head-test/key.sh (RVM alpha minus a luma key of the black shirt below the chin, zone.png / kill.png masks, 760x1100 crop) cut from the matte
footage at the phrase's source in/out, scaled to the sprite size, concatenated phrase after phrase (the scene holds the last frame through pauses) and tiled
16 x 12 per sheet: film/heads/lab-NN.png (192 frames each, frame i of the whole run = sheet i//192, cell i%192).
Sprite size 136x197 = head scale 0.1793 = face (chin to hairline, 665 key px) 119 px = oval of the body PNG (217 px) at body scale 0.55 (HEAD_K in the scene)."""
import json, os, subprocess
os.environ['PATH'] = '/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:' + os.environ['PATH']
B = os.path.expanduser('~/video-work/bunker'); HT = os.path.expanduser('~/video-work/head-test')
W, H, COLS, ROWS = 136, 197, 16, 12
e = json.load(open('out/s05-edl.json'))['edl']
LO, HI = 28, 58
# v8 (Liam, 2026-10-16): from c15 on (source 288 s+) Liam sits closer to the camera and further left (face 1.10x larger, centre ~70 px left), so the fixed
# zone/kill masks (centred on x 625, hard kill x < 453 below y 950) cut a rectangle out of his left jaw and the head sat oversized and off-centre on the collar.
# Each of those phrases is first mapped into the c1-c14 geometry (scale to WxH, pad onto the 1080x1440 canvas at x,y), so the face, jaw and chin land where the
# colour phrases have them: the unchanged masks clear the jaw and every sprite shares the lab coat head anchor (511.5 / 308). Values: per-phrase median of a
# gradient-NCC registration (glasses, nose, mouth, chin) of frames at in+0.15 s, mid and out-0.15 s against c8, mapped to the c1-c14 median.
NORM = {
    'c15': (990, 1318, 84, 73),
    'c16a': (984, 1312, 84, 79),
    'c16b': (984, 1312, 91, 75),
    'c17': (976, 1302, 100, 73),
    'c18': (966, 1286, 80, 77),
    'c19': (970, 1294, 79, 91),
    'c20a': (966, 1286, 84, 79),
    'c20b': (978, 1302, 65, 84),
    'c20c': (968, 1290, 85, 85),
    'c21': (994, 1326, 101, 69),
    'c22': (1000, 1334, 101, 71),
}
os.makedirs('out/heads', exist_ok=True); os.makedirs('film/heads', exist_ok=True)
cells = []
for x in e:
    n = x['frames']; S = str(x['src_in']); T = str(n / 30 + 0.2)
    # pad onto an oversized canvas, then crop back to 1080x1440: pad alone centres the image when it would overflow the canvas (c21/c22: x + w > 1080)
    nm = (lambda w, h, px, py: f",scale={w}:{h}:flags=lanczos,pad=1300:1660:{px + 110}:{py + 110}:color=black,crop=1080:1440:110:110")(*NORM[x['id']]) if x['id'] in NORM else ''
    fc = (f"[0:v]fps=30,format=gray{nm},gblur=sigma=1.5,lut=y='clip(({HI}-val)*255/({HI}-{LO}),0,255)'[s];[2:v]format=gray[z];[3:v]format=gray[kl];"
          f"[s][z]blend=all_mode=multiply,dilation,dilation[sd];[sd][kl]blend=all_mode=lighten,negate,gblur=sigma=1.2[k];"
          f"[1:v]fps=30,format=gray{nm}[a];[a][k]blend=all_mode=multiply,gblur=sigma=0.8[am];"
          f"[4:v]fps=30,format=rgb24{nm},despill=type=green:mix=0.6:expand=0.2,format=gbrp[rgb];[rgb][am]alphamerge,crop=760:1100:250:150,"
          f"scale={W}:{H}:flags=lanczos,format=rgba,trim=end_frame={n},setpts=PTS-STARTPTS[o]")
    f = f"out/heads/{x['id']}.mov"
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', S, '-t', T, '-i', B + '/matte-full-comp.mp4', '-ss', S, '-t', T, '-i', B + '/matte-full-alpha.mp4',
                    '-loop', '1', '-framerate', '30', '-i', HT + '/zone.png', '-loop', '1', '-framerate', '30', '-i', HT + '/kill.png', '-ss', S, '-t', T, '-i', B + '/matte-full-comp.mp4',
                    '-filter_complex', fc, '-map', '[o]', '-frames:v', str(n), '-c:v', 'qtrle', '-r', '30', f], check=True)
    cells.append(os.path.abspath(f)); print(x['id'], n, flush=True)
open('out/heads/list.txt', 'w').write(''.join(f"file '{c}'\n" for c in cells))
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'out/heads/list.txt', '-c', 'copy', 'out/heads/all.mov'], check=True)
for f in os.listdir('film/heads'):
    if f.startswith('lab-'): os.remove('film/heads/' + f)
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', 'out/heads/all.mov', '-vf', f'tile={COLS}x{ROWS}:padding=0:margin=0:color=0x00000000,format=rgba', '-f', 'image2', '-start_number', '0', 'film/heads/lab-%02d.png'], check=True)
print(sorted(os.listdir('film/heads')))
