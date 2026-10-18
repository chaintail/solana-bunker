#!/usr/bin/env python3
"""m1 level plot. Runs on do-box (python3 + matplotlib; plotting only, no media tools). Input: levels.npz from verify-m1.py.
usage: plot-levels-m1.py <levels.npz> <out.png>
Top: 100 ms RMS (10 ms hop) of the dialogue, music and sfx stems in dBFS, with the picture events marked. Bottom: dialogue minus music where the
dialogue is >= -30 dBFS, against the 16 dB guard."""
import sys, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

z = np.load(sys.argv[1], allow_pickle=False)
t, D, M, S = z['t'], z['dialogue'], z['music'], z['sfx']
ev = json.loads(str(z['events'])); title = str(z['title'])
C = {'dialogue': '#2a78d6', 'music': '#eb6834', 'sfx': '#1baf7a'}
INK, MUTED, GRID = '#1f1f1e', '#6b6a64', '#e4e3dd'
plt.rcParams.update({'font.size': 10, 'axes.edgecolor': GRID, 'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': MUTED})
fig, (a1, a2) = plt.subplots(2, 1, figsize=(21, 8.5), sharex=True, gridspec_kw={'height_ratios': [3, 1.3]}, dpi=110)
fl = lambda x: np.maximum(x, -80)
a1.plot(t, fl(D), color=C['dialogue'], lw=1.2, label='dialogue (delivered mix)')
a1.plot(t, fl(M), color=C['music'], lw=2, label='music')
a1.plot(t, fl(S), color=C['sfx'], lw=1.6, label='sfx')
key = []
for i, e in enumerate(sorted(ev, key=lambda e: e['t']), 1):     # numbered markers (events cluster within a few frames), names in a key
    a1.axvline(e['t'], color=MUTED, lw=0.6, ls=':', zorder=0)
    a1.text(e['t'], -78 + 6 * ((i - 1) % 3), str(i), fontsize=8, color=INK, ha='center', va='bottom',
            bbox=dict(boxstyle='round,pad=0.15', fc='white', ec=GRID, lw=0.6))
    key.append(f"{i}  {e['t']:.3f}  {e['name']}")
a1.text(1.005, 1.0, '\n'.join(key), transform=a1.transAxes, fontsize=7.5, color=INK, va='top', ha='left', family='monospace')
a1.set_ylim(-80, 0); a1.set_ylabel('dBFS (100 ms RMS)'); a1.grid(axis='y', color=GRID, lw=0.6)
a1.legend(loc='upper right', frameon=False, ncol=3)
a1.set_title(title, loc='left', color=INK, fontsize=12)
act = D - float(z['stem_gain_db']) >= -30
mg = np.where(act, D - M, np.nan)
a2.plot(t, mg, color=C['dialogue'], lw=1)
a2.axhline(16, color=INK, lw=1, ls='--')
a2.text(t[0], 16.8, '16 dB guard', fontsize=8, color=INK)
k = np.nanargmin(mg)
a2.plot([t[k]], [mg[k]], 'o', ms=6, color=INK)
a2.annotate(f'min {mg[k]:.1f} dB at {t[k]:.2f} s', (t[k], mg[k]), xytext=(8, -14), textcoords='offset points', fontsize=8.5, color=INK)
a2.set_ylim(0, 60); a2.set_ylabel('dialogue - music, dB\n(dialogue >= -30 dBFS)'); a2.set_xlabel('scene seconds')
a2.grid(axis='y', color=GRID, lw=0.6)
a2.set_xlim(t[0] - 0.1, t[-1] + 0.2)
for a in (a1, a2):
    for s in ('top', 'right'):
        a.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(sys.argv[2], facecolor='white')
print('wrote', sys.argv[2])
