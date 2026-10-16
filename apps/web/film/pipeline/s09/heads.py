#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s09. Head sprites for scene 9 (port of pipeline/s08/heads.py; same key as pipeline/head-test/key.sh:
RVM alpha minus a luma key of the black shirt below the chin, zone / kill masks recentred on the jaw (JX below), 760x1200 crop).
  every row of out/s09-edl.json 'heads' (Joe J1-J2, suit S1-S4, the lab coat's one closed-mouth frame LAB, his testimonial LAB2) cut at its in/out and
  concatenated, tiled 16 x 12 per sheet -> film/heads/s09-head-NN.png (frame i of the run = sheet i // 192, cell i % 192)
  per frame, the forehead point inside its 152x240 cell -> film/data/s09-headbox.js (window.S09_HB = {top:[], fx:[], fy:[], jx:{}}), for the sticky note:
  top = the centroid row of the glasses frame (dark pixels in rows 66-112), fy = 22 px above it, fx = the middle of the head's alpha at that row (5-frame median on both)
  (the hair reaches the top of the crop, so the hair line cannot track the head).
Sprite size 152x240 (760x1200 / 5). v3 (film-plan-ending.md part A, head fixes): the crop runs 100 px lower (760x1100 -> 760x1200, same top, so
KEY_CHIN_X 289 and the key chin row 905 stay valid) so more neck shows and it runs down behind the collar; the jaw masks are centred per row.
usage: heads.py [box]"""
import json, os, subprocess, sys
import numpy as np
os.environ['PATH'] = '/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:' + os.environ['PATH']
B = os.path.expanduser('~/video-work/bunker')
CW, CH = 760, 1200                      # key crop at (250, 150) of the 1080x1440 matte
W, H, COLS, ROWS = CW // 5, CH // 5, 16, 12
LO, HI = 28, 58
# zone / kill masks (1080x1440, as pipeline/head-test/zone.sh) recentred on Liam's jaw: zone.sh centres both on x 625 and hard-kills x < 453 below
# y 950, which cut a rectangle out of the left jaw (sprite x < 39, y > 161). The jaw spans about x 331..747 on rows 930-1080, centre JX.
# kill: outside JX +- 265 below y 950; zone (where the shirt luma key may act): outside the jaw ellipse (JX, 870) 255 x 245 below y 925, or outside JX +- 200 below y 955
# JX per row: the plan's values (539 for scene 9's own lines, 545 for the testimonial) are rechecked before keying: each row's median jaw-span centre
# (alpha > 128, rows 930-1080, up to 8 frames spread over the row). If every row lands within +-6 px of one value, that one shared value is used.
JX_PLAN = {'LAB2': 545}; JX_DEF = 539
def mask_files(jx): return f'out/heads/zone-jaw-{jx}.png', f'out/heads/kill-jaw-{jx}.png'
def masks(jx):
    zone, kill = mask_files(jx)
    for e, f in ((f"255*max(clip((hypot((X-{jx})/255,(Y-870)/245)-1)*12,0,1)*clip((Y-925)/40,0,1),clip((abs(X-{jx})-200)/20,0,1)*clip((Y-955)/15,0,1))", zone),
                 (f"255*clip((abs(X-{jx})-265)/18,0,1)*clip((Y-950)/12,0,1)", kill)):
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=1080x1440,format=gray', '-vf', f"geq=lum='{e}'", '-frames:v', '1', f], check=True)
def jaw_centre(src_in, n):
    ts = [src_in + (i + .5) * n / 30 / min(8, n) for i in range(min(8, n))]; cs = []
    for t in ts:
        raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{t:.3f}', '-i', B + '/matte-full-alpha.mp4', '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'],
                             capture_output=True, check=True).stdout
        a = np.frombuffer(raw, dtype=np.uint8).reshape(1440, 1080)[930:1081] > 128
        c = [(np.nonzero(r)[0].min() + np.nonzero(r)[0].max()) / 2 for r in a if r.any()]
        if c: cs.append(float(np.median(c)))
    return float(np.median(cs))
def key(src_in, n, out, jx):
    zone, kill = mask_files(jx)
    fc = (f"[0:v]fps=30,format=gray,gblur=sigma=1.5,lut=y='clip(({HI}-val)*255/({HI}-{LO}),0,255)'[s];[2:v]format=gray[z];[3:v]format=gray[kl];"
          f"[s][z]blend=all_mode=multiply,dilation,dilation[sd];[sd][kl]blend=all_mode=lighten,negate,gblur=sigma=1.2[k];"
          f"[1:v]fps=30,format=gray[a];[a][k]blend=all_mode=multiply,gblur=sigma=0.8[am];"
          f"[4:v]fps=30,format=rgb24,despill=type=green:mix=0.6:expand=0.2,format=gbrp[rgb];[rgb][am]alphamerge,crop={CW}:{CH}:250:150,"
          f"scale={W}:{H}:flags=lanczos,format=rgba,trim=end_frame={n},setpts=PTS-STARTPTS[o]")
    S, T = str(src_in), str(n / 30 + 0.2)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', S, '-t', T, '-i', B + '/matte-full-comp.mp4', '-ss', S, '-t', T, '-i', B + '/matte-full-alpha.mp4',
                    '-loop', '1', '-framerate', '30', '-i', zone, '-loop', '1', '-framerate', '30', '-i', kill, '-ss', S, '-t', T, '-i', B + '/matte-full-comp.mp4',
                    '-filter_complex', fc, '-map', '[o]', '-frames:v', str(n), '-c:v', 'qtrle', '-r', '30', out], check=True)
JXR = {}
if 'box' not in sys.argv[1:]:   # 'heads.py box' only recomputes the forehead track from out/heads/all.mov
    os.makedirs('out/heads', exist_ok=True); os.makedirs('film/heads', exist_ok=True)
    rows = json.load(open('out/s09-edl.json'))['heads']
    meas = {x['id']: jaw_centre(x['src_in'], x['frames']) for x in rows}
    mid = float(np.median(list(meas.values())))
    shared = all(abs(v - mid) <= 6 for v in meas.values())
    for x in rows:
        plan = JX_PLAN.get(x['id'], JX_DEF)
        JXR[x['id']] = int(round(mid)) if shared else int(round(meas[x['id']]))
        print('jaw', x['id'], 'measured', round(meas[x['id']], 1), 'plan', plan, '->', JXR[x['id']], flush=True)
    print('JX', 'shared' if shared else 'per row', JXR, flush=True)
    for jx in sorted(set(JXR.values())): masks(jx)
    cells = []
    for x in rows:
        f = f"out/heads/{x['id']}.mov"; key(x['src_in'], x['frames'], f, JXR[x['id']]); cells.append(os.path.abspath(f)); print(x['id'], x['frames'], flush=True)
    open('out/heads/list.txt', 'w').write(''.join(f"file '{c}'\n" for c in cells))
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'out/heads/list.txt', '-c', 'copy', 'out/heads/all.mov'], check=True)
    for f in os.listdir('film/heads'):
        if f.startswith('s09-head-'): os.remove('film/heads/' + f)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', 'out/heads/all.mov', '-vf', f'tile={COLS}x{ROWS}:padding=0:margin=0:color=0x00000000,format=rgba', '-f', 'image2', '-start_number', '0', 'film/heads/s09-head-%02d.png'], check=True)
    json.dump(JXR, open('out/heads/jx.json', 'w'))
else:
    JXR = json.load(open('out/heads/jx.json')) if os.path.exists('out/heads/jx.json') else {}
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
sheets = sorted(f for f in os.listdir('film/heads') if f.startswith('s09-head-'))
open('film/data/s09-headbox.js', 'w').write('window.S09_HB = ' + json.dumps({'top': top, 'fx': fx, 'fy': fy, 'cell': [W, H], 'sheets': len(sheets), 'jx': JXR}) + ';\n')
print('head frames', len(F), 'glasses y range', min(top), max(top), 'forehead y range', min(fy), max(fy), 'x range', min(fx), max(fx), sheets)
