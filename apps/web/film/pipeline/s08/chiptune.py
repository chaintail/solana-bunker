#!/usr/bin/env python3
"""Scene 8 tag: 8-bit chiptune, synthesised from scratch (square / triangle / noise, simple envelopes, 44.1 kHz mono 16 bit; numpy only, no samples).
usage (dev-mac, system python): python3 film/pipeline/s08/chiptune.py [outdir=film/audio/s08]
  jingle.wav  ~2.1 s level-complete success: rising C major arpeggio, two square voices (50 % and 25 % duty) + triangle bass, held chord; peak -12 dBFS
  bed.wav     8 bars at 124 BPM (15.48 s, seamless loop): C  Am  F  G  C  Am  F  G, thin 12.5 % square lead, triangle bass, noise hat; RMS -30 dBFS
  coin.wav    1-up / coin blip (B5 -> E6 square); peak -18 dBFS
  tick.wav    soft score tick (30 ms square, fast decay); peak -18 dBFS
Every file has 20 ms fades at both ends. Levels are absolute: build.sh mixes the files after the speech loudnorm (they are not renormalised)."""
import sys, os, wave, numpy as np
SR = 44100
def hz(n): return 440.0 * 2 ** ((n - 69) / 12)          # midi note -> Hz
def osc(kind, f, n, duty=.5):
    ph = (np.arange(n) * f / SR) % 1.0
    if kind == 'sq': return np.where(ph < duty, 1.0, -1.0)
    if kind == 'tri': return np.round((4 * np.abs(ph - .5) - 1) * 15) / 15      # 4-bit triangle, like the real thing
    raise ValueError(kind)
def env(n, a=.004, d=.08, s=.6, r=.05, hold=None):
    """attack / decay-to-sustain / release envelope over n samples (release inside the note)"""
    t = np.arange(n) / SR; T = n / SR; e = np.minimum(1, t / a) * (s + (1 - s) * np.exp(-t / d)); rr = min(r, T)
    return e * np.clip((T - t) / rr, 0, 1)
def note(buf, t0, dur, midi, kind='sq', duty=.5, vol=1.0, **kw):
    i0 = int(round(t0 * SR)); n = int(round(dur * SR)); n = min(n, len(buf) - i0)
    if n <= 0: return
    buf[i0:i0 + n] += vol * osc(kind, hz(midi), n, duty) * env(n, **kw)
def fades(x, ms=20):
    k = int(SR * ms / 1000); x[:k] *= np.linspace(0, 1, k); x[-k:] *= np.linspace(1, 0, k); return x
def peak_to(x, dbfs): return x * (10 ** (dbfs / 20) / np.abs(x).max())
def rms_to(x, dbfs): return x * (10 ** (dbfs / 20) / np.sqrt((x ** 2).mean()))
def save(path, x):
    with wave.open(path, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())
    print('%-28s %.3f s  peak %.1f dBFS  rms %.1f dBFS' % (os.path.basename(path), len(x) / SR, 20 * np.log10(np.abs(x).max()), 20 * np.log10(np.sqrt((x ** 2).mean()))))
def noise_hat(buf, t0, dur=.035, vol=1.0, rng=None):
    i0 = int(round(t0 * SR)); n = int(dur * SR); n = min(n, len(buf) - i0)
    if n <= 0: return
    z = rng.choice([-1.0, 1.0], n); z = np.diff(np.concatenate([[0], z])) / 2          # differenced white noise = bright 1-bit hat
    buf[i0:i0 + n] += vol * z * np.exp(-np.arange(n) / (SR * .008))

def jingle():
    L = int(2.1 * SR); lead = np.zeros(L); harm = np.zeros(L); bass = np.zeros(L); st = .085
    arp = [72, 76, 79, 84, 79, 84, 88]                    # C5 E5 G5 C6 G5 C6 E6 (midi 72 = C5)
    for i, m in enumerate(arp):
        note(lead, i * st, st * .95, m, 'sq', .5, 1, a=.002, d=.1, s=.8, r=.01)                  # voice 1: 50 % square
        note(harm, i * st + st / 2, st * .95, m - 5, 'sq', .25, .7, a=.002, d=.1, s=.8, r=.01)    # voice 2: 25 % square, a fourth below, half a step late
        note(bass, i * st, st, [36, 40, 43, 48, 43, 48, 52][i], 'tri', 1, a=.002, d=1, s=1, r=.01)   # triangle bass follows the arpeggio two octaves down
    t = len(arp) * st                                       # the held chord: E6 + C6 over C3
    note(lead, t, 1.35, 88, 'sq', .5, 1, a=.002, d=.5, s=.35, r=.35)
    note(harm, t, 1.35, 84, 'sq', .25, .8, a=.002, d=.5, s=.35, r=.35)
    note(bass, t, 1.4, 48, 'tri', 1, a=.002, d=.8, s=.7, r=.4)
    return peak_to(fades(lead * .5 + harm * .38 + bass * .6), -12)
def bed():
    BPM = 124; beat = 60 / BPM; bar = 4 * beat; N = int(round(8 * bar * SR)); b = np.zeros(N); lead = np.zeros(N); h = np.zeros(N); rng = np.random.default_rng(8)
    chords = [(48, [60, 64, 67]), (45, [57, 60, 64]), (41, [57, 60, 65]), (43, [55, 59, 62])] * 2          # C Am F G (root midi for bass, triad for the lead arpeggio)
    mel = [0, 1, 2, 1, 0, 1, 2, 1] ; sp = beat / 2                                                           # eighth-note arpeggio, thin 12.5 % lead
    for k, (root, tri) in enumerate(chords):
        t0 = k * bar
        for j in range(8):                                                                                   # bass: root on 1 and 3, fifth on 2 and 4 (eighths, short)
            m = root if j in (0, 3, 4, 7) else root + 7
            if j % 2 == 0: note(b, t0 + j * sp, sp * .9, m - 12, 'tri', vol=1, a=.003, d=1, s=1, r=.02)
        for j in range(8):
            m = tri[mel[j]] + (12 if (k >= 4 and j in (3, 7)) else 0)
            if j % 4 != 3 or k >= 4: note(lead, t0 + j * sp, sp * .8, m, 'sq', .125, 1, a=.002, d=.06, s=.35, r=.03)
        for j in range(8):
            if j % 2 == 1: noise_hat(h, t0 + j * sp, vol=.7, rng=rng)                                       # off-beat hat
    x = lead * .22 + b * .5 + h * .08
    x = rms_to(fades(x), -30); assert np.abs(x).max() < 10 ** (-12 / 20); return x
def coin():
    x = np.zeros(int(.42 * SR)); note(x, 0, .075, 83, 'sq', .5, 1, a=.001, d=1, s=1, r=.005); note(x, .075, .34, 88, 'sq', .5, 1, a=.001, d=.12, s=.25, r=.2)   # B5, E6
    return peak_to(fades(x), -18)
def tick():
    x = np.zeros(int(.03 * SR)); note(x, 0, .03, 91, 'sq', .5, 1, a=.001, d=.01, s=0.1, r=.006)    # G6, 30 ms
    return peak_to(fades(x, 5), -18)
if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'film/audio/s08'; os.makedirs(out, exist_ok=True)
    for name, fn in (('jingle', jingle), ('bed', bed), ('coin', coin), ('tick', tick)): save(os.path.join(out, name + '.wav'), fn())
