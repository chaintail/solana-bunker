#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s09 (system python). Scene 9 edit list (film-plan-s09.md section 1) -> out/s09-edl.json,
film/data/s09-edl.js (window.S09: edl, head rows, beat times T, SFX markers), out/s09-audio.filter.
Liam's only read of this passage (497.28-518.48 s), used as recorded; the stumble "from keys or like" is KEPT (composer ruling Q1).
Two segments of the denoised take: A 497.30-514.20 (Joe J1-J2, suit S1-S2, one continuous stretch with its own pauses) and B 515.18-517.36 (suit S3-S4).
The cut takes out the end of the "what if" pause and the click at 514.54-514.60; the reveal between them is 2.60 s of bed (ruling Q2).
In/out points sit in the pauses of silencedetect (n=-38dB, d=0.12) on the denoised take, rechecked with 10-30 ms energy and band scans; the word
times below are those rechecked take times (the transcript tokens run up to 0.3 s early in S1). Rows only assign the lip-synced heads."""
import json
FPS = 30
IN0 = 1.55            # scene time of segment A's first sample (after the TV static and the push-in)
REVEAL = 2.60         # bed-only gap between the segments
TAG = 6.60            # tag after the last word, the last 2.00 s a frozen hold
SEG = [(497.30, 514.20), (515.18, 517.36)]
OFF = [IN0 - SEG[0][0]]; OFF.append(IN0 + (SEG[0][1] - SEG[0][0]) + REVEAL - SEG[1][0])
rows = [  # id, speaker, text, src_in, src_out, segment
    ('J1', 'joe', "Okay, there's still one really annoying part.", 497.30, 499.92, 0),
    ('J2', 'joe', 'How are we supposed to keep track of our thousand one-time secrets?', 500.20, 503.20, 0),
    ('S1', 'suit', 'If only there was some kind of convenient way to derive a secret from keys or like something memorable.', 503.36, 509.86, 0),
    ('S2', 'suit', 'You know, rather than memorizing thousands of strings of gibberish, what if...', 509.86, 514.20, 0),
    ('S3', 'suit', 'yeah, we did that too.', 515.18, 516.50, 1),
    ('S4', 'suit', 'Go check it out.', 516.50, 517.36, 1),
]
edl = []
for id_, sp, text, si, so, sg in rows:
    oi = round(si + OFF[sg], 4); edl.append({'id': id_, 'speaker': sp, 'text': text, 'src_in': si, 'src_out': so, 'out_in': oi, 'out_out': round(so + OFF[sg], 4), 'frames': int(round((so - si) * FPS))})
for i in range(1, len(edl)): assert edl[i]['out_in'] >= edl[i - 1]['out_out'] - 1e-6, edl[i]['id']
# head-only row: the lab coat's closed-mouth frame, from the silence before "Okay" (496.27-497.40)
heads = edl + [{'id': 'LAB', 'speaker': 'lab', 'text': '(closed mouth)', 'src_in': 496.90, 'src_out': 496.90 + 1 / FPS, 'out_in': None, 'out_out': None, 'frames': 1}]
def S(src):   # take time -> scene time
    for sg, (a, b) in enumerate(SEG):
        if a - .05 <= src <= b + .05: return round(src + OFF[sg], 3)
    raise ValueError(src)
END = edl[-1]['out_out']; TOTAL = round(END + TAG, 2)
T = {'static': .12, 'static_end': .62, 'push_end': IN0, 'okay': S(497.37), 'annoying': S(499.16), 'part': S(499.70), 'how': S(500.28), 'keep': S(501.08),
     'thousand': S(501.72), 'onetime': S(502.12), 'secrets': S(502.68), 'j2end': edl[1]['out_out'], 'ifonly': S(503.47), 'convenient': S(504.92),
     'derive': S(506.18), 'secret': S(507.08), 'from': S(507.69), 'something': S(508.63), 'memorable': S(509.08), 'youknow': S(510.46),
     'rather': S(510.67), 'memorizing': S(511.00), 'thousands': S(511.64), 'strings': S(512.20), 'gibberish': S(512.56), 'whatif': S(513.67),
     'whatif_end': S(514.15), 'cut': edl[3]['out_out'], 'yeah': S(515.23), 'didthat': S(515.76), 'too_end': S(516.41), 'go': S(516.68),
     'check': S(516.84), 'itout': S(517.00), 'out_end': S(517.30), 'end': END, 'hold': round(TOTAL - 2.0, 3), 'total': TOTAL}
c = T['cut']
T.update({'scratch': c, 'snap': round(c + .15, 3), 'bip': round(c + .30, 3), 'parch': round(c + .80, 3), 'words': round(c + .95, 3),
          'ghost': round(c + 1.95, 3), 'key': round(c + 2.25, 3), 'fork': round(c + 2.35, 3)})
T.update({'stamp': T['yeah'], 'butwait': round(T['go'] - .05, 3), 'tag': round(END + .07, 3)})
g = T['tag']
T.update({'suit_out': g, 'shrink': round(g + .17, 3), 'free': round(g + .47, 3), 'callnow': round(g + 1.67, 3), 'flip': round(g + 2.87, 3), 'lab': round(g + 3.37, 3)})
markers = [{'id': k, 't': round(v, 3)} for k, v in [('SFX_TV_STATIC', T['static']), ('SFX_RECORD_SCRATCH', T['scratch']), ('SFX_STAMP', T['stamp'] + .03),
           ('SFX_WHOOSH', T['butwait']), ('SFX_CASH_REGISTER', T['free'])]]
doc = {'total': TOTAL, 'fps': FPS, 'edl': edl, 'heads': heads, 'T': T, 'markers': markers, 'note': 'markers are timing only (no SFX in the mix)'}
json.dump(doc, open('out/s09-edl.json', 'w'), indent=1)
open('film/data/s09-edl.js', 'w').write('window.S09 = ' + json.dumps(doc) + ';\n')
f = []
for i, (a, b) in enumerate(SEG):
    d = b - a; ms = int(round((a + OFF[i]) * 1000))
    f.append(f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={d - 0.02:.4f}:d=0.02,adelay={ms}|{ms}[a{i}];")
f.append(f"anullsrc=r=48000:cl=mono,atrim=0:{TOTAL},asetpts=PTS-STARTPTS[base];")
f.append(f"[base][a0][a1]amix=inputs=3:normalize=0:duration=longest,pan=mono|c0=c0,apad=whole_dur={TOTAL},atrim=0:{TOTAL},asetpts=PTS-STARTPTS[mix]")
open('out/s09-audio.filter', 'w').write('\n'.join(f) + '\n')
for e in edl: print(e['id'], e['speaker'], e['src_in'], e['src_out'], '->', e['out_in'], e['out_out'], e['frames'])
print('total', TOTAL, 'frames', round(TOTAL * FPS)); print({k: T[k] for k in ['cut', 'snap', 'yeah', 'go', 'tag', 'hold']})
