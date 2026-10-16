#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s06. Slide 6 edit list (film-plan-s06.md section 1) -> out/s06-edl.json, film/data/s06-edl.js, out/s06-audio.filter.
Needs out/take-dn.wav (build.sh step 1). The L1a/L1b cut ("things" | "start") has no silence in the take (plan R1). A band-energy scan (10 ms frames) shows "things" voicing to 339.12,
one shared sibilant 339.13-339.20 (the -s of "things" run into the s- of "start"), the t closure at 339.21 and the vowel from 339.24. The quietest point
(339.21) would leave "tart"; so the cut splits the shared sibilant in the middle (339.165 s), snapped to the nearest zero crossing: both words keep an s."""
import json, subprocess, numpy as np
SR = 48000
pcm = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', 'out/take-dn.wav', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout
x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32)
m = int(339.165 * SR)
zc = np.nonzero(np.diff(np.signbit(x[m - 960:m + 960])))[0] + (m - 960)
cut = float(zc[np.argmin(abs(zc - m))] / SR) if len(zc) else m / SR
print('L1a/L1b cut at %.4f s' % cut)
lines = [  # id, text, src_in, src_out, out_in (None = right after the previous line + gap)
    ('L1a', 'Alright, so this is where things', 337.70, cut, 0.30),
    ('L1b', 'start to get cool.', cut, 339.95, None),  # v7: no inserted gap (FREEZE = 0), the line plays continuously as recorded
    ('L2', 'The problem with version one and version two is that a secret is just a password.', 340.22, 343.75, 2.80),
    ('L3', 'Whoever shows the password first gets in the vault.', 343.95, 346.20, 7.00),
    ('L4', 'But a password says nothing about where the money should go.', 346.58, 349.58, 9.50),
    ('L5', 'So if someone steals it on the way to the vault, they can get in first.', 349.80, 353.02, 12.70),
    ('L6', 'What we actually want is a signature.', 353.42, 355.08, 16.40),
    # v3 (Liam): the line is split at the pause after "address" (silence 359.43-359.55); our form is signed and goes through the slot in the gap,
    # the speech pauses (about 0.8 s of bed on the shut door), then "and nothing else" plays over the devil's attempt and the slot slams on "else".
    ('L7a', 'Something that says this exact withdrawal, to this exact address,', 355.28, 359.49, 18.70),
    ('L7b', 'and nothing else.', 359.49, 360.70, 26.15),  # "else" ends 360.56 (silence to 361.02, then a lip click at 361.04)
]
TOTAL, FREEZE = 29.50, 0.0   # v7: the 0.5 s "*the math*" gap is removed, everything after it is 0.5 s earlier
edl = []
for i, (id_, text, si, so, oi) in enumerate(lines):
    if oi is None: oi = round(edl[-1]['out_out'] + FREEZE, 3)
    d = so - si
    edl.append({'id': id_, 'text': text, 'src_in': round(si, 4), 'src_out': round(so, 4), 'out_in': oi, 'out_out': round(oi + d, 4), 'frames': int(round(d * 30))})
for i in range(1, len(edl)): assert edl[i]['out_in'] >= edl[i - 1]['out_out'] - 1e-6, edl[i]['id']
l7b = edl[-1]
# SFX marker for Liam's slam sound (not in the mix): the slot shutter hits the devil's fingers at the end of "else" (take 360.56 s)
markers = [{'id': 'SFX_SLOT_SLAM', 't': round(l7b['out_in'] + 360.56 - l7b['src_in'], 3), 'note': 'slot shutter slams on the devil fingers; Liam supplies the sound, put its transient here'}]
doc = {'total': TOTAL, 'fps': 30, 'freeze': [edl[0]['out_out'], edl[1]['out_in']], 'edl': edl, 'markers': markers}
json.dump(doc, open('out/s06-edl.json', 'w'), indent=1)
open('film/data/s06-edl.js', 'w').write('window.S06 = ' + json.dumps(doc) + ';\n')
f = []
segs = []  # audio segments: contiguous EDL rows (src_out == next src_in and out_out == next out_in) are one cut, so no fade pair at the join
for e in edl:
    if segs and abs(segs[-1]['src_out'] - e['src_in']) < 1e-6 and abs(segs[-1]['out_out'] - e['out_in']) < 1e-6:
        segs[-1]['src_out'], segs[-1]['out_out'] = e['src_out'], e['out_out']
    else: segs.append(dict(e))
for i, e in enumerate(segs):
    d = e['src_out'] - e['src_in']; ms = int(round(e['out_in'] * 1000))
    f.append(f"[0:a]atrim=start={e['src_in']}:end={e['src_out']},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={d - 0.02:.4f}:d=0.02,adelay={ms}|{ms}[a{i}];")
f.append(f"anullsrc=r=48000:cl=mono,atrim=0:{TOTAL},asetpts=PTS-STARTPTS[base];")
f.append('[base]' + ''.join(f'[a{i}]' for i in range(len(segs))) + f"amix=inputs={len(segs) + 1}:normalize=0:duration=longest,pan=mono|c0=c0,apad=whole_dur={TOTAL},atrim=0:{TOTAL},asetpts=PTS-STARTPTS[mix]")
open('out/s06-audio.filter', 'w').write('\n'.join(f) + '\n')
for e in edl: print(e['id'], e['src_in'], e['src_out'], '->', e['out_in'], e['out_out'], e['frames'])
for m in markers: print('marker', m['id'], m['t'])
