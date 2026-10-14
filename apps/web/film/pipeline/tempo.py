#!/usr/bin/env python3
"""Tempo curve for the advisory voice-over.
Input : data/s00b-words-1x.json (word times of the 1x render)
Output: data/s00b-tempo.cmd (asendcmd file, times in 1x input time)
        data/s00b-words-out.json (word times mapped through the curve, i.e. in the stretched audio)
Curve : 1.1x at 'Warning', linear ramp to 2.0x by the end of 'hypothetical scenarios',
        back to 1.0x exactly at 'Viewer'. Integration of dt/tempo gives the output clock."""
import json, sys
words = json.load(open('data/s00b-words-1x.json'))
t_start = words[0]['s']
t_viewer = next(w for w in words if w['w'].lower().startswith('viewer'))['s']
t_peak = t_viewer - 0.45          # reach 2.0x here, hold, then drop to 1.0x at t_viewer
LEAD_IN = 0.8                      # seconds of silence before the VO in the scene clock

def tempo(t):
    if t < t_start: return 1.1
    if t < t_peak: return 1.1 + 0.9 * (t - t_start) / (t_peak - t_start)
    if t < t_viewer: return 2.0 - 1.0 * (t - t_peak) / (t_viewer - t_peak)
    return 1.0

STEP = 0.02
T = words[-1]['e'] + 1.0
cmds, acc, out_of = [], 0.0, {}
n = int(T / STEP) + 1
lut = []
for i in range(n):
    t = i * STEP
    lut.append(acc)
    cmds.append(f"{t:.3f} rubberband@rb tempo {tempo(t):.4f};")
    acc += STEP / tempo(t)
def out_t(t):
    i = min(int(t / STEP), n - 1); f = (t - i * STEP)
    return lut[i] + f / tempo(i * STEP)
open('data/s00b-tempo.cmd', 'w').write('\n'.join(cmds) + '\n')
res = [{'w': w['w'], 's': round(out_t(w['s']) + LEAD_IN, 3), 'e': round(out_t(w['e']) + LEAD_IN, 3)} for w in words]
json.dump({'leadIn': LEAD_IN, 'words': res, 'dur': round(out_t(T), 3)}, open('data/s00b-words-out.json', 'w'), indent=1)
print(json.dumps(res)[:2000]); print('end', res[-1]['e'])
# the scene reads the timings from a plain script so it works from file:// without fetch()
open('data/s00b-words-out.js', 'w').write('window.VO = ' + json.dumps({'leadIn': LEAD_IN, 'words': res, 'dur': round(out_t(T), 3)}) + ';\n')
