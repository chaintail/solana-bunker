#!/usr/bin/env python3
"""m2 loudness. Runs on do-box (/home/claude/venvs/manim, ffmpeg audio only).
usage: finish-m2.py <prefix> <final.wav> <stem prefix>
  reads <prefix>-pre.wav and the three stems (music-m2.py); writes <final.wav> (48 kHz mono 24-bit) and <stem prefix>-dialogue/-music/-sfx.wav
  (24-bit, the stems times the loudness gain, before the limiter).
Goal: -16.0 LUFS integrated (ebur128) and a true peak <= TP_MAX (-1.3 dBTP) before AAC. One gain (volume, = loudnorm's linear gain; loudnorm's
own linear mode cannot hold the peak ceiling on this mix) and one alimiter (level=0, latency=1: the dialogue keeps x12b's timing; asc off).
m1 ran x12b's limiter (0.95) after a -1.5 dB ceiling and delivered -1.0 dBTP; m2's single ceiling starts at -1.6 dB and steps down 0.2 dB until
the ebur128 true peak holds; the gain is corrected for the limiter's loudness loss (up to six passes)."""
import sys, json, re, subprocess
import numpy as np
from scipy.io import wavfile

pre, final, stems = sys.argv[1] + '-pre.wav', sys.argv[2], sys.argv[3]
GOAL, TP_MAX = -16.0, -1.3


def ff(args):
    return subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-vn'] + args, capture_output=True, text=True).stderr


def ebur(p):
    s = ff(['-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'])
    s = s[s.rindex('Summary:'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))
    return {'I': g('I'), 'LRA': g('LRA'), 'true_peak_dbtp': g('Peak')}


src = ebur(pre)
gain, ceil, log = GOAL - src["I"], -1.6, []
for it in range(6):
    lim = f'alimiter=limit={10 ** (ceil / 20):.5f}:level=0:latency=1:asc=0'
    ff(['-y', '-i', pre, '-af', f'volume={gain:.3f}dB,{lim}', '-ac', '1', '-ar', '48000', '-c:a', 'pcm_s24le', final])
    e = ebur(final)
    log.append(f'pass {it + 1}: pre {src["I"]} LUFS / {src["true_peak_dbtp"]} dBTP, volume {gain:+.2f} dB, alimiter ceiling {ceil:.1f} dB -> '
               f'{e["I"]} LUFS, LRA {e["LRA"]}, true peak {e["true_peak_dbtp"]} dBTP')
    ok_i, ok_tp = abs(e['I'] - GOAL) <= 0.05, e['true_peak_dbtp'] <= TP_MAX
    if ok_i and ok_tp:
        break
    if not ok_tp:
        ceil = round(ceil - 0.2, 2)
    if not ok_i:
        gain += GOAL - e['I']
else:
    sys.exit('loudness did not converge:\n' + '\n'.join(log))
for k in ('dialogue', 'music', 'sfx'):
    sr, y = wavfile.read(f'{sys.argv[1]}-{k}.wav')
    wavfile.write(f'{stems}-{k}.f32.wav', sr, (y * 10 ** (gain / 20)).astype(np.float32))
    ff(['-y', '-i', f'{stems}-{k}.f32.wav', '-c:a', 'pcm_s24le', f'{stems}-{k}.wav'])
r = {'goal_lufs': GOAL, 'tp_max': TP_MAX, 'pre': src, 'linear_gain_db': gain, 'limiter': lim, 'final': e, 'log': log}
print('\n'.join(log)); print(json.dumps({k: r[k] for k in ('linear_gain_db', 'limiter', 'final')}))
json.dump(r, open(sys.argv[1] + '-loudness.json', 'w'), indent=1)
