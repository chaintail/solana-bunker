#!/usr/bin/env python3
# v10 (do-box): sum of four 48 kHz mono stems -> f32 wav (as amix normalize=0). usage: s11-v10-mix.py out.wav voice.wav ja.wav jb.wav groove.wav
# ja = build.sh stems filter with the [1:a] adelay 54110S -> 30110S (jingle A 500 ms earlier); groove = s11-v10-groove.py; then the build.sh bed + alimiter 0.80 chain.
import sys,subprocess,numpy as np
from scipy.io import wavfile
def rd(f): return np.frombuffer(subprocess.run(['ffmpeg','-nostdin','-v','error','-vn','-i',f,'-f','f32le','-ac','1','-ar','48000','-'],capture_output=True).stdout,dtype='<f4').astype(np.float32)
v,ja,jb,g=[rd(f) for f in sys.argv[2:6]]
n=min(map(len,(v,ja,jb,g)));m=v[:n]+ja[:n]+jb[:n]+g[:n]
wavfile.write(sys.argv[1],48000,m.astype(np.float32))
