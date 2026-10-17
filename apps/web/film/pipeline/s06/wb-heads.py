#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s06 with /usr/bin/python3 (numpy/scipy). v10 whiteboard lab coat head (L1a + L1b only).
Slide 5 v8 (film/s05 a38d379, s05-heads.py NORM) cuts its heads from c15 on with the frame first scaled and padded into the c1-c14 geometry, then keyed with the
original zone/kill masks at 136x197, so its last frame shows c22's full-chin cut centred on the collar (head anchor 511.5 / 308). s06's own sheets (heads.py,
recentred masks, no NORM, 152x220) are 1.08x larger and placed differently, so the whiteboard figure that takes over from slide 5's last frame gets its own
sheet cut exactly the s05 v8 way:
  1. one NORM for L1a + L1b (one continuous take, cut at 339.165 with no gap, so a per-line NORM would jump at the cut), anchored on the takeover frame:
     start from c22's s05 NORM (1000, 1334, 101, 71), key L1a's first frame (the head on screen when the live figure takes over), register that sprite to
     c22's last sprite (s05 sheet lab-11.png cell 2163, the head on slide 5's last frame) by gradient NCC of the alpha-weighted face at 4x (scale about the
     sprite centre + translation), fold the correction into the NORM; two rounds (the masks act after the NORM, so one round is not exact);
     (a median over the phrase is not used: Liam leans in during L1a, so it would shrink the head at the takeover by about 6%)
  2. key = s05-heads.py v8's filter graph verbatim (head-test zone.png / kill.png, 760x1100 crop, 136x197) -> out/heads-wb/{L1a,L1b}.mov -> film/heads/s06-wb-00.png
     (16 x 12 tile, frame i = cell i; L1a + L1b = frames 0..67, the same indices as narrFrame() on the s06 run).
Prints each round's residual registration and the NORM used."""
import json, os, subprocess
import numpy as np
from scipy import ndimage as ndi, signal
from PIL import Image
os.environ['PATH'] = '/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:' + os.environ['PATH']
B = os.path.expanduser('~/video-work/bunker'); HT = os.path.expanduser('~/video-work/head-test')
W, H, COLS, ROWS = 136, 197, 16, 12
LO, HI = 28, 58
C22_IN, C22_FRAMES, C22_NORM = 326.35, 48, (1000, 1334, 101, 71)   # film/s05 a38d379 data/s05-edl.json, s05-heads.py NORM
FW, FH = 1080, 1440

C22_SHEET, C22_CELL = '../s05/film/heads/lab-11.png', (2116 + 47) % 192   # c22 frame0 2116 + last frame 47 = run frame 2163

def keycmd(src_in, n, norm, out, still=False):   # s05-heads.py v8 filter graph, unchanged
    S, T = str(src_in), str(n / 30 + 0.2)
    nm = (lambda w, h, px, py: f",scale={w}:{h}:flags=lanczos,pad=1300:1660:{px + 110}:{py + 110}:color=black,crop=1080:1440:110:110")(*norm)
    fc = (f"[0:v]fps=30,format=gray{nm},gblur=sigma=1.5,lut=y='clip(({HI}-val)*255/({HI}-{LO}),0,255)'[s];[2:v]format=gray[z];[3:v]format=gray[kl];"
          f"[s][z]blend=all_mode=multiply,dilation,dilation[sd];[sd][kl]blend=all_mode=lighten,negate,gblur=sigma=1.2[k];"
          f"[1:v]fps=30,format=gray{nm}[a];[a][k]blend=all_mode=multiply,gblur=sigma=0.8[am];"
          f"[4:v]fps=30,format=rgb24{nm},despill=type=green:mix=0.6:expand=0.2,format=gbrp[rgb];[rgb][am]alphamerge,crop=760:1100:250:150,"
          f"scale={W}:{H}:flags=lanczos,format=rgba,trim=end_frame={n},setpts=PTS-STARTPTS[o]")
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', S, '-t', T, '-i', B + '/matte-full-comp.mp4', '-ss', S, '-t', T, '-i', B + '/matte-full-alpha.mp4',
                    '-loop', '1', '-framerate', '30', '-i', HT + '/zone.png', '-loop', '1', '-framerate', '30', '-i', HT + '/kill.png', '-ss', S, '-t', T, '-i', B + '/matte-full-comp.mp4',
                    '-filter_complex', fc, '-map', '[o]', '-frames:v', str(n)] + (['-update', '1', out] if still else ['-c:v', 'qtrle', '-r', '30', out]), check=True)

def feat(a):   # alpha-weighted luma of an RGBA sprite at 4x -> gradient magnitude
    g = ndi.gaussian_filter(ndi.zoom(a[..., :3].mean(2) * a[..., 3] / 255, 4, order=1), 2)
    return np.hypot(ndi.sobel(g, 1), ndi.sobel(g, 0))

def register(ref, mov):   # -> (ncc, s, dx, dy): mov scaled by s about the sprite centre (68, 98), then shifted by (dx, dy) sprite px, lands on ref
    R = (slice(4 * 45, 4 * 150), slice(4 * 15, 4 * 120))           # face: hairline to chin, ear to ear
    P = ref[R] - ref[R].mean(); P /= np.linalg.norm(P); ones = np.ones_like(P); c = np.array([98 * 4, 68 * 4]); best = None
    for s in np.arange(0.90, 1.10, 0.005):
        w = ndi.affine_transform(mov, np.diag([1 / s, 1 / s]), offset=c - c / s, order=1)
        num = signal.fftconvolve(w, P[::-1, ::-1], mode='valid'); s1 = signal.fftconvolve(w, ones, mode='valid'); s2 = signal.fftconvolve(w * w, ones, mode='valid')
        ncc = num / np.sqrt(np.maximum(s2 - s1 * s1 / P.size, 1e-6)); k = np.unravel_index(np.argmax(ncc), ncc.shape)
        if best is None or ncc[k] > best[0]: best = (float(ncc[k]), float(s), (R[1].start - k[1]) / 4, (R[0].start - k[0]) / 4)
    return best

e = {x['id']: x for x in json.load(open('out/s06-edl.json'))['edl']}
sh = Image.open(C22_SHEET).convert('RGBA'); c = C22_CELL
ref = feat(np.array(sh.crop(((c % 16) * W, (c // 16) * H, (c % 16 + 1) * W, (c // 16 + 1) * H))).astype(float))
os.makedirs('out/heads-wb', exist_ok=True); os.makedirs('film/heads', exist_ok=True)
kx, ky = 760 / W, 1100 / H                                         # normalised-frame px per sprite px
nw, nh, px, py = map(float, C22_NORM)
for rnd in range(3):
    norm = tuple(int(round(v)) for v in (nw, nh, px, py))
    keycmd(e['L1a']['src_in'], 1, norm, 'out/heads-wb/first.png', still=True)
    sc, s, dx, dy = register(ref, feat(np.array(Image.open('out/heads-wb/first.png').convert('RGBA')).astype(float)))
    print('round %d NORM %s -> L1a frame 0 vs c22 last: ncc %.3f scale %.3f dx %+.2f dy %+.2f sprite px' % (rnd, norm, sc, s, dx, dy), flush=True)
    if rnd == 2: break
    # sprite correction about (68, 98) in normalised-frame px: x'' = s x' + ax (crop origin 250, 150)
    ax = (250 + 68 * kx) * (1 - s) + dx * kx; ay = (150 + 98 * ky) * (1 - s) + dy * ky
    nw, nh, px, py = nw * s, nh * s, px * s + ax, py * s + ay
print('L1 NORM', norm, flush=True)
os.makedirs('out/heads-wb', exist_ok=True); os.makedirs('film/heads', exist_ok=True)
cells = []
for pid in ('L1a', 'L1b'):
    f = f"out/heads-wb/{pid}.mov"; keycmd(e[pid]['src_in'], e[pid]['frames'], norm, f); cells.append(os.path.abspath(f)); print(pid, e[pid]['frames'], flush=True)
open('out/heads-wb/list.txt', 'w').write(''.join(f"file '{c}'\n" for c in cells))
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'out/heads-wb/list.txt', '-c', 'copy', 'out/heads-wb/all.mov'], check=True)
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', 'out/heads-wb/all.mov', '-vf', f'tile={COLS}x{ROWS}:padding=0:margin=0:color=0x00000000,format=rgba',
                '-frames:v', '1', '-update', '1', 'film/heads/s06-wb-00.png'], check=True)
n = int(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', 'out/heads-wb/all.mov'],
                       capture_output=True, text=True).stdout.strip())
print('wb frames', n, '(L1a + L1b =', e['L1a']['frames'] + e['L1b']['frames'], ')')
json.dump({'L1': norm}, open('out/heads-wb/norm.json', 'w'))
