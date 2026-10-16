#!/usr/bin/env python3
"""Cuts the three Codex thinking-pose candidates (Joe's chin scratch, v5) into assets/bodies/2-street-thinking{,-2,-3}.png (candidate 1 = the v4 pose).
Same cut as 8a38e17: flood the sticker (white border and background) from the image edge through every pixel brighter than 75 grey, so the sticker's
white border goes too. v5 addition: the white patch enclosed between the arm and the shirt (above the knees) becomes transparent as well.
usage: python3 pipeline/s09/thinking-cut.py <src1.png> <src2.png> <src3.png>"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
for n, f in zip(['2-street-thinking', '2-street-thinking-2', '2-street-thinking-3'], sys.argv[1:4]):
    a = np.array(Image.open(f).convert('RGB')).astype(int)
    lab, k = ndi.label(a.sum(-1) / 3 > 75)
    edge = set(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]) - {0}
    keep = ~np.isin(lab, list(edge))
    wl, wk = ndi.label((a.min(-1) > 215) & keep)   # enclosed near-white regions
    for i in range(1, wk + 1):
        ys, xs = np.where(wl == i)
        if ys.max() < 800 and len(ys) > 30: keep &= ~(wl == i); keep &= ~(ndi.binary_dilation(wl == i, iterations=3) & (a.min(-1) > 150)); print(n, 'enclosed white region', len(ys), 'px at y', ys.min(), ys.max(), 'x', xs.min(), xs.max())
    out = np.dstack([a, np.where(keep, 255, 0)]).astype('uint8')
    Image.fromarray(out).save('assets/bodies/' + n + '.png', optimize=True)
