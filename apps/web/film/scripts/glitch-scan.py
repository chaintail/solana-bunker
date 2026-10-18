#!/usr/bin/env python3
"""Glitch-frame scan. Runs on dev-mac: ~/venvs/audio/bin/python glitch-scan.py <video>
Decodes to 160x90 greyscale (ffmpeg on PATH) and flags frame i when its mean abs diff to BOTH neighbours
exceeds 3x the median neighbour diff while the two neighbours match each other (diff(i-1,i+1) < 0.25 x the smaller jump).
Prints flagged frames with times; exit 1 if any."""
import subprocess, sys
import numpy as np
W, H = 160, 90
if len(sys.argv) != 2: sys.exit('usage: glitch-scan.py <video>')
v = sys.argv[1]
fps = float(eval(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=r_frame_rate','-of','csv=p=0',v]).decode().strip()))
raw = subprocess.run(['ffmpeg','-nostdin','-v','error','-i',v,'-vf',f'scale={W}:{H}:flags=area','-pix_fmt','gray','-f','rawvideo','-'],capture_output=True,check=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(-1, H*W).astype(np.float32)
d = np.abs(np.diff(f, axis=0)).mean(axis=1)          # d[i] = diff(i, i+1)
med = max(float(np.median(d)), 0.05)
bad = []
for i in range(1, len(f)-1):
    skip = float(np.abs(f[i-1]-f[i+1]).mean())
    if d[i-1] > 3*med and d[i] > 3*med and skip < 0.25*min(d[i-1], d[i]):
        bad.append(i); print(f'frame {i} t={i/fps:.3f}s diff_prev={d[i-1]:.3f} diff_next={d[i]:.3f} neighbours={skip:.3f} (median {med:.3f})')
print(f'{len(f)} frames, median diff {med:.3f}, flagged {len(bad)}')
sys.exit(1 if bad else 0)
