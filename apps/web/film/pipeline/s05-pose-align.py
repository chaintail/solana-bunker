#!/usr/bin/env python3
"""Lab coat pose alignment for s05-hash.html (v6, Liam 16763 standing rule: across a pose switch the body's centre line, shoulder line and baseline stay put,
only the arm changes). Measures each lab coat sprite (assets/s05/physicist-*.png, 1024x1536 body px) and writes assets/s05/pose-align.js:
  window.POSE_ALIGN[pose] = {dx, dy, hx, hy}: the pose PNG is drawn translated by (dx, dy) body px so its collar centre / baseline land on the reference pose's,
  and every lab pose uses the same head anchor (hx = reference collar centre, hy = reference chin) so the head never moves on a switch.
Reference = shrug (the scene's last pose: the hand-off frame to slide 6 stays pixel-identical). Measurements (body px):
  collar centre = median centre of the neck-skin V (rows 322-338), cross-checked with the tie knot (dark run, rows 350-358);
  shoulder y = median top of the coat at collar +-120..180 px per side; collar top = top of the opaque collar at collar +-60; baseline = lowest opaque row (shoe soles);
  hem/leg offset = centre of the coat (rows 760-1000) and of the legs (rows 1100-1440) minus the collar centre (drawn into the art, cannot be fixed by placement).
usage (run from apps/web/film): python3 -I pipeline/s05-pose-align.py"""
import json
import numpy as np
from PIL import Image
D = 'assets/s05/'; POSES = ['physicist-shrug', 'physicist-holding-clipboard', 'physicist-professor-point']; REF = 'physicist-shrug'
M = {}
for n in POSES:
    im = np.array(Image.open(D + n + '.png').convert('RGBA')).astype(int); a = im[..., 3] > 128
    skin = (im[..., 0] > 200) & (im[..., 2] < 190) & (im[..., 0] - im[..., 2] > 40) & a
    dark = (im[..., :3].max(-1) < 70) & a
    v = [(xs.min() + xs.max()) / 2 for y in range(322, 339) for xs in [np.where(skin[y, 300:720])[0] + 300] if len(xs)]
    cx = float(np.median(v)); c = int(round(cx))
    k = [(xs.min() + xs.max()) / 2 for y in range(350, 359) for xs in [np.where(dark[y, c - 40:c + 40])[0] + c - 40] if len(xs)]
    top = lambda x: int(np.where(a[:, x])[0].min())
    shL = float(np.median([top(c - d) for d in range(120, 181, 5)])); shR = float(np.median([top(c + d) for d in range(120, 181, 5)]))
    col = int(np.where(a[:, c - 60:c + 60].any(1))[0].min()); base = int(np.where(a.any(1))[0].max())
    mid = lambda ys: float(np.median([(np.where(a[y])[0].min() + np.where(a[y])[0].max()) / 2 for y in ys])) - cx
    M[n] = dict(cx=cx, knot=float(np.median(k)), shL=shL, shR=shR, collar=col, base=base, coat=mid(range(760, 1001, 20)), legs=mid(range(1100, 1441, 20)))
r = M[REF]; AN = {}
src = open(D + 'anchors.js').read(); anch = json.loads(src[src.index('{'):src.rindex('}') + 1])
out = {}
for n in POSES:
    m = M[n]; dx = round(r['cx'] - m['cx'], 1); dy = 0.0   # collar top / shoulder / baseline already agree within 1-2 body px (table below), so no vertical move
    out[n] = {'dx': dx, 'dy': dy, 'hx': anch[REF]['cx'], 'hy': anch[REF]['chin']}
    m.update(dx=dx, oval=anch[n]['cx'])
open(D + 'pose-align.js', 'w').write('window.POSE_ALIGN = ' + json.dumps(out) + ';\n')
print(f"{'pose':30s} {'collar cx':>9s} {'knot':>6s} {'oval cx':>7s} {'shL':>5s} {'shR':>5s} {'collar':>6s} {'base':>5s} {'coat-cx':>7s} {'legs-cx':>7s} {'dx':>6s}")
for n, m in M.items(): print(f"{n:30s} {m['cx']:9.1f} {m['knot']:6.1f} {m['oval']:7.1f} {m['shL']:5.0f} {m['shR']:5.0f} {m['collar']:6d} {m['base']:5d} {m['coat']:7.1f} {m['legs']:7.1f} {m['dx']:6.1f}")
print(json.dumps(out))
