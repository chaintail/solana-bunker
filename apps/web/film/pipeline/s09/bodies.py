#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s09/film (or apps/web/film). Port of pipeline/s08/bodies.py (itself film/s05's s05-bodies.py) for the
scene 9 poses. The grey head oval and its outline are erased from each body PNG; the head sprite is drawn BEHIND the body, so the collar covers the neck.
Writes assets/s09/<pose>.png (same 1024x1536 canvas) and assets/s09/anchors.js: oval centre x, chin y (oval bottom), hx (collar centre x),
and KEY_CHIN_X (the chin centre x in the key crop, which goes on hx).
v9: the suit and lab coat bodies are the -notch variants (Liam 16788; they differ from the plain art only in a 12-row neck strip, rows 316-328).
v9 pose switches (s09-v9-plan.md, composer ruling 2): the head and collar are pinned across each switch. The switched-to pose's anchor (cx = hx, chin)
is moved by the measured collar offset, so a place() call with the same chin point puts both collars, and both heads, on the same screen pixel.
  suit: suit-point-right is pinned to suit-standing (section 2: arms at sides on the snap, points on "yeah").
  lab coat: physicist-holding-clipboard is pinned to physicist-professor-point (section 3 switches on "live"; professor-point keeps its v1-v8 anchor,
  so the section-3 call and the hand-off frame are unchanged).
  professor-point's legs: the sprite is split at the coat hem and its legs are moved so they land on holding-clipboard's legs (collar-pinned).
usage: /usr/bin/python3 pipeline/s09/bodies.py"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
SRC = 'assets/bodies/'; DST = 'assets/s09/'; os.makedirs(DST, exist_ok=True)
POSES = ['2-street-hands-in-pockets', '2-street-celebrate', '1-suit-standing', '1-suit-point-right', '5-physicist-holding-clipboard',
         '5-physicist-professor-point', '2-street-thinking', '2-street-thinking-2', '2-street-thinking-3']   # the testimonial (film-plan-ending.md part A): the lab coat points at the results cards
NOTCH = {'1-suit-standing', '1-suit-point-right', '5-physicist-holding-clipboard', '5-physicist-professor-point'}   # v9: -notch art (Liam 16788)
src = lambda n: SRC + n + ('-notch' if n in NOTCH else '') + '.png'
anch = {}
for n in POSES:
    im = np.array(Image.open(src(n)).convert('RGBA')).astype(int)
    a, r, g, b = im[..., 3], im[..., 0], im[..., 1], im[..., 2]
    gray = (abs(r - g) < 10) & (abs(g - b) < 10) & (r > 130) & (r < 230) & (a > 200); gray[345:] = False
    if n.startswith('2-street-thinking'):   # the hand covers the oval's chin: anchors and oval from the hands-in-pockets body (same oval, checked 1 px); keep the hand and its outline
        b0 = np.array(Image.open(SRC + '2-street-hands-in-pockets.png').convert('RGBA')).astype(int)
        r0, g0, b0_, a0 = b0[..., 0], b0[..., 1], b0[..., 2], b0[..., 3]
        gray = (abs(r0 - g0) < 10) & (abs(g0 - b0_) < 10) & (r0 > 130) & (r0 < 230) & (a0 > 200); gray[345:] = False
    lab, k = ndi.label(gray); i = np.argmax(ndi.sum(gray, lab, range(1, k + 1))) + 1
    m = ndi.binary_fill_holes(lab == i); ys, xs = np.where(m)
    chin = int(ys.max()); cx = float((xs.min() + xs.max()) / 2)
    m2 = ndi.binary_dilation(m, iterations=15); m2[chin + 8:] = False
    if n.startswith('2-street-thinking'):
        skin = (r > 200) & (g > 130) & (g < 235) & (b > 90) & (b < 210) & (r - b > 40) & (a > 200) & (np.arange(r.shape[0])[:, None] > 250)
        seed = ndi.binary_fill_holes(ndi.binary_closing(ndi.binary_opening(skin, iterations=2), iterations=9))   # the hand (the neck lies under the oval and is erased/kept like the other poses)
        keep = (ndi.binary_dilation(seed, iterations=6) & (r + g + b < 250)) | seed
        m2 &= ~keep
    out = im.copy(); out[m2, 3] = 0
    Image.fromarray(out.astype('uint8')).save(DST + n.split('-', 1)[1] + '.png', optimize=True)
    anch[n.split('-', 1)[1]] = {'cx': cx, 'chin': chin, 'top': int(ys.min()), 'hx': cx}   # hx: where the head's chin centre goes = the collar centre (on the oval centre for all five poses, checked on 2x crops)
# the lab coat's hand on its own layer (skin plus its outline), so the enlarged WHITEPAPER clipboard can sit between the body and the hand
im = np.array(Image.open(src('5-physicist-holding-clipboard')).convert('RGBA')).astype(int)
r, g, b, a = im[..., 0], im[..., 1], im[..., 2], im[..., 3]
box = np.zeros(a.shape, bool); box[520:720, 300:470] = True
skin = box & (r > 200) & (g > 160) & (g < 235) & (b > 110) & (b < 200) & (r - b > 40) & (a > 200)
skin = ndi.binary_fill_holes(ndi.binary_closing(skin, iterations=3))
lab, k = ndi.label(skin); skin = lab == (np.argmax(ndi.sum(skin, lab, range(1, k + 1))) + 1)
ring = ndi.binary_dilation(skin, iterations=7) & ~skin & (r + g + b < 200) & (a > 120)
hand = im.copy(); hand[~(ndi.binary_fill_holes(skin | ring) | ring), 3] = 0
Image.fromarray(hand.astype('uint8')).save(DST + 'physicist-hand.png', optimize=True)
ys, xs = np.nonzero(skin); print('hand bbox', xs.min(), xs.max(), ys.min(), ys.max())
# KEY_CHIN_X: Liam's chin centre line in the 760x1100 key crop = the midpoint of his jaw outline (alpha span) on cell rows 135-161, median over the
# 561 scene 9 head frames: 57.5-58.0 cell px (x5 = 289 crop px); mouth and glasses lie within about 2 cell px of it. Scene 8's 338 put every head
# about 16 body px left of its collar (v1 fix round, Liam 16292).
# ---- v9: pinning across the pose switches, and professor-point's legs
def lum(n):   # luminance over white, so transparent = white (n: a pose name or a png path)
    im = np.array(Image.open(n if n.endswith('.png') else src(n)).convert('RGBA')).astype(float); return 255 - (255 - im[..., :3].mean(-1)) * im[..., 3] / 255
def match(a, b, box, base, R=30, V=12):
    """(dx, dy): pose b's copy of the art inside box (x0, x1, y0, y1 in pose a's px) sits at (x + base + dx, y + dy); base = oval centre difference."""
    A, B = lum(a), np.pad(lum(b), 64, constant_values=255); x0, x1, y0, y1 = box; pa = A[y0:y1, x0:x1]; best = None
    for dy in range(-V, V + 1):
        for dx in range(base - R, base + R + 1):
            e = np.abs(pa - B[64 + y0 + dy:64 + y1 + dy, 64 + x0 + dx:64 + x1 + dx]).mean()
            if best is None or e < best[0]: best = (e, dx - base, dy)
    return best[1], best[2]
def oval(n): return anch[n.split('-', 1)[1]]
# suit: collar box (shirt collar, tie knot and tie) of suit-standing found in suit-point-right
S0, S1 = '1-suit-standing', '1-suit-point-right'; base = round(oval(S1)['cx'] - oval(S0)['cx'])
cdx, cdy = match(S0, S1, (430, 590, 300, 560), base)
p = oval(S1); p.update({'oval_cx': p['cx'], 'oval_chin': p['chin'], 'cx': oval(S0)['cx'] + base + cdx, 'chin': oval(S0)['chin'] + cdy}); p['hx'] = p['cx']
print('suit collar offset (point - standing, body px beyond the oval offset):', cdx, cdy, '-> suit-point-right anchor', p['cx'], p['chin'],
      '| legs', match(S0, S1, (280, 740, 840, 1300), base), 'shoes', match(S0, S1, (180, 840, 1300, 1470), base))
# lab coat: collar box of holding-clipboard found in professor-point; holding-clipboard's anchor moves (professor-point is the reference)
L0, L1 = '5-physicist-holding-clipboard', '5-physicist-professor-point'; base = round(oval(L1)['cx'] - oval(L0)['cx'])
cdx, cdy = match(L0, L1, (440, 580, 300, 520), base)
h = oval(L0); h.update({'oval_cx': h['cx'], 'oval_chin': h['chin'], 'cx': oval(L1)['cx'] - base - cdx, 'chin': oval(L1)['chin'] - cdy}); h['hx'] = h['cx']
legL, legR = match(L0, L1, (270, 480, 1250, 1470), base), match(L0, L1, (520, 830, 1250, 1470), base)
print('lab collar offset (professor-point - holding-clipboard, beyond the oval offset):', cdx, cdy, '-> holding-clipboard anchor', h['cx'], h['chin'],
      '| legs left', legL, 'right', legR, '| clipboard', match(L0, L1, (250, 440, 420, 720), base))
# professor-point's legs: the art draws them (and the coat) 10-17 px right of its collar compared with holding-clipboard. Split at the coat hem: the
# coat (white panels plus their outline) stays put; everything else from row Y0 down (trousers, the lining between the legs, shoes) is moved left by
# the leg offset minus the collar offset, the left leg and the right leg each by its own amount, with the seam down the middle of the gap between the
# legs (lining white, then empty background: nothing to cut). Under the coat the trousers are continued straight up from below the hem, so the moved
# legs never pull coat white into the opening. In the coat opening the move ramps in from 0 at Y0 to full at the hem row Y1 (a slope change of the
# trouser lines of a few degrees; rows below about 943 lie under the CALL NOW strip at the section-3 placement, so Y0 = 960 keeps every visible pixel
# of professor-point, and the hand-off frame, unchanged).
Y0, Y1 = 960, 1100
sL, sR = -(legL[0] - cdx), -(legR[0] - cdx)
P = np.array(Image.open(DST + 'physicist-professor-point.png').convert('RGBA')).astype(int)
r, g, b, a = P[..., 0], P[..., 1], P[..., 2], P[..., 3]
white = (r > 215) & (g > 215) & (b > 215) & (a > 200); lab, k = ndi.label(white)
panels = np.zeros_like(white)
for i, sl in enumerate(ndi.find_objects(lab), 1):   # the coat's two lower panels: white regions running from above the belt line to below row 1000
    if sl[0].start < 850 and sl[0].stop > 1000: panels |= lab == i
panels = ndi.binary_fill_holes(panels)
lumP = (r + g + b) / 3
grey = (lumP > 70) & (lumP < 150) & (np.ptp(P[..., :3], axis=-1) < 30) & (a > 200)   # trouser grey (the outline and its anti-aliasing are darker)
coat = (ndi.binary_dilation(panels, iterations=12) & ~grey) | panels   # the panels plus their whole black outline, not the trousers
coat[:Y0 - 40] = False
legs = P.copy(); H = P.shape[0]
for x in range(P.shape[1]):   # under the coat: continue whatever is below the coat in this column straight up
    ys = np.nonzero(coat[Y0 - 40:, x])[0] + Y0 - 40
    if len(ys):
        yb = ys.max() + 1; legs[ys, x] = P[min(yb, H - 1), x] if yb < H else 0
gapc = np.nonzero((lumP[1150:1300] > 200).all(0) | (a[1150:1300] < 40).all(0))[0]   # columns clear of both legs below the hem
mid = int(np.median(gapc[(gapc > 330) & (gapc < 480)]))
out = P.copy()
for y in range(Y0, H):
    w = min(1.0, (y - Y0) / (Y1 - Y0)); dl, dr = sL * w, sR * w
    xs = np.arange(P.shape[1]); srcL, srcR = xs - dl, xs - dr
    srcx = np.where(srcL < mid, srcL, srcR)
    x0 = np.floor(srcx).astype(int); f = (srcx - x0)[:, None]; x0c, x1c = np.clip(x0, 0, P.shape[1] - 1), np.clip(x0 + 1, 0, P.shape[1] - 1)
    row = legs[y, x0c] * (1 - f) + legs[y, x1c] * f; row[(x0 < 0) | (x0 + 1 >= P.shape[1])] = 0
    c = coat[y]; row[c] = P[y, c]; out[y] = np.rint(row).astype(int)
Image.fromarray(out.astype('uint8')).save(DST + 'physicist-professor-point.png', optimize=True)
print(f'professor-point legs moved: left {sL:+d} px, right {sR:+d} px (seam x {mid}, ramp rows {Y0}-{Y1}); after the move, legs (professor-point - holding-clipboard,',
      'collar-pinned): left', match(L0, DST + 'physicist-professor-point.png', (270, 480, 1250, 1470), base), 'right', match(L0, DST + 'physicist-professor-point.png', (520, 830, 1250, 1470), base),
      '(minus the collar offset', cdx, ')')
open(DST + 'anchors.js', 'w').write('window.ANCHORS_S09 = ' + json.dumps(anch) + ';\nwindow.KEY_CHIN_X = 289;\n'); print(anch)
