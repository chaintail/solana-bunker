#!/usr/bin/env python3
"""Slide 4 ("we made a Solana Bunker") audio edit list and word timings (runs on do-box, no media tools).
usage: s04-timing.py <bunker-transcript.json> <seg-sent.json> <out-dir>
Writes <out-dir>/s04-edl.json, s04-timing.js (window.S4 = {...}) and s04-audio.filter (input 0 = audio.wav, output [mix]).
Method as conspiracy-timing.py: each phrase is cut at [in, out] (source seconds, 0.12-0.15 s of margin around the energy-based
speech bounds e0/e1), placed on the output timeline with a gap after it, and the parakeet token times (which run 0.1-0.35 s early
at phrase onsets) are re-anchored linearly to the energy bounds.
CUT: "A few million tokens later and several hours of voice notes," (source 182.96-186.56, Liam: "I don't think that adds anything,
and the video is getting long") is dropped, so "...ED25519 algorithm." goes straight to "we built it."; the long breaths after
"algorithm." (181.3-183.3) and "it." (187.2-190.4) go with it."""
import json, sys, re
tr = json.load(open(sys.argv[1]))['sentences']
sg = json.load(open(sys.argv[2]))
out = sys.argv[3]
toks = []
for s in tr:
    for t in s['tokens']: toks.append((t['s'], t['e'], t['t']))
for s in sg:
    if s['start'] < 136.3:
        for t in s['tokens']: toks.append((t['s'], t['e'], t['t']))
toks = sorted(set(toks))
def words(a, b):
    ws = []
    for s, e, t in toks:
        if s < a or s >= b: continue
        if t.startswith(' ') or not ws: ws.append([t.strip(), s, e])
        elif re.match(r"^[,.?!']$", t): ws[-1][0] += t
        else: ws[-1][0] += t; ws[-1][2] = e
    return ws
# id, token window, e0, e1 (energy bounds, source s), cut in/out (source s), gap after (s), who (physicist / joe / engineer / '')
P = [
 ('a1',  (131.8, 133.9), 131.90, 133.67, 131.78, 133.82, 0.35, ''),
 ('a2',  (133.9, 136.2), 134.21, 136.00, 134.09, 136.15, 0.55, ''),
 ('b1',  (136.3, 139.2), 136.61, 138.81, 136.49, 138.96, 0.25, ''),
 ('b2',  (139.2, 141.9), 139.50, 141.73, 139.38, 141.88, 0.35, ''),
 ('c1',  (141.9, 145.0), 142.08, 144.49, 141.96, 144.64, 0.40, ''),
 ('c2',  (145.0, 148.3), 145.14, 147.10, 145.02, 147.25, 0.55, ''),
 ('d1',  (148.3, 151.4), 148.75, 151.13, 148.63, 151.28, 0.10, 'physicist'),
 ('d2',  (151.4, 152.9), 151.62, 152.69, 151.50, 152.84, 0.22, 'physicist'),
 ('d3',  (152.9, 154.85), 153.23, 154.62, 153.11, 154.77, 0.40, 'physicist'),
 ('e1',  (154.85, 159.0), 155.10, 158.12, 154.98, 158.27, 0.95, 'physicist'),
 ('f1',  (159.4, 162.9), 159.71, 162.83, 159.59, 162.98, 0.25, 'joe'),
 ('f2',  (162.9, 169.7), 163.16, 168.73, 163.04, 168.88, 0.30, 'joe'),
 ('g1',  (169.7, 173.9), 169.97, 173.55, 169.85, 173.70, 0.25, 'engineer'),
 ('g2',  (173.9, 175.55), 174.21, 175.25, 174.09, 175.40, 0.25, 'engineer'),
 ('g3',  (175.55, 182.9), 175.80, 181.26, 175.68, 181.41, 0.35, 'engineer'),
 ('h1',  (186.5, 188.0), 186.60, 187.24, 186.48, 187.39, 0.40, 'engineer'),
 ('h2',  (190.3, 193.0), 190.49, 192.84, 190.37, 192.99, 0.30, 'engineer'),
 ('h3',  (193.0, 195.6), 193.17, 195.18, 193.05, 195.33, 0.0, 'engineer'),
]
T_LEAD = 0.55   # folder slides off before the first word
TAIL = 0.15
edl, wordsout = [], {}
t = T_LEAD
for pid, (ta, tb), e0, e1, ci, co, gap, who in P:
    ws = [w for w in words(ta, tb) if w[0]]
    t0, t1 = ws[0][1], ws[-1][2]
    k = (e1 - e0) / (t1 - t0)
    mp = lambda x: e0 + (x - t0) * k
    off = t - ci
    wordsout[pid] = [(w[0], round(mp(w[1]) + off, 3), round(mp(w[2]) + off, 3)) for w in ws]
    edl.append({'id': pid, 'who': who, 'src_in': ci, 'src_out': co, 'out_in': round(t, 3), 'out_out': round(t + co - ci, 3), 'gap': gap, 'speech': [round(e0 + off, 3), round(e1 + off, 3)]})
    t = t + (co - ci) + gap
total = round(edl[-1]['out_out'] + TAIL, 3)
json.dump({'edl': edl, 'words': wordsout, 'total': total}, open(out + '/s04-edl.json', 'w'), indent=1)
open(out + '/s04-timing.js', 'w').write('window.S4 = ' + json.dumps({'edl': edl, 'words': wordsout, 'total': total}) + ';\n')
parts = []
for i, e in enumerate(edl):
    d = int(round(e['out_in'] * 1000)); dur = e['src_out'] - e['src_in']
    parts.append(f"[0:a]atrim=start={e['src_in']}:end={e['src_out']},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.020,afade=t=out:st={dur-0.020:.3f}:d=0.020,adelay={d}|{d}[a{i}]")
parts.append(f"anullsrc=r=48000:cl=mono,atrim=0:{total},asetpts=PTS-STARTPTS[base]")
ins = '[base]' + ''.join(f'[a{i}]' for i in range(len(edl)))
parts.append(f"{ins}amix=inputs={len(edl)+1}:normalize=0:duration=longest,pan=mono|c0=c0,apad=whole_dur={total},atrim=0:{total},asetpts=PTS-STARTPTS[mix]")
open(out + '/s04-audio.filter', 'w').write(';\n'.join(parts) + '\n')
print('total', total)
for e in edl: print(e['id'], e['who'], e['src_in'], e['src_out'], '->', e['out_in'], e['out_out'])
for k, v in wordsout.items(): print(k, ' '.join(f"{w}@{s:.2f}" for w, s, _ in v))
