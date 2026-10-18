#!/usr/bin/env python3
"""m2 audio verification (verify-m4.py with the scene's m1 as the reference). Runs on do-box (/home/claude/venvs/manim; ffmpeg audio only, -vn).
usage: verify-m2.py <spec.json> <work prefix> <stem prefix> <final.wav> <report dir> [<m2.mp4> <m2-phone.mp4>]   (run from the work root)
Checks:
  sync     lag of the final wav (and the mp4s' decoded audio) against the pre-limiter sum (0 = the delivered dialogue's timing)
  onsets   every effect on the m2 sfx stem vs its frame and vs the same measurement on m1's sfx stem; the music downbeats (spectral flux) on the
           pre-duck m2 music vs the same on m1's music stem (placement unchanged = 0 ms)
  start    first music sample above -80 dBFS, m2 and m1
  highs    music stem per-bin power in high-band frames (12-18 kHz > p60 + 6 dB): 4-9 kHz vs 12-17.2 kHz, m2 vs m1
  guard    dialogue minus music in 100 / 200 ms windows (10 ms hop) where the dialogue at its delivered level is >= -30 (and -35) dBFS:
           min, p05, median, share under 12 and 16 dB; m1 the same
  levels   music under speech / in open pauses (medians), dialogue - music under speech; music under speech vs m1
  loudness ebur128 of the final wav and the mp4s' decoded audio
Writes <report dir>/verify.json and levels.npz (plot-levels-m2.py)."""
import sys, os, json, re, subprocess, importlib.util
import numpy as np
from scipy.signal import fftconvolve, stft

here = os.path.dirname(os.path.abspath(__file__))
s_ = importlib.util.spec_from_file_location('mm', os.path.join(here, 'music-m4.py')); M = importlib.util.module_from_spec(s_); s_.loader.exec_module(M)
spec = json.load(open(sys.argv[1])); W, ST, FIN, R = sys.argv[2:6]; MP4 = sys.argv[6:8]
os.makedirs(R, exist_ok=True); SR = 48000; FPS = spec.get('fps', 30)
pl = json.load(open(W + '-placements.json')); G = json.load(open(W + '-loudness.json'))['linear_gain_db']
ref = spec['ref']; G1 = ref['gain_db']


def ebur(p):
    s = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-vn', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    s = s[s.rindex('Summary:'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))
    return {'I': g('I'), 'LRA': g('LRA'), 'true_peak_dbtp': g('Peak')}


def lag(a, b, maxlag=4800):
    n = min(len(a), len(b)); c = fftconvolve(a[:n], b[:n][::-1], mode='full'); mid = n - 1
    return int(np.argmax(c[mid - maxlag:mid + maxlag + 1]) - maxlag)


def onset_env(x, t0, t1, rel=-12.0):
    """mix-m1.py: first 1 ms block in [t0, t1] whose peak is within rel dB of the window's peak"""
    a, b = max(0, int(t0 * SR)), int(t1 * SR); n = 48; s = np.abs(x[a:b]); k = len(s) // n; e = s[:k * n].reshape(k, n).max(1)
    return a / SR + int(np.argmax(e >= e.max() * 10 ** (rel / 20))) * n / SR


def rms_peak(x, t0, t1, win=.05):
    a, b = int(t0 * SR), int(t1 * SR); n = int(win * SR); r = np.convolve(x[a:b] ** 2, np.ones(n) / n, 'same'); return t0 + int(np.argmax(r)) / SR


rms = lambda y: round(float(20 * np.log10(np.sqrt(np.mean(y * y)) + 1e-12)), 2)
dlg, mus, sfx = (M.read(f'{ST}-{k}.f32.wav') for k in ('dialogue', 'music', 'sfx'))
N = len(dlg); mus = mus[:N]
pre = M.read(W + '-pre.wav'); fin = M.read(FIN)
pdk = M.read(W + '-music-preduck.wav')[:N] * 10 ** (G / 20)
m1 = {k: M.read(f"{ref['stems']}-{k}.wav") for k in ('dialogue', 'music', 'sfx')}
m1 = {k: np.pad(v, (0, max(0, N - len(v))))[:N] for k, v in m1.items()}
m1_in = float(np.nonzero(np.abs(m1['music']) > 10 ** (-80 / 20))[0][0] / SR)
rep = {'sync': {'final_wav_vs_pre_samples': lag(fin, pre)}, 'onsets': [], 'start': {}, 'highs': {}, 'guard': {}, 'levels': {}, 'loudness': {'final_wav': ebur(FIN)}}
for p in MP4:
    dec = M.read(p)
    rep['sync'][os.path.basename(p) + '_audio_vs_pre_samples'] = lag(dec[:N], pre); rep['sync'][os.path.basename(p) + '_audio_len_s'] = len(dec) / SR
    rep['loudness'][os.path.basename(p)] = ebur(p)
# ---- onsets
for ev in pl['sfx']:
    tf = ev['frame'] / FPS if spec['sfx_mode'] == 'event_lufs' else ev['hit']
    meas = (lambda x: rms_peak(x, tf - .35, tf + .35)) if ev.get('swell') else (lambda x: onset_env(x, tf - .04, tf + .04))
    a2, a1 = meas(sfx), meas(m1['sfx'])
    rep['onsets'].append({'event': ev.get('id', ev.get('name')), 'layer': 'sfx', 'measured_s': round(a2, 4), 'frame': ev['frame'], 'picture_s': round(ev['frame'] / FPS, 4),
                          'error_ms': round((a2 - ev['frame'] / FPS) * 1000, 1), 'vs_m1_ms': round((a2 - a1) * 1000, 1), 'gain_db': ev['gain_applied_db'],
                          'level_vs_m1_db': round(rms(sfx[int((tf - .05) * SR):int((tf + .3) * SR)]) - rms(m1['sfx'][int((tf - .05) * SR):int((tf + .3) * SR)]) - (G - G1), 2)})
for c in spec['verify']['music']:
    pic = c['frame'] / FPS if 'frame' in c else c['at']
    a1 = M.flux_onset(m1['music'], c['at'])
    for nm, y in (('music (pre-duck)', pdk), ('music (delivered)', mus)):
        meas = M.flux_onset(y, c['at'])
        rep['onsets'].append({'event': c['name'], 'layer': nm, 'measured_s': round(meas, 4), 'frame': c.get('frame'), 'picture_s': round(pic, 4),
                              'error_ms': round((meas - pic) * 1000, 1), 'vs_m1_ms': round((meas - a1) * 1000, 1)})
aud = np.nonzero(np.abs(mus) > 10 ** (-80 / 20))[0]
rep['start'] = {'music_first_sample_s': aud[0] / SR, 'm1_music_first_sample_s': m1_in, 'music_last_sample_in_scene_s': aud[-1] / SR}
# ---- highs
def tickspec(y):
    f, t, Z = stft(y, SR, nperseg=2048, noverlap=2048 - 256); P = np.abs(Z) ** 2
    hb = 10 * np.log10(P[(f >= 12000) & (f < 18000)].sum(0) + 1e-20); live = P.sum(0) > 1e-12
    tk = (hb > np.percentile(hb[live], 60) + 6) & live
    return f, 10 * np.log10(P[:, tk].mean(1) + 1e-30)
fq, sp2 = tickspec(mus); _, sp1 = tickspec(m1['music']); _, spd = tickspec(dlg)
band = lambda sp, a, b: round(float(10 * np.log10(np.mean(10 ** (sp[(fq >= a) & (fq < b)] / 10)))), 2)
for nm, sp in (('m2', sp2), ('m1', sp1)):
    rep['highs'][nm] = {'4_9k_per_bin_db': band(sp, 4000, 9000), '12_17k2_per_bin_db': band(sp, 12000, 17200)}
    rep['highs'][nm]['high_minus_mid_db'] = round(rep['highs'][nm]['12_17k2_per_bin_db'] - rep['highs'][nm]['4_9k_per_bin_db'], 2)
# ---- guard and levels
hop = 480
env = lambda y, w: M.env_db(y, w, hop)
out = {}
for name, (d, mu, sx, g) in {'m2': (dlg, mus, sfx, G), 'm1': (m1['dialogue'], m1['music'], m1['sfx'], G1)}.items():
    for wms in (100, 200):
        w = wms * 48; D, Mu = env(d, w), env(mu, w)
        for thr in (-30, -35):
            act = (D - g >= thr) & (Mu > -100); m = np.where(act, D - Mu, np.inf); k = int(np.argmin(m))
            rep['guard'][f'{name}_{wms}ms_active{-thr}'] = {'windows': int(act.sum()), 'min_db': round(float(m[k]), 2), 'at_s': round(k * hop / SR + wms / 2000, 2),
                                                           'p05_db': round(float(np.percentile(m[act], 5)), 2), 'median_db': round(float(np.median(m[act])), 2),
                                                           'share_under_12_db': round(float((m[act] < 12).mean()), 3), 'share_under_16_db': round(float((m[act] < 16).mean()), 3)}
    D, Mu, S = env(d, 4800), env(mu, 4800), env(sx, 4800)
    t = np.arange(len(D)) * hop / SR + 0.05
    out[name] = dict(t=t, D=D, M=Mu, S=S)
frac = np.load(W + '-duckfrac.npy'); t = out['m2']['t']; fr = np.interp(t, np.arange(len(frac)) / 1000, frac)
fr_max = np.array([frac[max(0, int(x * 1000) - 50):int(x * 1000) + 50].max() for x in t])
s_in, e_from = pl['music']['in_scene'], pl['music']['end']['fade_from']
for name, g in (('m2', G), ('m1', G1)):
    D, Mu = out[name]['D'], out[name]['M']
    live = (t > s_in + 0.1) & (t < e_from - 0.05)
    act = (D - g >= -30) & live
    rep['levels'][name] = {'music_under_speech_median_dbfs': round(float(np.median(Mu[act])), 2),
                           'dialogue_minus_music_under_speech_median_db': round(float(np.median((D - Mu)[act])), 2),
                           'dialogue_active_median_dbfs': round(float(np.median(D[act])), 2), 'loudness_gain_db': g}
    opn = (fr_max < 0.02) & live
    if opn.any():
        rep['levels'][name]['music_open_pauses_median_dbfs'] = round(float(np.median(Mu[opn])), 2)
rep['levels']['m2']['open_minus_under_db'] = round(rep['levels']['m2'].get('music_open_pauses_median_dbfs', np.nan) - rep['levels']['m2']['music_under_speech_median_dbfs'], 2)
rep['levels']['music_under_speech_vs_m1_db'] = round(rep['levels']['m2']['music_under_speech_median_dbfs'] - rep['levels']['m1']['music_under_speech_median_dbfs'], 2)
rep['levels']['music_under_lufs_re_cue'] = pl['music']['under_lufs']
st2, st2p, st1 = M.short_term(mus), M.short_term(pdk), M.short_term(m1['music']); ts = np.arange(len(st2)) / 1000
np.savez(f'{R}/levels.npz', **{f'{k}_{x}': v[x] for k, v in out.items() for x in ('t', 'D', 'M', 'S')}, m2_frac=fr, m2_gain=G, m1_gain=G1,
         st_t=ts[::100], st_m2=st2[::100], st_m2_preduck=st2p[::100], st_m1=st1[::100], fq=fq, sp_m2=sp2, sp_m1=sp1, sp_dlg=spd,
         events=json.dumps([{'t': o['measured_s'], 'name': o['event']} for o in rep['onsets'] if o['layer'] != 'music (delivered)']), title=spec['title'],
         eq=json.dumps(pl['music']['eq']), stats=json.dumps(rep, default=float))
json.dump(rep, open(f'{R}/verify.json', 'w'), indent=1, default=float)
print(json.dumps({k: rep[k] for k in ('sync', 'start', 'highs', 'levels', 'loudness')}, indent=1, default=float))
for k, v in rep['guard'].items():
    print(f"guard {k:22s} min {v['min_db']:6.2f} dB at {v['at_s']:6.2f} s  p05 {v['p05_db']:6.2f}  median {v['median_db']:6.2f}  <12: {v['share_under_12_db']:.3f}  <16: {v['share_under_16_db']:.3f}  ({v['windows']} windows)")
for o in rep['onsets']:
    print(f"{o['layer']:17s} {o['event']:40s} measured {o['measured_s']:8.4f}  picture {o['picture_s']:8.4f} (frame {o['frame']})  err {o['error_ms']:+6.1f} ms  vs m1 {o['vs_m1_ms']:+5.1f} ms"
          + (f"  gain {o['gain_db']} dB, level vs m1 {o['level_vs_m1_db']:+.2f} dB" if o['layer'] == 'sfx' else ''))
