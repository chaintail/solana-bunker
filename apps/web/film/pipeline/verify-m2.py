#!/usr/bin/env python3
"""m2 audio verification. Runs on do-box (/home/claude/venvs/manim; ffmpeg audio only, -vn).
usage: verify-m2.py <spec.json> <work prefix> <stem prefix> <final.wav> <m1 dir> <report dir> [<m2.mp4> <m2-phone.mp4>]
  m1 dir holds m1's stems (m1-{dialogue,music,sfx}.wav before the loudness gain, m1-loudness.json) copied from dev-mac out/consp-m1.
Checks:
  sync     lag of the final wav (and, given the mp4s, their decoded audio) against the pre-limiter sum (cross-correlation; 0 = x12b timing)
  onsets   every sound effect on the sfx stem (music-m2.py attack detector with the effect's own thresholds, in a 0.3 s window), the music
           anchors on the music stem (spectral flux; the sidechain's gain moves and the 100 Hz high-pass can pull this a few ms), against
           frame / 30, and the lag of the m2 music stem (+ a 180 Hz high-pass) against m1's (+ a 100 Hz high-pass, so both carry the same filters) in the 1.3 s around each anchor (0 = placed as m1)
  guard    dialogue minus music in 100 ms and 200 ms windows (10 ms hop) where the dialogue, at x12b's delivered level, is >= -30 dBFS
           (and -35 for reference); minimum, 5th percentile, share of windows under the target; m1 the same way
  levels   music 100 ms RMS (median) where the dialogue is active (-30 dBFS) and in the pauses (sidechain fully open, after the music entry),
           dialogue minus music median under speech; m1 under speech and in its >= 0.8 s gaps
  loudness ebur128 of the final wav and of the mp4s' decoded audio
Writes <report dir>/verify.json and levels.npz (both mixes, for plot-levels-m2.py)."""
import sys, os, json, re, subprocess, importlib.util
import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve

here = os.path.dirname(os.path.abspath(__file__))
s_ = importlib.util.spec_from_file_location('mm', os.path.join(here, 'music-m2.py')); M = importlib.util.module_from_spec(s_); s_.loader.exec_module(M)
spec = json.load(open(sys.argv[1])); W, ST, FIN, M1D, R = sys.argv[2:7]; MP4 = sys.argv[7:9]
os.makedirs(R, exist_ok=True); SR = 48000
pl = json.load(open(W + '-placements.json')); G = json.load(open(W + '-loudness.json'))['linear_gain_db']
G1 = json.load(open(os.path.join(M1D, 'm1-loudness.json')))['linear_gain_db']


def ebur(p):
    s = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-vn', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    s = s[s.rindex('Summary:'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))
    return {'I': g('I'), 'LRA': g('LRA'), 'true_peak_dbtp': g('Peak')}


def lag(a, b, maxlag=4800):
    n = min(len(a), len(b)); c = fftconvolve(a[:n], b[:n][::-1], mode='full'); mid = n - 1
    return int(np.argmax(c[mid - maxlag:mid + maxlag + 1]) - maxlag)


dlg, mus, sfx = (M.read(f'{ST}-{k}.f32.wav') for k in ('dialogue', 'music', 'sfx'))
pre = M.read(W + '-pre.wav'); fin = M.read(FIN); N = len(dlg)
m1 = {k: M.read(os.path.join(M1D, f'm1-{k}.wav')) for k in ('dialogue', 'music', 'sfx')}     # m1 work stems: before m1's loudness gain
rep = {'sync': {'final_wav_vs_pre_samples': lag(fin, pre)}, 'onsets': [], 'guard': {}, 'levels': {}, 'loudness': {'final_wav': ebur(FIN)}}
for p in MP4:
    dec = M.read(p)
    rep['sync'][os.path.basename(p) + '_audio_vs_pre_samples'] = lag(dec[:N], pre); rep['sync'][os.path.basename(p) + '_audio_len_s'] = len(dec) / SR
    rep['loudness'][os.path.basename(p)] = ebur(p)
# ---- onsets
for ev in pl['sfx']:
    hit = ev['hit']; a = int((hit - 0.15) * SR); seg = sfx[a:int((hit + 0.15) * SR)]
    if ev is pl['sfx'][-1] or 'folder' in ev['name']:          # the folder and the ? are 0.3 s apart: isolate each from its own file start
        a = int(ev['file_start_scene_s'] * SR) + int(max(0, ev['attack_in_file_s'] - 0.03) * SR); seg = sfx[a:int((hit + 0.08) * SR)]
    meas = a / SR + M.attack(seg, ev.get('attack_peak_db', 12), ev.get('attack_rise_db', 9))
    rep['onsets'].append({'event': ev['name'], 'layer': 'sfx', 'measured_s': round(meas, 4), 'frame': ev['frame'], 'picture_s': round(ev['frame'] / 30, 4),
                          'error_ms': round((meas - ev['frame'] / 30) * 1000, 1)})
for c in spec['verify']['music']:
    meas = M.flux_onset(mus, c['at']); pic = c['frame'] / 30 if 'frame' in c else c['at']
    rep['onsets'].append({'event': c['name'], 'layer': 'music', 'measured_s': round(meas, 4), 'frame': c.get('frame'), 'picture_s': round(pic, 4),
                          'error_ms': round((meas - pic) * 1000, 1)})
for c in spec['verify']['music']:                           # placement against m1: the music stems differ in filter and gain, not in time
    a, b = int((c['at'] - 1.0) * SR), int((c['at'] + 0.3) * SR)
    rep['onsets'].append({'event': c['name'] + ' (m2 music stem lag vs m1 music stem, samples)', 'layer': 'music-vs-m1',
                          'lag_samples': lag(M.hp(mus[a:b], 180), M.hp(m1['music'][a:b], 100), 480)})
aud = np.nonzero(np.abs(mus) > 10 ** (-80 / 20))[0]
rep['music_audible_s'] = [aud[0] / SR, (aud[-1] + 1) / SR]
# ---- guard and levels
hop = 480
env = lambda y, w: M.env_db(y, w, hop)
out = {}
for name, (d, mu, sx, g) in {'m2': (dlg, mus, sfx, G), 'm1': (m1['dialogue'], m1['music'], m1['sfx'], 0.0)}.items():
    for wms in (100, 200):
        w = wms * 48; D, Mu = env(d, w), env(mu[:N], w)
        for thr in (-30, -35):
            act = D - g >= thr; m = np.where(act, D - Mu, np.inf); k = int(np.argmin(m))
            rep['guard'][f'{name}_{wms}ms_active{-thr}'] = {'windows': int(act.sum()), 'min_db': round(float(m[k]), 2), 'at_s': round(k * hop / SR + wms / 2000, 2),
                                                           'p05_db': round(float(np.percentile(m[act], 5)), 2), 'median_db': round(float(np.median(m[act])), 2),
                                                           'share_under_12_db': round(float((m[act] < 12).mean()), 3), 'share_under_16_db': round(float((m[act] < 16).mean()), 3)}
    D, Mu, S = env(d, 4800), env(mu[:N], 4800), env(sx, 4800)
    t = np.arange(len(D)) * hop / SR + 0.05
    out[name] = dict(t=t, D=D, M=Mu, S=S, g=g)
t, D, Mu = out['m2']['t'], out['m2']['D'], out['m2']['M']
frac = np.load(W + '-duckfrac.npy'); fr = np.interp(t, np.arange(len(frac)) / 1000, frac)
fr_max = np.array([frac[max(0, int(x * 1000) - 50):int(x * 1000) + 50].max() for x in t])     # whole 100 ms window open
live = (t > pl['music']['in_scene'] + 0.1) & (t < pl['music']['end']['fade_from'] - 0.05)
act = (D - G >= -30) & live; opn = (fr_max < 0.02) & live
rep['levels']['m2'] = {'music_under_speech_median_dbfs': round(float(np.median(Mu[act])), 2), 'music_open_pauses_median_dbfs': round(float(np.median(Mu[opn])), 2),
                       'open_minus_under_db': round(float(np.median(Mu[opn]) - np.median(Mu[act])), 2),
                       'dialogue_minus_music_under_speech_median_db': round(float(np.median((D - Mu)[act])), 2),
                       'dialogue_active_median_dbfs': round(float(np.median(D[act])), 2), 'open_windows': int(opn.sum()), 'note': 'stems after the m2 loudness gain'}
t1, D1, M1u = out['m1']['t'], out['m1']['D'], out['m1']['M']
gaps = [(5.40, 6.14), (19.75, 20.20), (22.77, 23.74), (55.35, 56.21)]       # m1's -14 gap holds (conspiracy-m1.json auto)
gp = np.zeros(len(t1), bool)
for a, b in gaps:
    gp |= (t1 >= a + 0.1) & (t1 <= b - 0.05)
act1 = (D1 >= -30) & live
rep['levels']['m1'] = {'music_under_speech_median_dbfs': round(float(np.median(M1u[act1])), 2), 'music_in_gaps_median_dbfs': round(float(np.median(M1u[gp])), 2),
                       'dialogue_minus_music_under_speech_median_db': round(float(np.median((D1 - M1u)[act1])), 2),
                       'dialogue_active_median_dbfs': round(float(np.median(D1[act1])), 2),
                       'note': 'm1 work stems, before m1 loudness gain (%+.2f dB); add it to compare absolute levels' % G1, 'm1_gain_db': G1}
rep['levels']['m2_music_under_speech_minus_m1_gap_db_at_delivery'] = round(rep['levels']['m2']['music_under_speech_median_dbfs'] - (rep['levels']['m1']['music_in_gaps_median_dbfs'] + G1), 2)
np.savez(f'{R}/levels.npz', **{f'{k}_{x}': v[x] for k, v in out.items() for x in ('t', 'D', 'M', 'S')}, m2_frac=fr, m2_gain=G, m1_gain=G1,
         events=json.dumps([{'t': o['measured_s'], 'name': o['event']} for o in rep['onsets'] if 'measured_s' in o]), title=spec['title'])
json.dump(rep, open(f'{R}/verify.json', 'w'), indent=1, default=float)
print(json.dumps({k: rep[k] for k in ('sync', 'levels', 'loudness', 'music_audible_s')}, indent=1, default=float))
for k, v in rep['guard'].items():
    print(f"guard {k:22s} min {v['min_db']:6.2f} dB at {v['at_s']:6.2f} s  p05 {v['p05_db']:6.2f}  median {v['median_db']:6.2f}  <12: {v['share_under_12_db']:.3f}  <16: {v['share_under_16_db']:.3f}  ({v['windows']} windows)")
for o in rep['onsets']:
    if 'lag_samples' in o:
        print(f"{o['layer']:5s} {o['event']}: {o['lag_samples']}"); continue
    print(f"{o['layer']:5s} {o['event']:42s} measured {o['measured_s']:8.4f}  picture {o['picture_s']:8.4f} (frame {o['frame']})  err {o['error_ms']:+6.1f} ms")
