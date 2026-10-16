#!/usr/bin/env python3
"""Glitch-frame scan. Runs on dev-mac: ~/venvs/audio/bin/python glitch-scan.py <video> [options]
Decodes to 160x90 greyscale (ffmpeg on PATH); d(a,b) = mean abs diff; med = median neighbour diff.
Checks (frame i flagged -> exit 1):
  single   d(i-1,i) and d(i,i+1) > max(3 med, --min-jump) while d(i-1,i+1) < 0.25 x the smaller jump (a one-frame flash)
  pair     frames i,i+1: d(i-1,i) and d(i+1,i+2) > max(3 med, --min-jump) while d(i-1,i+2) < 0.25 x the smaller jump (a two-frame flash,
           which the single rule misses because the two flash frames match each other)
  chunk    at every capture chunk start c (where a stale paint lands): the single and pair rules with a lower bar
           (jumps > 2 med, no --min-jump floor, skip < 0.5 x jump), and every chunk start's numbers are printed
  ref      every frame whose PSNR to a reference is >= --ref-db, in runs of <= 2 frames (a stale copy; a longer run is a hold
           and is printed as info). A reference is a PNG or a frame number of this video, e.g. the scene's frame 0 and the
           frame 0 of each later part (title + scene builds): --ref 0 --ref 191 --ref still.png. A run touching the ref's own frame is exempt.
Options:
  --chunk-starts N,M,...          explicit chunk-start frames
  --chunk-size N [--parts A,B,..] chunk starts A, A+N, ... for each part start (default part 0), each part ending at the next one
  --ref <png|frame> (repeatable), --ref-db X (default 30)
  --min-jump X (default 2.0)      floor for the whole-film single/pair jumps (small designed motion such as a swinging tag is ~1)
  --ignore F,F,...                reviewed frames (designed effects checked against a fresh render): reported, not flagged"""
import argparse, subprocess, sys
import numpy as np
W, H = 160, 90
ap = argparse.ArgumentParser(usage='glitch-scan.py <video> [--chunk-starts N,M | --chunk-size N [--parts A,B]] [--ref png|frame ...] [--ref-db X] [--min-jump X] [--ignore F,F]')
ap.add_argument('video'); ap.add_argument('--chunk-starts', default=''); ap.add_argument('--chunk-size', type=int, default=0)
ap.add_argument('--parts', default='0'); ap.add_argument('--ref', action='append', default=[]); ap.add_argument('--ref-db', type=float, default=30.0)
ap.add_argument('--ignore', default=''); ap.add_argument('--min-jump', type=float, default=2.0)
a = ap.parse_args()
ints = lambda s: [int(x) for x in s.split(',') if x.strip()]
def decode(src):
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', src, '-vf', f'scale={W}:{H}:flags=area', '-pix_fmt', 'gray', '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H * W).astype(np.float32)
fps = float(eval(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'csv=p=0', a.video]).decode().strip()))
f = decode(a.video); n = len(f)
D = lambda i, j: float(np.abs(f[i] - f[j]).mean())
d = np.abs(np.diff(f, axis=0)).mean(axis=1)          # d[i] = D(i, i+1)
med = max(float(np.median(d)), 0.05)
ignore = set(ints(a.ignore)); bad = {}
def flag(i, why):
    if i in ignore: print(f'  (ignored, reviewed) frame {i}: {why}')
    else: bad.setdefault(i, []).append(why)
def single(i, k, r, fl=0.0):   # frame i off both neighbours that match each other
    if 0 < i < n - 1 and min(d[i-1], d[i]) > max(k * med, fl) and D(i-1, i+1) < r * min(d[i-1], d[i]):
        return f'single prev={d[i-1]:.2f} next={d[i]:.2f} neighbours={D(i-1, i+1):.2f}'
def pair(i, k, r, fl=0.0):     # frames i,i+1 off the frames around them, which match each other
    if 0 < i < n - 2 and min(d[i-1], d[i+1]) > max(k * med, fl) and D(i-1, i+2) < r * min(d[i-1], d[i+1]):
        return f'pair {i},{i+1} in={d[i-1]:.2f} mid={d[i]:.2f} out={d[i+1]:.2f} around={D(i-1, i+2):.2f}'
for i in range(1, n - 1):
    if (w := single(i, 3, .25, a.min_jump)): flag(i, w)
    if (w := pair(i, 3, .25, a.min_jump)): flag(i, w)
# chunk starts
cs = set(ints(a.chunk_starts))
if a.chunk_size:
    ps = sorted(ints(a.parts)) + [n]
    for p, q in zip(ps, ps[1:]): cs.update(range(p, q, a.chunk_size))
for c in sorted(x for x in cs if 0 <= x < n):
    print(f'chunk start {c} t={c/fps:.3f}s: d_prev={d[c-1] if c else float("nan"):.2f} d_next={d[c] if c < n-1 else float("nan"):.2f} skip={D(c-1, c+1) if 0 < c < n-1 else float("nan"):.2f}')
    for i in (c, c - 1):   # the pair rule covers a two-frame stale run starting at c, or ending at c (i = c-1)
        if (w := (single(i, 2, .5) if i == c else None)): flag(i, 'chunk-start ' + w)
        if (w := pair(i, 2, .5)): flag(i, 'chunk-start ' + w)
# references
for r in a.ref:
    own = int(r) if r.isdigit() else None
    ref = f[own] if own is not None else decode(r)[0]
    mse = ((f - ref) ** 2).mean(axis=1); p = np.where(mse == 0, 99.0, 10 * np.log10(255 ** 2 / np.maximum(mse, 1e-9)))
    hit = np.where(p >= a.ref_db)[0]; runs = []
    for i in hit:
        if runs and i == runs[-1][-1] + 1: runs[-1].append(i)
        else: runs.append([i])
    for run in runs:
        s = f'ref {r}: frames {run[0]}-{run[-1]} psnr {max(p[run]):.1f} dB'
        if own is not None and run[0] <= own <= run[-1]: continue
        if len(run) <= 2: [flag(i, s) for i in run]
        else: print('  (hold, info) ' + s)
    q = p.copy()
    if own is not None: q[max(own - 2, 0):own + 3] = -1   # skip the ref's own frame and its 2 neighbours
    print(f'ref {r}: closest other frame {int(q.argmax())} at {q.max():.1f} dB')
for i in sorted(bad): print(f'frame {i} t={i/fps:.3f}s ' + ' | '.join(bad[i]))
print(f'{n} frames, median diff {med:.3f}, chunk starts {len(cs)}, refs {len(a.ref)}, flagged {len(bad)}' + (' -> clean' if not bad else ''))
sys.exit(1 if bad else 0)
