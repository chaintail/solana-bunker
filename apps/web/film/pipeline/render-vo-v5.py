#!/usr/bin/env python3
"""Runs ON dev-mac with ~/speech-lab/.venv/bin/python3 (numpy) and the speech-lab server (:8899, parakeet ASR only).
Revision 5 voice-over: the Google Cloud TTS Studio take (synthesised on do-box, SSML <break> pauses, rate 1.0, no stretching, see tts-google.py)
is trimmed to its voiced part, given a lead-in, loudness-normalised (-16 LUFS, 48 kHz mono) and word-timed with parakeet.
usage: render-vo-v5.py <in.wav> <outdir> <lead-seconds> <word list text>   -> <outdir>/vo-final.wav, words.json, words.js"""
import json, subprocess, sys, urllib.request, wave, io, os
import numpy as np

SR = 24000
FADE = int(0.020 * SR)
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
src, D, lead, text = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
os.makedirs(D, exist_ok=True)

def post(url, data, ctype):
    return urllib.request.urlopen(urllib.request.Request(url, data=data, headers={'Content-Type': ctype}), timeout=180).read()

def wav_bytes(x):
    b = io.BytesIO(); w = wave.open(b, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close(); return b.getvalue()

w = wave.open(src); assert w.getframerate() == SR and w.getnchannels() == 1
x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
thr = max(0.004, 0.02 * np.abs(x).max()); idx = np.nonzero(np.abs(x) > thr)[0]
a, b = max(0, idx[0] - int(0.012 * SR)), min(len(x), idx[-1] + int(0.05 * SR))
y = x[a:b].copy(); y[:FADE] *= np.linspace(0, 1, FADE); y[-FADE:] *= np.linspace(1, 0, FADE)
off = a / SR                                   # voiced part starts this far into the synthesised file
full = np.concatenate([np.zeros(int(lead * SR), dtype=np.float32), y])
open(f'{D}/raw.wav', 'wb').write(wav_bytes(full))

boundary = '----f0'
pre = ('--%s\r\nContent-Disposition: form-data; name="model"\r\n\r\nmlx-community/parakeet-tdt-0.6b-v3\r\n--%s\r\nContent-Disposition: form-data; name="file"; filename="a.wav"\r\nContent-Type: audio/wav\r\n\r\n' % (boundary, boundary)).encode()
d = json.loads(post('http://100.78.140.122:8899/v1/audio/transcriptions', pre + wav_bytes(full) + ('\r\n--%s--\r\n' % boundary).encode(), 'multipart/form-data; boundary=' + boundary))
asr = []
for s in d['sentences']:
    for tk in s['tokens']:
        if tk['text'].startswith(' ') or not asr: asr.append([tk['text'].strip(), tk['start'], tk['end']])
        else: asr[-1][0] += tk['text']; asr[-1][2] = tk['end']
exp = []
for wd, s0, e0 in asr:                          # parakeet writes 'fear-mongering' as one word: split on hyphens by letter count
    parts = wd.split('-')
    if len(parts) == 1: exp.append([wd, s0, e0]); continue
    tot = sum(len(q) for q in parts); k = s0
    for q in parts: e1 = k + (e0 - s0) * len(q) / tot; exp.append([q, k, e1]); k = e1
asr = exp
names = text.split()
print('asr :', ' '.join(a[0] for a in asr)); print('want:', text)
if len(asr) == len(names): words = [{'w': n, 's': round(s, 3), 'e': round(e, 3)} for n, (_, s, e) in zip(names, asr)]
else:
    a0, b0 = asr[0][1], asr[-1][2]; tot = sum(len(n) for n in names); k = a0; words = []
    for n in names: e = k + (b0 - a0) * len(n) / tot; words.append({'w': n, 's': round(k, 3), 'e': round(e, 3)}); k = e
    print('WARNING word-count mismatch, spread by letters')
# parakeet places word edges inside silences (e.g. 'by' 0.2 s before it is spoken after a long <break>); snap starts forward / ends back onto real energy
H = int(0.01 * SR); db = 20 * np.log10(np.sqrt(np.array([np.mean(full[i:i + H] ** 2) for i in range(0, len(full) - H, H)])) + 1e-9)
for wd in words:
    i = int(wd['s'] * 100)
    while i < len(db) - 1 and db[i] < -45: i += 1
    wd['s'] = round(max(wd['s'], i / 100), 3)
    k = min(int(wd['e'] * 100), len(db) - 1)
    while k > i and db[k] < -45: k -= 1
    wd['e'] = round(max(wd['s'] + 0.05, k / 100), 3)
m = subprocess.run([FF, '-nostdin', '-hide_banner', '-i', f'{D}/raw.wav', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
flt = f"aresample=48000,loudnorm=I=-16:TP=-1.5:LRA=7:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000"
subprocess.run([FF, '-nostdin', '-v', 'error', '-y', '-i', f'{D}/raw.wav', '-af', flt, '-ac', '1', '-ar', '48000', f'{D}/vo-final.wav'], check=True)
dur = round(len(full) / SR, 3)
res = {'leadIn': lead, 'words': words, 'dur': dur, 'voicedOffset': round(off, 3)}
json.dump(res, open(f'{D}/words.json', 'w'), indent=1)
open(f'{D}/words.js', 'w').write(f'window.VO = {json.dumps(res)};\n')
print(json.dumps(words)); print('dur', dur)
