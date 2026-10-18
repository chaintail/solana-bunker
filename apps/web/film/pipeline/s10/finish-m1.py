#!/usr/bin/env python3
"""m1 loudness: two-pass ffmpeg loudnorm (I, TP=-1.5, LRA=9, linear=true, as the scenes) on the summed mix, then the scene's own limiter.
Runs ON dev-mac with ~/speech-lab/.venv/bin/python3 and ffmpeg-full on PATH.
usage: finish-m1.py <prefix> <limiter filter> <final.wav> <stem prefix>
  reads <prefix>-pre.wav, -dialogue.wav, -music.wav, -sfx.wav (music-m1.py); writes <final.wav> (48 kHz mono 24-bit) and <stem prefix>-dialogue.wav,
  -music.wav, -sfx.wav: the stems times the same linear loudnorm gain, before the limiter (the music stem keeps any ring past the picture).
If the second pass would switch loudnorm to dynamic mode (measured true peak + the linear gain over TP), the same linear gain is applied with
volume instead and loudnorm's -1.5 dB peak ceiling is held by a delay-compensated alimiter (level=0, latency=1) before the scene's limiter, so the
scene's limiter sees the same peak range as in the scene's own build. If the limiter moves the integrated loudness off -16.0 by more than 0.05 LU, the loudnorm
target is corrected by the difference and the two passes run again (up to three times)."""
import sys, json, re, subprocess
import numpy as np, soundfile as sf

pre, LIM, final, stems = sys.argv[1] + '-pre.wav', sys.argv[2], sys.argv[3], sys.argv[4]
GOAL = -16.0


def ff(args):
    return subprocess.run(['ffmpeg', '-nostdin', '-hide_banner'] + args, capture_output=True, text=True).stderr


def js(s):
    if '{' not in s:
        sys.exit('ffmpeg printed no loudnorm json:\n' + s[-2000:])
    return json.loads(s[s.rindex('{'):s.rindex('}') + 1])


def ebur(p):
    s = ff(['-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'])
    s = s[s.rindex('Summary:'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))
    return {'I': g('I'), 'LRA': g('LRA'), 'peak': g('Peak')}


T, TP, log = GOAL, -1.5, []
for it in range(4):
    m1 = js(ff(['-i', pre, '-af', f'loudnorm=I={T}:TP={TP}:LRA=9:print_format=json', '-f', 'null', '-']))
    gain = T - float(m1['input_i'])
    if float(m1['input_tp']) + gain <= TP:                  # loudnorm's linear mode (as the scenes)
        lnf = (f"loudnorm=I={T}:TP={TP}:LRA=9:measured_I={m1['input_i']}:measured_TP={m1['input_tp']}:measured_LRA={m1['input_lra']}:"
               f"measured_thresh={m1['input_thresh']}:offset={m1['target_offset']}:linear=true:print_format=json,aresample=48000")
        how = 'loudnorm linear'
    else:                                                   # loudnorm would switch to dynamic: apply its linear gain, the limiter takes the peaks
        lnf = f'volume={gain:.4f}dB,alimiter=limit={10 ** (TP / 20):.4f}:level=0:latency=1'
        how = (f"volume {gain:+.2f} dB (= loudnorm's linear gain; loudnorm itself would go dynamic: true peak {m1['input_tp']} dBTP + gain > {TP}) "
               f"and loudnorm's {TP} dB peak ceiling held by alimiter level=0 latency=1")
    out = ff(['-y', '-i', pre, '-af', f'{lnf},{LIM}', '-ac', '1', '-ar', '48000', '-c:a', 'pcm_s24le', final])
    if how == 'loudnorm linear':
        assert js(out)['normalization_type'] == 'linear'
    e = ebur(final)
    log.append(f"pass {it + 1}: target {T:.2f}: input {m1['input_i']} LUFS / {m1['input_tp']} dBTP, {how}, after {LIM}: {e['I']} LUFS, "
               f"LRA {e['LRA']}, true peak {e['peak']} dBFS")
    if abs(e['I'] - GOAL) <= 0.05:
        break
    T = round(T + GOAL - e['I'], 2)
for k in ('dialogue', 'music', 'sfx'):
    y, sr = sf.read(f'{sys.argv[1]}-{k}.wav')
    sf.write(f'{stems}-{k}.wav', y * 10 ** (gain / 20), sr, subtype='PCM_24')
print('\n'.join(log))
print(json.dumps({'loudnorm_target': T, 'tp': TP, 'linear_gain_db': gain, 'final': e}))
json.dump({'loudnorm_target': T, 'tp': TP, 'linear_gain_db': gain, 'final': e, 'log': log}, open(sys.argv[1] + '-loudness.json', 'w'), indent=1)
