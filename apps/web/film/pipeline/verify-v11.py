#!/usr/bin/env python3
"""Runs ON dev-mac with ~/speech-lab/.venv/bin/python3 (numpy, soundfile, scipy). Opening v11 level checks on the final stems (pre-limiter, at the final gain).
 guard : the music stem against the voices (sponsor, advisory, desk, announcer) in 100 ms windows at a 10 ms hop, where the voice is active (>= -30 dBFS, the
         arcade score-check's threshold), and on the arcade check's own grid (200 ms windows, 50 ms hop). Reports the minimum margin and where it occurs.
 offset: the music stem's position in the decoded master by cross-correlation (the limiter's look-ahead delay).
 levels: music RMS while the voice is active, per cue span; writes <out.csv> with 100 ms RMS envelopes at a 50 ms hop (voice, music, stings, mix) for the plot.
usage: verify-v11.py <voice-final.wav> <music.wav> <stings.wav> <mix48.wav> <out.csv>"""
import sys, numpy as np, soundfile as sf
from scipy.signal import correlate
V, M, S, X, CSV = sys.argv[1:6]
rd = lambda p: sf.read(p, dtype='float64')[0]
v, m, s, x = rd(V), rd(M), rd(S), rd(X); SR = 48000; N = min(len(v), len(m), len(s), len(x)); v, m, s, x = v[:N], m[:N], s[:N], x[:N]
def env(y, win, hop):
    c = np.concatenate([[0], np.cumsum(y ** 2)]); st = np.arange(0, N - win + 1, hop)
    return st / SR, 10 * np.log10((c[st + win] - c[st]) / win + 1e-24)
for win, hop, name in [(4800, 480, '100 ms windows, 10 ms hop'), (9600, 2400, '200 ms windows, 50 ms hop (arcade grid)')]:
    t, vw = env(v, win, hop); _, mw = env(m, win, hop); a = (vw >= -30) & (mw > -120); mg = vw - mw
    k = np.argmin(np.where(a, mg, np.inf))
    print(f'guard, {name}: {int(((vw >= -30)).sum())} voiced windows, {int(a.sum())} with music; min margin {mg[k]:.1f} dB at {t[k]:.2f} s '
          f'(voice {vw[k]:.1f}, music {mw[k]:.1f}); median {np.median(mg[a]):.1f} dB; windows under 16 dB: {int((mg[a] < 16).sum())}')
for name, a0, a1 in [('groove (0.26-4.80)', 0.26, 4.80), ('news bed (17.85-52.93)', 17.85, 52.93)]:
    i0, i1 = int(a0 * SR), int(a1 * SR); t, vw = env(v[i0:i1] if False else v, 4800, 480); _, mw = env(m, 4800, 480)
    sel = (t >= a0) & (t <= a1 - 0.1); act = sel & (vw >= -30); qu = sel & (vw < -45)
    p = lambda e, k: 10 * np.log10(np.mean(10 ** (e[k] / 10))) if k.any() else float('nan')
    print(f'{name}: music RMS {p(mw, act):.1f} dBFS under voice (voice {p(vw, act):.1f}), {p(mw, qu):.1f} dBFS where the voice is silent')
k0, k1 = int(17.0 * SR), int(53.0 * SR); seg_x, seg_m = x[k0:k1], m[k0:k1]
c = correlate(seg_x, seg_m[2400:-2400], mode='valid'); lag = int(np.argmax(c)) - 2400
print(f'music stem offset in the master: {lag / SR * 1000:+.2f} ms (cross-correlation 17-53 s; positive = later in the master)')
t, vw = env(v, 4800, 2400); _, mw = env(m, 4800, 2400); _, sw = env(s, 4800, 2400); _, xw = env(x, 4800, 2400)
np.savetxt(CSV, np.c_[t + 0.05, vw, mw, sw, xw], delimiter=',', header='t,voice,music,stings,mix', comments='', fmt='%.3f')
