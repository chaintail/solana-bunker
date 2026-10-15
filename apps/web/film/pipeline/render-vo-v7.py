#!/usr/bin/env python3
"""Runs ON dev-mac with ~/speech-lab/.venv/bin/python3 (numpy) and the speech-lab server (:8899, parakeet ASR only).
Revision 7 advisory voice-over. NO synthesis: the four approved Chirp3-HD Enceladus phrase files (voices/advisory-r7/) are joined butt to butt with
silences 700 ms after warning, 150 ms after math, 400 ms before discretion; no trimming, fades or time stretching. A lead-in of silence is prepended,
the result is loudness-normalised (-16 LUFS, 48 kHz mono, two-pass loudnorm as in v5/v6) and word-timed with parakeet per phrase file (offsets are exact).
usage: render-vo-v7.py <voices-dir> <outdir> <lead-seconds>   -> <outdir>/{joined.wav,raw.wav,vo-final.wav,words.json,words.js}"""
import json, subprocess, sys, urllib.request, wave, io, os
import numpy as np
SR = 24000
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
V, D, lead = sys.argv[1], sys.argv[2], float(sys.argv[3])
os.makedirs(D, exist_ok=True)
def rd(f):
    w = wave.open(f); assert w.getframerate() == SR and w.getnchannels() == 1 and w.getsampwidth() == 2
    return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
def wb(x16):
    b = io.BytesIO(); w = wave.open(b, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(x16.astype(np.int16).tobytes()); w.close(); return b.getvalue()
sil = lambda s: np.zeros(int(round(s * SR)), dtype=np.int16)
names = ['1-warning', '2-contains-math', '3-conspiracy', '4-discretion']
texts = ['Warning', 'The following program contains math', 'conspiracy theories and fear mongering based on hypothetical scenarios', 'Viewer discretion is advised']
gaps = [0.7, 0.15, 0.4]
parts = [rd(f'{V}/{n}.wav') for n in names]
seq, starts, pos = [], [], 0
for i, p in enumerate(parts):
    starts.append(pos); seq.append(p); pos += len(p)
    if i < 3: g = sil(gaps[i]); seq.append(g); pos += len(g)
joined = np.concatenate(seq)
# check against the reference Liam heard: 300 ms lead and tail around exactly this join
ref = rd(f'{V}/joined-reference.wav'); L = int(0.3 * SR)
assert len(ref) == len(joined) + 2 * L, (len(ref), len(joined))
assert np.array_equal(ref[L:L + len(joined)], joined), 'join differs from joined-reference.wav'
assert not ref[:L].any() and not ref[L + len(joined):].any()
print('join matches joined-reference.wav sample for sample (%d samples, %.4f s)' % (len(joined), len(joined) / SR))
full = np.concatenate([sil(lead), joined, sil(0.3)])
open(f'{D}/joined.wav', 'wb').write(wb(joined)); open(f'{D}/raw.wav', 'wb').write(wb(full))
boundary = '----f0'
def asr(x16):
    pre = ('--%s\r\nContent-Disposition: form-data; name="model"\r\n\r\nmlx-community/parakeet-tdt-0.6b-v3\r\n--%s\r\nContent-Disposition: form-data; name="file"; filename="a.wav"\r\nContent-Type: audio/wav\r\n\r\n' % (boundary, boundary)).encode()
    r = urllib.request.urlopen(urllib.request.Request('http://100.78.140.122:8899/v1/audio/transcriptions', pre + wb(x16) + ('\r\n--%s--\r\n' % boundary).encode(), headers={'Content-Type': 'multipart/form-data; boundary=' + boundary}), timeout=180).read()
    out = []
    for s in json.loads(r)['sentences']:
        for tk in s['tokens']:
            if tk['text'].startswith(' ') or not out: out.append([tk['text'].strip(), tk['start'], tk['end']])
            else: out[-1][0] += tk['text']; out[-1][2] = tk['end']
    exp = []
    for wd, s0, e0 in out:
        ps = wd.split('-')
        if len(ps) == 1: exp.append([wd, s0, e0]); continue
        tot = sum(len(q) for q in ps); k = s0
        for q in ps: e1 = k + (e0 - s0) * len(q) / tot; exp.append([q, k, e1]); k = e1
    return exp
H = int(0.01 * SR)
words = []
for n, t, p, st in zip(names, texts, parts, starts):
    padded = np.concatenate([sil(0.3), p, sil(0.3)]); a = asr(padded); want = t.split()
    off = lead + st / SR - 0.3                      # time of padded-file t=0 on the final timeline
    print(n, 'asr :', ' '.join(x[0] for x in a)); print(n, 'want:', t)
    if len(a) == len(want): ws = [[w, s, e] for w, (_, s, e) in zip(want, a)]
    else:
        a0, b0 = a[0][1], a[-1][2]; tot = sum(len(w) for w in want); k = a0; ws = []
        for w in want: e = k + (b0 - a0) * len(w) / tot; ws.append([w, k, e]); k = e
        print('WARNING word-count mismatch, spread by letters')
    db = 20 * np.log10(np.sqrt(np.array([np.mean((padded[i:i + H] / 32768.0) ** 2) for i in range(0, len(padded) - H, H)])) + 1e-9)
    for w, s, e in ws:                              # snap starts forward / ends back onto real energy (as in render-vo-v5)
        i = int(s * 100)
        while i < len(db) - 1 and db[i] < -45: i += 1
        s2 = max(s, i / 100); k = min(int(e * 100), len(db) - 1)
        while k > i and db[k] < -45: k -= 1
        e2 = max(s2 + 0.05, k / 100)
        words.append({'w': w, 's': round(off + s2, 3), 'e': round(off + e2, 3)})
m = subprocess.run([FF, '-nostdin', '-hide_banner', '-i', f'{D}/raw.wav', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
flt = f"aresample=48000,loudnorm=I=-16:TP=-1.5:LRA=7:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000"
subprocess.run([FF, '-nostdin', '-v', 'error', '-y', '-i', f'{D}/raw.wav', '-af', flt, '-ac', '1', '-ar', '48000', f'{D}/vo-final.wav'], check=True)
res = {'leadIn': lead, 'words': words, 'dur': round(len(full) / SR, 3), 'voicedOffset': 0.0}
json.dump(res, open(f'{D}/words.json', 'w'), indent=1); open(f'{D}/words.js', 'w').write(f'window.VO = {json.dumps(res)};\n')
print(json.dumps(words)); print('dur', res['dur'])
