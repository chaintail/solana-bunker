#!/usr/bin/env python3
"""m4 audio verification. Runs on do-box (/home/claude/venvs/manim; ffmpeg audio only, -vn). Reference = m2 (spec.ref: m2's delivered stems, its gain).
usage: verify-m4.py <spec.json> <work prefix> <stem prefix> <final.wav> <report dir> [<m4.mp4> <m4-phone.mp4>]   (run from the work root)
Checks:
  sync     lag of the final wav (and the mp4s' decoded audio) against the pre-limiter sum (0 = x12b timing)
  onsets   sound effects on the sfx stem (attack detector, the effect's own thresholds) and the music anchors on the pre-duck music stem
           (spectral flux), against frame / 30
  start    first music sample above -80 dBFS; music RMS over frame 0 (0-33 ms) and 0-100 ms; music short-term (3 s, K-weighted) median over
           the first 10 s of music vs the body (scene 15-58 s), pre-duck and as delivered (ducked); m2 the same (its first 10 s from its entry)
  highs    music stem per-bin power in clock-tick frames (12-18 kHz > p60 + 6 dB), 4-9 kHz vs 12-17.2 kHz, m4 vs m2
  guard    dialogue minus music in 100 / 200 ms windows (10 ms hop) where the dialogue at x12b's delivered level is >= -30 (and -35) dBFS: min,
           p05, median, share under 12 and 16 dB; m2 the same
  levels   music under speech / in open pauses (medians), dialogue - music under speech, dialogue active median; dialogue drop vs m2
  loudness ebur128 of the final wav and the mp4s' decoded audio
Writes <report dir>/verify.json and levels.npz (for plot-levels-m4.py)."""
import sys, os, json, re, subprocess, importlib.util
import numpy as np
from scipy.signal import fftconvolve, stft

here = os.path.dirname(os.path.abspath(__file__))
s_ = importlib.util.spec_from_file_location('mm', os.path.join(here, 'music-m4.py')); M = importlib.util.module_from_spec(s_); s_.loader.exec_module(M)
spec = json.load(open(sys.argv[1])); W, ST, FIN, R = sys.argv[2:6]; MP4 = sys.argv[6:8]
os.makedirs(R, exist_ok=True); SR = 48000
pl = json.load(open(W + '-placements.json')); G = json.load(open(W + '-loudness.json'))['linear_gain_db']
ref = spec['ref']; G2 = ref['m2_gain_db']


def ebur(p):
    s = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-vn', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    s = s[s.rindex('Summary:'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))
    return {'I': g('I'), 'LRA': g('LRA'), 'true_peak_dbtp': g('Peak')}


def lag(a, b, maxlag=4800):
    n = min(len(a), len(b)); c = fftconvolve(a[:n], b[:n][::-1], mode='full'); mid = n - 1
    return int(np.argmax(c[mid - maxlag:mid + maxlag + 1]) - maxlag)


rms = lambda y: round(float(20 * np.log10(np.sqrt(np.mean(y * y)) + 1e-12)), 2)
dlg, mus, sfx = (M.read(f'{ST}-{k}.f32.wav') for k in ('dialogue', 'music', 'sfx'))
pre = M.read(W + '-pre.wav'); fin = M.read(FIN); N = len(dlg)
pdk = M.read(W + '-music-preduck.wav') * 10 ** (G / 20)
m2 = {k: M.read(f"{ref['m2_stems']}-{k}.wav")[:N] for k in ('dialogue', 'music', 'sfx')}
m2_in = float(np.nonzero(np.abs(m2['music']) > 10 ** (-80 / 20))[0][0] / SR)
rep = {'sync': {'final_wav_vs_pre_samples': lag(fin, pre)}, 'onsets': [], 'start': {}, 'highs': {}, 'guard': {}, 'levels': {}, 'loudness': {'final_wav': ebur(FIN)}}
for p in MP4:
    dec = M.read(p)
    rep['sync'][os.path.basename(p) + '_audio_vs_pre_samples'] = lag(dec[:N], pre); rep['sync'][os.path.basename(p) + '_audio_len_s'] = len(dec) / SR
    rep['loudness'][os.path.basename(p)] = ebur(p)
# ---- onsets
for ev in pl['sfx']:
    hit = ev['hit']; a = int((hit - 0.15) * SR); seg = sfx[a:int((hit + 0.15) * SR)]
    if ev is pl['sfx'][-1] or 'folder' in ev['name']:
        a = int(ev['file_start_scene_s'] * SR) + int(max(0, ev['attack_in_file_s'] - 0.03) * SR); seg = sfx[a:int((hit + 0.08) * SR)]
    meas = a / SR + M.attack(seg, ev.get('attack_peak_db', 12), ev.get('attack_rise_db', 9))
    rep['onsets'].append({'event': ev['name'], 'layer': 'sfx', 'measured_s': round(meas, 4), 'frame': ev['frame'], 'picture_s': round(ev['frame'] / 30, 4),
                          'error_ms': round((meas - ev['frame'] / 30) * 1000, 1)})
for c in spec['verify']['music']:
    pic = c['frame'] / 30 if 'frame' in c else c['at']
    for nm, y in (('music (pre-duck)', pdk), ('music (delivered)', mus)):
        meas = M.flux_onset(y, c['at'])
        rep['onsets'].append({'event': c['name'], 'layer': nm, 'measured_s': round(meas, 4), 'frame': c.get('frame'), 'picture_s': round(pic, 4),
                              'error_ms': round((meas - pic) * 1000, 1)})
# ---- start of the music and intro vs body
aud = np.nonzero(np.abs(mus) > 10 ** (-80 / 20))[0]
st4, st4d, st2 = M.short_term(pdk), M.short_term(mus), M.short_term(m2['music']); ts = np.arange(len(st4)) / 1000
med = lambda s, a, b: round(float(np.median(s[(ts >= a) & (ts <= b)])), 2)
rep['start'] = {'music_first_sample_s': aud[0] / SR, 'music_rms_frame0_dbfs': rms(mus[:1600]), 'music_rms_0_100ms_dbfs': rms(mus[:4800]),
                'music_rms_100_500ms_dbfs': rms(mus[4800:24000]), 'm2_music_first_sample_s': m2_in,
                'st3s_median_preduck': {'first_10s': med(st4, 1.5, 10), 'body_15_58': med(st4, 15, 58)},
                'st3s_median_delivered': {'first_10s': med(st4d, 1.5, 10), 'body_15_58': med(st4d, 15, 58)},
                'm2_st3s_median_delivered': {'first_10s_from_entry': med(st2, m2_in + 1.5, m2_in + 10), 'body_15_58': med(st2, 15, 58)},
                'note': 'short-term medians start 1.5 s in so every 3 s window is full'}
# ---- highs
def tickspec(y):
    f, t, Z = stft(y, SR, nperseg=2048, noverlap=2048 - 256); P = np.abs(Z) ** 2
    hb = 10 * np.log10(P[(f >= 12000) & (f < 18000)].sum(0) + 1e-20); tk = hb > np.percentile(hb, 60) + 6
    return f, 10 * np.log10(P[:, tk].mean(1) + 1e-30)
fq, sp4 = tickspec(mus); _, sp2 = tickspec(m2['music']); _, spd = tickspec(dlg)
band = lambda sp, a, b: round(float(10 * np.log10(np.mean(10 ** (sp[(fq >= a) & (fq < b)] / 10)))), 2)
for nm, sp in (('m4', sp4), ('m2', sp2)):
    rep['highs'][nm] = {'4_9k_per_bin_db': band(sp, 4000, 9000), '12_17k2_per_bin_db': band(sp, 12000, 17200), '16k5_17k2_per_bin_db': band(sp, 16500, 17200)}
    rep['highs'][nm]['high_minus_mid_db'] = round(rep['highs'][nm]['12_17k2_per_bin_db'] - rep['highs'][nm]['4_9k_per_bin_db'], 2)
# ---- guard and levels
hop = 480
env = lambda y, w: M.env_db(y, w, hop)
out = {}
for name, (d, mu, sx, g) in {'m4': (dlg, mus, sfx, G), 'm2': (m2['dialogue'], m2['music'], m2['sfx'], G2)}.items():
    for wms in (100, 200):
        w = wms * 48; D, Mu = env(d, w), env(mu[:N], w)
        for thr in (-30, -35):
            act = D - g >= thr; m = np.where(act, D - Mu, np.inf); k = int(np.argmin(m))
            rep['guard'][f'{name}_{wms}ms_active{-thr}'] = {'windows': int(act.sum()), 'min_db': round(float(m[k]), 2), 'at_s': round(k * hop / SR + wms / 2000, 2),
                                                           'p05_db': round(float(np.percentile(m[act], 5)), 2), 'median_db': round(float(np.median(m[act])), 2),
                                                           'share_under_12_db': round(float((m[act] < 12).mean()), 3), 'share_under_16_db': round(float((m[act] < 16).mean()), 3)}
    D, Mu, S = env(d, 4800), env(mu[:N], 4800), env(sx, 4800)
    t = np.arange(len(D)) * hop / SR + 0.05
    out[name] = dict(t=t, D=D, M=Mu, S=S)
frac = np.load(W + '-duckfrac.npy'); t = out['m4']['t']; fr = np.interp(t, np.arange(len(frac)) / 1000, frac)
fr_max = np.array([frac[max(0, int(x * 1000) - 50):int(x * 1000) + 50].max() for x in t])
for name, g, s_in in (('m4', G, pl['music']['in_scene']), ('m2', G2, m2_in)):
    D, Mu = out[name]['D'], out[name]['M']
    live = (t > s_in + 0.1) & (t < pl['music']['end']['fade_from'] - 0.05)
    act = (D - g >= -30) & live
    rep['levels'][name] = {'music_under_speech_median_dbfs': round(float(np.median(Mu[act])), 2),
                           'dialogue_minus_music_under_speech_median_db': round(float(np.median((D - Mu)[act])), 2),
                           'dialogue_active_median_dbfs': round(float(np.median(D[act])), 2), 'loudness_gain_db': g}
    if name == 'm4':
        opn = (fr_max < 0.02) & live
        rep['levels'][name].update(music_open_pauses_median_dbfs=round(float(np.median(Mu[opn])), 2), open_windows=int(opn.sum()),
                                   open_minus_under_db=round(float(np.median(Mu[opn]) - np.median(Mu[act])), 2))
rep['levels']['dialogue_drop_vs_m2_db'] = {'loudness_gain': round(G - G2, 2),
                                           'active_median': round(rep['levels']['m4']['dialogue_active_median_dbfs'] - rep['levels']['m2']['dialogue_active_median_dbfs'], 2)}
rep['levels']['music_under_speech_vs_m2_db'] = round(rep['levels']['m4']['music_under_speech_median_dbfs'] - rep['levels']['m2']['music_under_speech_median_dbfs'], 2)
rep['levels']['music_under_lufs_re_cue'] = pl['music']['norm_lufs'] + pl['music']['under_db_re_norm']
np.savez(f'{R}/levels.npz', **{f'{k}_{x}': v[x] for k, v in out.items() for x in ('t', 'D', 'M', 'S')}, m4_frac=fr, m4_gain=G, m2_gain=G2,
         st_t=ts[::100], st_m4=st4d[::100], st_m4_preduck=st4[::100], st_m2=st2[::100], fq=fq, sp_m4=sp4, sp_m2=sp2, sp_dlg=spd,
         events=json.dumps([{'t': o['measured_s'], 'name': o['event']} for o in rep['onsets'] if o['layer'] != 'music (delivered)']), title=spec['title'],
         extra_db=spec['music'].get('extra_db', 0), stats=json.dumps(rep))
json.dump(rep, open(f'{R}/verify.json', 'w'), indent=1, default=float)
print(json.dumps({k: rep[k] for k in ('sync', 'start', 'highs', 'levels', 'loudness')}, indent=1, default=float))
for k, v in rep['guard'].items():
    print(f"guard {k:22s} min {v['min_db']:6.2f} dB at {v['at_s']:6.2f} s  p05 {v['p05_db']:6.2f}  median {v['median_db']:6.2f}  <12: {v['share_under_12_db']:.3f}  <16: {v['share_under_16_db']:.3f}  ({v['windows']} windows)")
for o in rep['onsets']:
    print(f"{o['layer']:17s} {o['event']:42s} measured {o['measured_s']:8.4f}  picture {o['picture_s']:8.4f} (frame {o['frame']})  err {o['error_ms']:+6.1f} ms")
