#!/usr/bin/env python3
"""Runs ON dev-mac with ~/speech-lab/.venv/bin/python3 (numpy, soundfile). Opening v10 jingle stems (jingles-v9.py with two changes to A), mono 48 kHz, full
film length, sample-accurate envelopes.
 A  news-open-1-mini-jingle (mastered wav): v9 put its first big hit (measured attack 0.660 s into the file) on the ident's BREAKING NEWS landing. v10
    (Liam 2026-10-17) starts it a_lead seconds (0.45) earlier than that. The mastered file is the pre-master times 0.3802 with a 2 ms fade-in; v10 replaces
    its first 3 ms with the pre-master samples times the same gain, so there is no fade-in and the first onset (8 ms into the file) is at full level.
    Runs under the desk entry; at Liam's first word: duck -12 dB with a 100 ms attack (linear in dB) and a linear fade to silence over 1.0 s from the same
    instant.
 C  news-open-3-da-da-da-daaa (mastered wav), replacing x11's horn stabs: its last hit (the "daaa" attack, measured 0.467 s into the file) on the SPECIAL
    REPORT card's slam frame; gain from the caller (matched to the horn's event loudness in x11); never shortened: it rings on under "A special report."
    (ducked by duck_c dB over the voiced span, 100 ms ramps, when duck_c > 0) and to the end of the scene, where it fades with the bed (last 0.6 s).
Both are folded to mono like x11's horn (0.5 L + 0.5 R).
usage: jingles-v10.py <A.wav> <C.wav> <outdir> total a_hit a_gain_db liam_first_word c_hit c_gain_db ann.wav ann_at ann_gain_db duck_c_db a_lead <A.pre.wav>
  -> <outdir>/jingle-a.wav, jingle-c.wav and a voice-over-jingle margin table for the announcer"""
import sys, numpy as np, soundfile as sf
from scipy.signal import resample_poly
A, C, D = sys.argv[1:4]
total, a_hit, a_gain, t_word, c_hit, c_gain = map(float, sys.argv[4:10]); ANN = sys.argv[10]; ann_at, ann_gain, duck_c, a_lead = map(float, sys.argv[11:15]); APRE = sys.argv[15]
SR = 48000; N = int(round(total * SR)); A_HIT, C_HIT = 0.660, 0.467
db = lambda x: 10 ** (x / 20)
def mono(p):
    y, sr = sf.read(p, dtype='float64'); y = y.mean(1) if y.ndim > 1 else y
    return y if sr == SR else resample_poly(y, SR, sr)          # the announcer file is 24 kHz (margin table only; the mix resamples it in ffmpeg)
def place(y, t0):
    out = np.zeros(N); i = int(round(t0 * SR)); j = min(N, i + len(y)); assert i >= 0
    out[i:j] = y[:j - i]; return out
tt = np.arange(N) / SR
# --- A
am, ap = mono(A), mono(APRE); k = slice(int(0.01 * SR), int(3.0 * SR)); g = float(np.median(am[k][np.abs(ap[k]) > 1e-4] / ap[k][np.abs(ap[k]) > 1e-4]))
assert np.allclose(am[k], ap[k] * g, atol=1e-4), 'master is not a pure gain of the pre-master'
n3 = int(0.003 * SR); am[:n3] = ap[:n3] * g                  # undo the 2 ms fade-in
print(f'A: master = pre-master x {g:.4f}; first 3 ms replaced (fade-in removed): peak in the first 2 ms {np.max(np.abs(mono(A)[:96])):.5f} -> {np.max(np.abs(am[:96])):.5f}')
a_start = a_hit - A_HIT - a_lead
a = place(am * db(a_gain), a_start)
duck = np.where(tt < t_word, 0.0, np.clip((tt - t_word) / 0.1, 0, 1) * -12.0)
fade = np.clip(1 - (tt - t_word) / 1.0, 0, 1)
a *= db(duck) * fade
sf.write(f'{D}/jingle-a.wav', a, SR, subtype='PCM_24')
print(f'A: starts {a_start:.4f} s ({a_lead} s before v9 placement), first onset {a_start + 0.008:.4f}, hit {a_start + A_HIT:.4f} (slam {a_hit:.4f}), gain {a_gain} dB, duck -12 dB from {t_word:.4f} (100 ms), silent from {t_word + 1:.4f}')
# --- C
c0 = place(mono(C), c_hit - C_HIT) * db(c_gain)
ann = place(mono(ANN) * db(ann_gain), ann_at)
env = np.zeros(N)
if duck_c > 0:
    w = 4800; act = np.array([np.sqrt(np.mean(ann[k:k + w] ** 2)) > db(-45) for k in range(0, N, w)])
    ks = np.nonzero(act)[0]; v0, v1 = ks[0] * w / SR - 0.05, (ks[-1] + 1) * w / SR + 0.05     # the voiced span, 50 ms margins
    env = -duck_c * np.clip(np.minimum((tt - (v0 - 0.1)) / 0.1, ((v1 + 0.1) - tt) / 0.1), 0, 1)
    print(f'C: ducked {duck_c} dB over the voiced span {v0:.3f}-{v1:.3f} s (100 ms ramps)')
c = c0 * db(env) * np.clip((total - tt) / 0.6, 0, 1)
sf.write(f'{D}/jingle-c.wav', c, SR, subtype='PCM_24')
print(f'C: starts {c_hit - C_HIT:.4f} s, last hit {c_hit:.4f}, gain {c_gain:.2f} dB, plays {total - (c_hit - C_HIT):.3f} s of its {len(mono(C)) / SR:.3f} s (scene end, faded with the bed over the last 0.6 s)')
# --- margin of "A special report." over C, 100 ms windows where the voice is active
w = 4800; rows = []
for k in range(int(ann_at * SR), min(N, int(ann_at * SR) + len(mono(ANN))), w):
    ra, rc = np.sqrt(np.mean(ann[k:k + w] ** 2)) + 1e-12, np.sqrt(np.mean(c[k:k + w] ** 2)) + 1e-12
    if 20 * np.log10(ra) > -45: rows.append((k / SR, 20 * np.log10(ra), 20 * np.log10(rc)))
for t, va, vc in rows: print(f'  {t:.2f}  voice {va:6.1f}  C {vc:6.1f}  margin {va - vc:5.1f} dB')
print(f'  min window margin {min(r[1] - r[2] for r in rows):.1f} dB')
