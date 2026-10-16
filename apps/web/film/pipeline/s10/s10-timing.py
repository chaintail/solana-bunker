#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s10 (system python). Scene 10 edit list (film-plan-ending.md section 2) -> out/s10-edl.json,
film/data/s10-edl.js (window.S10: edl, beat times T), out/s10-audio.filter.
Two segments of the denoised take: B1 533.75-545.10 at scene 2.00 and B2 563.55-583.50 at 13.35 (the two false starts, 545.10-563.55, are cut).
In/out points sit in the pauses of silencedetect (n=-38dB, d=0.12) on the denoised take. Word times are take times rechecked on a 20 ms energy
envelope (full band plus a >3 kHz share for the fricatives); several moved from the plan's token+offset estimates: white 543.30 (was 543.70),
nerd 538.64 (538.78), stateless 565.68 (566.09), bigger 571.12 (571.36), never 571.94 (572.00), bunker 580.22 / 581.02, cook 582.44 (582.63).
The anchor footage runs on the same clock as the audio (matte-full-*.mp4 = take time), from 531.75 s so that scene t = take - 531.75 in B1."""
import json
FPS = 30
SEG = [(533.75, 545.10, 2.00), (563.55, 583.50, 13.35)]      # take in, take out, scene in
TOTAL = 33.40
OFF = [si - a for a, b, si in SEG]                          # scene = take + OFF
def S(src):
    for (a, b, si), o in zip(SEG, OFF):
        if a - .05 <= src <= b + .05: return round(src + o, 3)
    raise ValueError(src)
edl = [{'id': f'B{i + 1}', 'src_in': a, 'src_out': b, 'out_in': si, 'out_out': round(si + b - a, 3)} for i, (a, b, si) in enumerate(SEG)]
assert abs(edl[0]['out_out'] - edl[1]['out_in']) < 1e-6
T = {'wipe_in': 0.0, 'cover': .55, 'out_start': 1.10, 'out_end': 2.00, 'l3_in': 1.60,
     'thanks': S(533.98), 'crypto': S(538.32), 'nerd': S(538.64), 'us_end': S(539.44), 'told': S(540.52), 'white': S(543.30), 'go': S(543.92), 'go_end': S(544.72),
     'cut': SEG[1][2], 'the': S(563.77), 'stateless': S(565.68), 'slh': S(568.64), 'dsa': S(569.32), 'sigs': S(570.40), 'bigger': S(571.12), 'never': S(571.94),
     'track': S(572.24), 'spent_end': S(573.47), 'favorite': S(574.04), 'bunker': S(580.22), 'protecting': S(580.54), 'bunker2': S(581.02), 'bunker_end': S(581.37),
     'lots': S(581.99), 'cook': S(582.44), 'lab': S(582.88), 'end': S(583.22), 'total': TOTAL}
T.update({'graphy': round(T['nerd'] + .30, 3), 'ots_out': round(T['cook'] - .25, 3)})
T['graphy_end'] = round(T['graphy'] + .35, 3)
assert T['graphy_end'] < T['us_end'], 'GRAPHY must finish before "us" ends'
doc = {'total': TOTAL, 'fps': FPS, 'edl': edl, 'T': T, 'footage_src0': round(SEG[0][0] - SEG[0][2], 3)}   # v4: no punch-in at the cut (Liam): the head keeps one size
json.dump(doc, open('out/s10-edl.json', 'w'), indent=1)
open('film/data/s10-edl.js', 'w').write('window.S10 = ' + json.dumps(doc) + ';\n')
f = []
for i, (a, b, si) in enumerate(SEG):
    d = b - a; ms = int(round(si * 1000))
    f.append(f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={d - 0.02:.4f}:d=0.02,adelay={ms}|{ms}[a{i}];")
f.append(f"anullsrc=r=48000:cl=mono,atrim=0:{TOTAL},asetpts=PTS-STARTPTS[base];")
f.append(f"[base][a0][a1]amix=inputs=3:normalize=0:duration=longest,pan=mono|c0=c0,apad=whole_dur={TOTAL},atrim=0:{TOTAL},asetpts=PTS-STARTPTS[mix]")
open('out/s10-audio.filter', 'w').write('\n'.join(f) + '\n')
for e in edl: print(e)
print('total', TOTAL, 'frames', round(TOTAL * FPS)); print(T)
