#!/usr/bin/env python3
"""Revision 4 tweet parts. Run from apps/web/film: python3 scripts/tweet-parts-v4.py
1) assets/tweet-header-v4.jpg : the real header row (avatar, name, handle, X mark) cut tight from docs/presentation/assets/tweet-1-top.jpg
2) assets/tweet-footer.jpg    : the real footer strip (time, views, replies / retweets / likes / bookmarks) cut from tweet-7.jpg
3) data/tweet-hl.js           : per-sentence highlighter segments in assets/tweet-body.jpg pixel space, from word boxes.
   Word boxes come from tesseract on the inverted body (run on dev-mac: tesseract body-inv.png data/tweet-body --psm 6 tsv); the real pixels
   stay on screen, the OCR only supplies where each word is, so a marker can start and stop mid-line exactly at a sentence's first/last word."""
import csv, json, re
from PIL import Image
A = '../../../docs/presentation/assets/'
Image.open(A + 'tweet-1-top.jpg').convert('RGB').crop((0, 22, 1290, 212)).save('assets/tweet-header-v4.jpg', quality=90)
Image.open(A + 'tweet-7.jpg').convert('RGB').crop((0, 648, 1290, 858)).save('assets/tweet-footer.jpg', quality=90)

rows = [r for r in csv.DictReader(open('data/tweet-body.tsv'), delimiter='\t', quoting=csv.QUOTE_NONE) if r['level'] == '5' and r['text'].strip()]
toks = []
for r in rows:
    n = re.sub(r'[^a-z0-9]', '', r['text'].lower())
    if n: toks.append(dict(n=n, line=(r['block_num'], r['par_num'], r['line_num']), x0=int(r['left']), x1=int(r['left']) + int(r['width']), y0=int(r['top']), y1=int(r['top']) + int(r['height'])))

def find(seq, after=0):
    for i in range(after, len(toks) - len(seq) + 1):
        if [t['n'] for t in toks[i:i + len(seq)]] == seq: return i
    raise SystemExit('not found: %s' % seq)

# (name, first words, last words). 'i.e.' normalises to 'ie'.
SENT = [
    ('bunker',  ['today'], ['bunker', 'mode']),
    ('imo',     ['imo', 'it', 'is', 'now'], ['not', 'years']),
    ('fresh',   ['my', 'personal', 'recommendation'], ['behind', 'a', 'hash']),
    ('never',   ['holders', 'starting'], ['a', 'transaction']),
    ('hash',    ['ie', 'addresses', 'whose'], ['behind', 'a', 'hash']),
]
out = {}
for name, first, last in SENT:
    a = find(first); b = find(last, a); b += len(last) - 1
    segs = []; cur = None
    for t in toks[a:b + 1]:
        if cur and cur['line'] == t['line']: cur['x1'] = t['x1']; cur['y0'] = min(cur['y0'], t['y0']); cur['y1'] = max(cur['y1'], t['y1'])
        else:
            cur = dict(line=t['line'], x0=t['x0'], x1=t['x1'], y0=t['y0'], y1=t['y1']); segs.append(cur)
    out[name] = [dict(x0=s['x0'] - 6, x1=s['x1'] + 6, y0=s["y0"] - 11, y1=s["y1"] + 12) for s in segs]
    print(name, len(segs), 'lines, y', segs[0]['y0'], '-', segs[-1]['y1'])
open('data/tweet-hl.js', 'w').write('window.TWEET_HL = ' + json.dumps(out) + ';\n')
