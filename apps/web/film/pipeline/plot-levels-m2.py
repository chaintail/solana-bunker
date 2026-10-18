#!/usr/bin/env python3
"""m1 vs m2 level plot. Runs on do-box (/home/claude/venvs/manim, matplotlib). Input: levels.npz from verify-m2.py.
usage: plot-levels-m2.py <levels.npz> <out.png>
Rows: m1 and m2, 100 ms RMS (10 ms hop) of the dialogue, music and sfx stems at delivery level (m1's stems plus m1's loudness gain), with the
picture events; m2 also shows the sidechain (duck fraction, right axis). Bottom: dialogue minus music where the dialogue is >= -30 dBFS, m1 and m2,
against m1's 16 dB and m2's 12 dB guard targets."""
import sys, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

z = np.load(sys.argv[1], allow_pickle=False)
ev = json.loads(str(z['events'])); title = str(z['title'])
G1, G2 = float(z['m1_gain']), float(z['m2_gain'])
C = {'dialogue': '#2a78d6', 'music': '#eb6834', 'sfx': '#1baf7a', 'm1': '#9a9890', 'duck': '#7d4cc2'}
INK, MUTED, GRID = '#1f1f1e', '#6b6a64', '#e4e3dd'
plt.rcParams.update({'font.size': 10, 'axes.edgecolor': GRID, 'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': MUTED})
fig, ax = plt.subplots(3, 1, figsize=(21, 11.5), sharex=True, gridspec_kw={'height_ratios': [2.2, 2.2, 1.6]}, dpi=110)
fl = lambda x: np.maximum(x, -80)
for a, k, g, lab in ((ax[0], 'm1', G1, 'm1: -20 under speech, -14 in gaps >= 0.8 s, swells, 16.5 dB guard ducks (180 Hz HP)'),
                     (ax[1], 'm2', 0.0, 'm2: m1\'s gap level under speech, +5 dB between words (30 ms / 300 ms sidechain, 100 Hz HP, cue at -18 LUFS)')):
    t = z[f'{k}_t']
    a.plot(t, fl(z[f'{k}_D'] + g), color=C['dialogue'], lw=1.0, label='dialogue')
    a.plot(t, fl(z[f'{k}_M'] + g), color=C['music'], lw=1.8, label='music')
    a.plot(t, fl(z[f'{k}_S'] + g), color=C['sfx'], lw=1.4, label='sfx')
    a.set_ylim(-80, 0); a.set_ylabel('dBFS (100 ms RMS)'); a.grid(axis='y', color=GRID, lw=0.6)
    a.set_title(lab, loc='left', color=INK, fontsize=11)
    a.legend(loc='upper right', frameon=False, ncol=4)
    for e in ev:
        a.axvline(e['t'], color=MUTED, lw=0.6, ls=':', zorder=0)
b = ax[1].twinx(); b.fill_between(z['m2_t'], 0, z['m2_frac'], color=C['duck'], alpha=0.12, lw=0); b.set_ylim(0, 4); b.set_yticks([0, 1])
b.set_ylabel('sidechain\n(1 = ducked)', color=C['duck']); b.tick_params(axis='y', colors=C['duck'])
for s in ('top', 'right'):
    b.spines[s].set_visible(False)
key = [f"{e['t']:.3f}  {e['name']}" for e in sorted(ev, key=lambda e: e['t'])]
ax[0].text(1.005, 1.0, '\n'.join(key), transform=ax[0].transAxes, fontsize=7.5, color=INK, va='top', ha='left', family='monospace')
fig.suptitle(title, x=0.01, ha='left', color=INK, fontsize=12)
a = ax[2]
for k, g, col, lw in (('m1', G1, C['m1'], 0.9), ('m2', G2, C['dialogue'], 1.0)):
    D, M = z[f'{k}_D'], z[f'{k}_M']
    act = D - (0.0 if k == 'm1' else g) >= -30
    mg = np.where(act, D - M, np.nan); t = z[f'{k}_t']
    a.plot(t, mg, color=col, lw=lw, label=f'{k} dialogue - music')
    i = np.nanargmin(mg); a.plot([t[i]], [mg[i]], 'o', ms=5, color=col)
    a.annotate(f'{k} min {mg[i]:.1f} dB at {t[i]:.2f} s', (t[i], mg[i]), xytext=(8, -12 if k == 'm2' else 8), textcoords='offset points', fontsize=8.5, color=INK)
for y, s in ((16, 'm1 guard 16 dB'), (12, 'm2 target 12 dB')):
    a.axhline(y, color=INK, lw=0.9, ls='--'); a.text(0.2, y + 0.6, s, fontsize=8, color=INK)
a.set_ylim(-5, 55); a.set_ylabel('dialogue - music, dB\n(dialogue >= -30 dBFS)'); a.set_xlabel('scene seconds')
a.grid(axis='y', color=GRID, lw=0.6); a.legend(loc='upper right', frameon=False, ncol=2)
a.set_xlim(-0.1, float(z['m2_t'][-1]) + 0.2)
for a in ax:
    for s in ('top', 'right'):
        a.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(sys.argv[2], facecolor='white')
print('wrote', sys.argv[2])
