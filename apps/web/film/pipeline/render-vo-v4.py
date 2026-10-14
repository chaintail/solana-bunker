#!/usr/bin/env python3
"""Runs ON dev-mac with ~/speech-lab/.venv/bin/python3 (numpy) and the speech-lab server on :8899. Revision 4 voice-over.
No time stretching anywhere: every phrase is its own kokoro call at its own native `speed`, trimmed to its voiced part, given a 20 ms
fade at both edges, then butt-joined with explicit silences. Writes, per card, into out/<dir>/:
  vo-final.wav  (-16 LUFS, 48 kHz mono, lead-in silence included)   and   words.json / words.js (word times in the same clock as vo-final.wav)
usage: render-vo-v4.py sponsor|advisory"""
import json, subprocess, sys, urllib.request, wave, io, os, re
import numpy as np

SR = 24000
FADE = int(0.020 * SR)
MODEL = 'mlx-community/Kokoro-82M-bf16'
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
ROOT = os.path.expanduser('~/video-work/solana-bunker/out')

CARDS = {
    'sponsor': dict(dir='s00a-v4', voice='bf_emma', lead=0.4, items=[
        ('say', 'The following program is brought to you', 1.15, None),
        ('gap', 0.15),
        ('say', 'by Chaintail Labs', 1.0, None)]),
    'advisory': dict(dir='s00b-v4', voice='bm_lewis', lead=0.8, items=[
        ('say', 'Warning.', 1.0, None),
        ('gap', 0.70),
        ('say', 'The following program contains math', 1.0, None),
        ('gap', 0.30),
        ('say', 'conspiracy theories', 1.3, None),
        ('say', 'and fear [mongering](/mˈʌŋɡəɹɪŋ/)', 1.6, 'and fear mongering'),   # forced MUNG-ger-ing, see report
        ('say', 'based on hypothetical scenarios', 2.0, None),
        ('gap', 0.40),
        ('say', 'Viewer discretion is advised.', 0.85, None)]),
}


def post(url, data, ctype):
    r = urllib.request.Request(url, data=data, headers={'Content-Type': ctype})
    return urllib.request.urlopen(r, timeout=180).read()


def tts(text, voice, speed):
    body = json.dumps({'model': MODEL, 'input': text, 'voice': voice, 'speed': speed, 'response_format': 'wav'}).encode()
    raw = post('http://100.78.140.122:8899/v1/audio/speech', body, 'application/json')
    w = wave.open(io.BytesIO(raw)); assert w.getframerate() == SR and w.getsampwidth() == 2
    return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


def trim(x):
    thr = max(0.004, 0.02 * np.abs(x).max())
    idx = np.nonzero(np.abs(x) > thr)[0]
    a, b = max(0, idx[0] - int(0.012 * SR)), min(len(x), idx[-1] + int(0.03 * SR))
    y = x[a:b].copy()
    y[:FADE] *= np.linspace(0, 1, FADE); y[-FADE:] *= np.linspace(1, 0, FADE)
    return y


def wav_bytes(x):
    b = io.BytesIO(); w = wave.open(b, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close(); return b.getvalue()


def asr_words(x):
    """parakeet token times merged into words (same rule as words.py); returns [(word, start, end)] relative to x"""
    boundary = '----f0'
    pre = ('--%s\r\nContent-Disposition: form-data; name="model"\r\n\r\nmlx-community/parakeet-tdt-0.6b-v3\r\n--%s\r\nContent-Disposition: form-data; name="file"; filename="a.wav"\r\nContent-Type: audio/wav\r\n\r\n' % (boundary, boundary)).encode()
    d = json.loads(post('http://100.78.140.122:8899/v1/audio/transcriptions', pre + wav_bytes(x) + ('\r\n--%s--\r\n' % boundary).encode(), 'multipart/form-data; boundary=' + boundary))
    ws = []
    for s in d['sentences']:
        for tk in s['tokens']:
            if tk['text'].startswith(' ') or not ws: ws.append([tk['text'].strip(), tk['start'], tk['end']])
            else: ws[-1][0] += tk['text']; ws[-1][2] = tk['end']
    return ws


def main(name):
    c = CARDS[name]; D = f"{ROOT}/{c['dir']}"; os.makedirs(D, exist_ok=True)
    out, t, words, log = [np.zeros(int(c['lead'] * SR), dtype=np.float32)], c['lead'], [], []
    for it in c['items']:
        if it[0] == 'gap':
            out.append(np.zeros(int(it[1] * SR), dtype=np.float32)); t += it[1]; continue
        _, text, speed, shown = it
        y = trim(tts(text, c['voice'], speed)); dur = len(y) / SR
        plain = shown or text
        names = plain.replace('.', '').split()
        asr = asr_words(y)
        if len(asr) == len(names): ws = [(n, a, b) for n, (_, a, b) in zip(names, asr)]
        else:   # tokeniser split a word differently: spread the words over the voiced span by letter count
            a0, b0 = asr[0][1], asr[-1][2]; tot = sum(len(n) for n in names); k = a0; ws = []
            for n in names: e = k + (b0 - a0) * len(n) / tot; ws.append((n, k, e)); k = e
        for n, a, b in ws: words.append({'w': n, 's': round(t + a, 3), 'e': round(t + b, 3), 'speed': speed})
        log.append(f'{plain!r} speed {speed} voice {c["voice"]} at {t:.3f}-{t + dur:.3f}s (asr: {" ".join(w[0] for w in asr)})')
        out.append(y); t += dur
    x = np.concatenate(out); open(f'{D}/raw.wav', 'wb').write(wav_bytes(x))
    # one gain only (loudnorm, linear): timings are untouched
    m = subprocess.run([FF, '-nostdin', '-hide_banner', '-i', f'{D}/raw.wav', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
    flt = f"aresample=48000,loudnorm=I=-16:TP=-1.5:LRA=7:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000"
    subprocess.run([FF, '-nostdin', '-v', 'error', '-y', '-i', f'{D}/raw.wav', '-af', flt, '-ac', '1', '-ar', '48000', f'{D}/vo-final.wav'], check=True)
    res = {'leadIn': c['lead'], 'voice': c['voice'], 'words': words, 'dur': round(t, 3)}
    json.dump(res, open(f'{D}/words.json', 'w'), indent=1)
    open(f'{D}/words.js', 'w').write(f'window.VO = {json.dumps(res)};\n')
    print('\n'.join(log)); print('dur', round(t, 3)); print(json.dumps(words))


main(sys.argv[1])
