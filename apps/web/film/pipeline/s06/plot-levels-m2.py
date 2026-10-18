#!/usr/bin/env python3
"""m2 level plot (one scene, m2 against its m1). Runs on do-box (/home/claude/venvs/manim, matplotlib). Input: levels.npz from verify-m2.py.
usage: plot-levels-m2.py <out.png> <levels.npz> <scene label>
Rows: 100 ms RMS (10 ms hop) of the dialogue, music and sfx stems at delivery level with m1's music and the sidechain (right axis) and the
picture events; dialogue minus music where the dialogue is >= -30 dBFS and the music plays, m1 vs m2 (12 / 16 dB lines); music short-term loudness (3 s), m1 vs
m2 (delivered and before the sidechain); music per-bin spectrum in high-band frames, m1 vs m2 (the high cut), with the dialogue's."""
import sys, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

out, npz, label = sys.argv[1], sys.argv[2], sys.argv[3]
z = np.load(npz, allow_pickle=False)
C = {'dialogue': '#2a78d6', 'music': '#eb6834', 'sfx': '#1baf7a', 'm1': '#9a9890', 'duck': '#7d4cc2'}
INK, MUTED, GRID = '#1f1f1e', '#6b6a64', '#e4e3dd'
plt.rcParams.update({'font.size': 10, 'axes.edgecolor': GRID, 'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': MUTED})
fig = plt.figure(figsize=(21, 14), dpi=100)
gs = fig.add_gridspec(3, 2, height_ratios=[2.4, 1.6, 2.0], width_ratios=[3, 1.2])
fl = lambda x: np.maximum(x, -80)
ev = json.loads(str(z['events'])); st = json.loads(str(z['stats'])); g = st['guard']['m2_100ms_active30']; g1 = st['guard']['m1_100ms_active30']; lv = st['levels']
T = float(z['m2_t'][-1]) + 0.2
a = fig.add_subplot(gs[0, :])
t = z['m2_t']
a.plot(t, fl(z['m2_D']), color=C['dialogue'], lw=1.0, label='dialogue')
a.plot(t, fl(z['m1_M']), color=C['m1'], lw=1.0, label='m1 music')
a.plot(t, fl(z['m2_M']), color=C['music'], lw=1.8, label='m2 music')
a.plot(t, fl(z['m2_S']), color=C['sfx'], lw=1.2, label='sfx')
a.set_ylim(-80, 0); a.set_ylabel('dBFS (100 ms RMS)'); a.grid(axis='y', color=GRID, lw=0.6); a.set_xlim(-0.1, T)
a.set_title(f"{label} m2: music under speech at cue {lv['music_under_lufs_re_cue']:.1f} LUFS (conspiracy m4c), {lv['music_under_speech_vs_m1_db']:+.1f} dB vs m1; "
            f"dialogue - music (100 ms, dlg >= -30 dBFS) median {g['median_db']:.1f} / p05 {g['p05_db']:.1f} / min {g['min_db']:.1f} dB "
            f"(m1 {g1['median_db']:.1f} / {g1['p05_db']:.1f} / {g1['min_db']:.1f})", loc='left', color=INK, fontsize=10.5)
a.legend(loc='upper right', frameon=False, ncol=5)
for e in ev:
    a.axvline(e['t'], color=MUTED, lw=0.6, ls=':', zorder=0)
b = a.twinx(); b.fill_between(t, 0, z['m2_frac'], color=C['duck'], alpha=0.12, lw=0); b.set_ylim(0, 4); b.set_yticks([0, 1])
b.set_ylabel('sidechain\n(1 = ducked)', color=C['duck']); b.tick_params(axis='y', colors=C['duck'])
for s in ('top', 'right'):
    b.spines[s].set_visible(False)
a.text(1.005, 1.0, '\n'.join(f"{e['t']:.3f}  {e['name']}" for e in sorted(ev, key=lambda e: e['t'])), transform=a.transAxes, fontsize=7.5, color=INK, va='top', ha='left', family='monospace')
a2 = fig.add_subplot(gs[1, :], sharex=a)
for nm, col in (('m1', C['m1']), ('m2', C['music'])):
    mg = np.where((z[f'{nm}_D'] - float(z[f'{nm}_gain']) >= -30) & (z[f'{nm}_M'] > -100), z[f'{nm}_D'] - z[f'{nm}_M'], np.nan)   # windows with music, as verify-m2.py
    a2.plot(z[f'{nm}_t'], mg, color=col, lw=0.9, label=f'{nm} dialogue - music (median {np.nanmedian(mg):.1f} dB)')
for y in (12, 16):
    a2.axhline(y, color=INK, lw=0.8, ls='--'); a2.text(0.2, y + 0.6, f'{y} dB', fontsize=8, color=INK)
a2.set_ylim(-10, 50); a2.set_ylabel('dialogue - music, dB\n(dialogue >= -30 dBFS)'); a2.grid(axis='y', color=GRID, lw=0.6); a2.legend(loc='upper right', frameon=False, ncol=2)
a2.set_xlabel('scene seconds')
a3 = fig.add_subplot(gs[2, 0])
a3.plot(z['st_t'], np.maximum(z['st_m1'], -60), color=C['m1'], lw=1.4, label='m1 music (delivered)')
a3.plot(z['st_t'], np.maximum(z['st_m2'], -60), color=C['music'], lw=1.6, label='m2 music (delivered, ducked)')
a3.plot(z['st_t'], np.maximum(z['st_m2_preduck'], -60), color=C['music'], lw=0.9, ls='--', label='m2 music before the sidechain')
a3.set_xlim(-0.1, T); a3.set_ylim(-60, -10); a3.set_ylabel('music short-term LUFS (3 s)'); a3.set_xlabel('scene seconds')
a3.grid(color=GRID, lw=0.6); a3.legend(loc='lower right', frameon=False, ncol=2, fontsize=8.5); a3.set_title('music short-term loudness, m1 vs m2', loc='left', color=INK, fontsize=10.5)
a4 = fig.add_subplot(gs[2, 1])
f = z['fq'] / 1000; sm = lambda x: np.convolve(x, np.ones(5) / 5, mode='same')
a4.plot(f, sm(z['sp_m1']), color=C['m1'], lw=1.2, label='m1 music')
a4.plot(f, sm(z['sp_m2']), color=C['music'], lw=1.2, label='m2 music')
a4.plot(f, sm(z['sp_dlg']), color=C['dialogue'], lw=0.9, label='dialogue')
eqs = json.loads(str(z['eq']))
a4.set_xlim(2, 20); a4.set_xlabel('kHz'); a4.set_ylabel('dB per bin (high-band frames)'); a4.grid(color=GRID, lw=0.6)
a4.legend(loc='lower left', frameon=False, fontsize=8.5)
a4.set_title('highs: ' + ', '.join(f"{'shelf' if b['type'] == 'highshelf' else 'notch'} {b['f'] / 1000:g} kHz {b['gain_db']:+g}" for b in eqs), loc='left', color=INK, fontsize=10)
for ax in fig.axes:
    ax.spines['top'].set_visible(False)
fig.suptitle(str(z['title']), x=0.01, ha='left', color=INK, fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.98))
fig.savefig(out, facecolor='white')
print('wrote', out)
