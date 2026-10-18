#!/usr/bin/env python3
"""m3 level plot (one scene against its previous build, m2): plot-levels-m2.py relabelled. Runs on do-box (/home/claude/venvs/manim, matplotlib). Input: levels.npz from verify-m3.py.
usage: plot-levels-m3.py <out.png> <levels.npz> <scene label>
Rows: 100 ms RMS (10 ms hop) of the dialogue, the ref music, the m3 music and the sfx at delivery level, with the sidechain (right axis) and the picture
events; dialogue minus music where the dialogue is >= -30 dBFS and the music plays (ref and m3, 12 / 16 dB lines); music short-term loudness (3 s), ref
vs m3 (delivered and before the sidechain); long-term music spectrum ref vs m3 (the high cut) with the dialogue's."""
import sys, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

out, z, label = sys.argv[1], np.load(sys.argv[2], allow_pickle=False), sys.argv[3]
C = {'dialogue': '#2a78d6', 'music': '#eb6834', 'sfx': '#1baf7a', 'ref': '#9a9890', 'duck': '#7d4cc2'}
INK, MUTED, GRID = '#1f1f1e', '#6b6a64', '#e4e3dd'
plt.rcParams.update({'font.size': 10, 'axes.edgecolor': GRID, 'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': MUTED})
st = json.loads(str(z['stats'])); ev = json.loads(str(z['events'])); rn = str(z['ref_name']); g = st['guard']['m3_100ms_active30']; gr = st['guard']['ref_100ms_active30']
lv = st['levels']; T = float(z['m3_t'][-1]) + 0.2
fig = plt.figure(figsize=(21, 16), dpi=100)
gs = fig.add_gridspec(3, 2, height_ratios=[2.4, 1.6, 2.0], width_ratios=[3, 1.2])
fl = lambda x: np.maximum(x, -80)
a = fig.add_subplot(gs[0, :]); ax0 = a; t = z['m3_t']
a.plot(t, fl(z['m3_D']), color=C['dialogue'], lw=1.0, label='dialogue')
a.plot(z['ref_t'], fl(z['ref_M']), color=C['ref'], lw=1.0, label=f'{rn} music')
a.plot(t, fl(z['m3_M']), color=C['music'], lw=1.8, label='m3 music')
a.plot(t, fl(z['m3_S']), color=C['sfx'], lw=1.0, label='sfx / stings')
a.set_ylim(-80, 0); a.set_ylabel('dBFS (100 ms RMS)'); a.grid(axis='y', color=GRID, lw=0.6)
a.set_title(f"{label} m3: music under speech at {lv['under_lufs_re_cue']:.1f} LUFS cue loudness, +5 dB between words (sidechain 30 ms / 300 ms); "
            f"dialogue - music (100 ms, dlg >= -30 dBFS, music playing) median {g['median_db']:.1f} / p05 {g['p05_db']:.1f} / min {g['min_db']:.1f} dB "
            f"({rn}: {gr['median_db']:.1f} / {gr['p05_db']:.1f} / {gr['min_db']:.1f})", loc='left', color=INK, fontsize=10.5)
a.legend(loc='upper right', frameon=False, ncol=4)
for e in ev:
    a.axvline(e['t'], color=MUTED, lw=0.6, ls=':', zorder=0)
b = a.twinx(); b.fill_between(t, 0, z['m3_frac'], color=C['duck'], alpha=0.12, lw=0); b.set_ylim(0, 4); b.set_yticks([0, 1])
b.set_ylabel('sidechain\n(1 = ducked)', color=C['duck']); b.tick_params(axis='y', colors=C['duck'])
key = [f"{e['t']:.3f}  {e['name'][:44]}" for e in sorted(ev, key=lambda e: e['t'])]
a.text(1.005, 1.0, '\n'.join(key), transform=a.transAxes, fontsize=7.5, color=INK, va='top', ha='left', family='monospace')
a.set_xlim(-0.1, T)
a = fig.add_subplot(gs[1, :], sharex=ax0)
for nm, col, gg in ((rn, C['ref'], float(z['ref_gain'])), ('m3', C['music'], float(z['m3_gain']))):
    p = 'ref' if nm == rn else 'm3'; D, Mu = z[f'{p}_D'], z[f'{p}_M']
    mg = np.where((D - gg >= -30) & (Mu > -90), D - Mu, np.nan)
    a.plot(z[f'{p}_t'], mg, color=col, lw=0.9, label=f'{nm} dialogue - music (median {np.nanmedian(mg):.1f} dB)')
for y in (12, 16):
    a.axhline(y, color=INK, lw=0.8, ls='--'); a.text(0.2, y + 0.6, f'{y} dB', fontsize=8, color=INK)
a.set_ylim(-10, 50); a.set_ylabel('dialogue - music, dB\n(dialogue >= -30 dBFS)'); a.grid(axis='y', color=GRID, lw=0.6); a.legend(loc='upper right', frameon=False, ncol=2)
a.set_xlabel('scene seconds')
a = fig.add_subplot(gs[2, 0], sharex=ax0)
a.plot(z['st_t'], np.maximum(z['st_ref'], -60), color=C['ref'], lw=1.4, label=f'{rn} music (delivered)')
a.plot(z['st_t'], np.maximum(z['st_m3'], -60), color=C['music'], lw=1.6, label='m3 music (delivered, ducked)')
a.plot(z['st_t'], np.maximum(z['st_m3_preduck'], -60), color=C['music'], lw=0.9, ls='--', label='m3 music before the sidechain')
a.set_ylim(-60, -10); a.set_ylabel('music short-term LUFS (3 s)'); a.set_xlabel('scene seconds')
a.grid(color=GRID, lw=0.6); a.legend(loc='lower right', frameon=False, ncol=3, fontsize=8.5); a.set_title('music short-term loudness (intro levelled, no swells or dips)', loc='left', color=INK, fontsize=10.5)
a = fig.add_subplot(gs[2, 1])
f = z['fq'] / 1000; sm = lambda x: np.convolve(x, np.ones(5) / 5, mode='same')
a.plot(f, sm(z['sp_ref']), color=C['ref'], lw=1.2, label=f'{rn} music')
a.plot(f, sm(z['sp_m3']), color=C['music'], lw=1.2, label='m3 music')
a.plot(f, sm(z['sp_dlg']), color=C['dialogue'], lw=0.9, label='dialogue')
a.set_xscale('log'); a.set_xlim(0.04, 22); a.set_ylim(-150, -40); a.set_xlabel('kHz'); a.set_ylabel('dB per bin (music playing)'); a.grid(color=GRID, lw=0.6)
a.legend(loc='lower left', frameon=False, fontsize=8.5); a.set_title('music spectrum: HP 100 Hz, shelf 6 kHz -6, shelf 11 kHz -8', loc='left', color=INK, fontsize=10.5)
for a in fig.axes:
    a.spines['top'].set_visible(False)
fig.suptitle(str(z['title']), x=0.01, ha='left', color=INK, fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.98))
fig.savefig(out, facecolor='white')
print('wrote', out)
