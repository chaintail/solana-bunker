#!/usr/bin/env python3
"""Music + sound-effect layer for conspiracy m4 (audio-only remix on the x12b picture). Runs on do-box with /home/claude/venvs/manim
(numpy, scipy) and ffmpeg for audio decoding only (-vn).
usage: music-m4.py <spec.json> <work root> <out-prefix>
m4 = music-m3.py (m2 + music.extra_db) plus, all optional in the spec (absent = m3 behaviour):
  music.eq          biquads (RBJ cookbook) after the high-pass, before the -18 LUFS normalisation, so the level targets hold on the
                    filtered cue: {"type": "highshelf"|"peak", "f": Hz, "gain_db": dB, "q": Q}. m4: the "whistle" is the clock-tick
                    transients' 12-17.2 kHz band (peak 16.8 kHz), above everything else in the cue and above the dialogue's 8.5 kHz band edge.
  music.level_intro upward-only slow leveller on the normalised cue in track time: gain = clip(target - ST, 0, max_boost_db), ST = K-weighted
                    short-term loudness (st_window_s, centred), target = median ST over body [a, b] (track s); applied only before until_track
                    (weight ramps 1 -> 0 over ramp_s ending there), gain smoothed by a smooth_s moving average. Body untouched.
  music.in.scene    the cue enters at this scene time (m4: 0.0) with a linear fade of in.fade s, instead of at the in.track onset.
  Anchors: as m2, two (track onset, scene) pairs fix speed and offset; m4 moves the cue 4 bars (one phrase) earlier: bar 17 on f632, bar 41 on 58.40.
  Also writes <out>-music-preduck.wav (placed, levelled, EQ'd cue at the under level, no sidechain) and <out>-introgain.npy (track-time dB, 1 ms).
m2/m3 notes follow.
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


def biquad(b):
    """RBJ cookbook biquad as one sos row"""
    A = 10 ** (b['gain_db'] / 40); w = 2 * np.pi * b['f'] / SR; c, sn = np.cos(w), np.sin(w); al = sn / (2 * b.get('q', 0.7071))
    if b['type'] == 'highshelf':
        sq = 2 * np.sqrt(A) * al
        bb = [A * ((A + 1) + (A - 1) * c + sq), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - sq)]
        aa = [(A + 1) - (A - 1) * c + sq, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - sq]
    elif b['type'] == 'peak':
        bb = [1 + al * A, -2 * c, 1 - al * A]; aa = [1 + al / A, -2 * c, 1 - al / A]
    else:
        raise ValueError(b['type'])
    return np.array(bb + aa) / aa[0]


def eq(y, bands):
    return sosfilt(np.array([biquad(b) for b in bands]), y) if bands else y


def short_term(y, w_s=3.0):
    """K-weighted short-term loudness (LUFS) on a 1 ms grid, window centred on each ms"""
    z = lfilter([1.53512485958697, -2.69169618940638, 1.19839281085285], [1, -1.69065929318241, 0.73248077421585], y)
    z = lfilter([1.0, -2.0, 1.0], [1, -1.99004745483398, 0.99007225036621], z)
    c = np.concatenate([[0.0], np.cumsum(z * z)]); W = int(w_s * SR); h = W // 2
    k = np.arange(0, len(z), 48); a = np.clip(k - h, 0, len(z)); b = np.clip(k + h, 0, len(z))
    return -0.691 + 10 * np.log10((c[b] - c[a]) / np.maximum(b - a, 1) + 1e-20)


def level_intro(y, li):
    """gain (dB, per sample) of the intro leveller (see the module doc)"""
    st = short_term(y, li.get('st_window_s', 3.0)); t = np.arange(len(st)) / 1000
    a, b = li['body']; target = float(np.median(st[(t >= a) & (t <= b)]))
    g = np.clip(target - st, 0, li['max_boost_db'])
    u, r = li['until_track'], li['ramp_s']
    g *= np.clip((u - t) / r, 0, 1)
    k = int(li.get('smooth_s', 1.0) * 1000) | 1
    g = np.convolve(np.pad(g, k // 2, mode='edge'), np.ones(k) / k, mode='valid')
    g *= np.clip((u - t) / r, 0, 1)                            # exactly 0 from until_track on
    return np.interp(np.arange(len(y)) / SR, t, g), g, target, st


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
    L_hp = lufs(y)
    y = eq(y, m.get('eq'))
    L_cue = lufs(y); g_norm = m['norm_lufs'] - L_cue
    y = y * db(g_norm)
    li = m.get('level_intro'); lirep = None
    if li:
        gs, gms, li_target, st_before = level_intro(y, li)
        y = y * db(gs)
        st_after = short_term(y, li.get('st_window_s', 3.0)); tt_ = np.arange(len(st_after)) / 1000
        np.save(f'{out}-introgain.npy', gms.astype(np.float32))
        w = lambda s, a, b: round(float(np.median(s[(tt_ >= a) & (tt_ <= b)])), 2)
        lirep = {**li, 'target_st_lufs': li_target, 'max_gain_db': float(gms.max()), 'gain_db_at_track': {str(x): float(gms[int(x * 1000)]) for x in (4, 6, 8, 10, 12, 14, 16, 18)},
                 'st_median_before': {'track_3.95_13.95': w(st_before, 3.95, 13.95), 'body': w(st_before, *li['body'])},
                 'st_median_after': {'track_3.95_13.95': w(st_after, 3.95, 13.95), 'body': w(st_after, *li['body'])}}
    lv = m['level_from_m1']                                     # m1's gap level: gain re the raw cue at m1's high-pass -> equal loudness on the normalised cue
    L_m1 = lufs(hp(raw, lv['m1_hp'])) + lv['m1_gap_db']
    under = round(L_m1 - m['norm_lufs'], 2) + m.get('extra_db', 0)   # extra_db louder than m2 under speech; pause opening (depth_db) unchanged
    anc = [dict(a, track_onset=flux_onset(det, a['track'])) for a in m['anchors']]
    f_req = (anc[1]['track_onset'] - anc[0]['track_onset']) / (anc[1]['scene'] - anc[0]['scene'])
    fr = Fraction(1 / f_req).limit_denominator(4000)
    up, down = fr.numerator, fr.denominator
    yr = resample_poly(y, up, down) if up != down else y
    f = down / up
    a0 = anc[0]
    off = a0['scene'] - a0['track_onset'] / f
    if 'scene' in m['in']:                                     # m4: the cue plays from this scene time (0 = frame 0)
        s_in = m['in']['scene']; tin = (s_in - off) * f
    else:
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
    preduck = mus * db(under) * amp
    frac, key = sidechain(dlg, N, d)
    gain_db = under + d['depth_db'] * (1 - frac)               # open = under + depth between words, under while he speaks
    mus *= db(gain_db) * amp
    rep['music'] = {'file': m['file'], 'hp': m['hp'], 'cue_lufs_at_hp_before_eq': L_hp, 'eq': m.get('eq'), 'eq_loudness_change_db': L_cue - L_hp,
                    'level_intro': lirep, 'cue_track_at_scene_0': (0 - off) * f, 'cue_lufs_at_hp': L_cue, 'norm_gain_db': g_norm, 'norm_lufs': m['norm_lufs'],
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
    mus *= tail; sfx *= tail; preduck *= tail
    write(f'{out}-dialogue.wav', dlg); write(f'{out}-music.wav', mus); write(f'{out}-sfx.wav', sfx); write(f'{out}-pre.wav', dlg + mus + sfx); write(f'{out}-music-preduck.wav', preduck)
    np.save(f'{out}-duckfrac.npy', frac[::48].astype(np.float32))   # 1 ms grid, for the plot
    json.dump(rep, open(f'{out}-placements.json', 'w'), indent=1, default=float)
    mu = rep['music']
    print(f"music: cue {mu['cue_lufs_at_hp']:.2f} LUFS at {m['hp']} Hz -> {m['norm_lufs']} ({g_norm:+.2f} dB); m1 gap level {L_m1:.2f} LUFS "
          f"-> under {under:+.2f} dB, open {under + d['depth_db']:+.2f} dB re the normalised cue")
    print(f"  eq {m.get('eq')}: cue {L_hp:.2f} -> {L_cue:.2f} LUFS ({L_cue - L_hp:+.2f} dB, made up by the normalisation)")
    if lirep:
        print(f"  intro leveller: target ST {lirep['target_st_lufs']:.2f} LUFS, max +{lirep['max_gain_db']:.2f} dB, ST median track 3.95-13.95 "
              f"{lirep['st_median_before']['track_3.95_13.95']} -> {lirep['st_median_after']['track_3.95_13.95']} (body {lirep['st_median_after']['body']}); "
              f"gain at track s {lirep['gain_db_at_track']}")
    print(f"  cue track time at scene 0: {mu['cue_track_at_scene_0']:.3f} s; bars at scene: " + ', '.join(f'{k} {v:.3f}' for k, v in mu['bars_scene'].items()))
    print(f"  speed {f:.6f} ({mu['pitch_cents']:+.1f} cents), in at {s_in:.3f} s; ducked (>50%) {mu['ms_ducked_over_half']} ms, fully open {mu['ms_fully_open']} ms")
    for a in anc:
        print(f"  anchor {a['name']}: track onset {a['track_onset']:.3f} -> scene {a['scene']:.3f}")
    for r in rep['sfx']:
        print(f"sfx {r['name']}: {os.path.basename(r['file'])} attack {r['attack_in_file_s']:.3f} s in file, hit {r['hit']:.4f}, gain {r['gain']} dB, "
              f"file starts {r['file_start_scene_s']:.4f}")


if __name__ == '__main__':
    main()
