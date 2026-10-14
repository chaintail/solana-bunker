#!/usr/bin/env python3
"""Build the two images the film tweet component scrolls (apps/web/film/assets/tweet-header.jpg, tweet-body.jpg)
from the real screenshot pieces docs/presentation/assets/tweet-*.jpg. Run from apps/web/film: python3 scripts/stitch-tweet-film.py
- header: Justin's profile row from tweet-1-top (fixed at the top of the component)
- body  : the tweet text, pieces joined where their screenshots overlap (strip matching), footer (time, views, likes, retweets, replies) cut away
- tweet-3 is the phone capture of the same top text and is not used; tweet-2 is contained in tweet-4 and is only used for the join order.
Prints the y of each landmark line (body px, 1290 wide) so the scene can aim its highlight bands."""
import numpy as np
from PIL import Image

A = '../../../docs/presentation/assets/'
W = 1290
HEADER_H = 235
FOOT7 = 575  # tweet-7: text lines end at y 564, the timestamp / views / like row starts at 673


def load(n):
    im = Image.open(f'{A}tweet-{n}.jpg').convert('RGB')
    if im.width != W:
        im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    return im


def rows(im):
    g = np.asarray(im.convert('L'), dtype=np.int16)
    return (g > 90).sum(axis=1)  # bright pixels per row = text


def trim(im, top=True):
    r = rows(im); idx = np.nonzero(r > 2)[0]
    y0 = idx[0] if top else 0
    return im.crop((0, max(0, y0 - 10), W, idx[-1] + 12))


def blocks(im):
    r = rows(im) > 2; out = []; y = 0; n = len(r)
    while y < n:
        if r[y]:
            y0 = y
            while y < n and r[y]: y += 1
            out.append((y0, y))
        else: y += 1
    return out


def replace_last(acc, nxt):
    # the last text line of acc is cut off by the screenshot edge and nxt starts with that same paragraph:
    # drop it and append nxt after the paragraph gap that preceded it
    bl = blocks(acc)
    gap = bl[-1][0] - bl[-2][1]
    keep = bl[-2][1] + 1
    print('replace_last: dropped acc line at', bl[-1], 'gap', gap)
    out = Image.new('RGB', (W, keep + gap + nxt.height)); out.paste(acc.crop((0, 0, W, keep)), (0, 0)); out.paste(nxt, (0, keep + gap))
    return out


def join(acc, nxt, gap=70):
    bl = blocks(acc)
    end = bl[-1][1] - 1  # last (possibly cut) text row
    # strip = the last three complete text lines (the final, probably cut, line is left out)
    y0, y1 = bl[-4][0] - 6, bl[-2][1] + 6
    strip = np.asarray(acc.convert('L'), dtype=np.float32)[y0:y1]
    sh = y1 - y0
    nb = np.asarray(nxt.convert('L'), dtype=np.float32)
    best, by = 1e18, None
    for y in range(0, nb.shape[0] - sh):
        s = ((nb[y:y + sh] - strip) ** 2).mean()
        if s < best: best, by = s, y
    if best < 150:  # overlap found: continue after the matched strip, from the line the strip ended with
        print('overlap', round(best, 1), 'at next y', by)
        cut = by + sh
        out = Image.new('RGB', (W, y1 + nxt.height - cut)); out.paste(acc.crop((0, 0, W, y1)), (0, 0)); out.paste(nxt.crop((0, cut, W, nxt.height)), (0, y1))
    else:
        print('no overlap (best', round(best, 1), '): paragraph gap')
        out = Image.new('RGB', (W, end + 1 + gap + nxt.height)); out.paste(acc.crop((0, 0, W, end + 1)), (0, 0)); out.paste(nxt, (0, end + 1 + gap))
    return out


top = load('1-top')
header = top.crop((0, 0, W, HEADER_H))
body = trim(top.crop((0, HEADER_H, W, top.height)))
for n in ['2', '4', '5', '6', '7']:
    piece = load(n)
    if n == '7':  # cut the footer: the body text ends before the timestamp / views row
        print('7 blocks', blocks(piece)[:40])
        piece = piece.crop((0, 0, W, FOOT7))
    body = (replace_last if n in '567' else join)(body, trim(piece, top=True))
header.save('assets/tweet-header.jpg', quality=88)
body.save('assets/tweet-body.jpg', quality=84)
print('header', header.size, 'body', body.size)
