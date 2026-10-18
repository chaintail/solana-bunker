#!/usr/bin/env python3
"""s06 + s07 m3: prove the join is continuous. Runs on do-box (/home/claude/venvs/manim; ffmpeg audio only).
usage: continuity-m3.py <m3-noir.json> <work root> <work dir> <out.json>      (reads music-m3-noir.py's and finish-m3.py's files in <work dir>, prefixes s06-m3 / s07-m3)
  1. render == split: the two scenes' delivered music stems (finish-m3.py's .f32 stems) divided by their scene gains concatenate to the unsplit
     render sample for sample.
  2. delivered music across the cut: the level step at the cut (s07 gain + join compensation - s06 gain); the sample step |d[cut] - d[cut-1]|
     against the sample steps within +-0.5 s; the 6 kHz high-passed energy in the 2 ms around the cut against all 2 ms windows within +-0.5 s
     (a click would stand out).
  3. the two final wavs concatenated: the same click test on the full program, and the limiter's deviation from the stem sum within +-100 ms
     of the cut (the limiter restarts in each scene; 0 = it is not acting there).
  4. s06 music before m2's old fade (19.40 s) against m2's delivered s06 music (both divided by their scene gains): m3 is m2 there.
  5. the loop crossfade: the same click test around it on the unsplit render, and on the cue itself (filtered, unlooped) at both downbeats
     (the downbeat's own attack is the reference: the loop should look like either of them).
  Contrast for 2: the same click test on the unsplit render at the cut. The render carries the join compensation as a step at the cut (cancelled
  by the scene gains in the delivered stems), so it shows what an uncompensated scene-gain step looks like."""
import sys, os, json, importlib.util
import numpy as np
from scipy.signal import butter, sosfilt

here = os.path.dirname(os.path.abspath(__file__))
s_ = importlib.util.spec_from_file_location('m4', os.path.join(here, 'music-m4.py')); M = importlib.util.module_from_spec(s_); s_.loader.exec_module(M)
spec = json.load(open(sys.argv[1])); M.ROOT = sys.argv[2]; W, OUTJ = sys.argv[3], sys.argv[4]; SR = 48000
pl = json.load(open(f'{W}/s06-s07-m3-placements.json')); cut = pl['cut_sample']; comp = pl['level']['join_comp_db']
G = {s: json.load(open(f'{W}/{s}-m3-loudness.json'))['linear_gain_db'] for s in ('s06', 's07')}
un = M.read(f'{W}/s06-s07-m3-music-unsplit.wav')
mu = {s: M.read(f'{W}/{s}-m3-music.f32.wav') for s in ('s06', 's07')}
st = {s: {k: M.read(f'{W}/{s}-m3-{k}.f32.wav') for k in ('dialogue', 'sfx')} for s in ('s06', 's07')}
fin = {s: M.read(f'{W}/{s}-m3-final.wav') for s in ('s06', 's07')}
hp6 = butter(4, 6000, 'hp', fs=SR, output='sos')


def click(x, at, half=0.5, w=0.002):
    """sample step at `at` and the 6 kHz high-passed 2 ms energy around it, each against the same within +-half s"""
    a, b = at - int(half * SR), at + int(half * SR); seg = x[a:b]; k = at - a
    dd = np.abs(np.diff(seg)); step = dd[k - 1]
    h = sosfilt(hp6, seg) ** 2; n = int(w * SR); c = np.concatenate([[0.0], np.cumsum(h)])
    e = 10 * np.log10((c[n:] - c[:-n]) / n + 1e-30); ec = e[k - n // 2]
    return {'sample_step': float(step), 'sample_step_percentile_in_window': round(float((dd < step).mean() * 100), 1),
            'sample_step_median_in_window': float(np.median(dd)), 'hf_2ms_db_at': round(float(ec), 2),
            'hf_2ms_db_median': round(float(np.median(e)), 2), 'hf_2ms_percentile_in_window': round(float((e < ec).mean() * 100), 1), 'hf_2ms_db_p99': round(float(np.percentile(e, 99)), 2),
            'hf_2ms_at_minus_median_db': round(float(ec - np.median(e)), 2)}


r = {'scene_gain_db': G, 'join_comp_db': comp}
cat = np.concatenate([mu['s06'] / 10 ** (G['s06'] / 20), mu['s07'] / 10 ** (G['s07'] / 20)])
r['render_eq_split'] = {'unsplit_samples': len(un), 'split_samples': [len(mu['s06']), len(mu['s07'])], 'cut_sample': cut,
                        'max_abs_diff': float(np.abs(cat - un).max()) if len(cat) == len(un) else 'length mismatch', 'unsplit_peak': float(np.abs(un).max())}
d = np.concatenate([mu['s06'], mu['s07']])
r['delivered_music'] = {'level_step_at_cut_db': round(G['s07'] + comp - G['s06'], 3), **click(d, cut)}
r['unsplit_render_at_cut_with_comp_step'] = click(un, cut)
F = np.concatenate([fin['s06'], fin['s07']])
S = np.concatenate([st['s06']['dialogue'] + mu['s06'] + st['s06']['sfx'], st['s07']['dialogue'] + mu['s07'] + st['s07']['sfx']])
a, b = cut - 4800, cut + 4800
r['final_concat'] = {**click(F, cut), 'limiter_dev_pm100ms_max_db': round(float(20 * np.log10(np.abs(F[a:b] - S[a:b]).max() / np.abs(S[a:b]).max() + 1e-12)), 1),
                     'limiter_dev_pm100ms_max_abs': float(np.abs(F[a:b] - S[a:b]).max()), 'program_peak_pm100ms': float(np.abs(S[a:b]).max())}
sc6 = spec['scenes'][0]['ref']; m2 = M.read(sc6['stems'] + '-music.wav'); g2 = json.load(open(M.path(sc6['loudness'])))['linear_gain_db']
n = int(19.40 * SR); x3 = mu['s06'][:n] / 10 ** (G['s06'] / 20); x2 = m2[:n] / 10 ** (g2 / 20)
r['s06_vs_m2_before_19_40'] = {'max_abs_diff': float(np.abs(x3 - x2).max()), 'diff_re_peak_db': round(float(20 * np.log10(np.abs(x3 - x2).max() / np.abs(x2).max())), 1),
                               'note': 'm2 stem is 24-bit at m2 gain; diff at the 24-bit floor = identical'}
lx = int(round(pl['loop']['joint_s'] * SR))
r['loop_unsplit'] = click(un, lx - int(0.005 * SR))
m = spec['music']; y = M.eq(M.hp(M.read(m['file']), m['hp']), m['eq']); y = y * np.abs(un).max() / np.abs(y).max()
for k in ('from', 'to'):
    r[f'loop_cue_{k}_bar_unlooped'] = click(y, int(round(pl['loop'][f'{k}_track_s'] * SR)) - int(0.005 * SR))
json.dump(r, open(OUTJ, 'w'), indent=1)
print(json.dumps(r, indent=1))
