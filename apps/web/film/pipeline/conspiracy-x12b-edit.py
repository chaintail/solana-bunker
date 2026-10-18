#!/usr/bin/env python3
"""x12b end trim (Liam, voice 2026-10-16): cut the pause before "We'll let you draw your own conclusions" and end the scene on that line.
Runs on do-box (no media tools). Rewrites film/data/conspiracy-edl.json, conspiracy-timing.js and conspiracy-audio.filter in place
(idempotent: the p13/p14 rows, words and the total are set to absolute values; p1-p12 and t1 are left as they are).

Measured on out/consp4/take-dn.wav (16 kHz, -50 dB RMS crossings, 10 ms windows; words from faster-whisper small on the x12 1x mix):
  "real." ends 126.68 s; a low bump (about -45 dB) starts 126.875 s; "We'll" starts 128.28 s; "conclusions." ends 129.84 s; a blip at 130.35 s.
  The old p13/p14 word table (energy bounds 127.69 / 131.07) was 1.2-1.6 s late, so the old close ran after the line and left a 3.2 s quiet tail.
Splice: p13 and p14 become one continuous piece of the take, joined with no fade at rising zero crossings:
  p13 125.45 s (sample 2007200) -> sample 2029812 (126.863250 s)  +  sample 2049601 (128.100063 s) -> sample 2084803 (130.300187 s)
  pause "real." -> "We'll" = 0.183 + 0.180 = 0.363 s at 1x = 0.303 s at 1.2x (was 1.9 s / 1.58 s). 20 ms fades on the outer edges only.
Output (1x, global): the piece starts 67.26; "We'll" 68.853; "conclusions." ends 70.413 (58.678 s at 1.2x); total 70.92 (1773 frames at 1.2x)."""
import json, os, sys
d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'data')
SR = 16000
A0, A1, B0, B1 = 2007200, 2029812, 2049601, 2084803      # source samples: p13 in/out, p14 in/out
OUT0 = 67.26; TOTAL = 70.92
la, lb = (A1 - A0) / SR, (B1 - B0) / SR
p14_in = round(OUT0 + la, 6); off14 = p14_in - B0 / SR      # output = source + off14 for p14
r = lambda x: round(x, 3)
e = json.load(open(f'{d}/conspiracy-edl.json'))
edl = [x for x in e['edl'] if x['id'] not in ('p13', 'p14')]
edl.append({'id': 'p13', 'src_in': A0 / SR, 'src_out': A1 / SR, 'out_in': OUT0, 'out_out': r(p14_in), 'speech': [r(OUT0 + 125.60 - 125.45), r(OUT0 + 126.68 - 125.45)], 'join_next': True})
edl.append({'id': 'p14', 'src_in': B0 / SR, 'src_out': B1 / SR, 'out_in': r(p14_in), 'out_out': r(p14_in + lb), 'speech': [r(128.28 + off14), r(129.84 + off14)]})
w = e['words']
w['p13'] = [['The', 67.41, 67.5], ['silence', 67.5, 67.8], ['is', 67.8, 68.08], ['real.', 68.08, 68.49]]
# x12 1x mix whisper times shifted by the splice (x12 p14 output = source - 57.92; now source + off14); onset/end from the energy bounds
sh = off14 + 57.92
ws = [["We'll", 70.36, 70.48], ['let', 70.48, 70.60], ['you', 70.60, 70.68], ['draw', 70.68, 70.88], ['your', 70.88, 71.02], ['own', 71.02, 71.16], ['conclusions.', 71.16, 71.92]]
w['p14'] = [[t, r(a + sh), r(b + sh)] for t, a, b in ws]
e.update(edl=edl, words=w, total=TOTAL)
json.dump(e, open(f'{d}/conspiracy-edl.json', 'w'), indent=1)
open(f'{d}/conspiracy-timing.js', 'w').write('window.CONSP = ' + json.dumps({'edl': edl, 'words': w, 'total': TOTAL, 's1End': e['s1_end']}) + ';\n')
# audio filter: keep the t1..p12 chains, replace p13 + p14 with one joined chain, rebuild base + amix at the new total
lines = [l.rstrip(';\n') for l in open(f'{d}/conspiracy-audio.filter') if l.strip()]
keep = [l for l in lines if l.startswith('[0:a]') and not l.endswith(('[a16]', '[a17]'))]
assert len(keep) == 16, len(keep)
n = len(keep)
ln = la + lb
keep.append(f"[0:a]atrim=start_sample={A0}:end_sample={A1},asetpts=PTS-STARTPTS[j0];[0:a]atrim=start_sample={B0}:end_sample={B1},asetpts=PTS-STARTPTS[j1];"
            f"[j0][j1]concat=n=2:v=0:a=1,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={ln - 0.02:.4f}:d=0.02,adelay={round(OUT0 * 1000)}|{round(OUT0 * 1000)}[a{n}]")
keep.append(f"anullsrc=r=48000:cl=mono,atrim=0:{TOTAL},asetpts=PTS-STARTPTS[base]")
keep.append('[base]' + ''.join(f'[a{i}]' for i in range(n + 1)) + f"amix=inputs={n + 2}:normalize=0:duration=longest,pan=mono|c0=c0,apad=whole_dur={TOTAL},atrim=0:{TOTAL},asetpts=PTS-STARTPTS[mix]")
open(f'{d}/conspiracy-audio.filter', 'w').write(';\n'.join(keep) + '\n')
print('p14 out_in', p14_in, 'off14', round(off14, 6), "We'll", w['p14'][0], 'end', w['p14'][-1], 'total', TOTAL)
