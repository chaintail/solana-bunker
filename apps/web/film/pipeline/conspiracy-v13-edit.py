#!/usr/bin/env python3
"""v13 script cuts (Liam, 2026-10-18: "we can cut out the 'they were quick to point out'" and the first Twitter line, "because I say it again
right later"). Runs on do-box (no media tools). Rewrites film/data/conspiracy-edl.json, conspiracy-timing.js and conspiracy-audio.filter in place;
input must be x12b's edit (total 70.92, p8b present); a second run on the v13 files is a no-op.

Measured on out/consp4/take-dn.wav (16 kHz; 10 ms / 2.5 ms RMS, 80-500 Hz and > 2.5 kHz bands; words from faster-whisper medium on the take):
  cut 1, inside p7b: "minded," ends 76.10; "they" starts 76.865 (x12b out 31.455); "out" closes 77.86; "that" 77.90-77.96, its closure murmur
    (-40 dB) to 77.985; "the" starts with its dental release at 77.987 (x12b out 32.577), voiced from 78.005; "U.S." 78.11-78.40.
    p7b now starts at the rising zero crossing at sample 1247609 (77.975563 s, in the closure, -40 dB) with a 10 ms fade-in, so "the" keeps its
    onset. Shift 1.12 s (28 frames at 1.2x): "the" lands where "they" was (pause after "minded," 0.69 s at 1x / 0.57 s at 1.2x, x12b 0.68).
  cut 2, all of p8b ("At least that's what crypto Twitter kept repeating."): "this." (p8a) ends 95.10 (x12b out 39.02); "Apparently," (p9a)
    starts 99.255 (x12b out 43.145). p8b's piece is dropped and p9a onward move 3.40 s (85 frames) earlier: pause "this." -> "Apparently,"
    0.725 s at 1x / 0.604 s at 1.2x (the edit's other sentence gaps are 0.63-0.76 s at 1x).
Timeline cuts (x12b global 1x seconds, title included; output time at 1.2x = global / 1.2, frame = global / 0.04):
  [31.445563, 32.565563)  1.12 s   x12b output frames 787-814 removed
  [39.45, 42.85)          3.40 s   x12b output frames 987-1071 removed (ends where the line-chart board starts to slide in, 0.295 s before
                                   "Apparently," as in x12b)
  total 4.52 s at 1x = 3.7667 s at 1.2x = 113 frames: 70.92 -> 66.40 s (1773 -> 1660 frames, 59.100 -> 55.333 s)
The cuts are written to the timing data (CONSP.cuts) so s03-conspiracy.html maps its hand-placed x12b times through them; word times in the data
are v13 times."""
import json, os, sys
d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'data')
SR = 16000
P7B = 1247609                      # new p7b in-point (take sample, rising zero crossing)
S1, S2 = 1.12, 3.40                # removed at cut 1 / cut 2 (s at 1x)
A1 = round(P7B / SR - 45.41 - S1, 6)   # x12b p7b: out = src - 45.41; cut 1 starts where the new p7b starts (31.445563)
A2 = 39.45                          # cut 2 start (x12b time), A2 + S2 = 42.85 = the line-chart board's slide-in
CUTS = [[A1, S1], [A2, S2]]
X12B_TOTAL, TOTAL = 70.92, round(70.92 - S1 - S2, 4)
r = lambda x: round(x, 3)
e = json.load(open(f'{d}/conspiracy-edl.json'))
if e.get('cuts') == CUTS and e['total'] == TOTAL:
    print('already v13'); sys.exit(0)
assert e['total'] == X12B_TOTAL and 'p8b' in e['words'], 'input is not the x12b edit'


def warp(t):                        # x12b global time -> v13 global time (a time inside a cut lands on its start)
    s = 0.0
    for a, dd in CUTS:
        if t >= a + dd: s += dd
        elif t > a: s += t - a
    return round(t - s, 6)


edl = []
for x in e['edl']:
    x = dict(x)
    if x['id'] == 'p8b':
        continue
    if x['id'] == 'p7b':
        old_off = x['out_in'] - x['src_in']                      # -45.41
        x['src_in'] = P7B / SR
        x['out_in'] = A1
        x['out_out'] = r(A1 + x['src_out'] - x['src_in'])
        x['speech'] = [r(77.987 + old_off - S1), r(x['speech'][1] - S1)]
        x['cut_in_fade'] = 0.01
    elif x['out_in'] >= A2 + S2:
        x['out_in'], x['out_out'] = r(x['out_in'] - S1 - S2), r(x['out_out'] - S1 - S2)
        x['speech'] = [r(t - S1 - S2) for t in x['speech']]
    elif x['out_in'] >= A1 + S1:
        x['out_in'], x['out_out'] = r(x['out_in'] - S1), r(x['out_out'] - S1)
        x['speech'] = [r(t - S1) for t in x['speech']]
    edl.append(x)
w = {}
for pid, ws in e['words'].items():
    if pid == 'p8b':
        continue
    if pid == 'p7b':
        ws = ws[[x[0] for x in ws].index('the'):]                  # drop "they were quick to point out that"
        ws = [[t, r(a - S1), r(b - S1)] for t, a, b in ws]
        ws[0][1] = r(77.987 - 45.41 - S1)                          # "the": measured release onset
    else:
        ws = [[t, warp(a), warp(b)] for t, a, b in ws]
    w[pid] = ws
e.update(edl=edl, words=w, total=TOTAL, cuts=CUTS,
         cuts_note='v13: x12b global seconds [start, removed]; cut 1 "they were quick to point out that", cut 2 p8b "At least that\'s what crypto Twitter kept repeating."')
json.dump(e, open(f'{d}/conspiracy-edl.json', 'w'), indent=1)
open(f'{d}/conspiracy-timing.js', 'w').write('window.CONSP = ' + json.dumps({'edl': edl, 'words': w, 'total': TOTAL, 's1End': e['s1_end'], 'cuts': CUTS}) + ';\n')
# audio filter: x12b's chains a0..a16 are t1 p1..p7a p7b p8a p8b p9a..p12 p13+p14; p7b gets the new in-point, p8b goes, the rest move
lines = [l.rstrip(';\n') for l in open(f'{d}/conspiracy-audio.filter') if l.strip()]
ch = [l for l in lines if l.startswith('[0:a]')]
assert len(ch) == 17, len(ch)
out = []
for i, l in enumerate(ch):
    if i == 10:                                                    # p8b
        continue
    if i == 8:                                                     # p7b
        x = next(p for p in edl if p['id'] == 'p7b'); end = round(x['src_out'] * SR)
        ln = (end - P7B) / SR; dl = P7B * 3 - round((P7B / SR - A1) * 48000)
        l = (f"[0:a]atrim=start_sample={P7B}:end_sample={end},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.01,"
             f"afade=t=out:st={ln - 0.02:.4f}:d=0.02,adelay={dl}S|{dl}S[a8]")
    else:
        sh = 0 if i < 8 else (S1 if i == 9 else S1 + S2)
        pre, rest = l.split('adelay=')
        ms = int(rest.split('|')[0]); nm = round(ms - sh * 1000)
        l = f"{pre}adelay={nm}|{nm}[a{len(out)}]"
    out.append(l)
n = len(out)
out.append(f"anullsrc=r=48000:cl=mono,atrim=0:{TOTAL},asetpts=PTS-STARTPTS[base]")
out.append('[base]' + ''.join(f'[a{i}]' for i in range(n)) + f"amix=inputs={n + 1}:normalize=0:duration=longest,pan=mono|c0=c0,apad=whole_dur={TOTAL},atrim=0:{TOTAL},asetpts=PTS-STARTPTS[mix]")
open(f'{d}/conspiracy-audio.filter', 'w').write(';\n'.join(out) + '\n')
print('cuts', CUTS, 'total', TOTAL, 'p7b', next(p for p in edl if p['id'] == 'p7b'))
print('the', w['p7b'][0], 'Apparently', w['p9a'][0], 'conclusions', w['p14'][-1])
