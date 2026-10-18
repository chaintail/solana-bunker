#!/usr/bin/env python3
"""v13 level plot: plot-levels-m4.py with the reference relabelled. verify-m4.py is run with spec.ref = m4c's delivered stems with the same two
spans removed (in its "m2" slot), so "ref" below is m4c cut the same way. Runs on do-box (/home/claude/venvs/manim, matplotlib).
usage: plot-levels-v13.py <out.png> <name>=<levels.npz> [<name>=<levels.npz> ...]
Rows: per variant, 100 ms RMS (10 ms hop) of the dialogue, music and sfx stems at delivery level with the sidechain (right axis) and the picture
events; dialogue minus music where the dialogue is >= -30 dBFS (m2 and the variants, 12 / 16 dB lines); music short-term loudness (3 s) as
delivered, m2 vs the variants (frame-0 start, intro levelling); music per-bin spectrum in clock-tick frames, m2 vs m4 (the high cut), with the
dialogue's spectrum."""
import sys, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

out = sys.argv[1]; V = [(a.split('=', 1)[0], np.load(a.split('=', 1)[1], allow_pickle=False)) for a in sys.argv[2:]]
C = {'dialogue': '#2a78d6', 'music': '#eb6834', 'sfx': '#1baf7a', 'm2': '#9a9890', 'duck': '#7d4cc2'}
REF = 'm4c (same cuts)'
VC = ['#eb6834', '#b8336a', '#2f8f5b']
INK, MUTED, GRID = '#1f1f1e', '#6b6a64', '#e4e3dd'
plt.rcParams.update({'font.size': 10, 'axes.edgecolor': GRID, 'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': MUTED})
nv = len(V)
fig = plt.figure(figsize=(21, 5.0 * nv + 9), dpi=100)
gs = fig.add_gridspec(nv + 2, 2, height_ratios=[2.2] * nv + [1.6, 2.0], width_ratios=[3, 1.2])
fl = lambda x: np.maximum(x, -80)
ax0 = None
z0 = V[0][1]; ev = json.loads(str(z0['events']))
for i, (nm, z) in enumerate(V):
    a = fig.add_subplot(gs[i, :], sharex=ax0); ax0 = ax0 or a
    t = z['m4_t']; st = json.loads(str(z['stats'])); g = st['guard']['m4_100ms_active30']; lv = st['levels']
    a.plot(t, fl(z['m4_D']), color=C['dialogue'], lw=1.0, label='dialogue')
    a.plot(t, fl(z['m2_M']), color=C['m2'], lw=1.0, label=REF + ' music')
    a.plot(t, fl(z['m4_M']), color=C['music'], lw=1.8, label=f'{nm} music')
    a.plot(t, fl(z['m4_S']), color=C['sfx'], lw=1.2, label='sfx')
    a.set_ylim(-80, 0); a.set_ylabel('dBFS (100 ms RMS)'); a.grid(axis='y', color=GRID, lw=0.6)
    a.set_title(f"{nm}: m4c treatment (music +{float(z['extra_db']):.0f} dB over m2 under speech, cue {lv['music_under_lufs_re_cue']:.1f} LUFS, from frame 0); "
                f"dialogue - music (100 ms, dlg >= -30 dBFS) median {g['median_db']:.1f} / p05 {g['p05_db']:.1f} / min {g['min_db']:.1f} dB; "
                f"dialogue {lv['dialogue_drop_vs_m2_db']['loudness_gain']:+.2f} dB vs m4c", loc='left', color=INK, fontsize=10.5)
    a.legend(loc='upper right', frameon=False, ncol=5)
    for e in ev:
        a.axvline(e['t'], color=MUTED, lw=0.6, ls=':', zorder=0)
    b = a.twinx(); b.fill_between(t, 0, z['m4_frac'], color=C['duck'], alpha=0.12, lw=0); b.set_ylim(0, 4); b.set_yticks([0, 1])
    b.set_ylabel('sidechain\n(1 = ducked)', color=C['duck']); b.tick_params(axis='y', colors=C['duck'])
    for s in ('top', 'right'):
        b.spines[s].set_visible(False)
key = [f"{e['t']:.3f}  {e['name']}" for e in sorted(ev, key=lambda e: e['t'])]
ax0.text(1.005, 1.0, '\n'.join(key), transform=ax0.transAxes, fontsize=7.5, color=INK, va='top', ha='left', family='monospace')
a = fig.add_subplot(gs[nv, :], sharex=ax0)
rows = [(REF, z0['m2_t'], z0['m2_D'], z0['m2_M'], float(z0['m2_gain']), C['m2'])] + [(nm, z['m4_t'], z['m4_D'], z['m4_M'], float(z['m4_gain']), VC[i]) for i, (nm, z) in enumerate(V)]
for nm, t, D, Mu, g, col in rows:
    mg = np.where(D - g >= -30, D - Mu, np.nan)
    a.plot(t, mg, color=col, lw=0.9, label=f'{nm} dialogue - music (median {np.nanmedian(mg):.1f} dB)')
for y in (12, 16):
    a.axhline(y, color=INK, lw=0.8, ls='--'); a.text(0.2, y + 0.6, f'{y} dB', fontsize=8, color=INK)
a.set_ylim(-10, 45); a.set_ylabel('dialogue - music, dB\n(dialogue >= -30 dBFS)'); a.grid(axis='y', color=GRID, lw=0.6); a.legend(loc='upper right', frameon=False, ncol=3)
a.set_xlim(-0.1, float(z0['m4_t'][-1]) + 0.2); a.set_xlabel('scene seconds')
a = fig.add_subplot(gs[nv + 1, 0])
a.plot(z0['st_t'], np.maximum(z0['st_m2'], -60), color=C['m2'], lw=1.4, label=REF + ' music (delivered)')
for i, (nm, z) in enumerate(V):
    a.plot(z['st_t'], np.maximum(z['st_m4'], -60), color=VC[i], lw=1.6, label=f'{nm} music (delivered, ducked)')
    a.plot(z['st_t'], np.maximum(z['st_m4_preduck'], -60), color=VC[i], lw=0.9, ls='--', label=f'{nm} music before the sidechain')
a.set_xlim(-0.1, float(z0['m4_t'][-1]) + 0.2); a.set_ylim(-60, -10); a.set_ylabel('music short-term LUFS (3 s)'); a.set_xlabel('scene seconds')
a.grid(color=GRID, lw=0.6); a.legend(loc='lower right', frameon=False, ncol=2, fontsize=8.5); a.set_title('music short-term loudness (3 s): v13 against m4c with the same spans removed (m4c has a splice at each cut, v13 a continuous cue)', loc='left', color=INK, fontsize=10.5)
a = fig.add_subplot(gs[nv + 1, 1])
f = z0['fq'] / 1000; sm = lambda x: np.convolve(x, np.ones(5) / 5, mode='same')
a.plot(f, sm(z0['sp_m2']), color=C['m2'], lw=1.2, label=REF + ' music')
a.plot(f, sm(z0['sp_m4']), color=VC[0], lw=1.2, label=f'{V[0][0]} music')
a.plot(f, sm(z0['sp_dlg']), color=C['dialogue'], lw=0.9, label='dialogue')
a.axvspan(12, 17.2, color='#f2c94c', alpha=0.25, lw=0); a.text(12.2, -30, 'tick band\n12-17.2 kHz', fontsize=8, color=INK)
a.set_xlim(2, 20); a.set_ylim(-140, -20); a.set_xlabel('kHz'); a.set_ylabel('dB per bin (clock-tick frames)'); a.grid(color=GRID, lw=0.6)
a.legend(loc='lower left', frameon=False, fontsize=8.5); a.set_title('highs: shelf 6 kHz -6, shelf 11 kHz -8, notch 16.8 kHz', loc='left', color=INK, fontsize=10.5)
for a in fig.axes:
    for s in ('top',):
        a.spines[s].set_visible(False)
fig.suptitle('Conspiracy ' + ', '.join(nm for nm, _ in V) + ' (two script cuts, 55.333 s, 1660 frames) vs ' + REF, x=0.01, ha='left', color=INK, fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.98))
fig.savefig(out, facecolor='white')
print('wrote', out)
