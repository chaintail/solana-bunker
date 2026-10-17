#!/usr/bin/env python3
"""Runs on do-box with a matplotlib venv (e.g. ~/venvs/gantt-chart). Opening v11 level plot from verify-v11.py's CSV (100 ms RMS, 50 ms hop, final stems):
the voices, the music and the stings over time, the guard line (voice - 16 dB where the voice is active, >= -30 dBFS) and the picture events.
usage: levels-plot-v11.py <levels.csv> <out.png>"""
import sys, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d = np.genfromtxt(sys.argv[1], delimiter=',', names=True); t = d['t']
C = dict(voice='#2a78d6', music='#eb6834', stings='#1baf7a', ink='#3d3d3a', muted='#8a8980', grid='#e4e3dd')
EV = [(4.300, 'WARNING card'), (15.867, 'ident'), (17.267, 'slam'), (18.067, 'desk'), (18.347, 'first word'), (52.433, 'SPECIAL REPORT'), (53.217, 'announcer')]
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': C['muted'], 'axes.labelcolor': C['ink'], 'xtick.color': C['ink'], 'ytick.color': C['ink']})
fig = plt.figure(figsize=(15, 8.2), dpi=130, facecolor='white'); gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 1], hspace=0.38, wspace=0.12)
def panel(ax, x0, x1, title, labels):
    k = (t >= x0) & (t <= x1); act = d['voice'] >= -30
    for name in ('voice', 'music', 'stings'): ax.plot(t[k], np.maximum(d[name][k], -80), color=C[name], lw=1.3 if name != 'stings' else 1.0, label={'voice': 'voices (sponsor, advisory, Liam, announcer)', 'music': 'music (groove, news bed)', 'stings': 'stings (jingles A, C)'}[name])
    g = np.where(act, d['voice'] - 16, np.nan); ax.plot(t[k], g[k], color=C['muted'], lw=0.9, ls='--', label='guard: voice - 16 dB (voice active)')
    for x, s in EV:
        if x0 <= x <= x1: ax.axvline(x, color=C['grid'], lw=1, zorder=0); labels and ax.text(x, -79, ' ' + s, rotation=90, va='bottom', ha='right', fontsize=7.5, color=C['muted'])
    ax.set_xlim(x0, x1); ax.set_ylim(-80, -5); ax.set_ylabel('RMS, dBFS (100 ms)'); ax.set_xlabel('film time, s'); ax.set_title(title, loc='left', fontsize=10, color=C['ink'])
    ax.grid(axis='y', color=C['grid'], lw=0.6); ax.spines[['top', 'right']].set_visible(False)
ax = fig.add_subplot(gs[0, :]); panel(ax, 0, 54.567, 'Opening v11, final stems at -16 LUFS', True)
ax.legend(loc='upper center', ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.13), fontsize=8.5)
panel(fig.add_subplot(gs[1, 0]), 0, 5.2, 'Sponsor read: groove 0.26-4.30 s, tail to 4.80, advisory dry', True)
panel(fig.add_subplot(gs[1, 1]), 41.5, 54.567, 'Desk end: gap rise 44.5 s, dip from 51.4 s, bed out at 52.43 s', True)
fig.savefig(sys.argv[2], facecolor='white', bbox_inches='tight')
