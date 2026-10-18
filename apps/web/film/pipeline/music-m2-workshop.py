#!/usr/bin/env python3
"""m2 music + sound effects for the bunker (s04) and the whiteboard (s05): m1's workshop-cue plan with the conspiracy m4c treatment. Same file on film/s04
and film/s05; the placements are in pipeline/m2-workshop.json. Runs on do-box with /home/claude/venvs/manim (numpy, scipy); ffmpeg for audio decoding only
(-vn, via music-m4.py's read()). Spec paths are relative to <work root> (build-s04-s05-m2.sh copies the inputs there from dev-mac).
usage: music-m2-workshop.py <spec.json> <work root> <out dir>
  -> <out dir>/s04-s05-m2-music-unsplit.wav (the one render on the film timeline, before the scene gains), and per scene <out dir>/<scene>-m2-dialogue.wav
     (the delivered audio-final.wav, unchanged), -music.wav (this scene's part of the render), -sfx.wav, -pre.wav (their sum), -music-preduck.wav,
     -key.wav, -duckfrac.npy, -placements.json (for finish-m3.py and verify-m2.py)
Timeline, segments, splices: m1-workshop.py's code (film time F = s04 time, then 46.5 s + s05 time; segments placed from anchors and chains on measured
  downbeat attacks; 20 ms equal-power edges ending 5 ms before the attack; tails), with the attacks measured on m1's detection signal so every splice sits on
  m1's sample, and the treated cue (music-m4.py: hp, eq, -18 LUFS, level_intro) as the material.
Level: music-m4.py sidechain() on the two dialogues concatenated, gain = under + depth x (1 - duck): no gap logic, swells, dips or guard trim.
SFX: m1's method (mono fold, gain = -20 - m1's measured event loudness + spec gain, hit on the frame); checked against m1's stem with m1's gains."""
import sys, os, json, importlib.util
import numpy as np

here = os.path.dirname(os.path.abspath(__file__))
s_ = importlib.util.spec_from_file_location('m4', os.path.join(here, 'music-m4.py')); M = importlib.util.module_from_spec(s_); s_.loader.exec_module(M)
SR = M.SR; db = M.db


def flux_attack(x, t0, t1, hop=96, N=512):
    """m1-workshop.py: time where the largest spectral-flux rise in [t0, t1] enters (the window's trailing quarter)"""
    a = int(t0 * SR); w = np.hanning(N); S = []
    for i in range(a - N, int(t1 * SR), hop):
        seg = x[max(0, i):i + N]
        if len(seg) < N: seg = np.pad(seg, (N - len(seg), 0))
        S.append(np.log1p(np.abs(np.fft.rfft(seg * w)) * 10))
    f = np.maximum(np.diff(np.array(S), axis=0), 0).sum(1)
    return (a - N) / SR + (int(np.argmax(f)) + 1) * hop / SR + .75 * N / SR


def main():
    spec = json.load(open(sys.argv[1])); M.ROOT = sys.argv[2]; OUT = sys.argv[3]; os.makedirs(OUT, exist_ok=True)
    FPS = spec['fps']; SC = spec['scenes']; names = list(SC)
    L = {s: SC[s]['frames'] / FPS for s in names}; NS = {s: int(round(L[s] * SR)) for s in names}
    OFF = {}; acc = 0.0
    for s in names: OFF[s] = acc; acc += L[s]
    N = sum(NS.values()); JOIN = NS[names[0]]
    F = lambda s, t: OFF[s] + t; Ff = lambda s, f: OFF[s] + f / FPS
    t = np.arange(N) / SR
    d = {}
    for s in names:
        x = M.read(SC[s]['dialogue']); assert abs(len(x) - NS[s]) <= 2, (s, len(x), NS[s]); d[s] = np.pad(x, (0, max(0, NS[s] - len(x))))[:NS[s]]
    dd = np.concatenate([d[s] for s in names])
    # ---------------- music: attacks on m1's detection signal, material = the treated cue
    m = spec['music']; raw = M.read(m['file'])
    det = M.hp(raw * db(m['detect']['gain_db']), m['detect']['hp'])
    DB = json.load(open(M.path(m['analysis'])))['downbeats_s']
    att = {k + 1: flux_attack(det, b - .06, b + .04) for k, b in enumerate(DB)}
    m1 = json.load(open(M.path(m['m1_report'])))
    m1att = {int(b): v['measured'] for b, v in m1['music_source']['attacks'].items()}
    att_diff_ms = {b: round(1000 * (att[b] - m1att[b]), 2) for b in att}
    assert max(abs(v) for v in att_diff_ms.values()) <= 0.1, att_diff_ms        # m1's report rounds to 0.1 ms
    y = M.hp(raw, m['hp']); L_hp = M.lufs(y); y = M.eq(y, m['eq']); L_cue = M.lufs(y); g_norm = m['norm_lufs'] - L_cue; y = y * db(g_norm)
    li = m['level_intro']; gs, gms, li_t, st0 = M.level_intro(y, li); y = y * db(gs)
    st1 = M.short_term(y, li['st_window_s']); ts = np.arange(len(st1)) / 1000
    w_ = lambda s_, a, b: round(float(np.median(s_[(ts >= a) & (ts <= b)])), 2)
    lirep = {**li, 'target_st_lufs': li_t, 'max_gain_db': float(gms.max()), 'st_median_intro_before': w_(st0, 0, li['until_track']),
             'st_median_intro_after': w_(st1, 0, li['until_track']), 'st_median_body_after': w_(st1, *li['body']),
             'gain_db_per_bar': {str(k + 1): round(float(np.median(gms[int(DB[k] * 1000):int(DB[k + 1] * 1000)])), 2) for k in range(7)}}
    # ---------------- segments (m1-workshop.py)
    segs = [dict(s_) for s_ in m['segments']]
    for g in segs:
        g['tin'] = att[g['bar_in']]; g['tout'] = att[g['bar_out']] if g.get('bar_out') else len(y) / SR
        if g.get('anchor'):
            a = g['anchor']; g['off'] = Ff(a['scene'], a['frame']) - att[a['bar']]
    for _ in range(len(segs)):
        for i, g in enumerate(segs):
            if 'off' in g: continue
            if g.get('chain') == 'next' and 'off' in segs[i + 1]: g['off'] = segs[i + 1]['off'] + segs[i + 1]['tin'] - g['tout']
            if g.get('chain') == 'prev' and 'off' in segs[i - 1]: g['off'] = segs[i - 1]['off'] + segs[i - 1]['tout'] - g['tin']
    E, LEAD = m['edge'], m['edge_lead']; placed = np.zeros(N); rows = []
    m1seg = {r['id']: r for r in m1['segments']}
    for g in segs:
        fa, fb = g['tin'] + g['off'], g['tout'] + g['off']; a0 = fa - LEAD - E
        tail = g.get('tail', 0.0); end = fb + tail if tail else (fb - LEAD if g.get('bar_out') else fb)
        i0, i1 = max(0, int(round(a0 * SR))), min(N, int(round(end * SR)))
        tt = t[i0:i1]; src = np.round((tt - g['off']) * SR).astype(np.int64); ok = (src >= 0) & (src < len(y))
        w = np.ones(len(tt))
        u = np.clip((tt - a0) / E, 0, 1); w *= np.sin(.5 * np.pi * u)
        if tail:
            h = fb + .05; v = np.clip((tt - h) / (end - h), 0, 1); w *= .5 + .5 * np.cos(np.pi * v)
        elif g.get('bar_out'):
            v = np.clip((tt - (fb - LEAD - E)) / E, 0, 1); w *= np.cos(.5 * np.pi * v)
        else:
            v = np.clip((tt - (fb - .02)) / .02, 0, 1); w *= 1 - v
        seg = np.zeros(len(tt)); seg[ok] = y[src[ok]]; placed[i0:i1] += seg * w
        r1 = m1seg[g['id']]
        rows.append(dict(id=g['id'], bars=f"{g['bar_in']}-{g.get('bar_out', 'end')}", track_in=round(g['tin'], 4), film_in=round(fa, 4), film_out=round(fb, 4),
                         film_end=round(end, 4), tail_s=tail, film_in_vs_m1_ms=round(1000 * (fa - r1['film_in']), 2), film_out_vs_m1_ms=round(1000 * (fb - r1['film_out']), 2)))
    # ---------------- sidechain level
    dk = m['duck']; under = m['under_db_re_norm']
    frac, key = M.sidechain(dd, N, dk)
    gain_db = under + dk['depth_db'] * (1 - frac)
    music = placed * db(gain_db); preduck = placed * db(under)
    M.write(f'{OUT}/s04-s05-m2-music-unsplit.wav', music)
    common = {'title': spec['title'], 'cue': m['file'], 'hp': m['hp'], 'eq': m['eq'], 'cue_lufs_at_hp_before_eq': L_hp, 'cue_lufs_after_eq': L_cue,
              'norm_gain_db': g_norm, 'level_intro': lirep, 'under_db_re_norm': under, 'under_lufs': m['norm_lufs'] + under,
              'open_lufs': m['norm_lufs'] + under + dk['depth_db'], 'duck': dk, 'attack_vs_m1_ms': att_diff_ms, 'segments': rows, 'join_sample': JOIN,
              'moved_bars': 0}
    print(f"cue {L_hp:.2f} LUFS at 100 Hz, EQ {L_cue - L_hp:+.2f} dB, norm {g_norm:+.2f} dB; under {under:+.2f} dB ({m['norm_lufs'] + under:.1f} LUFS), "
          f"open {under + dk['depth_db']:+.2f} dB; attacks vs m1 max {max(abs(v) for v in att_diff_ms.values()):.2f} ms")
    print(f"intro leveller: target ST {li_t:.2f}, max +{gms.max():.2f} dB, intro ST median {lirep['st_median_intro_before']} -> {lirep['st_median_intro_after']} "
          f"(body {lirep['st_median_body_after']}); median gain per bar {lirep['gain_db_per_bar']}")
    for r in rows:
        print(f"  segment {r['id']} bars {r['bars']}: film {r['film_in']:.4f}-{r['film_out']:.4f} (vs m1 {r['film_in_vs_m1_ms']:+.2f} / {r['film_out_vs_m1_ms']:+.2f} ms)")
    # ---------------- per scene
    lo = 0
    for s in names:
        S = SC[s]; n = NS[s]; sl = slice(lo, lo + n); lo += n
        sfx = np.zeros(n); sfx_m1 = np.zeros(n); srep = []
        for e in S['sfx']:
            x = M.read(e['file'])
            for arr, gdb in ((sfx, e['gain']), (sfx_m1, e['m1_gain'])):
                z = x * 10 ** ((spec['sfx_ref_lufs'] - e['event_lufs'] + gdb) / 20)
                at = e['frame'] / FPS - e['hit']; i0 = int(round(at * SR)); a = max(0, -i0); b = min(len(z), n - i0); arr[i0 + a:i0 + b] += z[a:b]
            srep.append({k: e[k] for k in ('id', 'file', 'frame', 'hit', 'event_lufs', 'm1_gain', 'gain')})
        m1sfx = M.read(f"{S['m1_stems']}-sfx.wav")[:n] / 10 ** (S['m1_gain_db'] / 20)
        resid = float(20 * np.log10(np.abs(sfx_m1 - m1sfx).max() / np.abs(m1sfx).max() + 1e-20))
        mus = music[sl]; dl = d[s]
        M.write(f'{OUT}/{s}-m2-dialogue.wav', dl); M.write(f'{OUT}/{s}-m2-music.wav', mus); M.write(f'{OUT}/{s}-m2-sfx.wav', sfx)
        M.write(f'{OUT}/{s}-m2-pre.wav', dl + mus + sfx); M.write(f'{OUT}/{s}-m2-music-preduck.wav', preduck[sl]); M.write(f'{OUT}/{s}-m2-key.wav', dl)
        np.save(f'{OUT}/{s}-m2-duckfrac.npy', frac[sl][::48].astype(np.float32))
        live = []
        for r in rows:
            a, b = r['film_in'] - OFF[s], r['film_out'] - OFF[s]
            if b > 0.15 and a < L[s] - 0.15: live.append([max(a, 0.0), min(b, L[s])])
        ev = [{'name': e['id'], 'layer': 'sfx', 'at': e['frame'] / FPS, 'frame': e['frame']} for e in S['sfx']]
        for c in m['checks']:
            if c['scene'] == s: ev.append({'name': c['id'], 'layer': 'music', 'at': c['frame'] / FPS if 'frame' in c else c['t'], **({'frame': c['frame']} if 'frame' in c else {})})
        for r in rows:
            x = r['film_in'] - OFF[s]
            if 0.05 < x < L[s] - 0.05 and not any(abs(x - e['at']) < 0.05 for e in ev): ev.append({'name': f"segment {r['id']} in (bar {r['bars'].split('-')[0]})", 'layer': 'music', 'at': x})
        pl = {**common, 'title': f"{s} m2: " + spec['title'].split(': ', 1)[1], 'scene': s, 'scene_s': L[s], 'film_offset_s': OFF[s], 'sfx': srep,
              'sfx_m1_residual_db_re_peak': resid, 'music_live': live, 'events': sorted(ev, key=lambda e: e['at']), 'key': f'{OUT}/{s}-m2-key.wav',
              'ref': {'name': 'm1', 'music': f"{S['m1_stems']}-music.wav", 'key': S['dialogue'], 'gain_db': S['m1_gain_db']}}
        json.dump(pl, open(f'{OUT}/{s}-m2-placements.json', 'w'), indent=1, default=float)
        print(f"{s}: sfx {[(e['id'], e['gain']) for e in srep]}; m1-gain re-render vs m1 sfx stem: max residual {resid:.1f} dB re peak; music live {[[round(a, 3), round(b, 3)] for a, b in live]}")


if __name__ == '__main__':
    main()
