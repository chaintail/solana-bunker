#!/usr/bin/env python3
"""Transcript check for m1: faster-whisper small int8 (do-box /home/claude/venvs/localstt) on the source master and on the m1 mix of a scene;
prints both and the word-level difference. Audio is decoded on dev-mac (ffmpeg is banned on do-box).
Usage: python3 m1-transcribe.py out/s04-v8-x12.mp4 out/s04-m1.mp4   (paths relative to ~/video-work/solana-bunker on dev-mac)"""
import difflib, re, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel
m = WhisperModel('small', device='cpu', compute_type='int8')
words = {}
for p in sys.argv[1:]:
    raw = subprocess.run(['ssh', 'dev-mac', f'cd ~/video-work/solana-bunker && /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -nostdin -v error -i {p} -ar 16000 -ac 1 -f f32le -'],
                         capture_output=True, check=True).stdout
    segs, _ = m.transcribe(np.frombuffer(raw, np.float32), language='en', beam_size=5, vad_filter=False)
    txt = ' '.join(s.text.strip() for s in segs); words[p] = re.sub(r'[^a-z0-9 ]', '', txt.lower()).split()
    print(f'== {p}\n{txt}\n')
a, b = words[sys.argv[1]], words[sys.argv[2]]
ops = [o for o in difflib.SequenceMatcher(a=a, b=b).get_opcodes() if o[0] != 'equal']
print('identical word sequence' if not ops else 'differences:'); [print(' ', o[0], a[o[1]:o[2]], '->', b[o[3]:o[4]]) for o in ops]
print(f'words {len(a)} vs {len(b)}')
