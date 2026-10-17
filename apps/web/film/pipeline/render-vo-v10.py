#!/usr/bin/env python3
"""Runs ON dev-mac with ~/speech-lab/.venv/bin/python3 (numpy, soundfile). Opening v10 (Liam, voice 2026-10-17): the sponsor read with "Chaintail Labs" back
at 1.0x. Everything through "by" stays at 1.2x as in v9, "Chaintail Labs" and the end tail are the original 1.0 render, unchanged.
 inputs : out/s00a-v5/vo-final.wav (the 1.0 Studio render, 48 kHz mono) and opening-v9/out/vo/sponsor-vo.wav (v9: the same render at atempo 1.2)
 join   : the silence between "by" and "Chaintail" is digital near-silence (about -88 dBFS) in both files. The "Chaintail" onset is the first sample after
          the by/Chaintail silence with |x| above -50 dBFS. Both files are cut MARGIN (10 ms) before their own onset, moved to the nearest zero crossing, and
          joined with no crossfade. The silence before "Chaintail" is therefore v9's (the 1.0 gap scaled by 1/1.2), with no added pause.
usage: render-vo-v10.py <vo-final.wav> <v9-sponsor-vo.wav> <out.wav>   -> prints the join, the "Chaintail Labs" span in both files and the new length"""
import sys, numpy as np, soundfile as sf
ONE, V9, OUT = sys.argv[1:4]
MARGIN, THR = 0.010, 10 ** (-50 / 20)
x1, sr = sf.read(ONE, dtype='float64'); x9, sr9 = sf.read(V9, dtype='float64'); assert sr == sr9 == 48000 and x1.ndim == x9.ndim == 1
def onset(x, t_silent):                         # first sample above THR after a point inside the by/Chaintail silence
    i = int(t_silent * sr); assert np.max(np.abs(x[i:i + int(0.05 * sr)])) < THR, 'search start is not silent'
    return i + int(np.argmax(np.abs(x[i:]) > THR))
def zc(x, i):                                   # nearest sign change to i (search +-2 ms)
    r = int(0.002 * sr); seg = np.signbit(x[i - r:i + r]); k = np.nonzero(seg[1:] != seg[:-1])[0]
    return i if len(k) == 0 else i - r + 1 + int(k[np.argmin(np.abs(k + 1 - r))])
o1 = onset(x1, 3.0); o9 = onset(x9, 2.5)           # silence: 2.76-3.29 s in the 1.0 render; 2.30-2.74 s in v9's 1.2x
c1 = zc(x1, o1 - int(MARGIN * sr)); c9 = zc(x9, o9 - int(MARGIN * sr))
assert max(abs(x1[c1]), abs(x9[c9]), np.max(np.abs(x1[c1 - 480:c1 + 1])), np.max(np.abs(x9[c9 - 480:c9 + 1]))) < THR
y = np.concatenate([x9[:c9], x1[c1:]])
sf.write(OUT, y, sr, subtype='PCM_16')
by_end9 = c9 - int(np.argmax(np.abs(x9[:c9][::-1]) > THR))
print(f'1.0 render: Chaintail onset {o1 / sr:.4f} s, cut {c1 / sr:.4f} s, file {len(x1) / sr:.4f} s ("Chaintail Labs" + tail = {(len(x1) - c1) / sr:.4f} s at 1.0)')
print(f'v9 1.2x   : "by" decays below -50 dBFS at {by_end9 / sr:.4f} s, Chaintail onset {o9 / sr:.4f} s, cut {c9 / sr:.4f} s, file {len(x9) / sr:.4f} s')
print(f'v10       : join at {c9 / sr:.4f} s, Chaintail onset {(c9 + o1 - c1) / sr:.4f} s, silence before it {(c9 + o1 - c1 - by_end9) / sr:.4f} s, '
      f'length {len(y) / sr:.4f} s (v9 {len(x9) / sr:.4f}, +{(len(y) - len(x9)) / sr:.4f} s)')
