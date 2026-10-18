#!/usr/bin/env python3
"""Opening m2 music layer: v11's music plan with the conspiracy m4c treatment. Runs on do-box with /home/claude/venvs/manim (numpy, scipy);
ffmpeg for audio decoding only (-vn, via music-m4.py's read()).
usage: music-m2-opening.py <spec.json> <work root> <out prefix>
  spec paths are relative to <work root> (build-opening-m2.sh copies v11's stems and the cues there from dev-mac).
  -> <out>-dialogue.wav (v11's dialogue-and-sound stem, unchanged), <out>-music.wav, <out>-sfx.wav (v11's stings stem, unchanged), <out>-pre.wav (their
     sum), <out>-music-preduck.wav (placed, treated cues at the under level, no sidechain), <out>-duckfrac.npy (1 ms grid), <out>-placements.json
Placement: as music-v11.py cue(): track [a_in - pre, a_end + tail] placed so the a_end attack lands on at_scene, 5 ms raised-cosine head, raised-cosine tail
  from at_scene over tail s. Treatment and sidechain: music-m4.py's functions (hp, eq, lufs, level_intro, sidechain), see opening-m2.json notes."""
import sys, os, json, importlib.util
import numpy as np

here = os.path.dirname(os.path.abspath(__file__))
s_ = importlib.util.spec_from_file_location('m4', os.path.join(here, 'music-m4.py')); M = importlib.util.module_from_spec(s_); s_.loader.exec_module(M)
SR = M.SR; db = M.db


def treat(raw, m, c):
    """mono cue -> 100 Hz HP, EQ, -18 LUFS, intro levelled (music-m4.py main(), per cue)"""
    y = M.hp(raw, m['hp']); L_hp = M.lufs(y)
    bands = m.get('eq', []) + c.get('eq_extra', [])
    y = M.eq(y, bands); L = M.lufs(y); g = m['norm_lufs'] - L; y = y * db(g)
    rep = {'cue_lufs_at_hp_before_eq': L_hp, 'eq': bands, 'eq_loudness_change_db': L - L_hp, 'cue_lufs_after_eq': L, 'norm_gain_db': g, 'level_intro': None}
    li = c.get('level_intro')
    if li:
        gs, gms, tgt, st0 = M.level_intro(y, li); y = y * db(gs); st1 = M.short_term(y, li.get('st_window_s', 3.0)); t = np.arange(len(st1)) / 1000
        w = lambda s, a, b: round(float(np.median(s[(t >= a) & (t <= b)])), 2)
        rep['level_intro'] = {**li, 'target_st_lufs': tgt, 'max_gain_db': float(gms.max()),
                              'st_median_intro_before': w(st0, 0, li['until_track']), 'st_median_intro_after': w(st1, 0, li['until_track']),
                              'st_median_body_after': w(st1, *li['body']),
                              'gain_db_at_track': {str(x): round(float(gms[int(x * 1000)]), 2) for x in np.arange(0.5, li['until_track'], 1.0)}}
    return y, rep


def place(y, a_in, a_end, at_scene, N, PRE, TAIL):
    """music-v11.py cue(), on the treated signal"""
    tt = np.arange(N) / SR
    off = at_scene - a_end; i0 = int(round((a_in - PRE) * SR)); i1 = int(round((a_end + TAIL) * SR)); s0 = int(round((a_in - PRE + off) * SR))
    assert s0 >= 0 and s0 + (i1 - i0) <= N; out = np.zeros(N); out[s0:s0 + i1 - i0] = y[i0:i1]
    t_in = a_in + off; fin = np.clip((tt - (t_in - PRE)) / PRE, 0, 1); fout = np.clip((tt - at_scene) / TAIL, 0, 1)
    env = (0.5 - 0.5 * np.cos(np.pi * fin)) * (0.5 + 0.5 * np.cos(np.pi * fout)) * ((tt >= t_in - PRE) & (tt <= at_scene + TAIL))
    return out * env, off, t_in


def main():
    spec = json.load(open(sys.argv[1])); M.ROOT = sys.argv[2]; out = sys.argv[3]
    dlg = M.read(spec['dialogue']); key = M.read(spec['key']); sfx = M.read(spec['sfx']); N = len(dlg)
    assert len(key) == N and len(sfx) == N, (N, len(key), len(sfx))
    m = spec['music']; PRE, TAIL = m['pre'], m['tail']; under = m['under_db_re_norm']; d = m['duck']
    placed = np.zeros(N); rep = {'scene_s': N / SR, 'under_db_re_norm': under, 'under_lufs': m['norm_lufs'] + under,
                                 'open_lufs': m['norm_lufs'] + under + d['depth_db'], 'duck': d, 'cues': [], 'music_live': []}
    for c in m['cues']:
        y, r = treat(M.read(c['file']), m, c)
        p, off, t_in = place(y, c['a_in'], c['a_end'], c['at_scene'], N, PRE, TAIL)
        placed += p
        r.update(name=c['name'], file=c['file'], scene_eq_track_plus=off, in_scene=t_in - PRE, in_attack_scene=t_in, last_downbeat_scene=c['at_scene'],
                 tail_to=c['at_scene'] + TAIL, moved_bars=0)
        rep['cues'].append(r); rep['music_live'].append([t_in, c['at_scene']])
    frac, k = M.sidechain(key, N, d)
    gain_db = under + d['depth_db'] * (1 - frac)
    mus = placed * db(gain_db); preduck = placed * db(under)
    tt = np.arange(N) / SR; live = np.zeros(N, bool)
    for a, b in rep['music_live']:
        live |= (tt >= a) & (tt < b)
    rep['ms_ducked_over_half_while_live'] = int(((frac > 0.5) & live).sum() / 48); rep['ms_fully_open_while_live'] = int(((frac < 0.02) & live).sum() / 48)
    rep['dialogue'] = spec['dialogue']; rep['key'] = spec['key']; rep['sfx_file'] = spec['sfx']
    rep['events'] = spec['events']; rep['ref'] = spec['ref']; rep['title'] = spec['title']
    M.write(f'{out}-dialogue.wav', dlg); M.write(f'{out}-music.wav', mus); M.write(f'{out}-sfx.wav', sfx); M.write(f'{out}-pre.wav', dlg + mus + sfx)
    M.write(f'{out}-music-preduck.wav', preduck); M.write(f'{out}-key.wav', key)
    np.save(f'{out}-duckfrac.npy', frac[::48].astype(np.float32))
    json.dump(rep, open(f'{out}-placements.json', 'w'), indent=1, default=float)
    print(f"music under speech {under:+.2f} dB re -18 LUFS ({rep['under_lufs']:.1f} LUFS), open {under + d['depth_db']:+.2f} dB ({rep['open_lufs']:.1f} LUFS)")
    for r in rep['cues']:
        li = r['level_intro']
        print(f"  {r['name']}: cue {r['cue_lufs_at_hp_before_eq']:.2f} LUFS at 100 Hz, EQ {r['eq_loudness_change_db']:+.2f} dB, norm {r['norm_gain_db']:+.2f} dB; "
              f"in {r['in_scene']:.4f} (attack {r['in_attack_scene']:.4f}), last downbeat {r['last_downbeat_scene']:.4f}, tail to {r['tail_to']:.4f}; scene = track {r['scene_eq_track_plus']:+.4f}")
        if li:
            print(f"    intro leveller: target ST {li['target_st_lufs']:.2f}, max +{li['max_gain_db']:.2f} dB, intro ST median {li['st_median_intro_before']} -> "
                  f"{li['st_median_intro_after']} (body {li['st_median_body_after']}); gain at track s {li['gain_db_at_track']}")
    print(f"  ducked (>50%) {rep['ms_ducked_over_half_while_live']} ms, fully open {rep['ms_fully_open_while_live']} ms while the music plays")


if __name__ == '__main__':
    main()
