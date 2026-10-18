#!/usr/bin/env python3
"""s05 m3 music + sound effects: music-m2-workshop.py with the workshop cue continuing from the freeze through the robbery to the scene end. Runs on
do-box with /home/claude/venvs/manim (numpy, scipy); ffmpeg for audio decoding only (-vn, via music-m4.py's read()). Spec: pipeline/m3-s05-workshop.json
(paths relative to <work root>; build-s05-m3.sh copies the inputs there).
usage: music-m3-workshop.py <spec.json> <work root> <out dir>
  -> <out dir>/s04-s05-m3-music-unsplit.wav (the one render on the film timeline, before the scene gains), and per scene <out dir>/<scene>-m3-dialogue.wav,
     -music.wav, -sfx.wav, -pre.wav, -music-preduck.wav, -key.wav, -duckfrac.npy, -placements.json (finish-m3.py and verify-m3.py), and
     <out dir>/s04-s05-m3-vs-m2.json (the render against m2's: identical before the freeze, s04 part bit-identical).
Segment options on top of music-m2-workshop.py (bar_in / bar_out / chain / anchor / tail):
  out_beat [bar, beat]  the segment ends on that beat's measured attack (analysis.json beats_s, refined on m1's detection signal) instead of a downbeat
  in_grid               bar_in's downbeat is the bar grid (mean of the measured attacks of the bars either side): for a bar with no measurable attack
  xfade_prev            the 20 ms equal-power fade-in starts where the previous segment's fade-out starts (a crossfade); when the incoming downbeat
                        lands later than the outgoing cut, the incoming side's pre-roll (the track just before bar_in) covers the difference
Level, treatment and SFX: m2's, unchanged (music-m4.py sidechain on the two dialogues concatenated, gain = under + depth x (1 - duck))."""
import sys, os, json, importlib.util
import numpy as np

here = os.path.dirname(os.path.abspath(__file__))
s_ = importlib.util.spec_from_file_location('m4', os.path.join(here, 'music-m4.py')); M = importlib.util.module_from_spec(s_); s_.loader.exec_module(M)
s2 = importlib.util.spec_from_file_location('w2', os.path.join(here, 'music-m2-workshop.py')); W2 = importlib.util.module_from_spec(s2); s2.loader.exec_module(W2)
SR = M.SR; db = M.db; flux_attack = W2.flux_attack; TAG = 'm3'


def main():
    spec = json.load(open(sys.argv[1])); M.ROOT = sys.argv[2]; OUT = sys.argv[3]; os.makedirs(OUT, exist_ok=True)
    FPS = spec['fps']; SC = spec['scenes']; names = list(SC)
    L = {s: SC[s]['frames'] / FPS for s in names}; NS = {s: int(round(L[s] * SR)) for s in names}
    OFF = {}; acc = 0.0
    for s in names: OFF[s] = acc; acc += L[s]
    N = sum(NS.values()); JOIN = NS[names[0]]
    Ff = lambda s, f: OFF[s] + f / FPS
    t = np.arange(N) / SR
    d = {}
    for s in names:
        x = M.read(SC[s]['dialogue']); assert abs(len(x) - NS[s]) <= 2, (s, len(x), NS[s]); d[s] = np.pad(x, (0, max(0, NS[s] - len(x))))[:NS[s]]
    dd = np.concatenate([d[s] for s in names])
    # ---------------- music: attacks on m1's detection signal, material = the treated cue (m2)
    m = spec['music']; raw = M.read(m['file'])
    det = M.hp(raw * db(m['detect']['gain_db']), m['detect']['hp'])
    AN = json.load(open(M.path(m['analysis']))); DB = AN['downbeats_s']; BT = AN['beats_s']
    att = {k + 1: flux_attack(det, b - .06, b + .04) for k, b in enumerate(DB)}
    m1 = json.load(open(M.path(m['m1_report'])))
    m1att = {int(b): v['measured'] for b, v in m1['music_source']['attacks'].items()}
    att_diff_ms = {b: round(1000 * (att[b] - m1att[b]), 2) for b in att}
    assert max(abs(v) for v in att_diff_ms.values()) <= 0.1, att_diff_ms
    y = M.hp(raw, m['hp']); L_hp = M.lufs(y); y = M.eq(y, m['eq']); L_cue = M.lufs(y); g_norm = m['norm_lufs'] - L_cue; y = y * db(g_norm)
    li = m['level_intro']; gs, gms, li_t, st0 = M.level_intro(y, li); y = y * db(gs)
    bar_s = (att[27] - att[1]) / 26
    # ---------------- segments
    segs = [dict(s_) for s_ in m['segments']]; notes = {}
    for g in segs:
        if g.get('in_grid'):
            b = g['bar_in']; g['tin'] = (att[b - 1] + att[b + 1]) / 2
            notes[g['id']] = {'bar_in_grid': round(g['tin'], 4), 'bar_in_detector': round(att[b], 4), 'detector_vs_grid_ms': round(1000 * (att[b] - g['tin']), 1)}
        else:
            g['tin'] = att[g['bar_in']]
        if g.get('out_beat'):
            b, k = g['out_beat']; ib = BT.index(DB[b - 1]) + (k - 1); g['tout'] = flux_attack(det, BT[ib] - .06, BT[ib] + .04)
            notes[g['id']] = {'out_beat': [b, k], 'beat_analysis': BT[ib], 'beat_measured': round(g['tout'], 4),
                              'beat_grid': round(att[b] + (k - 1) * bar_s / 4, 4)}
        else:
            g['tout'] = att[g['bar_out']] if g.get('bar_out') else len(y) / SR
        if g.get('anchor'):
            a = g['anchor']; g['off'] = Ff(a['scene'], a['frame']) - att[a['bar']]
    for _ in range(len(segs)):
        for i, g in enumerate(segs):
            if 'off' in g: continue
            if g.get('chain') == 'next' and 'off' in segs[i + 1]: g['off'] = segs[i + 1]['off'] + segs[i + 1]['tin'] - g['tout']
            if g.get('chain') == 'prev' and 'off' in segs[i - 1]: g['off'] = segs[i - 1]['off'] + segs[i - 1]['tout'] - g['tin']
    E, LEAD = m['edge'], m['edge_lead']; placed = np.zeros(N); rows = []
    m1seg = {r['id']: r for r in m1['segments']}
    for i, g in enumerate(segs):
        fa, fb = g['tin'] + g['off'], g['tout'] + g['off']
        cut_out = g.get('bar_out') or g.get('out_beat')
        if g.get('xfade_prev'):
            p = segs[i - 1]; a0 = p['tout'] + p['off'] - LEAD - E; g['preroll'] = fa - a0
        else:
            a0 = fa - LEAD - E
        tail = g.get('tail', 0.0); end = fb + tail if tail else (fb - LEAD if cut_out else fb)
        i0, i1 = max(0, int(round(a0 * SR))), min(N, int(round(end * SR)))
        tt = t[i0:i1]; src = np.round((tt - g['off']) * SR).astype(np.int64); ok = (src >= 0) & (src < len(y))
        w = np.ones(len(tt))
        u = np.clip((tt - a0) / E, 0, 1); w *= np.sin(.5 * np.pi * u)
        if tail:
            h = fb + .05; v = np.clip((tt - h) / (end - h), 0, 1); w *= .5 + .5 * np.cos(np.pi * v)
        elif cut_out:
            v = np.clip((tt - (fb - LEAD - E)) / E, 0, 1); w *= np.cos(.5 * np.pi * v)
        else:
            v = np.clip((tt - (fb - .02)) / .02, 0, 1); w *= 1 - v
        seg = np.zeros(len(tt)); seg[ok] = y[src[ok]]; placed[i0:i1] += seg * w
        r1 = m1seg.get(g['id']); same_in = r1 is not None and r1['bars'].split('-')[0] == str(g['bar_in'])
        rows.append(dict(id=g['id'], bars=f"{g['bar_in']}-{g.get('bar_out') or ('%d.%d' % tuple(g['out_beat']) if g.get('out_beat') else 'end')}",
                         track_in=round(g['tin'], 4), track_out=round(g['tout'], 4), film_in=round(fa, 4), film_out=round(fb, 4), film_fade_start=round(a0, 4),
                         film_end=round(end, 4), tail_s=tail, preroll_s=round(g.get('preroll', LEAD + E), 4),
                         film_in_vs_m1_ms=round(1000 * (fa - r1['film_in']), 2) if same_in else None, **notes.get(g['id'], {})))
    # ---------------- sidechain level (m2)
    dk = m['duck']; under = m['under_db_re_norm']
    frac, key = M.sidechain(dd, N, dk)
    gain_db = under + dk['depth_db'] * (1 - frac)
    music = placed * db(gain_db); preduck = placed * db(under)
    M.write(f'{OUT}/s04-s05-{TAG}-music-unsplit.wav', music)
    # ---------------- against m2's render
    m2 = m['m2']; un2 = M.read(m2['unsplit']); fr = int(round(Ff('s05', m2['freeze_frame']) * SR))
    dif = np.abs(music.astype(np.float32).astype(np.float64) - un2[:N])  # both as written (float32)
    first = int(np.argmax(dif > 0)) if (dif > 0).any() else N
    vs = {'m2_unsplit_samples': len(un2), 'm3_unsplit_samples': N, 's04_part_bit_identical_float32': bool(dif[:JOIN].max() == 0),
          'first_differing_sample': first, 'first_differing_s05_s': round(first / SR - OFF['s05'], 4), 'freeze_s05_s': round(fr / SR - OFF['s05'], 4),
          'identical_until_freeze_plus_ms': round(1000 * (first - fr) / SR, 2)}
    json.dump(vs, open(f'{OUT}/s04-s05-{TAG}-vs-m2.json', 'w'), indent=1)
    common = {'title': spec['title'], 'cue': m['file'], 'hp': m['hp'], 'eq': m['eq'], 'cue_lufs_at_hp_before_eq': L_hp, 'cue_lufs_after_eq': L_cue,
              'norm_gain_db': g_norm, 'under_db_re_norm': under, 'under_lufs': m['norm_lufs'] + under, 'open_lufs': m['norm_lufs'] + under + dk['depth_db'],
              'duck': dk, 'attack_vs_m1_ms': att_diff_ms, 'bar_s': bar_s, 'segments': rows, 'join_sample': JOIN, 'vs_m2': vs}
    print(f"cue {L_hp:.2f} LUFS at 100 Hz, EQ {L_cue - L_hp:+.2f} dB, norm {g_norm:+.2f} dB; under {under:+.2f} dB ({m['norm_lufs'] + under:.1f} LUFS), "
          f"open {under + dk['depth_db']:+.2f} dB; attacks vs m1 max {max(abs(v) for v in att_diff_ms.values()):.2f} ms; bar {bar_s:.4f} s")
    for r in rows:
        print(f"  segment {r['id']} bars {r['bars']}: film {r['film_in']:.4f}-{r['film_out']:.4f} (fade from {r['film_fade_start']:.4f}, end {r['film_end']:.4f}; "
              f"s05 {r['film_in'] - OFF['s05']:.4f}-{r['film_out'] - OFF['s05']:.4f}) vs m1 in {r['film_in_vs_m1_ms']} ms "
              + ' '.join(f'{k}={r[k]}' for k in ('bar_in_grid', 'bar_in_detector', 'detector_vs_grid_ms', 'beat_measured', 'beat_grid', 'preroll_s') if k in r))
    print('vs m2:', json.dumps(vs))
    # ---------------- per scene
    lo = 0
    for s in names:
        S = SC[s]; n = NS[s]; sl = slice(lo, lo + n); lo += n
        sfx = np.zeros(n); srep = []
        for e in S['sfx']:
            x = M.read(e['file']); z = x * 10 ** ((spec['sfx_ref_lufs'] - e['event_lufs'] + e['gain']) / 20)
            at = e['frame'] / FPS - e['hit']; i0 = int(round(at * SR)); a = max(0, -i0); b = min(len(z), n - i0); sfx[i0 + a:i0 + b] += z[a:b]
            srep.append({k: e[k] for k in ('id', 'file', 'frame', 'hit', 'event_lufs', 'm1_gain', 'gain')})
        mus = music[sl]; dl = d[s]
        M.write(f'{OUT}/{s}-{TAG}-dialogue.wav', dl); M.write(f'{OUT}/{s}-{TAG}-music.wav', mus); M.write(f'{OUT}/{s}-{TAG}-sfx.wav', sfx)
        M.write(f'{OUT}/{s}-{TAG}-pre.wav', dl + mus + sfx); M.write(f'{OUT}/{s}-{TAG}-music-preduck.wav', preduck[sl]); M.write(f'{OUT}/{s}-{TAG}-key.wav', dl)
        np.save(f'{OUT}/{s}-{TAG}-duckfrac.npy', frac[sl][::48].astype(np.float32))
        live = []
        for r in rows:
            a, b = r['film_in'] - OFF[s], (r['film_end'] if r['tail_s'] or r['bars'].endswith('end') else r['film_out']) - OFF[s]
            if b > 0.15 and a < L[s] - 0.15: live.append([max(a, 0.0), min(b, L[s])])
        # placement check against m2 only where m2 had the same music: up to the freeze, and m2's final-chord span
        fz = m2['freeze_frame'] / FPS if s == 's05' else None
        place = [[a, min(b, fz) if fz else b] for a, b in live if not fz or a < fz]
        if s == 's05': place.append(m2['chord_span'])
        ev = [{'name': e['id'], 'layer': 'sfx', 'at': e['frame'] / FPS, 'frame': e['frame']} for e in S['sfx']]
        for c in m['checks']:
            if c['scene'] == s: ev.append({'name': c['id'], 'layer': 'music', 'at': c['frame'] / FPS if 'frame' in c else c['t'], **({'frame': c['frame']} if 'frame' in c else {})})
        for r in rows:
            x = r['film_in'] - OFF[s]
            if 0.05 < x < L[s] - 0.05 and not any(abs(x - e['at']) < 0.05 for e in ev): ev.append({'name': f"segment {r['id']} in (bar {r['bars'].split('-')[0]})", 'layer': 'music', 'at': x})
        pl = {**common, 'title': f"{s} {TAG}: " + spec['title'].split(': ', 1)[1], 'scene': s, 'scene_s': L[s], 'film_offset_s': OFF[s], 'sfx': srep,
              'music_live': live, 'place_spans': place, 'events': sorted(ev, key=lambda e: e['at']), 'key': f'{OUT}/{s}-{TAG}-key.wav',
              'ref': {'name': 'm2', 'music': m2[f'{s}_music'], 'key': S['dialogue'], 'gain_db': S['m2_gain_db']}}
        json.dump(pl, open(f'{OUT}/{s}-{TAG}-placements.json', 'w'), indent=1, default=float)
        print(f"{s}: sfx {[(e['id'], e['gain']) for e in srep]}; music live {[[round(a, 3), round(b, 3)] for a, b in live]}; place-check spans "
              f"{[[round(a, 3), round(b, 3)] for a, b in place]}")


if __name__ == '__main__':
    main()
