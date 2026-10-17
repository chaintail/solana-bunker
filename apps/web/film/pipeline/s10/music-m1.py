#!/usr/bin/env python3
"""Music + sound-effect layer for a finished scene (m1). Runs ON dev-mac with ~/speech-lab/.venv/bin/python3 (numpy, scipy, soundfile).
usage: music-m1.py <spec.json> <out-prefix>
  -> <out>-dialogue.wav (the scene's delivered mix, unchanged), <out>-music.wav, <out>-sfx.wav, <out>-pre.wav (their sum, float, scene length),
     <out>-placements.json (every placement with its measured onset)
All times are scene seconds. The scene's delivered mix is the dialogue stem; nothing in it is changed.
Music: the cue is folded to mono (0.5 L + 0.5 R), high-passed at 180 Hz (2nd-order Butterworth, as ffmpeg highpass), placed by one or two anchors
  (track onset -> scene time; with two anchors the cue is resampled by the ratio of the two spans, so both land exactly; with one, speed 1).
  Anchor and entry track times are refined to the spectral-flux onset within +-60 ms of the analysis.json downbeat.
  Gain: piecewise-linear dB breakpoints (spec "auto"), then the dialogue guard: in every 100 ms window (10 ms hop) where the dialogue is at or above
  guard.active_db dBFS RMS, the music must sit guard.target dB under it; any shortfall becomes an extra duck; ducks less than guard.bridge_ms
  (600) apart are joined (grey closing), so the music holds through a short pause instead of dipping at every word edge; then a 100 ms attack
  (ramp complete when the window starts) and a 300 ms release after it ends (linear in dB).
Sound effects: each file folded to mono; its hit is the measured attack (first 5 ms window, 1 ms hop, that rises 9 dB over the previous 25 ms and is
  within 12 dB of the file's peak), or with align "cut" the end of its last window within 12 dB of the peak (a swell that stops on the event);
  or the spec's attack_s; the file is placed so that this point lands on the spec's hit time. Optional duck (dB from a time, 100 ms ramp) and
  linear fade to silence. A file that would start before 0 has its head trimmed (5 ms fade-in); everything is cut at the scene end (15 ms fade)."""
import sys, json, os
import numpy as np, soundfile as sf
from fractions import Fraction
from scipy.signal import butter, sosfilt, resample_poly, stft
from scipy.ndimage import grey_closing

SR = 48000
db = lambda x: 10 ** (x / 20)
X = os.path.expanduser


def mono(p):
    y, sr = sf.read(X(p), dtype='float64')
    y = y.mean(1) if y.ndim > 1 else y
    assert sr == SR, (p, sr)
    return y


def env_db(y, w, hop):
    """RMS level (dBFS) of windows [k*hop, k*hop + w)"""
    c = np.concatenate([[0.0], np.cumsum(y * y)])
    k = np.arange(0, max(1, len(y) - w + 1), hop)
    return 10 * np.log10((c[k + w] - c[k]) / w + 1e-20)


def attack(y):
    """seconds into y of the hit: first 5 ms window (1 ms hop) rising >= 9 dB over the max of the previous 25 ms and within 12 dB of the peak"""
    e = env_db(np.concatenate([np.zeros(int(0.03 * SR)), y]), int(0.005 * SR), int(0.001 * SR))   # 30 ms of silence first: a file may start on its hit
    pk = e.max()
    for k in range(25, len(e)):
        if e[k] >= pk - 12 and e[k] - e[k - 25:k - 2].max() >= 9:
            return k / 1000 - 0.03
    raise ValueError('no attack found')


def cut(y):
    """seconds into y where a swelling effect stops: end of the last 5 ms window (1 ms hop) within 12 dB of the peak"""
    e = env_db(y, int(0.005 * SR), int(0.001 * SR))
    return (np.nonzero(e >= e.max() - 12)[0][-1] + 5) / 1000


def flux_onset(y, t, win=0.06):
    """time (s in y) of the largest spectral-flux peak within +-win of t (1 ms hop, 512-point frames)"""
    a = max(0, int((t - win - 0.03) * SR)); b = min(len(y), int((t + win + 0.03) * SR))
    f, tt, Z = stft(y[a:b], SR, nperseg=512, noverlap=512 - 48, boundary=None, padded=False)
    M = np.log1p(np.abs(Z) * 50)
    fl = np.maximum(M[:, 1:] - M[:, :-1], 0).sum(0)
    ts = a / SR + tt[1:]                                     # frame centre of the frame where the flux rises
    m = np.abs(ts - t) <= win
    return float(ts[m][np.argmax(fl[m])])


def breakpoints(tt, pts):
    p = np.array(pts, float)
    return np.interp(tt, p[:, 0], p[:, 1])


def guard_duck(dlg, mus, target, active_db, n, bridge_ms=600):
    """extra music attenuation (dB, per sample) so that every active 100 ms window keeps the music target dB under the dialogue"""
    w, hop = int(0.1 * SR), int(0.01 * SR)
    D, M = env_db(dlg, w, hop), env_db(mus[:len(dlg)], w, hop)
    need = np.where(D >= active_db, np.maximum(0, M - D + target), 0)
    ms = np.zeros(n // 48 + 2)                               # 1 ms grid: each window's need covers its 100 ms
    for k in np.nonzero(need)[0]:
        a = k * 10; ms[a:a + 100] = np.maximum(ms[a:a + 100], need[k])
    ms = grey_closing(ms, size=bridge_ms)                      # ducks less than bridge_ms apart hold through the pause instead of pumping
    d = ms.copy()
    for s in range(1, 101):                                  # fully down 100 ms before: ramp from 0 at -100 ms
        d[:-s] = np.maximum(d[:-s], ms[s:] * (1 - s / 100))
    for s in range(1, 301):                                  # recover over 300 ms after
        d[s:] = np.maximum(d[s:], ms[:-s] * (1 - s / 300))
    return np.interp(np.arange(n) / SR, np.arange(len(d)) / 1000, d), need


def main():
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]
    dlg = mono(spec['dialogue']); N = len(dlg); T = N / SR
    rep = {'scene_s': T, 'music': {}, 'sfx': []}
    # ---------------- music
    m = spec['music']
    y = mono(m['file'])
    y = sosfilt(butter(2, m.get('hp', 180), 'hp', fs=SR, output='sos'), y)
    anc = [dict(a, track_onset=flux_onset(y, a['track'])) for a in m['anchors']]
    if len(anc) == 2:
        f_req = (anc[1]['track_onset'] - anc[0]['track_onset']) / (anc[1]['scene'] - anc[0]['scene'])
        fr = Fraction(1 / f_req).limit_denominator(4000)       # resample_poly(up/down): output sample j is track time j/SR * f
        up, down = fr.numerator, fr.denominator
        yr = resample_poly(y, up, down) if up != down else y
        f = down / up
    else:
        yr, f, f_req = y, 1.0, 1.0
    a0 = anc[0]
    off = a0['scene'] - a0['track_onset'] / f                   # scene = off + track / f
    tin = flux_onset(y, m['in']['track'])
    s_in = off + (tin - m['in'].get('preroll', 0.015)) / f      # cut a little before the entry onset, short fade-in
    NM = N + int(round(m.get('stem_extra_s', 0) * SR))         # the music stem may ring past the picture (for the stitch)
    tt = np.arange(NM) / SR
    jj = np.round((tt - off) * SR).astype(np.int64)            # index into yr (yr[j] is track time j*f/SR, scene off + j/SR)
    ok = (jj >= 0) & (jj < len(yr)) & (tt >= s_in)
    mus = np.zeros(NM); mus[ok] = yr[jj[ok]]
    g = breakpoints(tt, m['auto'])
    fin = m['in'].get('fade', 0.01)
    amp = np.clip((tt - s_in) / fin, 0, 1)
    e = m['end']
    if 'fade_from' in e:                                        # cosine fade to silence
        p = np.clip((tt - e['fade_from']) / (e['fade_to'] - e['fade_from']), 0, 1)
        amp *= 0.5 * (1 + np.cos(np.pi * p))
    mus *= db(g) * amp
    gd = spec.get('guard', {'target': 16.5, 'active_db': -30})
    if os.environ.get('M1_NO_GUARD'):                           # diagnostics only
        gd = dict(gd, active_db=99)
    duck, need = guard_duck(dlg, mus, gd['target'], gd['active_db'], NM, gd.get('bridge_ms', 600))
    mus *= db(-duck)
    rep['music'] = {'file': m['file'], 'speed': f, 'speed_requested': f_req, 'pitch_cents': 1200 * np.log2(f), 'scene_eq_track_over_speed_plus': off,
                    'in_scene': s_in, 'in_track_onset': tin, 'anchors': [{k: v for k, v in a.items()} for a in anc],
                    'auto': m['auto'], 'end': e, 'guard_duck_max_db': float(duck.max()), 'guard_duck_ms_over_1db': int((duck > 1).sum() / 48),
                    'guard_windows_ducked': int((need > 0).sum())}
    rep['music']['bars_scene'] = {str(b): off + flux_onset(y, t) / f for b, t in m.get('report_bars', {}).items()}
    # ---------------- sound effects
    sfx = np.zeros(N)
    for ev in spec['sfx']:
        z = mono(ev['file'])
        if 'attack_s' in ev:                                    # a measured hit given by the spec (a jingle whose quiet pickup comes first)
            at = ev['attack_s']
        else:
            at = cut(z) if ev.get('align') == 'cut' else attack(z)    # 'cut': the effect's end lands on the hit (a swell that stops on the event)
        st = ev['hit'] - at
        i0 = int(round(st * SR))
        zz = z * db(ev['gain'])
        if i0 < 0:
            zz = zz[-i0:].copy(); zz[:240] *= np.linspace(0, 1, 240); i0 = 0
        seg = np.zeros(N); j = min(N, i0 + len(zz)); seg[i0:j] = zz[:j - i0]
        t = np.arange(N) / SR
        if 'duck' in ev:
            dk = ev['duck']
            seg *= db(np.clip((t - dk['at']) / dk.get('attack', 0.1), 0, 1) * dk['db'])
            seg *= np.clip(1 - (t - dk['at']) / dk['fade'], 0, 1)
        sfx += seg
        rep['sfx'].append({**ev, 'attack_in_file_s': at, 'file_start_scene_s': st, 'head_trimmed_s': max(0.0, -st)})
    # ---------------- out (scene length; 15 ms fade on the music and sfx at the scene end, the stem keeps its ring)
    tail = np.ones(N); tail[-720:] = np.linspace(1, 0, 720)
    pre = dlg + mus[:N] * tail + sfx * tail
    sf.write(f'{out}-dialogue.wav', dlg, SR, subtype='FLOAT')
    sf.write(f'{out}-music.wav', mus, SR, subtype='FLOAT')
    sf.write(f'{out}-sfx.wav', sfx * tail, SR, subtype='FLOAT')
    sf.write(f'{out}-pre.wav', pre, SR, subtype='FLOAT')
    json.dump(rep, open(f'{out}-placements.json', 'w'), indent=1, default=float)
    mu = rep['music']
    print(f"music: speed {mu['speed']:.6f} ({mu['pitch_cents']:+.1f} cents), in at {mu['in_scene']:.3f} s (track onset {mu['in_track_onset']:.3f}), "
          f"guard duck max {mu['guard_duck_max_db']:.1f} dB over {mu['guard_duck_ms_over_1db']} ms (>1 dB)")
    for a in anc:
        print(f"  anchor {a['name']}: track onset {a['track_onset']:.3f} -> scene {a['scene']:.3f}")
    for b, s in mu['bars_scene'].items():
        print(f'  bar {b}: scene {s:.3f}')
    for r in rep['sfx']:
        print(f"sfx {r['name']}: {os.path.basename(r['file'])} attack {r['attack_in_file_s']:.3f} s in file, hit {r['hit']:.3f}, gain {r['gain']} dB, "
              f"file starts {r['file_start_scene_s']:.3f}" + (f", head trimmed {r['head_trimmed_s']:.3f} s" if r['head_trimmed_s'] else ''))


if __name__ == '__main__':
    main()
