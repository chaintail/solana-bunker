#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s09/film (or apps/web/film). Port of pipeline/s08/bodies.py (itself film/s05's s05-bodies.py) for the
scene 9 poses. The grey head oval and its outline are erased from each body PNG; the head sprite is drawn BEHIND the body, so the collar covers the neck.
Writes assets/s09/<pose>.png (same 1024x1536 canvas) and assets/s09/anchors.js: oval centre x, chin y (oval bottom), hx (collar centre x),
and KEY_CHIN_X (the chin centre x in the key crop, which goes on hx).
usage: /usr/bin/python3 pipeline/s09/bodies.py"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
SRC = 'assets/bodies/'; DST = 'assets/s09/'; os.makedirs(DST, exist_ok=True)
POSES = ['2-street-hands-in-pockets', '2-street-celebrate', '1-suit-standing', '1-suit-point-right', '5-physicist-holding-clipboard',
         '5-physicist-professor-point']   # the testimonial (film-plan-ending.md part A): the lab coat points at the results cards
anch = {}
for n in POSES:
    im = np.array(Image.open(SRC + n + '.png').convert('RGBA')).astype(int)
    a, r, g, b = im[..., 3], im[..., 0], im[..., 1], im[..., 2]
    gray = (abs(r - g) < 10) & (abs(g - b) < 10) & (r > 130) & (r < 230) & (a > 200); gray[345:] = False
    lab, k = ndi.label(gray); i = np.argmax(ndi.sum(gray, lab, range(1, k + 1))) + 1
    m = ndi.binary_fill_holes(lab == i); ys, xs = np.where(m)
    chin = int(ys.max()); cx = float((xs.min() + xs.max()) / 2)
    m2 = ndi.binary_dilation(m, iterations=15); m2[chin + 8:] = False
    out = im.copy(); out[m2, 3] = 0
    Image.fromarray(out.astype('uint8')).save(DST + n.split('-', 1)[1] + '.png', optimize=True)
    anch[n.split('-', 1)[1]] = {'cx': cx, 'chin': chin, 'top': int(ys.min()), 'hx': cx}   # hx: where the head's chin centre goes = the collar centre (on the oval centre for all five poses, checked on 2x crops)
# the lab coat's hand on its own layer (skin plus its outline), so the enlarged WHITEPAPER clipboard can sit between the body and the hand
im = np.array(Image.open(SRC + '5-physicist-holding-clipboard.png').convert('RGBA')).astype(int)
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
open(DST + 'anchors.js', 'w').write('window.ANCHORS_S09 = ' + json.dumps(anch) + ';\nwindow.KEY_CHIN_X = 289;\n'); print(anch)
