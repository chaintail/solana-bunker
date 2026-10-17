#!/usr/bin/env python3
"""Runs ON dev-mac with ~/speech-lab/.venv/bin/python3 (numpy, soundfile, scipy). Opening v10 check: is "Chaintail Labs" in the final mix the 1.0 render's,
at the same length? The 1.0 render's segment from 10 ms before "Chaintail" to its end is located in the mix by cross-correlation (0-4.3 s), and the
"Chaintail" onset and the end of "Labs" are measured in both, high-passed at 300 Hz (the bed is brown noise low-passed at 220 Hz), as the first and last
10 ms RMS window above -45 dBFS. usage: sponsor-check-v10.py <mix48.wav> <vo-final.wav> <cut_1x_s>"""
import sys, numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt, correlate
MIX, ONE, CUT = sys.argv[1], sys.argv[2], float(sys.argv[3])
m, sr = sf.read(MIX); x, sr1 = sf.read(ONE); assert sr == sr1 == 48000
m = m[:int(4.3 * sr)]; seg = x[int(CUT * sr):]
hp = butter(4, 300, 'hp', fs=sr, output='sos'); mh, sh = sosfiltfilt(hp, m), sosfiltfilt(hp, seg)
c = correlate(mh, sh, mode='valid'); k = int(np.argmax(c))
win = mh[k:k + len(sh)]; r = float(np.dot(win, sh) / np.sqrt(np.dot(win, win) * np.dot(sh, sh)))
def span(y):
    w = int(0.01 * sr); e = np.array([20 * np.log10(np.sqrt(np.mean(y[i:i + w] ** 2)) + 1e-12) for i in range(0, len(y) - w, w // 10)])
    on = np.nonzero(e > -45)[0]; return on[0] * (w // 10) / sr, (on[-1] * (w // 10) + w) / sr
s1, e1 = span(sh); s2, e2 = span(mh[k:k + len(sh)])
print(f'segment found in the mix at {k / sr:.4f} s (expected join 2.7415), normalised correlation {r:.4f}')
print(f'1.0 render: Chaintail onset {CUT + s1:.4f} s, Labs end {CUT + e1:.4f} s, "Chaintail Labs" {e1 - s1:.4f} s')
print(f'mix       : Chaintail onset {k / sr + s2:.4f} s, Labs end {k / sr + e2:.4f} s, "Chaintail Labs" {e2 - s2:.4f} s; difference {(e2 - s2) - (e1 - s1) :+.4f} s')
