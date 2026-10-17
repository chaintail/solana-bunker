#!/usr/bin/env python3
"""m1 transcript check. Runs on do-box with /home/claude/venvs/localstt/bin/python3 (faster-whisper small, int8, CPU). The 16 kHz 16-bit wavs come
from verify-m1.py on dev-mac and are read with the wave module (no media tools on do-box).
usage: transcribe-m1.py <audio16k-src.wav> <audio16k-m1.wav>
Prints both transcripts and the word-level differences (case and punctuation ignored)."""
import sys, wave, re, difflib
import numpy as np
from faster_whisper import WhisperModel


def load(p):
    with wave.open(p) as w:
        assert w.getframerate() == 16000 and w.getsampwidth() == 2 and w.getnchannels() == 1
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


m = WhisperModel('small', device='cpu', compute_type='int8')
out = []
for p in sys.argv[1:3]:
    segs, _ = m.transcribe(load(p), language='en', beam_size=5, vad_filter=False)
    txt = ' '.join(s.text.strip() for s in segs)
    out.append(txt); print(f'--- {p}\n{txt}\n')
norm = lambda s: re.sub(r"[^a-z0-9' ]", ' ', s.lower()).split()
a, b = norm(out[0]), norm(out[1])
d = [x for x in difflib.ndiff(a, b) if x[0] in '+-']
print(f'words: source {len(a)}, m1 {len(b)}; differences: {d if d else "none"}')
