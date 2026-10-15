#!/usr/bin/env python3
"""Prepares the generated bodies (assets/bodies, 1024x1536, grey oval where the head goes) for the head-behind-body layering used in s05-hash.html:
the grey oval and its outline are erased from the body PNG (the head sprite is drawn behind the body, so the collar covers the neck), the body's own neck
skin below the oval stays. Writes assets/s05/<name>.png (same canvas) and assets/s05/anchors.js: oval centre x, chin y (oval bottom), face height (oval height 217 px).
usage (run from apps/web/film): python3 -I pipeline/s05-bodies.py"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
SRC = 'assets/bodies/'; DST = 'assets/s05/'; os.makedirs(DST, exist_ok=True)
POSES = ['5-physicist-professor-point', '5-physicist-shrug', '5-physicist-holding-clipboard', '2-street-celebrate', '4-engineer-thumbs-up']
anch = {}
for n in POSES:
    im = np.array(Image.open(SRC + n + '.png').convert('RGBA')).astype(int)
    a, r, g, b = im[..., 3], im[..., 0], im[..., 1], im[..., 2]
    gray = (abs(r - g) < 10) & (abs(g - b) < 10) & (r > 130) & (r < 230) & (a > 200); gray[345:] = False
    lab, k = ndi.label(gray); i = np.argmax(ndi.sum(gray, lab, range(1, k + 1))) + 1
    m = ndi.binary_fill_holes(lab == i); ys, xs = np.where(m)
    chin = int(ys.max()); cx = float((xs.min() + xs.max()) / 2)
    m2 = ndi.binary_dilation(m, iterations=15); m2[chin + 8:] = False
    if 'engineer' in n: m2[:int(ys.min()) + 50] = m[:int(ys.min()) + 50]   # keep the hard hat brim
    out = im.copy(); out[m2, 3] = 0
    Image.fromarray(out.astype('uint8'), 'RGBA').save(DST + n.split('-', 1)[1] + '.png', optimize=True)
    anch[n.split('-', 1)[1]] = {'cx': cx, 'chin': chin}
open(DST + 'anchors.js', 'w').write('window.ANCHORS = ' + json.dumps(anch) + ';\n'); print(anch)
