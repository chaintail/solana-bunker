#!/usr/bin/env python3
"""Whiteboard takeover check (dev-mac, /usr/bin/python3): before.png = the baked slide-5 frame on screen (page 0.28, x12 frame 7), after.png = the live lab coat
(page 0.32, x12 frame 8). Prints the best integer shift (+-6 px, minimum mean |diff|) of head, collar/tie and legs/shoes from before to after, and writes
<out>/takeover-pair.png (whole figure, 2x) and <out>/takeover-head.png (head and collar, 4x), before left, after right.
usage: takeover-check.py before.png after.png outdir"""
import sys
import numpy as np
from PIL import Image
a, b = (np.array(Image.open(p).convert('RGB')).astype(int) for p in sys.argv[1:3]); out = sys.argv[3]
REG = [((205, 300, 135, 215), 'head'), ((300, 380, 150, 205), 'collar/tie'), ((640, 706, 110, 250), 'legs/shoes')]
for (y0, y1, x0, x1), name in REG:
    A = a[y0:y1, x0:x1]; best = None
    for dy in range(-6, 7):
        for dx in range(-6, 7):
            e = np.abs(A - b[y0 + dy:y1 + dy, x0 + dx:x1 + dx]).mean()
            if best is None or e < best[0]: best = (e, dx, dy)
    print('%-10s shift dx %+d dy %+d px (mean |diff| %.2f there, %.2f at 0,0)' % (name, best[1], best[2], best[0], np.abs(A - b[y0:y1, x0:x1]).mean()))
def pair(box, k, f):
    y0, y1, x0, x1 = box; im = [Image.fromarray(x[y0:y1, x0:x1].astype(np.uint8)).resize(((x1 - x0) * k, (y1 - y0) * k), Image.NEAREST) for x in (a, b)]
    c = Image.new('RGB', (im[0].width * 2 + 12, im[0].height), 'white'); c.paste(im[0], (0, 0)); c.paste(im[1], (im[0].width + 12, 0)); c.save(f)
pair((160, 720, 40, 330), 2, out + '/takeover-pair.png')
pair((190, 390, 110, 240), 4, out + '/takeover-head.png')
