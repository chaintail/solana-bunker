#!/usr/bin/env python3
"""Scene m2: the conspiracy m4c music treatment on a scene's m1 music plan (audio-only remix; the picture is stream-copied at the mux).
Runs on do-box with /home/claude/venvs/manim (numpy, scipy); ffmpeg for audio decoding / ebur128 only (-vn).
usage: music-m2.py <spec.json> <work root> <out-prefix>        spec paths are relative to <work root> (build-m2.sh fetches them from dev-mac)
Treatment (conspiracy m4c, music-m4.py on film/conspiracy 70fecfa):
  cue      mono fold (0.5 L + 0.5 R), high-pass music.hp (100 Hz, 2nd-order Butterworth), music.eq biquads (high shelf 6 kHz -6 dB, high shelf
           11 kHz -8 dB, plus a notch only where the cue has a tonal spike above 12 kHz), then normalised to music.norm_lufs (-18 LUFS integrated,
           BS.1770, whole cue), so the level targets hold on the filtered cue. Optional music.level_intro as music-m4.py (unused when the cue's
           used span starts in its body).
  level    a sidechain on the dialogue stem, no breakpoints, no swells, no dips, no guard trim, no minimum-gap logic: the cue sits at
           music.under_lufs (-29.3 LUFS = m4c's level, +9 dB over conspiracy m2) while Liam speaks and duck.depth_db (5 dB) higher between words.
           key = dialogue 10 ms RMS (1 ms hop); duck fraction 0 at <= key_lo_db (-44), 1 at >= key_hi_db (-38); attack_ms (30) look-ahead,
           release_ms (300) linear in dB. Identical to music-m4.py's sidechain().
Placement: the scene's m1 placement, unchanged (the plan's cue, entry, exit, downbeat landings):
  music.place.mode "cut"     (mix-m1.py, s06/s07/s09): track_in -> scene_in at speed 1, raised-cosine head fade head_fade s
  music.place.mode "anchor"  (music-m1.py, s10): one anchor (track onset, spectral flux on a detect_hp copy, -> scene) at speed 1; entry at the
                             in.track onset minus preroll with a linear fade in.fade
  music.end.fade_from/fade_to  raised-cosine fade to silence (both m1 builders); music.stem_extra_s: the music stem rings past the picture
Sound effects: as built in m1, with a per-event gain change (sfx[].gain_change_db, the stamp rule: stamps -2 dB):
  sfx_mode "event_lufs"      (mix-m1.py): file (L+R)/2, gained to sfx_ref_lufs event loudness (ebur128, 1 s of silence appended) + gain, the
                             file's 'hit' seconds land on frame / fps; no tail fade
  sfx_mode "raw"             (music-m1.py): file mono fold times gain, attack_s on 'hit', optional duck/fade, head trim with 5 ms fade,
                             15 ms fade at the scene end on music (mix only) and sfx
  The sfx stem with the m1 gains is compared with m1's delivered sfx stem (divided by m1's loudness gain): the residual proves 'unchanged'.
-> <out>-dialogue.wav (the delivered scene mix, unchanged), -music.wav, -sfx.wav, -pre.wav (their sum, scene length), -music-preduck.wav,
   -duckfrac.npy (1 ms grid), -placements.json"""
import sys, json, os, re, subprocess, importlib.util
import numpy as np
from scipy.signal import resample_poly
from scipy.io import wavfile

here = os.path.dirname(os.path.abspath(__file__))
s_ = importlib.util.spec_from_file_location('m4', os.path.join(here, 'music-m4.py')); M = importlib.util.module_from_spec(s_); s_.loader.exec_module(M)
SR = 48000
db = lambda x: 10 ** (x / 20)


def read(p):
    return M.read(path(p))


def path(p):
    p = os.path.expanduser(p)
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def write(p, y):
    wavfile.write(p, SR, np.asarray(y, np.float32))


def ebur_I(x, pad=0.0):
    """ebur128 integrated loudness of a mono float signal (ffmpeg, audio only), as mix-m1.py lufs(x, pad)"""
    if pad: x = np.concatenate([x, np.zeros(int(pad * SR))])
    r = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-nostats', '-vn', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-',
                        '-af', 'ebur128=peak=true', '-f', 'null', '-'], input=np.asarray(x, np.float32).tobytes(), capture_output=True)
    s = r.stderr.decode(); s = s[s.rfind('Summary'):]
    return float(re.search(r'I:\s+(-?[\d.]+) LUFS', s).group(1))


def place_sfx(spec, N, gain_key):
    """sfx stem (N samples) and per-event report, with the gains in ev[gain_key] (+ gain_change_db when gain_key == 'gain_m2')"""
    fps = spec.get('fps', 30); mode = spec['sfx_mode']; out = np.zeros(N); rep = []
    t = np.arange(N) / SR
    for ev in spec['sfx']:
        z = read(ev['file']); g = ev['gain'] + (ev.get('gain_change_db', 0) if gain_key == 'gain_m2' else 0)
        if mode == 'event_lufs':
            I0 = ebur_I(z, pad=1.0); x = z * db(spec['sfx_ref_lufs'] - I0 + g)
            hit_t = ev['frame'] / fps; at = hit_t - ev['hit']; i0 = int(round(at * SR)); a = max(0, -i0); b = min(len(x), N - i0)
            seg = np.zeros(N); seg[i0 + a:i0 + b] = x[a:b]
            r = dict(ev, gain_applied_db=g, event_lufs_raw=I0, hit_scene_s=hit_t, file_start_scene_s=at)
        else:
            at_f = ev['attack_s'] if 'attack_s' in ev else (M.cut(z) if ev.get('align') == 'cut' else M.attack(z, ev.get('attack_peak_db', 12), ev.get('attack_rise_db', 9)))
            st = ev['hit'] - at_f; i0 = int(round(st * SR)); zz = z * db(g)
            if i0 < 0:
                zz = zz[-i0:].copy(); zz[:240] *= np.linspace(0, 1, 240); i0 = 0
            seg = np.zeros(N); j = min(N, i0 + len(zz)); seg[i0:j] = zz[:j - i0]
            if 'duck' in ev:
                dk = ev['duck']
                seg *= db(np.clip((t - dk['at']) / dk.get('attack', 0.1), 0, 1) * dk['db'])
                seg *= np.clip(1 - (t - dk['at']) / dk['fade'], 0, 1)
            r = dict(ev, gain_applied_db=g, attack_in_file_s=at_f, hit_scene_s=ev['hit'], file_start_scene_s=st, head_trimmed_s=max(0.0, -st))
        out += seg; rep.append(r)
    if mode == 'raw':
        tail = np.ones(N); tail[-720:] = np.linspace(1, 0, 720); out *= tail
    return out, rep


def main():
    global ROOT
    spec = json.load(open(sys.argv[1])); ROOT = sys.argv[2]; out = sys.argv[3]; M.ROOT = ROOT
    dlg = read(spec['dialogue'])
    N = int(round(spec['frames'] / spec.get('fps', 30) * SR)) if 'frames' in spec else len(dlg)
    assert abs(len(dlg) - N) <= 2, (len(dlg), N)
    dlg = np.pad(dlg, (0, max(0, N - len(dlg))))[:N]
    rep = {'scene_s': N / SR, 'music': {}, 'sfx': []}
    # ---------------- music: the cue, filtered and normalised
    m = spec['music']
    raw = read(m['file'])
    y = M.hp(raw, m['hp']); L_hp = M.lufs(y)
    y = M.eq(y, m.get('eq')); L_cue = M.lufs(y); g_norm = m['norm_lufs'] - L_cue
    y = y * db(g_norm)
    lirep = None
    if m.get('level_intro'):
        gs, gms, li_target, _ = M.level_intro(y, m['level_intro']); y = y * db(gs)
        lirep = {**m['level_intro'], 'target_st_lufs': li_target, 'max_gain_db': float(gms.max())}
    under = m['under_lufs'] - m['norm_lufs']; d = m['duck']
    # ---------------- placement (m1's)
    NM = N + int(round(m.get('stem_extra_s', 0) * SR)); tt = np.arange(NM) / SR
    pl = m['place']
    if pl['mode'] == 'cut':
        off = pl['scene_in'] - pl['track_in']; s_in = pl['scene_in']; f = 1.0; anc = []
        s0 = int(round(s_in * SR)); a0 = int(round(pl['track_in'] * SR)); jj = np.arange(NM) - s0 + a0   # mix-m1.py's integer cut
        ok = (jj >= 0) & (jj < len(y)) & (np.arange(NM) >= s0)
        mus = np.zeros(NM); mus[ok] = y[jj[ok]]
        amp = np.ones(NM); amp[:s0] = 0; hd = int(pl['head_fade'] * SR); amp[s0:s0 + hd] *= .5 - .5 * np.cos(np.pi * np.arange(hd) / hd)
        tin = pl['track_in']
    else:
        det = M.hp(raw, pl.get('detect_hp', 180))
        anc = [dict(a, track_onset=M.flux_onset(det, a['track'])) for a in pl['anchors']]
        f = 1.0; a0 = anc[0]; off = a0['scene'] - a0['track_onset']
        tin = M.flux_onset(det, pl['in']['track']); s_in = off + (tin - pl['in'].get('preroll', 0.015))
        jj = np.round((tt - off) * SR).astype(np.int64)
        ok = (jj >= 0) & (jj < len(y)) & (tt >= s_in)
        mus = np.zeros(NM); mus[ok] = y[jj[ok]]
        amp = np.clip((tt - s_in) / pl['in'].get('fade', 0.01), 0, 1)
    e = m['end']; p = np.clip((tt - e['fade_from']) / (e['fade_to'] - e['fade_from']), 0, 1)
    amp *= 0.5 * (1 + np.cos(np.pi * p))
    # ---------------- sidechain (music-m4.py)
    dlgM = np.pad(dlg, (0, NM - N))
    preduck = mus * db(under) * amp
    frac, key = M.sidechain(dlgM, NM, d)
    gain_db = under + d['depth_db'] * (1 - frac)
    mus = mus * db(gain_db) * amp
    rep['music'] = {'file': m['file'], 'hp': m['hp'], 'eq': m.get('eq'), 'cue_lufs_at_hp_before_eq': L_hp, 'cue_lufs_after_eq': L_cue,
                    'eq_loudness_change_db': L_cue - L_hp, 'norm_gain_db': g_norm, 'norm_lufs': m['norm_lufs'], 'level_intro': lirep,
                    'under_lufs': m['under_lufs'], 'under_db_re_norm': under, 'open_db_re_norm': under + d['depth_db'], 'duck': d,
                    'place': pl, 'scene_eq_track_plus': off, 'speed': f, 'in_scene': s_in, 'in_track': tin, 'anchors': anc, 'end': e,
                    'stem_extra_s': m.get('stem_extra_s', 0), 'cue_track_at_scene_0': -off,
                    'ms_ducked_over_half': int((frac[:N] > 0.5).sum() / 48), 'ms_fully_open_after_in': int((frac[:N][tt[:N] >= s_in] < 0.02).sum() / 48)}
    det = M.hp(raw, 180)
    rep['music']['bars_scene'] = {str(b): off + M.flux_onset(det, t) for b, t in m.get('report_bars', {}).items()}
    # ---------------- sound effects (m1's, stamp rule)
    sfx, rep['sfx'] = place_sfx(spec, N, 'gain_m2')
    nl = spec.get('sfx_null')
    if nl:
        sfx1, _ = place_sfx(spec, N, 'gain_m1')
        ref = read(nl['m1_stem'])[:N] * db(-nl['m1_gain_db']); ref = np.pad(ref, (0, N - len(ref)))
        res = sfx1 - ref
        rep['sfx_null_vs_m1'] = {'m1_stem': nl['m1_stem'], 'm1_gain_db': nl['m1_gain_db'], 'ref_peak_dbfs': 20 * np.log10(np.abs(ref).max() + 1e-20),
                                 'residual_peak_dbfs': 20 * np.log10(np.abs(res).max() + 1e-20),
                                 'residual_rms_re_ref_db': 10 * np.log10((res ** 2).sum() / ((ref ** 2).sum() + 1e-30) + 1e-30)}
    musN = mus[:N].copy()
    if spec['sfx_mode'] == 'raw':
        tail = np.ones(N); tail[-720:] = np.linspace(1, 0, 720); musN *= tail
    write(f'{out}-dialogue.wav', dlg); write(f'{out}-music.wav', mus); write(f'{out}-sfx.wav', sfx); write(f'{out}-pre.wav', dlg + musN + sfx)
    write(f'{out}-music-preduck.wav', preduck)
    np.save(f'{out}-duckfrac.npy', frac[::48].astype(np.float32))
    json.dump(rep, open(f'{out}-placements.json', 'w'), indent=1, default=float)
    mu = rep['music']
    print(f"music: cue {L_hp:.2f} LUFS at {m['hp']} Hz, eq {L_cue - L_hp:+.2f} dB -> {L_cue:.2f}, normalised {g_norm:+.2f} dB to {m['norm_lufs']}; "
          f"under {under:+.2f} dB ({m['under_lufs']} LUFS), open {under + d['depth_db']:+.2f} dB")
    print(f"  in at scene {s_in:.4f} (track {tin:.4f}); scene = track + {off:.4f}; ducked (>50%) {mu['ms_ducked_over_half']} ms, fully open {mu['ms_fully_open_after_in']} ms")
    print('  bars at scene: ' + ', '.join(f'{k} {v:.3f}' for k, v in mu['bars_scene'].items()))
    for a in anc:
        print(f"  anchor {a['name']}: track onset {a['track_onset']:.4f} -> scene {a['scene']:.4f}")
    for r in rep['sfx']:
        print(f"sfx {r.get('id', r.get('name'))}: {os.path.basename(r['file'])} gain {r['gain']} -> {r['gain_applied_db']} dB, hit {r['hit_scene_s']:.4f}, file starts {r['file_start_scene_s']:.4f}")
    if nl:
        print('sfx null vs m1 stem:', json.dumps(rep['sfx_null_vs_m1'], default=float))


if __name__ == '__main__':
    main()
