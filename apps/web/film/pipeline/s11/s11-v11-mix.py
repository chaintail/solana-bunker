#!/usr/bin/env python3
# v11 (do-box): identical to s11-v10-mix.py (sum of four 48 kHz mono stems -> f32 wav). usage: s11-v11-mix.py out.wav voice.wav ja.wav jb.wav groove.wav
# v11 changes only the groove stem (s11-v11-groove.py: 2.0 s raised-cosine fade-in from the 2.26 s entry); ja (adelay 30110S), voice, jb as v10.
import sys,subprocess,numpy as np
from scipy.io import wavfile
def rd(f): return np.frombuffer(subprocess.run(['ffmpeg','-nostdin','-v','error','-vn','-i',f,'-f','f32le','-ac','1','-ar','48000','-'],capture_output=True).stdout,dtype='<f4').astype(np.float32)
v,ja,jb,g=[rd(f) for f in sys.argv[2:6]]
n=min(map(len,(v,ja,jb,g)));m=v[:n]+ja[:n]+jb[:n]+g[:n]
wavfile.write(sys.argv[1],48000,m.astype(np.float32))
