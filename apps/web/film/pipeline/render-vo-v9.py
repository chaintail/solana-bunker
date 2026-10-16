#!/usr/bin/env python3
"""Runs ON dev-mac with ~/speech-lab/.venv/bin/python3 (numpy, soundfile). Opening v9 (Liam 2026-10-16): the sponsor read and the advisory read at 1.2x,
by speeding up the existing renders (atempo, pitch kept), no re-synthesis.
 sponsor : out/s00a-v5/vo-final.wav (Studio take, already -16 LUFS with its 0.4 s lead-in) -> atempo=1.2 -> <outdir>/sponsor-vo.wav. The card has fixed
           animation times, so it is captured with capture.mjs --speed=1.2 and the lead-in shrinks with it.
 advisory: the four approved Chirp3-HD Enceladus phrase files (voices/advisory-r7/) were synthesised at speaking rates 1.0, 1.08, 1.15 and 1.0. Each is
           brought to an effective 1.2 from its OWN render: atempo 1.2/rate (1.2, 1.1111, 1.0435, 1.2), so no phrase is stacked to 1.3 or 1.38.
           Lead-in, the three silences (700/150/400 ms) and the tail are divided by 1.2. Then two-pass loudnorm -16 LUFS / TP -1.5 / LRA 7 as in v7.
           Word times: v7's (data/s00b-words-v7.json) mapped per phrase, new = lead' + start'_k + (t - start_k) / atempo_k (atempo is uniform in time).
usage: render-vo-v9.py <voices-dir> <v7-words.json> <sponsor-vo-final.wav> <outdir> <film-data-dir>
  -> <outdir>/{adv-raw.wav,adv-vo.wav,sponsor-vo.wav,p?.wav}, <film-data-dir>/s00b-words-v9.{json,js}"""
import json, subprocess, sys, os
import numpy as np, soundfile as sf
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
V, W7, SP, D, FD = sys.argv[1:6]
os.makedirs(D, exist_ok=True)
S = 1.2
names = ['1-warning', '2-contains-math', '3-conspiracy', '4-discretion']
rate = [1.0, 1.08, 1.15, 1.0]
gaps = [0.7, 0.15, 0.4]; LEAD7, TAIL7 = 0.8, 0.3
phrase_of = [0] + [1] * 5 + [2] * 9 + [3] * 4          # word index -> phrase (Warning | The following program contains math | conspiracy..scenarios | Viewer discretion is advised)
def run(*a): subprocess.run([FF, '-nostdin', '-v', 'error', '-y', *a], check=True)
# --- advisory: per-phrase atempo on the approved files
SR = 24000; parts, a_k = [], []
for n, r in zip(names, rate):
    a = S / r; a_k.append(a)
    run('-i', f'{V}/{n}.wav', '-af', f'atempo={a:.6f}', '-ar', str(SR), '-ac', '1', '-c:a', 'pcm_s16le', f'{D}/p-{n}.wav')
    x, sr = sf.read(f'{D}/p-{n}.wav', dtype='int16'); assert sr == SR; parts.append(x)
    print(f'{n}: rate {r} -> atempo {a:.4f}, {len(sf.read(f"{V}/{n}.wav")[0]) / SR:.4f} s -> {len(x) / SR:.4f} s')
sil = lambda s: np.zeros(int(round(s * SR)), dtype=np.int16)
lead = LEAD7 / S; seq, starts, pos = [sil(lead)], [], int(round(lead * SR))
for i, p in enumerate(parts):
    starts.append(pos / SR); seq.append(p); pos += len(p)
    if i < 3: g = sil(gaps[i] / S); seq.append(g); pos += len(g)
seq.append(sil(TAIL7 / S)); full = np.concatenate(seq)
sf.write(f'{D}/adv-raw.wav', full, SR, subtype='PCM_16')
m = subprocess.run([FF, '-nostdin', '-hide_banner', '-i', f'{D}/adv-raw.wav', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
run('-i', f'{D}/adv-raw.wav', '-af', f"aresample=48000,loudnorm=I=-16:TP=-1.5:LRA=7:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000", '-ac', '1', '-ar', '48000', f'{D}/adv-vo.wav')
# --- word times: v7 phrase starts from the approved file lengths, same join
old = json.load(open(W7)); ow = old['words']; assert len(ow) == 19 and abs(old['leadIn'] - LEAD7) < 1e-9
lens7 = [len(sf.read(f'{V}/{n}.wav')[0]) / SR for n in names]; st7, p = [], LEAD7
for i, L in enumerate(lens7): st7.append(p); p += L + (gaps[i] if i < 3 else 0)
mp = lambda t, k: round(starts[k] + (t - st7[k]) / a_k[k], 3)
words = [{'w': w['w'], 's': mp(w['s'], k), 'e': mp(w['e'], k)} for w, k in zip(ow, phrase_of)]
res = {'leadIn': round(lead, 4), 'words': words, 'dur': round(len(full) / SR, 3), 'voicedOffset': 0.0, 'speed': S, 'atempo': [round(a, 4) for a in a_k]}
json.dump(res, open(f'{FD}/s00b-words-v9.json', 'w'), indent=1); open(f'{FD}/s00b-words-v9.js', 'w').write(f'window.VO = {json.dumps(res)};\n')
print('advisory: v7 voice', old['dur'], 's -> v9', res['dur'], 's; phrase starts', [round(s, 4) for s in starts], '; last word ends', words[-1]['e'])
# --- sponsor: the whole render at 1.2x
run('-i', SP, '-af', f'atempo={S}', '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', f'{D}/sponsor-vo.wav')
print('sponsor:', round(len(sf.read(SP)[0]) / 48000, 3), 's ->', round(len(sf.read(f'{D}/sponsor-vo.wav')[0]) / 48000, 3), 's')
