#!/usr/bin/env python3
"""m1 verification. Runs ON dev-mac with ~/speech-lab/.venv/bin/python3 and ffmpeg-full on PATH.
usage: verify-m1.py <spec.json> <work prefix> <report dir>
Checks, from the delivered files:
  video   md5 of the video stream (stream copy) of the source master and the m1 file, main and phone; frame counts and durations
  sync    lag of the m1 mp4's decoded audio against the pre-limiter sum, and of the source master's audio against the dialogue stem
          (cross-correlation, samples; 0 = the dialogue sits where it did in the locked master)
  onsets  every sound effect: its hit measured on the sfx stem (attack detector of music-m1.py, isolated 0.3 s window) or, for a swell aligned by
          its end, its position by cross-correlation with the file; every music in / anchor / out: spectral-flux onset or first/last audible
          sample on the music stem. Each is compared with its picture time (frame / 30) and the delivered time adds the measured lag.
  guard   dialogue stem minus music stem in 100 ms windows (10 ms hop) where the dialogue, at the level the locked scene delivered it (before
          the m1 loudness gain), is >= -30 dBFS (and, for reference, >= -35 dBFS),
          plus dialogue minus music+sfx (reference)
  loudness ebur128 of the decoded m1 mp4 audio, main and phone
Writes <report dir>/verify.json, levels.npz (100 ms envelopes for the plot) and audio16k-{src,m1}.wav (for the transcript)."""
import sys, os, json, re, subprocess, importlib.util
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve

spec = json.load(open(sys.argv[1])); W = sys.argv[2]; R = sys.argv[3]; os.makedirs(R, exist_ok=True)
here = os.path.dirname(os.path.abspath(__file__))
mm = importlib.util.spec_from_file_location('mm', os.path.join(here, 'music-m1.py')); M1 = importlib.util.module_from_spec(mm); mm.loader.exec_module(M1)
SR = 48000; V = spec['verify']; X = os.path.expanduser
pl = json.load(open(W + '-placements.json'))


def run(a):
    return subprocess.run(a, capture_output=True, text=True)


def md5(p):
    return run(['ffmpeg', '-nostdin', '-v', 'error', '-i', p, '-map', '0:v', '-c', 'copy', '-f', 'md5', '-']).stdout.strip()


def probe(p):
    s = run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,nb_frames,duration', '-of', 'json', p]).stdout
    return {x['codec_type']: {'frames': x.get('nb_frames'), 'duration': x.get('duration')} for x in json.loads(s)['streams']}


def decode(p, sr=SR):
    return np.frombuffer(subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', p, '-map', '0:a', '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'],
                                        capture_output=True).stdout, np.float32).astype(float)


def ebur(p):
    s = run(['ffmpeg', '-nostdin', '-hide_banner', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr
    s = s[s.rindex('Summary:'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))
    return {'I': g('I'), 'LRA': g('LRA'), 'true_peak_dbfs': g('Peak')}


def lag(a, b, maxlag=4800):
    """samples by which a is late against b"""
    n = min(len(a), len(b)); c = fftconvolve(a[:n], b[:n][::-1], mode='full'); mid = n - 1
    k = np.argmax(c[mid - maxlag:mid + maxlag + 1]); return int(k - maxlag)


rep = {'video': {}, 'onsets': [], 'guard': {}, 'loudness': {}}
for a, b in (('src', 'dst'), ('src_phone', 'dst_phone')):
    rep['video'][b] = {'src_md5': md5(V[a]), 'm1_md5': md5(V[b]), 'src': probe(V[a]), 'm1': probe(V[b])}
    rep['video'][b]['identical'] = rep['video'][b]['src_md5'] == rep['video'][b]['m1_md5']
dlg, _ = sf.read(V['stems'] + '-dialogue.wav'); mus, _ = sf.read(V['stems'] + '-music.wav'); sfx, _ = sf.read(V['stems'] + '-sfx.wav')
pre, _ = sf.read(W + '-pre.wav'); fin, _ = sf.read(V['final'])
N = len(dlg); dec = decode(V['dst'])
rep['sync'] = {'final_wav_vs_pre_samples': lag(fin, pre), 'm1_mp4_audio_vs_final_wav_samples': lag(dec[:N], fin), 'm1_mp4_audio_vs_pre_samples': lag(dec[:N], pre),
               'src_mp4_audio_vs_dialogue_stem_samples': lag(decode(V['src'])[:N], dlg), 'decoded_len_s': len(dec) / SR, 'scene_s': N / SR}
L = rep['sync']['m1_mp4_audio_vs_pre_samples'] / SR
# ---- onsets
for ev in pl['sfx']:
    hit = ev['hit']; z = M1.mono(ev['file']) * 10 ** (ev['gain'] / 20)
    def locate(a, b):                                       # the file where music-m1.py put it, then the lag of the stem against that
        ref = np.zeros(N); i0 = int(round(ev['file_start_scene_s'] * SR)); zz = z[max(0, -i0):]; i0 = max(0, i0)
        ref[i0:i0 + len(zz)] = zz[:N - i0]
        a, b = max(0, int(a * SR)), min(N, int(b * SR))
        return ev['file_start_scene_s'] + lag(sfx[a:b], ref[a:b], 2400) / SR
    if ev.get('align') == 'cut':                            # a swell that stops on the event: up to 5 ms before the event it lands on
        meas = locate(ev['file_start_scene_s'] - 0.05, hit - 0.005) + ev['attack_in_file_s']; how = 'cross-correlation with the file, + its cut point'
    elif 'attack_s' in ev:
        meas = locate(hit - 0.3, hit + 0.15) + ev['attack_in_file_s']; how = 'cross-correlation with the file, + its measured hit'
    else:
        a = int((hit - 0.15) * SR); seg = sfx[max(0, a):int((hit + 0.15) * SR)]
        try:
            meas = max(0, a) / SR + M1.attack(seg); how = 'attack detector on the sfx stem'
        except ValueError:                                  # another effect runs into it: locate the file in the stem instead
            meas = locate(ev['file_start_scene_s'] - 0.05, ev['file_start_scene_s'] + 0.25) + ev['attack_in_file_s']; how = 'cross-correlation with the file + its attack'
    pic = ev['frame'] / 30
    rep['onsets'].append({'event': ev['name'], 'layer': 'sfx', 'measured_stem_s': round(meas, 4), 'delivered_s': round(meas + L, 4), 'picture_frame': ev['frame'],
                          'picture_s': round(pic, 4), 'error_ms': round((meas - pic) * 1000, 1), 'delivered_error_ms': round((meas + L - pic) * 1000, 1), 'how': how})
mt = mus
aud = np.nonzero(np.abs(mt) > 10 ** (-80 / 20))[0]
for c in V['music']:
    if c['kind'] == 'in':
        meas = aud[0] / SR; how = 'first music-stem sample above -80 dBFS'
    elif c['kind'] == 'silent':
        meas = (aud[-1] + 1) / SR; how = 'last music-stem sample above -80 dBFS'
    else:
        meas = M1.flux_onset(mt, c['at'], c.get('win', 0.06)); how = 'spectral-flux onset on the music stem'
    rep['onsets'].append({'event': c['name'], 'layer': 'music', 'measured_stem_s': round(meas, 4), 'delivered_s': round(meas + L, 4),
                          'picture_frame': c.get('frame'), 'picture_s': round(c['picture'], 4), 'error_ms': round((meas - c['picture']) * 1000, 1),
                          'delivered_error_ms': round((meas + L - c['picture']) * 1000, 1), 'how': how, 'note': c.get('note', '')})
# ---- guard
w, hop = 4800, 480
D, Mu, S = M1.env_db(dlg, w, hop), M1.env_db(mus[:N], w, hop), M1.env_db(sfx, w, hop)
MS = 10 * np.log10(10 ** (Mu / 10) + 10 ** (S / 10))
G = json.load(open(W + '-loudness.json'))['linear_gain_db']      # the stems carry the loudness gain; activity is judged on the dialogue as the
rep['guard']['stem_gain_db'] = G                                  # locked scene delivered it (the level music-m1.py guarded)
for thr in (-30, -35):
    act = D - G >= thr
    m = np.where(act, D - Mu, np.inf); k = int(np.argmin(m))
    m2 = np.where(act & (MS > -90), D - MS, np.inf); k2 = int(np.argmin(m2))
    rep['guard'][f'active_{-thr}'] = {'windows': int(act.sum()), 'min_dialogue_minus_music_db': round(float(m[k]), 2), 'at_s': k * hop / SR,
                                      'min_dialogue_minus_music_plus_sfx_db': round(float(m2[k2]), 2), 'mms_at_s': k2 * hop / SR,
                                      'p05_dialogue_minus_music_db': round(float(np.percentile(m[act], 5)), 2)}
# ---- loudness
rep['loudness'] = {'m1': ebur(V['dst']), 'm1_phone': ebur(V['dst_phone']), 'src': ebur(V['src'])}
# ---- plot data + transcript audio
t = np.arange(len(D)) * hop / SR + 0.05
np.savez(f'{R}/levels.npz', t=t, dialogue=D, music=Mu, sfx=S,
         events=json.dumps([{'t': o['measured_stem_s'], 'name': o['event'], 'layer': o['layer']} for o in rep['onsets']]),
         auto=json.dumps(pl['music']['auto']), title=spec.get('title', ''), stem_gain_db=G)
for k, p in (('src', V['src']), ('m1', V['dst'])):
    sf.write(f'{R}/audio16k-{k}.wav', decode(p, 16000), 16000, subtype='PCM_16')
json.dump(rep, open(f'{R}/verify.json', 'w'), indent=1, default=float)
print(json.dumps({k: rep[k] for k in ('sync', 'guard', 'loudness')}, indent=1, default=float))
for k, v in rep['video'].items():
    print(f"video {k}: identical={v['identical']} {v['m1_md5']} frames {v['m1']['video']['frames']} audio {v['m1']['audio']['duration']}")
for o in rep['onsets']:
    print(f"{o['layer']:5s} {o['event']:42s} stem {o['measured_stem_s']:8.3f}  delivered {o['delivered_s']:8.3f}  picture {o['picture_s']:8.3f}"
          f" (frame {o['picture_frame']})  err {o['error_ms']:+6.1f} ms  delivered {o['delivered_error_ms']:+6.1f} ms  [{o['how']}]")
