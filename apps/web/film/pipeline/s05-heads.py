#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s05. Lip-synced head-and-neck sprites for slide 5 (lab coat Liam), cut with the audio edit list (out/s05-edl.json).
Same key as ~/video-work/head-test/key.sh (RVM alpha minus a luma key of the black shirt below the chin, zone.png / kill.png masks, 760x1100 crop) cut from the matte
footage at the phrase's source in/out, scaled to the sprite size, concatenated phrase after phrase (the scene holds the last frame through pauses) and tiled
16 x 12 per sheet: film/heads/lab-NN.png (192 frames each, frame i of the whole run = sheet i//192, cell i%192).
Sprite size 136x197 = head scale 0.1793 = face (chin to hairline, 665 key px) 119 px = oval of the body PNG (217 px) at body scale 0.55 (HEAD_K in the scene)."""
import json, os, subprocess
os.environ['PATH'] = '/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:' + os.environ['PATH']
B = os.path.expanduser('~/video-work/bunker'); HT = os.path.expanduser('~/video-work/head-test')
W, H, COLS, ROWS = 136, 197, 16, 12
e = json.load(open('out/s05-edl.json'))['edl']
LO, HI = 28, 58
os.makedirs('out/heads', exist_ok=True); os.makedirs('film/heads', exist_ok=True)
cells = []
for x in e:
    n = x['frames']; S = str(x['src_in']); T = str(n / 30 + 0.2)
    fc = (f"[0:v]fps=30,format=gray,gblur=sigma=1.5,lut=y='clip(({HI}-val)*255/({HI}-{LO}),0,255)'[s];[2:v]format=gray[z];[3:v]format=gray[kl];"
          f"[s][z]blend=all_mode=multiply,dilation,dilation[sd];[sd][kl]blend=all_mode=lighten,negate,gblur=sigma=1.2[k];"
          f"[1:v]fps=30,format=gray[a];[a][k]blend=all_mode=multiply,gblur=sigma=0.8[am];"
          f"[4:v]fps=30,format=rgb24,despill=type=green:mix=0.6:expand=0.2,format=gbrp[rgb];[rgb][am]alphamerge,crop=760:1100:250:150,"
          f"scale={W}:{H}:flags=lanczos,format=rgba,trim=end_frame={n},setpts=PTS-STARTPTS[o]")
    f = f"out/heads/{x['id']}.mov"
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', S, '-t', T, '-i', B + '/matte-full-comp.mp4', '-ss', S, '-t', T, '-i', B + '/matte-full-alpha.mp4',
                    '-loop', '1', '-framerate', '30', '-i', HT + '/zone.png', '-loop', '1', '-framerate', '30', '-i', HT + '/kill.png', '-ss', S, '-t', T, '-i', B + '/matte-full-comp.mp4',
                    '-filter_complex', fc, '-map', '[o]', '-frames:v', str(n), '-c:v', 'qtrle', '-r', '30', f], check=True)
    cells.append(os.path.abspath(f)); print(x['id'], n, flush=True)
open('out/heads/list.txt', 'w').write(''.join(f"file '{c}'\n" for c in cells))
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'out/heads/list.txt', '-c', 'copy', 'out/heads/all.mov'], check=True)
for f in os.listdir('film/heads'):
    if f.startswith('lab-'): os.remove('film/heads/' + f)
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', 'out/heads/all.mov', '-vf', f'tile={COLS}x{ROWS}:padding=0:margin=0:color=0x00000000,format=rgba', '-f', 'image2', '-start_number', '0', 'film/heads/lab-%02d.png'], check=True)
print(sorted(os.listdir('film/heads')))
