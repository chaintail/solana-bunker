#!/usr/bin/env python3
"""Builds the conspiracy-v1 audio edit list and word timings (runs on do-box, no media tools).
usage: conspiracy-timing.py <transcript.json> <seg-sent.json> <out-dir>
transcript.json = bunker-transcript.json (sentences, parakeet tokens); seg-sent.json = tokens re-run on 84-138 s.
Writes <out-dir>/conspiracy-edl.json, conspiracy-timing.js (window.CONSP = {...}), conspiracy-audio.filter.
Token times from the TDT model run 0.1-0.35 s early at phrase onsets, so each phrase is re-anchored
to the energy-based speech bounds (e0, e1) given below and token times are mapped linearly inside it."""
import json, sys, re
tr = json.load(open(sys.argv[1]))['sentences']
sg = json.load(open(sys.argv[2]))
out = sys.argv[3]
toks = []
for s in tr + sg:
    for t in s['tokens']:
        toks.append((t['s'], t['e'], t['t']))
toks.sort()
def words(a, b):
    """tokens with start in [a,b) merged to words -> (text, s, e)"""
    ws = []
    for s, e, t in toks:
        if s < a or s >= b: continue
        if t.startswith(' ') or not ws or re.match(r"^[\W]$", t) and False:
            ws.append([t.strip(), s, e])
        elif re.match(r"^[,.?!']$", t):
            ws[-1][0] += t; ws[-1][2] = max(ws[-1][2], e) if t == "'" else ws[-1][2]
        else:
            ws[-1][0] += t; ws[-1][2] = e
    return ws
# phrase id, token window, energy bounds (source s), cut in/out (source s), gap after (s)
P = [
 # slide 1
 ('t1', (1.2, 8.4),    1.66, 7.53, 1.50, 7.70, 0.0),
 # slide 3
 ('p1', (53.4, 56.3),  53.86, 55.77, 53.70, 55.95, 0.30),
 ('p2', (56.3, 60.1),  56.43, 59.79, 56.28, 60.00, 0.20),
 ('p3', (60.1, 63.0),  60.35, 62.61, 60.20, 62.80, 0.30),
 ('p4', (63.0, 66.2),  63.31, 66.00, 63.15, 66.20, 0.30),
 ('p5', (66.2, 70.8),  66.39, 70.50, 66.25, 70.70, 0.85),
 ('p6', (70.8, 73.8),  71.16, 73.55, 71.00, 73.70, 0.35),
 ('p7a',(73.8, 76.6),  73.78, 76.20, 73.65, 76.40, 0.22),
 ('p7b',(76.6, 83.3),  76.84, 82.25, 76.70, 82.45, 0.40),
 ('p8a',(93.3, 95.4),  93.67, 95.01, 93.52, 95.15, 0.25),
 ('p8b',(95.4, 99.0),  95.60, 98.50, 95.45, 98.65, 0.45),
 ('p9a',(99.0, 100.4), 99.23, 99.95, 99.08, 100.15, 0.12),
 ('p9b',(100.4,109.6), 100.50, 108.40, 100.33, 108.60, 0.40),
 ('p10',(109.6,115.4), 109.98, 114.30, 109.82, 114.50, 0.30),
 ('p11',(115.4,121.2), 115.56, 120.27, 115.40, 120.45, 0.22),
 ('p12',(121.2,125.3), 121.37, 124.51, 121.22, 124.70, 0.70),
 ('p13',(125.3,127.8), 125.61, 127.69, 125.45, 127.85, 0.50),
 ('p14',(127.8,131.9), 128.23, 131.07, 128.08, 131.15, 0.0),
]
T1_LEAD = 0.40          # silence before Liam's first word on slide 1
S1_END = 7.0            # slide 1 length (s)
S3_LEAD = 0.25          # silence after slide 1 ends before p1 cut-in
TAIL = 1.9              # after last audio: folder closes, stamp, hard cut
edl, wordsout = [], {}
t = T1_LEAD; section = 's1'
for i, (pid, (ta, tb), e0, e1, ci, co, gap) in enumerate(P):
    if pid == 'p1':
        t = S1_END + S3_LEAD
    ws = words(ta, tb)
    ws = [w for w in ws if w[0]]
    t0, t1 = ws[0][1], ws[-1][2]
    k = (e1 - e0) / (t1 - t0)
    mp = lambda x: e0 + (x - t0) * k
    # source -> output for this segment: out = t + (src - ci)
    off = t - ci
    wl = [(w[0], round(mp(w[1]) + off, 3), round(mp(w[2]) + off, 3)) for w in ws]
    edl.append({'id': pid, 'src_in': ci, 'src_out': co, 'out_in': round(t, 3), 'out_out': round(t + co - ci, 3), 'speech': [round(e0 + off, 3), round(e1 + off, 3)]})
    wordsout[pid] = wl
    t = t + (co - ci) + gap
last = edl[-1]['out_out']
total = round(last + TAIL, 3)
json.dump({'edl': edl, 'words': wordsout, 'total': total, 's1_end': S1_END}, open(out + '/conspiracy-edl.json', 'w'), indent=1)
open(out + '/conspiracy-timing.js', 'w').write('window.CONSP = ' + json.dumps({'edl': edl, 'words': wordsout, 'total': total, 's1End': S1_END}) + ';\n')
# audio filter: input 0 = audio.wav (16 kHz mono) -> 48 kHz; each cut gets 12 ms fades; segments placed with adelay; output label [mix] (loudness is normalised in a second pass by build-conspiracy.sh)
parts = []
for i, e in enumerate(edl):
    d = int(round(e['out_in'] * 1000))
    dur = e['src_out'] - e['src_in']
    parts.append(f"[0:a]atrim=start={e['src_in']}:end={e['src_out']},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.012,afade=t=out:st={dur-0.012:.3f}:d=0.012,adelay={d}|{d}[a{i}]")
parts.append(f"anullsrc=r=48000:cl=mono,atrim=0:{total},asetpts=PTS-STARTPTS[base]")
ins = '[base]' + ''.join(f'[a{i}]' for i in range(len(edl)))
parts.append(f"{ins}amix=inputs={len(edl)+1}:normalize=0:duration=longest,pan=mono|c0=c0,apad=whole_dur={total},atrim=0:{total},asetpts=PTS-STARTPTS[mix]")
open(out + '/conspiracy-audio.filter', 'w').write(';\n'.join(parts) + '\n')
print('total', total)
for e in edl: print(e)
for k, v in wordsout.items(): print(k, ' '.join(f"{w}@{s:.2f}" for w, s, _ in v))
