#!/usr/bin/env python3
"""s06 + s07 m3: one noir cue rendered across both scenes, split at the s06/s07 cut sample (audio-only remix; the pictures are stream-copied at the mux).
Runs on do-box with /home/claude/venvs/manim (numpy, scipy); ffmpeg for audio decoding / ebur128 only (-vn).
usage: music-m3-noir.py <m3-noir.json> <work root> <out dir> [<join_comp_db>]      spec paths are relative to <work root>
Joint timeline: the scenes' delivered mixes (dialogue stems) end to end; s07 starts at joint sample N06 = frames06 / fps * 48000.
  cue      as m2 (music-m2.py): mono fold, high-pass music.hp, music.eq shelves, normalised to music.norm_lufs on the whole filtered cue.
  place    m2's s06 cut: track_in at scene_in (integer sample cut, raised-cosine head fade). One loop (music.loop): at the measured downbeat of
           from_bar the track jumps to the measured downbeat of to_bar (spectral-flux onsets on a 180 Hz high-passed copy, as m1/m2 measured
           bars); equal-power crossfade of xfade_s ending xfade_end_before_s before the downbeat. Outside the crossfade every output sample is one
           cue sample (no resampling).
  level    m2's sidechain (music-m4.py sidechain(); under_lufs while Liam speaks, +depth_db between words), keyed on the joint dialogue, plus a
           joint offset X (dB): 0 in s06; in s07 X goes from join_comp_db at the cut to lecture_db over ramp_down_s (linear in dB), holds
           lecture_db to the alley cut (frame alley_frame), then goes back to 0 over a linear-in-dB ramp ending on the measured downbeat of
           ramp_up_to_bar (asserted <= ramp_up_max_s). join_comp_db = s06 scene gain - s07 scene gain (finish-m3.py), so the delivered music
           (each scene times its own loudness gain) has no level step at the cut; the build iterates it.
  end      raised-cosine fade fade_from -> fade_to (scene s07 seconds), as m2.
Sound effects: per scene, as m2 (music-m2.py place_sfx with the stamp rule gains); nulled against m2's delivered sfx stem / m2's loudness gain.
Checks reported (not enforced): the intro levelling rule on each used span (3 s short-term median of the span vs its first 2 s), the high-band
tonal spike scan (100 Hz high-passed span, Welch 16384 long-term and STFT 4096 high-band frames, bin over its +-400 Hz median, >= 12 kHz).
-> <out>/s06-s07-m3-music-unsplit.wav (joint music, float32), s06-s07-m3-placements.json, s06-s07-m3-xgain.npy (X, 1 ms grid)
   per scene <out>/<sc>-m3-dialogue.wav, -music.wav, -sfx.wav, -pre.wav, -music-preduck.wav, -duckfrac.npy, -placements.json, -spec.json
   (the scene's spec for verify-m2.py)"""
import sys, json, os, importlib.util
import numpy as np
from scipy.signal import welch, stft
from scipy.io import wavfile

here = os.path.dirname(os.path.abspath(__file__))
def load(name, fn):
    s_ = importlib.util.spec_from_file_location(name, os.path.join(here, fn)); m = importlib.util.module_from_spec(s_); s_.loader.exec_module(m); return m
M = load('m4', 'music-m4.py'); MM = load('m2', 'music-m2.py')
SR = 48000
db = lambda x: 10 ** (x / 20)


def write(p, y):
    wavfile.write(p, SR, np.asarray(y, np.float32))


def highs(y, a, b, hc):
    """largest tonal spike (bin over its +-halfwidth median) >= min_hz in the span [a, b) s: long-term (Welch 16384) and high-band frames (STFT 4096)"""
    x = y[int(a * SR):int(b * SR)]
    out = {}
    f, P = welch(x, SR, nperseg=16384); L = 10 * np.log10(P + 1e-30)
    f2, _, Z = stft(x, SR, nperseg=4096, noverlap=2048); Q = np.abs(Z) ** 2
    hb = 10 * np.log10(Q[(f2 >= 12000) & (f2 < 18000)].sum(0) + 1e-20); live = Q.sum(0) > 1e-12
    tk = (hb > np.percentile(hb[live], 60) + 6) & live
    L2 = 10 * np.log10(Q[:, tk].mean(1) + 1e-30)
    for nm, ff, LL in (('long_term', f, L), ('high_band_frames', f2, L2)):
        df = ff[1] - ff[0]; hw = int(round(hc['median_halfwidth_hz'] / df))
        sp = np.array([LL[k] - np.median(LL[max(0, k - hw):k + hw + 1]) for k in range(len(LL))])
        for lab, hi in (('below_19900', 19900), ('to_nyquist', SR / 2)):
            m = (ff >= hc['min_hz']) & (ff < hi); k = np.argmax(np.where(m, sp, -np.inf))
            out[f'{nm}_{lab}'] = {'hz': round(float(ff[k]), 1), 'spike_db': round(float(sp[k]), 2)}
    out['notch_needed'] = bool(max(out['long_term_below_19900']['spike_db'], out['high_band_frames_below_19900']['spike_db']) >= hc['spike_db'])
    return out


def main():
    spec = json.load(open(sys.argv[1])); ROOT = sys.argv[2]; OUT = sys.argv[3]; comp = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
    M.ROOT = ROOT; MM.ROOT = ROOT; os.makedirs(OUT, exist_ok=True)
    fps = spec.get('fps', 30); m = spec['music']; sc = spec['scenes']
    Ns = [int(round(s['frames'] / fps * SR)) for s in sc]; N06 = Ns[0]; N = sum(Ns); off_sc = [0, N06]
    dl = []
    for s, n in zip(sc, Ns):
        d = M.read(s['dialogue']); assert abs(len(d) - n) <= 2, (s['name'], len(d), n); dl.append(np.pad(d, (0, max(0, n - len(d))))[:n])
    dlg = np.concatenate(dl)
    # ---------------- cue (m2 treatment)
    raw = M.read(m['file'])
    y = M.hp(raw, m['hp']); L_hp = M.lufs(y)
    y = M.eq(y, m['eq']); L_cue = M.lufs(y); g_norm = m['norm_lufs'] - L_cue; y = y * db(g_norm)
    det = M.hp(raw, 180)
    ana = json.load(open(MM.path(m['analysis']))); dbs = ana['downbeats_s']
    bar = lambda k: M.flux_onset(det, dbs[k - 1])             # measured downbeat of bar k (track s)
    # ---------------- placement: m2's s06 cut, then one loop
    pl = m['place']; s0 = int(round(pl['scene_in'] * SR)); a0 = int(round(pl['track_in'] * SR))
    lp = m['loop']; tA, tB = bar(lp['from_bar']), bar(lp['to_bar'])
    A, B = int(round(tA * SR)), int(round(tB * SR)); shift = A - B
    nA = A - a0 + s0                                              # joint sample where the cue reaches bar from_bar's downbeat
    xe = nA - int(round(lp['xfade_end_before_s'] * SR)); xs = xe - int(round(lp['xfade_s'] * SR))
    n = np.arange(N); jA = n - s0 + a0; jB = jA - shift
    assert jB[-1] < len(y) and jB[xs] >= 0
    vA = np.where((jA >= 0) & (jA < len(y)), y[np.clip(jA, 0, len(y) - 1)], 0.0); vB = np.where(jB >= 0, y[np.clip(jB, 0, len(y) - 1)], 0.0)
    u = np.clip((n - xs) / (xe - xs), 0, 1)
    mus = vA * np.cos(np.pi / 2 * u) + vB * np.sin(np.pi / 2 * u)
    mus[n < s0] = 0
    amp = np.ones(N); hd = int(pl['head_fade'] * SR); amp[:s0] = 0; amp[s0:s0 + hd] *= .5 - .5 * np.cos(np.pi * np.arange(hd) / hd)
    e = m['end']; te = n / SR - (off_sc[1] / SR if e['scene'] == 's07' else 0)
    p = np.clip((te - e['fade_from']) / (e['fade_to'] - e['fade_from']), 0, 1); amp *= 0.5 * (1 + np.cos(np.pi * p))
    # track time -> joint time for the bars actually played
    def joint_t(tt):
        if pl['track_in'] <= tt < tA: return (tt * SR - a0 + s0) / SR
        if tt >= tB: return (tt * SR + shift - a0 + s0) / SR
        return None
    # ---------------- level: sidechain + joint offset X
    lv = m['level']; t7 = (n - N06) / SR; alley = lv['alley_frame'] / fps
    t_up = joint_t(bar(lv['ramp_up_to_bar'])) - N06 / SR; r_up = t_up - alley
    assert 0 < r_up <= lv['ramp_up_max_s'], r_up
    X = np.zeros(N); L = lv['lecture_db']; s7 = t7 >= 0
    X[s7] = np.interp(t7[s7], [0, lv['ramp_down_s'], alley, t_up], [comp, L, L, 0.0])
    d = m['duck']; under = m['under_lufs'] - m['norm_lufs']
    frac, _ = M.sidechain(dlg, N, d)
    gdb = under + d['depth_db'] * (1 - frac) + X
    preduck = mus * db(under + X) * amp
    out_m = mus * db(gdb) * amp
    write(f'{OUT}/s06-s07-m3-music-unsplit.wav', out_m); np.save(f'{OUT}/s06-s07-m3-xgain.npy', X[::48].astype(np.float32))
    # ---------------- checks: intro levelling rule, highs
    spans = {'pre_loop': [pl['track_in'], tA], 'post_loop': [tB - lp['xfade_s'] - lp['xfade_end_before_s'], float(jB[-1] / SR)]}
    st = M.short_term(y, m['intro_check']['st_window_s']); ts = np.arange(len(st)) / 1000
    med = lambda a, b: round(float(np.median(st[(ts >= a) & (ts <= b)])), 2)
    intro = {'whole_cue_st_median': med(0, len(y) / SR)}
    for k, (a, b) in spans.items():
        intro[k] = {'span_track_s': [round(a, 3), round(b, 3)], 'st_median_span': med(a, b), 'st_median_first_2s': med(a, a + m['intro_check']['first_s'])}
        intro[k]['first_minus_span_db'] = round(intro[k]['st_median_first_2s'] - intro[k]['st_median_span'], 2)
    yh = M.hp(raw, m['hp'])
    hi = {k: highs(yh, a, b, m['highs_check']) for k, (a, b) in spans.items()}
    # ---------------- per scene: split at the cut sample, effects, files
    rep = {'joint_samples': N, 'scene_samples': dict(zip([s['name'] for s in sc], Ns)), 'cut_sample': N06,
           'cue': {'file': m['file'], 'len_s': len(y) / SR, 'lufs_hp': L_hp, 'lufs_eq': L_cue, 'norm_gain_db': g_norm, 'natural_end_analysis_s': ana.get('natural_end_s')},
           'place': {'s06_scene_eq_track_minus': (a0 - s0) / SR, 'track_at_s06_end': (N06 - s0 + a0) / SR},
           'loop': {**lp, 'from_track_s': tA, 'to_track_s': tB, 'from_analysis_s': dbs[lp['from_bar'] - 1], 'to_analysis_s': dbs[lp['to_bar'] - 1],
                    'shift_samples': int(shift), 'joint_s': nA / SR, 's07_s': (nA - N06) / SR, 'xfade_joint_s': [xs / SR, xe / SR],
                    'track_at_s07_end': float(jB[-1] / SR)},
           'level': {**lv, 'join_comp_db': comp, 'alley_s07': alley, 'ramp_up_ends_s07': t_up, 'ramp_up_s': r_up,
                     'under_db_re_norm': under, 'lecture_under_lufs': m['under_lufs'] + L, 'open_db': d['depth_db']},
           'cue_used_s': (A - a0) / SR + (jB[-1] - B) / SR, 'intro_check': intro, 'highs_check': hi, 'bars': {}, 'scenes': {}}
    for i, s in enumerate(sc):
        a, b = off_sc[i], off_sc[i] + Ns[i]; nm = s['name']; pre = f'{OUT}/{nm}-m3'
        bars = {}
        for k in m['report_bars'][nm]:
            jt = joint_t(bar(k)); bars[str(k)] = None if jt is None else jt - a / SR
        rep['bars'][nm] = bars
        sspec = {'fps': fps, 'sfx_mode': s['sfx_mode'], 'sfx_ref_lufs': s['sfx_ref_lufs'], 'sfx': s['sfx']}
        sfx, srep = MM.place_sfx(sspec, Ns[i], 'gain_m2')
        g2 = json.load(open(MM.path(s['ref']['loudness'])))['linear_gain_db']
        ref = M.read(s['ref']['stems'] + '-sfx.wav')[:Ns[i]] * db(-g2); ref = np.pad(ref, (0, Ns[i] - len(ref))); res = sfx - ref
        null = {'m2_stem': s['ref']['stems'] + '-sfx.wav', 'm2_gain_db': g2, 'residual_peak_dbfs': 20 * np.log10(np.abs(res).max() + 1e-20),
                'residual_rms_re_ref_db': 10 * np.log10((res ** 2).sum() / ((ref ** 2).sum() + 1e-30) + 1e-30)}
        mu = out_m[a:b]
        write(f'{pre}-dialogue.wav', dl[i]); write(f'{pre}-music.wav', mu); write(f'{pre}-sfx.wav', sfx); write(f'{pre}-pre.wav', dl[i] + mu + sfx)
        write(f'{pre}-music-preduck.wav', preduck[a:b]); np.save(f'{pre}-duckfrac.npy', frac[a:b][::48].astype(np.float32))
        in_s = max(0.0, s0 / SR - a / SR)
        endd = ({'fade_from': e['fade_from'], 'fade_to': e['fade_to']} if e['scene'] == nm else {'fade_from': Ns[i] / SR, 'fade_to': Ns[i] / SR})
        mp = {'music': {'file': m['file'], 'hp': m['hp'], 'eq': m['eq'], 'under_lufs': m['under_lufs'], 'in_scene': in_s, 'end': endd, 'bars_scene': bars,
                        'joint_offset_s': a / SR}, 'sfx': srep, 'sfx_null_vs_m2': null}
        json.dump(mp, open(f'{pre}-placements.json', 'w'), indent=1, default=float)
        ver = [dict(v, at=bars[str(v['bar'])]) for v in s['verify']['music']]
        json.dump({'title': s['title'], 'fps': fps, 'sfx_mode': s['sfx_mode'], 'verify': {'music': ver},
                   'ref': {'name': 'm2', 'stems': s['ref']['stems'], 'gain_db': g2}}, open(f'{pre}-spec.json', 'w'), indent=1)
        rep['scenes'][nm] = {'samples': Ns[i], 'joint_start_s': a / SR, 'music_in_scene_s': in_s, 'end': endd, 'sfx_null_vs_m2': null,
                             'sfx': [{k: r[k] for k in ('id', 'frame', 'gain_applied_db', 'hit_scene_s')} for r in srep]}
    json.dump(rep, open(f'{OUT}/s06-s07-m3-placements.json', 'w'), indent=1, default=float)
    print(f"cue {L_hp:.2f} LUFS at {m['hp']} Hz, eq {L_cue - L_hp:+.2f} dB, normalised {g_norm:+.2f} dB to {m['norm_lufs']}; {len(y) / SR:.2f} s")
    print(f"s06: track {pl['track_in']} at {pl['scene_in']} s (scene = track - {(a0 - s0) / SR:.4f}); track at s06 end {(N06 - s0 + a0) / SR:.4f}")
    lr = rep['loop']
    print(f"loop bar {lp['from_bar']} {tA:.4f} -> bar {lp['to_bar']} {tB:.4f} (shift {shift} samples) at joint {nA / SR:.4f} = s07 {lr['s07_s']:.4f}; "
          f"crossfade joint {xs / SR:.4f}-{xe / SR:.4f}; track at s07 end {lr['track_at_s07_end']:.3f}; cue used {rep['cue_used_s']:.2f} s")
    print(f"level: X {comp:+.3f} dB at the cut -> {L} dB by s07 {lv['ramp_down_s']} s; alley cut s07 {alley:.4f}, back to 0 dB at bar "
          f"{lv['ramp_up_to_bar']} s07 {t_up:.4f} (ramp {r_up:.3f} s)")
    for nm, bb in rep['bars'].items():
        print(f'  bars {nm}: ' + ', '.join(f'{k} {v:.3f}' if v is not None else f'{k} -' for k, v in bb.items()))
    print('intro check:', json.dumps(intro))
    print('highs check:', json.dumps(hi))
    for nm, r in rep['scenes'].items():
        print(f"{nm}: sfx null vs m2 residual peak {r['sfx_null_vs_m2']['residual_peak_dbfs']:.1f} dBFS; " + ', '.join(f"{x['id']} {x['gain_applied_db']} dB" for x in r['sfx']))


if __name__ == '__main__':
    main()
