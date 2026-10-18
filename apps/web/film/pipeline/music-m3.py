#!/usr/bin/env python3
"""Music + sound-effect layer for conspiracy m2 (audio-only remix of m1 on the x12b picture). Runs on do-box with /home/claude/venvs/manim
(numpy, scipy) and ffmpeg for audio decoding only (-vn).
usage: music-m3.py (copy of music-m2.py; the only change is music.extra_db added to under_db, default 0 = m2)
usage: music-m2.py <spec.json> <work root> <out-prefix>
  spec paths are relative to <work root> (build-conspiracy-m2.sh copies m1's inputs there from dev-mac).
  -> <out>-dialogue.wav (x12b's delivered mix, unchanged), <out>-music.wav, <out>-sfx.wav, <out>-pre.wav (their sum), <out>-placements.json
Changes from music-m1.py (Liam on the m1 film):
  Music level: the cue (mono fold, high-pass music.hp = 100 Hz, 2nd-order Butterworth) is normalised to music.norm_lufs (-18 LUFS integrated,
    BS.1770, whole cue) before placement, so every cue starts from a common loudness. Its gain is then a sidechain on the dialogue stem, no
    breakpoint automation and no swells: music.duck.under_db (re the -18 LUFS cue) while Liam speaks, under_db + depth_db in the pauses between
    words. under_db is m1's gap level (-14 dB on the raw cue at a 180 Hz high-pass) converted to the normalised cue (equal loudness, measured,
    see the placements json), so the music under speech is where m1's gaps were and it opens about 5 dB between words.
  Sidechain: key = dialogue 10 ms RMS (1 ms hop); duck fraction 0 at <= key_lo_db, 1 at >= key_hi_db (linear in dB between); the duck is fully
    down when a word starts (attack_ms linear ramp ahead of it, offline look-ahead) and recovers over release_ms (linear in dB) after the key
    drops. No minimum-gap logic, no bridging, no stepped lifts.
  Anchors: the track onsets are found on a 180 Hz high-passed copy (m1's detection signal), so the placement and speed are m1's exactly.
  Guard: not enforced (the music is deliberately louder); measured and reported by verify-m2.py.
Sound effects: as music-m1.py (attack detector / 'cut' alignment / attack_s); optional per-effect attack_peak_db (default 12) and attack_rise_db
  (default 9) select which transient counts as the hit (folder-close-2 has a small click 0.14 s before its main impact, whose 5 ms rise is
  8 dB: 6 / 6 picks the main impact)."""
import sys, json, os, subprocess
import numpy as np
from fractions import Fraction
from scipy.signal import butter, sosfilt, resample_poly, stft, lfilter
from scipy.io import wavfile

SR = 48000
db = lambda x: 10 ** (x / 20)
X = os.path.expanduser
ROOT = '.'


def path(p):
    p = X(p)
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def read(p):
    """float64 samples (mono fold 0.5 L + 0.5 R, as soundfile + mean in music-m1.py), decoded by ffmpeg (audio only)"""
    p = path(p)
    ch = int(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=channels,sample_rate', '-of', 'csv=p=0', p],
                            capture_output=True, text=True, check=True).stdout.strip().split(',')[1])
    b = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-vn', '-i', p, '-ar', str(SR), '-f', 'f64le', '-'], capture_output=True, check=True).stdout
    y = np.frombuffer(b, np.float64).reshape(-1, ch)
    return y.mean(1)


mono = read


def write(p, y):
    wavfile.write(p, SR, np.asarray(y, np.float32))


def env_db(y, w, hop):
    """RMS level (dBFS) of windows [k*hop, k*hop + w)"""
    c = np.concatenate([[0.0], np.cumsum(y * y)])
    k = np.arange(0, max(1, len(y) - w + 1), hop)
    return 10 * np.log10((c[k + w] - c[k]) / w + 1e-20)


def lufs(y):
    """BS.1770-4 integrated loudness of a mono signal at 48 kHz (K-weighting, 400 ms blocks, 75% overlap, -70 / -10 LU gates)"""
    z = lfilter([1.53512485958697, -2.69169618940638, 1.19839281085285], [1, -1.69065929318241, 0.73248077421585], y)
    z = lfilter([1.0, -2.0, 1.0], [1, -1.99004745483398, 0.99007225036621], z)
    c = np.concatenate([[0.0], np.cumsum(z * z)]); w, h = 19200, 4800
    k = np.arange(0, len(z) - w + 1, h); ms = (c[k + w] - c[k]) / w
    L = -0.691 + 10 * np.log10(ms + 1e-20)
    g = ms[L > -70]
    rel = -0.691 + 10 * np.log10(g.mean()) - 10
    return float(-0.691 + 10 * np.log10(g[-0.691 + 10 * np.log10(g) > rel].mean()))


def attack(y, peak_db=12, rise_db=9):
    """seconds into y of the hit: first 5 ms window (1 ms hop) rising >= rise_db over the max of the previous 25 ms and within peak_db of the peak"""
    e = env_db(np.concatenate([np.zeros(int(0.03 * SR)), y]), int(0.005 * SR), int(0.001 * SR))
    pk = e.max()
    for k in range(25, len(e)):
        if e[k] >= pk - peak_db and e[k] - e[k - 25:k - 2].max() >= rise_db:
            return k / 1000 - 0.03
    raise ValueError('no attack found')


def cut(y):
    e = env_db(y, int(0.005 * SR), int(0.001 * SR))
    return (np.nonzero(e >= e.max() - 12)[0][-1] + 5) / 1000


def flux_onset(y, t, win=0.06):
    """time (s in y) of the largest spectral-flux peak within +-win of t (1 ms hop, 512-point frames)"""
    a = max(0, int((t - win - 0.03) * SR)); b = min(len(y), int((t + win + 0.03) * SR))
    f, tt, Z = stft(y[a:b], SR, nperseg=512, noverlap=512 - 48, boundary=None, padded=False)
    M = np.log1p(np.abs(Z) * 50)
    fl = np.maximum(M[:, 1:] - M[:, :-1], 0).sum(0)
    ts = a / SR + tt[1:]
    m = np.abs(ts - t) <= win
    return float(ts[m][np.argmax(fl[m])])


def hp(y, f):
    return sosfilt(butter(2, f, 'hp', fs=SR, output='sos'), y)


def sidechain(dlg, n, d):
    """duck fraction 0..1 per sample from the dialogue key (see the module doc)"""
    E = env_db(dlg, int(0.010 * SR), int(0.001 * SR))       # 10 ms RMS on a 1 ms grid (window k covers k..k+10 ms)
    E = np.concatenate([np.full(5, E[0]), E])                  # centre the window on its ms (shift by 5 ms)
    k = np.clip((E - d['key_lo_db']) / (d['key_hi_db'] - d['key_lo_db']), 0, 1)
    out = k.copy(); A, R = int(d['attack_ms']), int(d['release_ms'])
    for s in range(1, A + 1):                                  # look-ahead attack: fully down when the key reaches it
        out[:-s] = np.maximum(out[:-s], k[s:] * (1 - s / A))
    o2 = out.copy()
    for s in range(1, R + 1):                                  # linear (in dB) release after the key drops
        o2[s:] = np.maximum(o2[s:], out[:-s] * (1 - s / R))
    return np.interp(np.arange(n) / SR, np.arange(len(o2)) / 1000, o2), k


def main():
    global ROOT
    spec = json.load(open(sys.argv[1])); ROOT = sys.argv[2]; out = sys.argv[3]
    dlg = read(spec['dialogue']); N = len(dlg)
    rep = {'scene_s': N / SR, 'music': {}, 'sfx': []}
    # ---------------- music
    m = spec['music']
    raw = read(m['file'])
    det = hp(raw, m.get('detect_hp', 180))                     # onset detection signal = m1's (placement identical to m1)
    y = hp(raw, m['hp'])
    L_cue = lufs(y); g_norm = m['norm_lufs'] - L_cue
    y = y * db(g_norm)
    lv = m['level_from_m1']                                     # m1's gap level: gain re the raw cue at m1's high-pass -> equal loudness on the normalised cue
    L_m1 = lufs(hp(raw, lv['m1_hp'])) + lv['m1_gap_db']
    under = round(L_m1 - m['norm_lufs'], 2) + m.get('extra_db', 0)   # m3a/m3b: extra_db louder than m2 under speech; pause opening (depth_db) unchanged
    anc = [dict(a, track_onset=flux_onset(det, a['track'])) for a in m['anchors']]
    f_req = (anc[1]['track_onset'] - anc[0]['track_onset']) / (anc[1]['scene'] - anc[0]['scene'])
    fr = Fraction(1 / f_req).limit_denominator(4000)
    up, down = fr.numerator, fr.denominator
    yr = resample_poly(y, up, down) if up != down else y
    f = down / up
    a0 = anc[0]
    off = a0['scene'] - a0['track_onset'] / f
    tin = flux_onset(det, m['in']['track'])
    s_in = off + (tin - m['in'].get('preroll', 0.015)) / f
    tt = np.arange(N) / SR
    jj = np.round((tt - off) * SR).astype(np.int64)
    ok = (jj >= 0) & (jj < len(yr)) & (tt >= s_in)
    mus = np.zeros(N); mus[ok] = yr[jj[ok]]
    amp = np.clip((tt - s_in) / m['in'].get('fade', 0.01), 0, 1)
    e = m['end']
    p = np.clip((tt - e['fade_from']) / (e['fade_to'] - e['fade_from']), 0, 1)
    amp *= 0.5 * (1 + np.cos(np.pi * p))
    d = m['duck']
    frac, key = sidechain(dlg, N, d)
    gain_db = under + d['depth_db'] * (1 - frac)               # open = under + depth between words, under while he speaks
    mus *= db(gain_db) * amp
    rep['music'] = {'file': m['file'], 'hp': m['hp'], 'cue_lufs_at_hp': L_cue, 'norm_gain_db': g_norm, 'norm_lufs': m['norm_lufs'],
                    'm1_gap_level_lufs_at_m1_hp': L_m1, 'under_db_re_norm': under, 'open_db_re_norm': under + d['depth_db'],
                    'speed': f, 'speed_requested': f_req, 'pitch_cents': 1200 * np.log2(f), 'scene_eq_track_over_speed_plus': off,
                    'in_scene': s_in, 'in_track_onset': tin, 'anchors': anc, 'end': e, 'duck': d,
                    'ms_ducked_over_half': int((frac > 0.5).sum() / 48), 'ms_fully_open': int((frac[tt >= s_in] < 0.02).sum() / 48)}
    rep['music']['bars_scene'] = {str(b): off + flux_onset(det, t) / f for b, t in m.get('report_bars', {}).items()}
    # ---------------- sound effects
    sfx = np.zeros(N)
    for ev in spec['sfx']:
        z = read(ev['file'])
        if 'attack_s' in ev:
            at = ev['attack_s']
        else:
            at = cut(z) if ev.get('align') == 'cut' else attack(z, ev.get('attack_peak_db', 12), ev.get('attack_rise_db', 9))
        st = ev['hit'] - at
        i0 = int(round(st * SR))
        zz = z * db(ev['gain'])
        if i0 < 0:
            zz = zz[-i0:].copy(); zz[:240] *= np.linspace(0, 1, 240); i0 = 0
        seg = np.zeros(N); j = min(N, i0 + len(zz)); seg[i0:j] = zz[:j - i0]
        sfx += seg
        rep['sfx'].append({**ev, 'attack_in_file_s': at, 'file_start_scene_s': st, 'head_trimmed_s': max(0.0, -st)})
    tail = np.ones(N); tail[-720:] = np.linspace(1, 0, 720)
    mus *= tail; sfx *= tail
    write(f'{out}-dialogue.wav', dlg); write(f'{out}-music.wav', mus); write(f'{out}-sfx.wav', sfx); write(f'{out}-pre.wav', dlg + mus + sfx)
    np.save(f'{out}-duckfrac.npy', frac[::48].astype(np.float32))   # 1 ms grid, for the plot
    json.dump(rep, open(f'{out}-placements.json', 'w'), indent=1, default=float)
    mu = rep['music']
    print(f"music: cue {mu['cue_lufs_at_hp']:.2f} LUFS at {m['hp']} Hz -> {m['norm_lufs']} ({g_norm:+.2f} dB); m1 gap level {L_m1:.2f} LUFS "
          f"-> under {under:+.2f} dB, open {under + d['depth_db']:+.2f} dB re the normalised cue")
    print(f"  speed {f:.6f} ({mu['pitch_cents']:+.1f} cents), in at {s_in:.3f} s; ducked (>50%) {mu['ms_ducked_over_half']} ms, fully open {mu['ms_fully_open']} ms")
    for a in anc:
        print(f"  anchor {a['name']}: track onset {a['track_onset']:.3f} -> scene {a['scene']:.3f}")
    for r in rep['sfx']:
        print(f"sfx {r['name']}: {os.path.basename(r['file'])} attack {r['attack_in_file_s']:.3f} s in file, hit {r['hit']:.4f}, gain {r['gain']} dB, "
              f"file starts {r['file_start_scene_s']:.4f}")


if __name__ == '__main__':
    main()
