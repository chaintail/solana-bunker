#!/usr/bin/env python3
"""Runs ON dev-mac with ~/speech-lab/.venv/bin/python3 (numpy, scipy, soundfile). Opening v11 music stem (music-plan.md, Opening, Levels, Transition rules),
mono 48 kHz, full film length, sample-accurate envelopes.
 Cues are folded to mono (0.5 L + 0.5 R, as the jingles) and high-passed at 180 Hz (2-pole Butterworth, as ffmpeg highpass). Each cue is first brought to
 -16 LUFS over the span it plays (ref gain from the caller, measured with ffmpeg ebur128 on the folded, high-passed span), so a plan level of -20 dB puts the
 music 20 LU under the voices (sponsor -15.9, desk -16.1 LUFS).
 Cut points are the measured attacks (onsets-fine.py, flux backtrack), not analysis.json's beat times, which run 29-46 ms late:
  groove  suno-1-reassuring-groove-a: bar 3 downbeat attack 5.312 s (analysis 5.341) on the WARNING card cut. Two bars (4.60 s) do not fit between the read
          (0.330 s) and the cut (4.300 s), so the groove enters on beat 2 of bar 1 (attack 1.278 s, analysis 1.324), the beat nearest before the read.
  news    suno-2-breaking-news-a: bar 18 downbeat attack 34.697 s (analysis 34.737) on the SPECIAL REPORT slam; bar 1 (attack 0.117 s, analysis 0.139) then
          lands 34.58 s earlier, under jingle A, just before the desk entry.
 Each cue starts 5 ms before its entry attack (5 ms raised-cosine fade-in) and ends with a 0.5 s raised-cosine tail from its last downbeat (downbeat end).
 Levels: groove -20 throughout. News -20 under speech; in every gap of 0.8 s or more in the voice (10 ms RMS above -45 dBFS) it rises to -14 over 300 ms from
 the end of the speech and is back at -20 20 ms before the next word (100 ms ramp); dip to -26 from 1 s before the slam (100 ms ramp).
 Dialogue guard: in every 100 ms and every 200 ms window (10 ms hop; the brief's windows and the arcade score-check's) where the voice stem is at or above
 GUARD_THR dBFS (pre-loudnorm scale, 1.5 dB below the check's -30 to cover the final gain), the music is held at least GUARD_DB (17) under the voice: the
 needed reduction is applied over the window with a 100 ms attack before it (look-ahead) and a 300 ms release after it.
usage: music-v11.py <voice.wav> <groove.wav> <news.wav> <outdir> total card_cut slam groove_ref_db news_ref_db
  -> <outdir>/music.wav (float32) and music-env.npz (10 ms grid: plan gain, guard reduction, gaps)"""
import sys, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
V, GW, NW, D = sys.argv[1:5]; total, cut, slam, gref, nref = map(float, sys.argv[5:10])
SR = 48000; N = int(round(total * SR)); tt = np.arange(N) / SR
G_IN, G_END, N_IN, N_END = 1.278, 5.312, 0.117, 34.697
PRE, TAIL, GUARD_THR, GUARD_DB = 0.005, 0.5, -31.5, 17.0
db = lambda x: 10 ** (x / 20)
hp = butter(2, 180, 'hp', fs=SR, output='sos')
def cue(path, a_in, a_end, at_scene):                 # place track [a_in - PRE, a_end + TAIL] so that a_end lands at at_scene
    y, sr = sf.read(path, dtype='float64'); assert sr == SR; y = sosfilt(hp, y.mean(1))
    off = at_scene - a_end; i0 = int(round((a_in - PRE) * SR)); i1 = int(round((a_end + TAIL) * SR)); s0 = int(round((a_in - PRE + off) * SR))
    assert s0 >= 0 and s0 + (i1 - i0) <= N; out = np.zeros(N); out[s0:s0 + i1 - i0] = y[i0:i1]
    t_in = a_in + off; fin = np.clip((tt - (t_in - PRE)) / PRE, 0, 1); fout = np.clip((tt - at_scene) / TAIL, 0, 1)
    env = (0.5 - 0.5 * np.cos(np.pi * fin)) * (0.5 + 0.5 * np.cos(np.pi * fout)) * ((tt >= t_in - PRE) & (tt <= at_scene + TAIL))
    return out * env, off, t_in
g, g_off, g_t = cue(GW, G_IN, G_END, cut); n, n_off, n_t = cue(NW, N_IN, N_END, slam)
print(f'groove: scene = track {g_off:+.4f}; in {g_t - PRE:.4f} (beat 2 of bar 1, attack at {g_t:.4f}), '
      f'bar 3 downbeat at {cut:.4f} (card cut), tail to {cut + TAIL:.4f}; ref gain {gref:+.2f} dB')
print(f'news  : scene = track {n_off:+.4f}; in {n_t - PRE:.4f} (bar 1 attack at {n_t:.4f}), bar 18 downbeat at {slam:.4f} (SPECIAL REPORT slam), '
      f'tail to {slam + TAIL:.4f}; ref gain {nref:+.2f} dB')
v, sr = sf.read(V, dtype='float64'); assert sr == SR and len(v) >= N; v = v[:N]
# speech gaps in the news span (10 ms RMS above -45 dBFS)
w10 = SR // 100; e = 20 * np.log10(np.sqrt(np.mean(v[:N // w10 * w10].reshape(-1, w10) ** 2, 1)) + 1e-12); act = e > -45
on = np.nonzero(act)[0]; segs = []
for k in on:
    if segs and k - segs[-1][1] <= 1: segs[-1][1] = k
    else: segs.append([k, k])
segs = [(a * 0.01, (b + 1) * 0.01) for a, b in segs]
gaps = [(segs[i][1], segs[i + 1][0]) for i in range(len(segs) - 1) if segs[i + 1][0] - segs[i][1] >= 0.8 and segs[i][1] > n_t and segs[i + 1][0] < slam]
gplan = np.full(N, -20.0)
for a, b in gaps:
    gplan += 6 * np.clip((tt - a) / 0.3, 0, 1) * np.clip((b - 0.02 - tt) / 0.1, 0, 1) * (tt > n_t)
    print(f'  gap {a:.2f}-{b:.2f} ({b - a:.2f} s): -14 from {a + 0.3:.2f} to {b - 0.12:.2f}')
gplan = np.where(tt > n_t, np.minimum(gplan, -20 - 6 * np.clip((tt - (slam - 1.0)) / 0.1, 0, 1)), gplan)
mplan = g * db(gref) * db(gplan) + n * db(nref) * db(gplan)
# dialogue guard: required extra reduction per 100 ms window (10 ms hop), spread over the window's 10 ms slots, then 100 ms attack / 300 ms release ramps
cs = lambda x: np.concatenate([[0], np.cumsum(np.add.reduceat(x ** 2, np.arange(0, N, w10)))])
cv, cm = cs(v), cs(mplan); S = len(cv) - 1
wdb = lambda c, W: 10 * np.log10((c[W:] - c[:-W]) / (W * w10) + 1e-24)
slot = np.zeros(S); nwin = nvoiced = 0
for W in (10, 20):
    vw, mw = wdb(cv, W), wdb(cm, W); need = np.where(vw >= GUARD_THR, np.maximum(0, mw - (vw - GUARD_DB)), 0)
    nwin += int((need > 0).sum()); nvoiced += int((vw >= GUARD_THR).sum())
    for k in np.nonzero(need > 0)[0]: slot[k:k + W] = np.maximum(slot[k:k + W], need[k])
red = np.zeros(S); A, R = 10, 30                       # 10 ms slots: 100 ms attack, 300 ms release
for k in np.nonzero(slot > 0)[0]:
    lo, hi = max(0, k - A), min(S, k + R + 1); j = np.arange(lo, hi)
    ramp = np.where(j < k, 1 - (k - j) / A, np.where(j > k, 1 - (j - k) / R, 1))
    red[lo:hi] = np.maximum(red[lo:hi], slot[k] * np.clip(ramp, 0, 1))
redS = np.repeat(red, w10)[:N]
m = mplan * db(-redS)
sf.write(f'{D}/music.wav', m.astype(np.float32), SR, subtype='FLOAT')
np.savez(f'{D}/music-env.npz', plan=gplan[::w10], red=red, gaps=np.array(gaps))
ducked = slot > 0
print(f'guard: {nwin} of {nvoiced} voiced 100/200 ms windows needed extra reduction; {ducked.sum() * 0.01:.2f} s of slots ducked, '
      f'max {slot.max():.1f} dB, median of ducked slots {np.median(slot[ducked]) if ducked.any() else 0:.1f} dB')
c2 = cs(m)
for W in (10, 20):
    vw, mw2 = wdb(cv, W), wdb(c2, W); a = (vw >= GUARD_THR) & (mw2 > -120)
    print(f'guard after duck, {W * 10} ms windows (pre-loudnorm, voice >= {GUARD_THR} dBFS): min margin {np.min((vw - mw2)[a]):.1f} dB')
