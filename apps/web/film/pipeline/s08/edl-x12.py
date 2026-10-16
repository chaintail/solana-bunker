#!/usr/bin/env python3
"""x12 build mode (Liam 16583): data/s08-edl.js -> data/s08-edl-x12.js, every scene time divided by 1.2 (Liam's voice at 1.2x, picture captured with --speed=1.2).
Scaled: edl[].out_in/out_out, T.* (lists element-wise), markers[].t, sfx[].t (tag cue times). Not scaled: src_in/src_out (take times) and frames (head sprite counts).
total = the x12 picture length, ceil(round(total*30)/1.2)/30 (the last output frame is the scene's last frame), so score.py renders the score to the cut's length.
score.py and score-check.py read the copy with --edl data/s08-edl-x12.js (the score's tempo map and every sting follow the scaled markers).
usage: python3 pipeline/s08/edl-x12.py   (from apps/web/film; no media tools)"""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__)); FILM = os.path.dirname(os.path.dirname(HERE)); S = 1.2
src = open(os.path.join(FILM, 'data/s08-edl.js')).read(); D = json.loads(src[src.index('{'):src.rindex('}') + 1])
r = lambda t: [r(x) for x in t] if isinstance(t, list) else round(t / S, 4)   # T.trucks is a list
N = round(D['total'] * D['fps']); M = math.ceil(N / S - 1e-9)
X = dict(D); X['total'] = round(M / D['fps'], 4); X['speed'] = S
X['edl'] = [dict(e, out_in=r(e['out_in']), out_out=r(e['out_out'])) for e in D['edl']]
X['T'] = {k: r(v) for k, v in D['T'].items()}
X['markers'] = [dict(m, t=r(m['t'])) for m in D['markers']]
# the jingle's arpeggio (0.595 s) has a fixed tempo; its hold is shortened so the chord still ends 0.1 s before the end: hold = tail - 0.595 - 0.05 - 0.1
X['sfx'] = [dict(x, t=r(x['t'])) for x in D['sfx']]
for x in X['sfx']:
    if 'hold' in x: x['hold'] = round(X['total'] - x['t'] - 0.595 - 0.05 - 0.1, 3)
X['note'] = 'x12 copy of s08-edl.js (pipeline/s08/edl-x12.py): scene times / 1.2, total = %d frames (scene %d frames at 1.2x). ' % (M, N) + D.get('note', '')
open(os.path.join(FILM, 'data/s08-edl-x12.js'), 'w').write('window.S08 = ' + json.dumps(X) + ';\n')
print('total', D['total'], '->', X['total'], '(%d -> %d frames)' % (N, M))
