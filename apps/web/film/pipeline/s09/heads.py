#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s09. Head sprites for scene 9 (port of pipeline/s08/heads.py; same key as pipeline/head-test/key.sh:
RVM alpha minus a luma key of the black shirt below the chin, zone.png / kill.png masks, 760x1100 crop).
  every row of out/s09-edl.json 'heads' (Joe J1-J2, suit S1-S4, the lab coat's one closed-mouth frame) cut at its in/out and concatenated,
  tiled 16 x 12 per sheet -> film/heads/s09-head-NN.png (frame i of the run = sheet i // 192, cell i % 192)
  per frame, the forehead point inside its 152x220 cell -> film/data/s09-headbox.js (window.S09_HB = {top:[], fx:[], fy:[]}), for the sticky note:
  top = the centroid row of the glasses frame (dark pixels in rows 66-112), fy = 22 px above it, fx = the middle of the head's alpha at that row (5-frame median on both)
  (the hair reaches the top of the crop, so the hair line cannot track the head).
Sprite size 152x220 (760x1100 / 5). usage: heads.py [box]"""
import json, os, subprocess, sys
import numpy as np
os.environ['PATH'] = '/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:' + os.environ['PATH']
B = os.path.expanduser('~/video-work/bunker'); HT = os.path.expanduser('~/video-work/head-test')
W, H, COLS, ROWS = 152, 220, 16, 12
LO, HI = 28, 58
def key(src_in, n, out):
    fc = (f"[0:v]fps=30,format=gray,gblur=sigma=1.5,lut=y='clip(({HI}-val)*255/({HI}-{LO}),0,255)'[s];[2:v]format=gray[z];[3:v]format=gray[kl];"
          f"[s][z]blend=all_mode=multiply,dilation,dilation[sd];[sd][kl]blend=all_mode=lighten,negate,gblur=sigma=1.2[k];"
          f"[1:v]fps=30,format=gray[a];[a][k]blend=all_mode=multiply,gblur=sigma=0.8[am];"
          f"[4:v]fps=30,format=rgb24,despill=type=green:mix=0.6:expand=0.2,format=gbrp[rgb];[rgb][am]alphamerge,crop=760:1100:250:150,"
          f"scale={W}:{H}:flags=lanczos,format=rgba,trim=end_frame={n},setpts=PTS-STARTPTS[o]")
    S, T = str(src_in), str(n / 30 + 0.2)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', S, '-t', T, '-i', B + '/matte-full-comp.mp4', '-ss', S, '-t', T, '-i', B + '/matte-full-alpha.mp4',
                    '-loop', '1', '-framerate', '30', '-i', HT + '/zone.png', '-loop', '1', '-framerate', '30', '-i', HT + '/kill.png', '-ss', S, '-t', T, '-i', B + '/matte-full-comp.mp4',
                    '-filter_complex', fc, '-map', '[o]', '-frames:v', str(n), '-c:v', 'qtrle', '-r', '30', out], check=True)
if 'box' not in sys.argv[1:]:   # 'heads.py box' only recomputes the forehead track from out/heads/all.mov
    os.makedirs('out/heads', exist_ok=True); os.makedirs('film/heads', exist_ok=True)
    cells = []
    for x in json.load(open('out/s09-edl.json'))['heads']:
        f = f"out/heads/{x['id']}.mov"; key(x['src_in'], x['frames'], f); cells.append(os.path.abspath(f)); print(x['id'], x['frames'], flush=True)
    open('out/heads/list.txt', 'w').write(''.join(f"file '{c}'\n" for c in cells))
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'out/heads/list.txt', '-c', 'copy', 'out/heads/all.mov'], check=True)
    for f in os.listdir('film/heads'):
        if f.startswith('s09-head-'): os.remove('film/heads/' + f)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', 'out/heads/all.mov', '-vf', f'tile={COLS}x{ROWS}:padding=0:margin=0:color=0x00000000,format=rgba', '-f', 'image2', '-start_number', '0', 'film/heads/s09-head-%02d.png'], check=True)
raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', 'out/heads/all.mov', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-'], capture_output=True, check=True).stdout
F = np.frombuffer(raw, dtype=np.uint8).reshape(-1, H, W, 4).astype(int)
cy, cx = [], []
for fr in F:
    a = fr[..., 3] > 128; lum = (fr[..., 0] * 3 + fr[..., 1] * 6 + fr[..., 2]) / 10
    dark = a & (lum < 70); dark[:66] = False; dark[112:] = False; dark[:, :25] = False; dark[:, 125:] = False   # the glasses frame, below the hair
    ys = np.nonzero(dark)[0]; y = ys.mean() if len(ys) else 85.0; cy.append(y)
    span = np.nonzero(a[int(round(y - 22))])[0]; cx.append((span.min() + span.max()) / 2 if len(span) else 60.0)   # middle of the head at the forehead row
med = lambda v: [float(np.median(v[max(0, i - 2):i + 3])) for i in range(len(v))]   # 5-frame median: no jitter from rim to rim
cy, cx = med(cy), med(cx)
top = [round(v, 1) for v in cy]; fy = [round(v - 22, 1) for v in cy]; fx = [round(v, 1) for v in cx]
open('film/data/s09-headbox.js', 'w').write('window.S09_HB = ' + json.dumps({'top': top, 'fx': fx, 'fy': fy}) + ';\n')
print('head frames', len(F), 'glasses y range', min(top), max(top), 'forehead y range', min(fy), max(fy), 'x range', min(fx), max(fx), sorted(f for f in os.listdir('film/heads') if f.startswith('s09-head-')))
