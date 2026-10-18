#!/usr/bin/env python3
"""s06 + s07 m3 levels on one timeline (joint seconds; s07 starts at 22.100). Runs on do-box (/home/claude/venvs/manim, matplotlib; ffmpeg audio only).
usage: plot-levels-m3.py <m3-noir.json> <work root> <work dir> <out.png> <out.json>
Sections: s06 (music from 0.236 s), lecture (s07 0 to the alley cut, frame 774), alley (from the alley cut). Per section, at delivery level (each
scene's stems times its loudness gain), 100 ms windows on a 10 ms hop as verify-m2.py: dialogue minus music where the dialogue is >= -30 dBFS
before the scene gain and the music plays (median, p05, min), music under speech and in open pauses (medians), and the level offset X.
Rows: 100 ms RMS of dialogue, music, sfx with m2's music and the sidechain; the music gain (dB re the -18 LUFS cue = under-speech LUFS + 18);
dialogue minus music, m2 vs m3, 12 / 16 dB lines; music short-term loudness (3 s) m2 vs m3; zooms on the delivered music at the cut and at
the loop crossfade."""
import sys, os, json, importlib.util
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

here = os.path.dirname(os.path.abspath(__file__))
s_ = importlib.util.spec_from_file_location('m4', os.path.join(here, 'music-m4.py')); M = importlib.util.module_from_spec(s_); s_.loader.exec_module(M)
spec = json.load(open(sys.argv[1])); M.ROOT = sys.argv[2]; W, PNG, OJ = sys.argv[3:6]; SR = 48000; hop = 480
pl = json.load(open(f'{W}/s06-s07-m3-placements.json')); cut = pl['cut_sample']; T6 = cut / SR
alley = T6 + pl['level']['alley_s07']; up_end = T6 + pl['level']['ramp_up_ends_s07']; loop = pl['loop']['joint_s']
sc = [s['name'] for s in spec['scenes']]
G = {s: json.load(open(f'{W}/{s}-m3-loudness.json'))['linear_gain_db'] for s in sc}
G2 = {s: json.load(open(M.path(x['ref']['loudness'])))['linear_gain_db'] for s, x in zip(sc, spec['scenes'])}
st = {k: np.concatenate([M.read(f'{W}/{s}-m3-{k}.f32.wav') for s in sc]) for k in ('dialogue', 'music', 'sfx')}
m2 = np.concatenate([np.pad(v := M.read(x['ref']['stems'] + '-music.wav'), (0, max(0, n - len(v))))[:n] for x, n in zip(spec['scenes'], pl['scene_samples'].values())])
gsc = np.concatenate([np.full(n, G[s]) for s, n in zip(sc, pl['scene_samples'].values())])
gsc2 = np.concatenate([np.full(n, G2[s]) for s, n in zip(sc, pl['scene_samples'].values())])
env = lambda y, w=4800: M.env_db(y, w, hop)
D, Mu, S, M2 = env(st['dialogue']), env(st['music']), env(st['sfx']), env(m2)
t = np.arange(len(D)) * hop / SR + 0.05
gw, gw2 = gsc[(np.arange(len(D)) * hop + 2400)], gsc2[(np.arange(len(D)) * hop + 2400)]
X = np.load(f'{W}/s06-s07-m3-xgain.npy'); frac = np.concatenate([np.load(f'{W}/{s}-m3-duckfrac.npy') for s in sc])
tx = np.arange(len(X)) / 1000
under = pl['level']['under_db_re_norm']; depth = pl['level']['open_db']
gain_trace = under + depth * (1 - frac) + X                    # dB re the -18 LUFS cue
sect = {'s06': (pl['place']['s06_scene_eq_track_minus'] * 0 + 0.236 + 0.1, T6), 'lecture': (T6, alley), 'alley': (alley, T6 + 33.14)}
fr_max = np.array([frac[max(0, int(x * 1000) - 50):int(x * 1000) + 50].max() for x in t])
rep = {'sections_joint_s': {k: [round(a, 3), round(b, 3)] for k, (a, b) in sect.items()}, 'scene_gain_db': G, 'm2_scene_gain_db': G2, 'sections': {}}
for k, (a, b) in sect.items():
    live = (t >= a) & (t < b)
    act = (D - gw >= -30) & (Mu > -100) & live
    dm = (D - Mu)[act]
    xs = X[int(a * 1000):int(b * 1000)]
    r = {'windows': int(act.sum()), 'dlg_minus_music_median_db': round(float(np.median(dm)), 2), 'dlg_minus_music_p05_db': round(float(np.percentile(dm, 5)), 2),
         'dlg_minus_music_min_db': round(float(dm.min()), 2), 'dlg_minus_music_min_at_joint_s': round(float(t[act][np.argmin(dm)]), 2),
         'music_under_speech_median_dbfs': round(float(np.median(Mu[act])), 2), 'X_db_range': [round(float(xs.min()), 2), round(float(xs.max()), 2)],
         'X_db_median': round(float(np.median(xs)), 2), 'under_speech_target_lufs': round(spec['music']['under_lufs'] + float(np.median(xs)), 2)}
    opn = (fr_max < 0.02) & live & (Mu > -100)
    if opn.any(): r['music_open_pauses_median_dbfs'] = round(float(np.median(Mu[opn])), 2)
    act2 = (D - gw >= -30) & (M2 > -100) & live
    if act2.sum() > 10:
        r['m2_dlg_minus_music_median_db'] = round(float(np.median((D - M2)[act2])), 2); r['m2_music_under_speech_median_dbfs'] = round(float(np.median(M2[act2])), 2)
    rep['sections'][k] = r
L = rep['sections']
rep['lecture_vs_s06_music_under_speech_db'] = round(L['lecture']['music_under_speech_median_dbfs'] - L['s06']['music_under_speech_median_dbfs'], 2)
rep['alley_vs_lecture_music_under_speech_db'] = round(L['alley']['music_under_speech_median_dbfs'] - L['lecture']['music_under_speech_median_dbfs'], 2)
json.dump(rep, open(OJ, 'w'), indent=1)
print(json.dumps(rep, indent=1))
# ---------------- plot
C = {'dialogue': '#2a78d6', 'music': '#eb6834', 'sfx': '#1baf7a', 'm2': '#9a9890', 'duck': '#7d4cc2', 'gain': '#b8326b'}
INK, MUTED, GRID = '#1f1f1e', '#6b6a64', '#e4e3dd'
plt.rcParams.update({'font.size': 10, 'axes.edgecolor': GRID, 'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': MUTED})
fig = plt.figure(figsize=(24, 16), dpi=100)
gs = fig.add_gridspec(4, 2, height_ratios=[2.4, 1.2, 1.6, 1.8], width_ratios=[3, 1.1])
fl = lambda x: np.maximum(x, -80); TT = t[-1] + 0.2
def marks(ax, lab=False):
    for x, nm, ls, lw in ((T6, 's06 | s07 cut', '-', 1.6), (loop, 'loop bar 29 -> bar 1', '--', 1.0), (alley, 'alley cut (s07 f774)', '-', 1.2), (up_end, 'bar 8', ':', 1.0)):
        ax.axvline(x, color=INK, lw=lw, ls=ls, zorder=1)
        if lab: ax.text(x + 0.12, 0.97, nm, transform=ax.get_xaxis_transform(), fontsize=8.5, color=INK, va='top', rotation=90)
a = fig.add_subplot(gs[0, :])
a.plot(t, fl(D), color=C['dialogue'], lw=1.0, label='dialogue'); a.plot(t, fl(M2), color=C['m2'], lw=1.0, label='m2 music')
a.plot(t, fl(Mu), color=C['music'], lw=1.8, label='m3 music'); a.plot(t, fl(S), color=C['sfx'], lw=1.2, label='sfx')
a.set_ylim(-80, 0); a.set_xlim(-0.1, TT); a.set_ylabel('dBFS (100 ms RMS, delivery level)'); a.grid(axis='y', color=GRID, lw=0.6); marks(a, True)
a.legend(loc='lower left', frameon=False, ncol=4)
b = a.twinx(); b.fill_between(tx, 0, frac, color=C['duck'], alpha=0.12, lw=0); b.set_ylim(0, 4); b.set_yticks([0, 1]); b.set_ylabel('sidechain (1 = ducked)', color=C['duck'])
for k, (x0, x1) in sect.items():
    r = L[k]; xm = {'s06': (x0 + x1) / 2, 'lecture': (x0 + x1) / 2, 'alley': TT - 0.1}[k]; a.text(xm, -3, f"{k}: dlg - music median {r['dlg_minus_music_median_db']:.1f} / p05 {r['dlg_minus_music_p05_db']:.1f} / min {r['dlg_minus_music_min_db']:.1f} dB\n"
                     f"music under speech {r['music_under_speech_median_dbfs']:.1f} dBFS, target {r['under_speech_target_lufs']:.1f} LUFS", ha='right' if k == 'alley' else 'center', va='top', fontsize=9, color=INK)
a.set_title(f"m3: one noir cue across s06 and s07, split at sample {cut} (joint {T6:.3f} s); lecture {rep['lecture_vs_s06_music_under_speech_db']:+.1f} dB vs s06 under speech, "
            f"alley {rep['alley_vs_lecture_music_under_speech_db']:+.1f} dB vs lecture; scene gains s06 {G['s06']:+.1f} / s07 {G['s07']:+.1f} dB, join compensation "
            f"{pl['level']['join_comp_db']:+.2f} dB", loc='left', color=INK, fontsize=10.5)
g = fig.add_subplot(gs[1, :], sharex=a)
gx = np.where(tx < T6, G['s06'], G['s07'])                    # delivered: each scene's loudness gain on top
g.plot(tx, gain_trace + spec['music']['norm_lufs'] + gx, color=C['gain'], lw=1.0, label='music gain as cue loudness incl. the scene loudness gain (LUFS): -29.3 + X under speech, +5 between words')
g.plot(tx, spec['music']['under_lufs'] + X + gx, color=INK, lw=1.2, ls='--', label='under speech: -29.3 + X + scene gain (continuous at the cut: X starts at the join compensation)')
g.set_ylim(-35, -21); g.set_ylabel('LUFS (cue)'); g.grid(color=GRID, lw=0.6); g.legend(loc='lower left', frameon=False, ncol=2, fontsize=8.5); marks(g)
a2 = fig.add_subplot(gs[2, :], sharex=a)
for nm, Mx, gg, col in (('m2', M2, gw2, C['m2']), ('m3', Mu, gw, C['music'])):
    mg = np.where((D - gg >= -30) & (Mx > -100), D - Mx, np.nan)
    a2.plot(t, mg, color=col, lw=0.9, label=f'{nm} dialogue - music')
for yv in (12, 16):
    a2.axhline(yv, color=INK, lw=0.8, ls='--'); a2.text(0.2, yv + 0.6, f'{yv} dB', fontsize=8, color=INK)
a2.set_ylim(-10, 50); a2.set_ylabel('dialogue - music, dB\n(dialogue >= -30 dBFS)'); a2.grid(axis='y', color=GRID, lw=0.6); a2.legend(loc='upper right', frameon=False, ncol=2); marks(a2)
a3 = fig.add_subplot(gs[3, 0], sharex=a)
s3, s2 = M.short_term(st['music']), M.short_term(m2); ts = np.arange(len(s3)) / 1000
a3.plot(ts, np.maximum(s2, -60), color=C['m2'], lw=1.3, label='m2 music'); a3.plot(ts, np.maximum(s3, -60), color=C['music'], lw=1.6, label='m3 music')
a3.set_ylim(-60, -15); a3.set_ylabel('music short-term LUFS (3 s)'); a3.set_xlabel('joint seconds (s07 = joint - 22.100)'); a3.grid(color=GRID, lw=0.6)
a3.legend(loc='lower right', frameon=False, fontsize=8.5); marks(a3)
z = fig.add_subplot(gs[3, 1])
k = np.arange(-2880, 961); y = st['music'][cut + k]
z.plot(k / 48, y, color=C['music'], lw=0.9, label='delivered music (s06 stem | s07 stem)'); z.axvline(0, color=INK, lw=1.2)
lx = int(round(loop * SR)); xf = pl['loop']['xfade_joint_s']
y2 = st['music'][lx + k]; sc2 = np.abs(y).max() / max(np.abs(y2).max(), 1e-9)
z.plot(k / 48, y2 * sc2 - 1.2 * np.abs(y).max() * 2, color=C['duck'], lw=0.8, label=f'loop (offset, x{sc2:.1f}); crossfade shaded')
z.axvspan((xf[0] * SR - lx) / 48, (xf[1] * SR - lx) / 48, color=C['duck'], alpha=0.12)
z.set_xlim(-60, 20); z.set_xlabel('ms from the cut (upper) / from the bar 1 downbeat (lower)'); z.set_yticks([]); z.legend(loc='upper left', frameon=False, fontsize=8)
z.set_title('join: delivered music across the cut, sample-continuous', loc='left', color=INK, fontsize=10)
for ax in fig.axes:
    ax.spines['top'].set_visible(False)
fig.suptitle(spec['title'], x=0.01, ha='left', color=INK, fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.98)); fig.savefig(PNG, facecolor='white'); print('wrote', PNG)
