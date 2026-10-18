#!/usr/bin/env python3
"""m3 audio verification (music treatment per conspiracy m4c), shared by the opening, s04 and s05. Runs on do-box (/home/claude/venvs/manim; ffmpeg audio
only, -vn). Adapted from conspiracy verify-m4.py.
usage: verify-m3.py <work prefix> <stem prefix> <final.wav> <report dir> [<m3.mp4> <m3-phone.mp4>]   (run from the work root)
  reads <work prefix>-placements.json (key = the dialogue that drives the sidechain at its delivered level; ref = the previous build's music stem and
  key, with ref.gain_db = that build's gain over the key's level; events; music_live spans), <work prefix>-loudness.json (finish-m3.py) and the stems
  finish-m3.py wrote (<stem prefix>-dialogue/-music/-sfx.f32.wav, at the final gain).
Checks:
  sync     lag of the final wav (and the mp4s' decoded audio) against the pre-limiter sum (0 = the source timing)
  place    lag of the pre-duck music against the ref music, per live span (cross-correlation, +-10 ms): 0 = placement unchanged
  onsets   sfx events: attack detector on the sfx stem; music events: spectral flux on the pre-duck music and on the ref music (same detector)
  guard    dialogue minus music in 100 / 200 ms windows (10 ms hop) where the key (delivered level) is >= -30 dBFS (and -35) and the music is present
           (window RMS > -90 dBFS): min, p05, median, share under 12 / 16 dB; the ref the same
  levels   music under speech / in open pauses (medians of 100 ms RMS), dialogue - music under speech
  highs    long-term music spectrum (Welch 4096) m3 vs ref: 4-9 kHz and 12-17.2 kHz per-bin power
  loudness ebur128 of the final wav and the mp4s' decoded audio
Writes <report dir>/verify.json and levels.npz (for plot-levels-m3.py)."""
import sys, os, json, re, subprocess, importlib.util
import numpy as np
from scipy.signal import fftconvolve, welch

here = os.path.dirname(os.path.abspath(__file__))
s_ = importlib.util.spec_from_file_location('m4', os.path.join(here, 'music-m4.py')); M = importlib.util.module_from_spec(s_); s_.loader.exec_module(M)
W, ST, FIN, R = sys.argv[1:5]; MP4 = sys.argv[5:7]
os.makedirs(R, exist_ok=True); SR = 48000
pl = json.load(open(W + '-placements.json')); G = json.load(open(W + '-loudness.json'))['linear_gain_db']
ref = pl['ref']; G2 = ref['gain_db']


def ebur(p):
    s = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-vn', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    s = s[s.rindex('Summary:'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))
    return {'I': g('I'), 'LRA': g('LRA'), 'true_peak_dbtp': g('Peak')}


def lag(a, b, maxlag=4800):
    n = min(len(a), len(b)); c = fftconvolve(a[:n], b[:n][::-1], mode='full'); mid = n - 1
    return int(np.argmax(c[mid - maxlag:mid + maxlag + 1]) - maxlag)


dlg, mus, sfx = (M.read(f'{ST}-{k}.f32.wav') for k in ('dialogue', 'music', 'sfx')); N = len(dlg)
key = M.read(pl['key'])[:N]; pre = M.read(W + '-pre.wav'); fin = M.read(FIN)
pdk = M.read(W + '-music-preduck.wav')
rmus = M.read(ref['music'])[:N]; rkey = M.read(ref['key'])[:N]
rep = {'sync': {'final_wav_vs_pre_samples': lag(fin, pre)}, 'place': [], 'onsets': [], 'guard': {}, 'levels': {}, 'highs': {}, 'loudness': {'final_wav': ebur(FIN)}}
for p in MP4:
    dec = M.read(p)
    rep['sync'][os.path.basename(p) + '_audio_vs_pre_samples'] = lag(dec[:N], pre); rep['sync'][os.path.basename(p) + '_audio_len_s'] = len(dec) / SR
    rep['loudness'][os.path.basename(p)] = ebur(p)
# ---- placement vs the ref music, per live span
for a, b in pl['music_live']:
    i, j = int(a * SR), int(b * SR)
    rep['place'].append({'span_s': [round(a, 3), round(b, 3)], 'preduck_vs_ref_lag_samples': lag(pdk[i:j], rmus[i:j], 480)})
# ---- onsets
for ev in pl['events']:
    pic = ev['frame'] / 30 if 'frame' in ev else ev['at']
    if ev['layer'] == 'sfx':
        a = int((ev['at'] - 0.15) * SR); meas = a / SR + M.attack(sfx[a:int((ev['at'] + 0.15) * SR)], ev.get('attack_peak_db', 12), ev.get('attack_rise_db', 9))
        rep['onsets'].append({'event': ev['name'], 'layer': 'sfx', 'measured_s': round(meas, 4), 'frame': ev.get('frame'), 'picture_s': round(pic, 4),
                              'error_ms': round((meas - pic) * 1000, 1)})
    else:
        m3 = M.flux_onset(pdk, ev['at']); m1 = M.flux_onset(rmus, ev['at'])
        rep['onsets'].append({'event': ev['name'], 'layer': 'music (pre-duck)', 'measured_s': round(m3, 4), 'ref_measured_s': round(m1, 4), 'frame': ev.get('frame'),
                              'picture_s': round(pic, 4), 'error_ms': round((m3 - pic) * 1000, 1), 'vs_ref_ms': round((m3 - m1) * 1000, 1)})
# ---- guard and levels
hop = 480
env = lambda y, w: M.env_db(y, w, hop)
out = {}
for name, (k, mu, g) in {'m3': (key, mus, G), 'ref': (rkey, rmus, G2)}.items():
    for wms in (100, 200):
        w = wms * 48; D, Mu = env(k, w), env(mu[:N], w)
        for thr in (-30, -35):
            act = (D >= thr) & (Mu > -90); m = np.where(act, D + g - Mu, np.inf); i = int(np.argmin(m))
            rep['guard'][f'{name}_{wms}ms_active{-thr}'] = {'windows': int(act.sum()), 'windows_no_music': int(((D >= thr) & (Mu <= -90)).sum()),
                                                           'min_db': round(float(m[i]), 2), 'at_s': round(i * hop / SR + wms / 2000, 2),
                                                           'p05_db': round(float(np.percentile(m[act], 5)), 2), 'median_db': round(float(np.median(m[act])), 2),
                                                           'share_under_12_db': round(float((m[act] < 12).mean()), 3), 'share_under_16_db': round(float((m[act] < 16).mean()), 3)}
    D, Mu = env(k, 4800) + g, env(mu[:N], 4800)
    t = np.arange(len(D)) * hop / SR + 0.05
    out[name] = dict(t=t, D=D, M=Mu)
out['m3']['S'] = env(sfx, 4800)
frac = np.load(W + '-duckfrac.npy'); t = out['m3']['t']; fr = np.interp(t, np.arange(len(frac)) / 1000, frac)
fr_max = np.array([frac[max(0, int(x * 1000) - 50):int(x * 1000) + 50].max() for x in t])
live = np.zeros(len(t), bool)
for a, b in pl['music_live']:
    live |= (t > a + 0.1) & (t < b - 0.05)
for name, g in (('m3', G), ('ref', G2)):
    D, Mu = out[name]['D'], out[name]['M']; act = (D - g >= -30) & live & (Mu > -90)
    rep['levels'][name] = {'music_under_speech_median_dbfs': round(float(np.median(Mu[act])), 2),
                           'dialogue_minus_music_under_speech_median_db': round(float(np.median((D - Mu)[act])), 2),
                           'dialogue_active_median_dbfs': round(float(np.median(D[act])), 2), 'gain_db': g}
opn = (fr_max < 0.02) & live & (out['m3']['M'] > -90)
rep['levels']['m3'].update(music_open_pauses_median_dbfs=round(float(np.median(out['m3']['M'][opn])), 2) if opn.any() else None, open_windows=int(opn.sum()),
                           open_minus_under_db=round(float(np.median(out['m3']['M'][opn]) - rep['levels']['m3']['music_under_speech_median_dbfs']), 2) if opn.any() else None)
rep['levels']['music_under_speech_vs_ref_db'] = round(rep['levels']['m3']['music_under_speech_median_dbfs'] - rep['levels']['ref']['music_under_speech_median_dbfs'], 2)
rep['levels']['under_lufs_re_cue'] = pl.get('under_lufs')
# ---- highs
lv = np.zeros(N, bool); tt = np.arange(N) / SR
for a, b in pl['music_live']:
    lv |= (tt >= a) & (tt < b)
fq, sp2 = welch(mus[lv], SR, nperseg=4096); _, spr = welch(rmus[lv], SR, nperseg=4096); _, spd = welch(dlg[lv], SR, nperseg=4096)
sp2, spr, spd = (10 * np.log10(x + 1e-30) for x in (sp2, spr, spd))
band = lambda sp, a, b: round(float(10 * np.log10(np.mean(10 ** (sp[(fq >= a) & (fq < b)] / 10)))), 2)
for nm, sp in (('m3', sp2), ('ref', spr)):
    rep['highs'][nm] = {'4_9k_per_bin_db': band(sp, 4000, 9000), '12_17k2_per_bin_db': band(sp, 12000, 17200)}
    rep['highs'][nm]['high_minus_mid_db'] = round(rep['highs'][nm]['12_17k2_per_bin_db'] - rep['highs'][nm]['4_9k_per_bin_db'], 2)
st2, st2p, str_ = M.short_term(mus), M.short_term(pdk * 10 ** (G / 20)), M.short_term(rmus)
np.savez(f'{R}/levels.npz', **{f'{k}_{x}': v[x] for k, v in out.items() for x in v}, m3_frac=fr, m3_gain=G, ref_gain=G2, ref_name=ref['name'],
         st_t=np.arange(len(st2))[::100] / 1000, st_m3=st2[::100], st_m3_preduck=st2p[::100], st_ref=str_[::100], fq=fq, sp_m3=sp2, sp_ref=spr, sp_dlg=spd,
         events=json.dumps([{'t': o['measured_s'], 'name': o['event']} for o in rep['onsets']]), title=pl['title'], stats=json.dumps(rep),
         live=json.dumps(pl['music_live']))
json.dump(rep, open(f'{R}/verify.json', 'w'), indent=1, default=float)
print(json.dumps({k: rep[k] for k in ('sync', 'place', 'levels', 'highs', 'loudness')}, indent=1, default=float))
for k, v in rep['guard'].items():
    print(f"guard {k:22s} min {v['min_db']:6.2f} dB at {v['at_s']:6.2f} s  p05 {v['p05_db']:6.2f}  median {v['median_db']:6.2f}  <12: {v['share_under_12_db']:.3f}  "
          f"<16: {v['share_under_16_db']:.3f}  ({v['windows']} windows, {v['windows_no_music']} active without music)")
for o in rep['onsets']:
    print(f"{o['layer']:17s} {o['event'][:60]:60s} measured {o['measured_s']:8.4f}  picture {o['picture_s']:8.4f} (frame {o['frame']})  err {o['error_ms']:+6.1f} ms"
          + (f"  vs ref {o['vs_ref_ms']:+.1f} ms" if 'vs_ref_ms' in o else ''))
