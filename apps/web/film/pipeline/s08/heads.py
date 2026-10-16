#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s08. Head sprites for scene 8 (same key as pipeline/head-test/key.sh: RVM alpha minus a luma key of the
black shirt below the chin, zone.png / kill.png masks, 760x1100 crop; adapted from the slide 5 heads script).
  every line of out/s08-edl.json (engineer E-lines and lab coat S1/C1) cut at the audio in/out and concatenated, tiled 16 x 12 per sheet -> film/heads/s08-head-NN.png
            (frame i of the run = sheet i // 192, cell i % 192; the scene holds a line's last frame through the pauses that follow it)
  the scene picks, per character, the frames of that character's own lines
Sprite size 152x220 (760x1100 / 5)."""
import json, os, subprocess, sys
os.environ['PATH'] = '/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:' + os.environ['PATH']
B = os.path.expanduser('~/video-work/bunker'); HT = os.path.expanduser('~/video-work/head-test')
W, H, COLS, ROWS = 152, 220, 16, 12
LO, HI = 28, 58
def key(src_in, n, out, post='', still=False):
    fc = (f"[0:v]fps=30,format=gray,gblur=sigma=1.5,lut=y='clip(({HI}-val)*255/({HI}-{LO}),0,255)'[s];[2:v]format=gray[z];[3:v]format=gray[kl];"
          f"[s][z]blend=all_mode=multiply,dilation,dilation[sd];[sd][kl]blend=all_mode=lighten,negate,gblur=sigma=1.2[k];"
          f"[1:v]fps=30,format=gray[a];[a][k]blend=all_mode=multiply,gblur=sigma=0.8[am];"
          f"[4:v]fps=30,format=rgb24,despill=type=green:mix=0.6:expand=0.2,format=gbrp[rgb];[rgb][am]alphamerge,crop=760:1100:250:150,"
          f"scale={W}:{H}:flags=lanczos,format=rgba{post},trim=end_frame={n},setpts=PTS-STARTPTS[o]")
    S, T = str(src_in), str(n / 30 + 0.2)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', S, '-t', T, '-i', B + '/matte-full-comp.mp4', '-ss', S, '-t', T, '-i', B + '/matte-full-alpha.mp4',
                    '-loop', '1', '-framerate', '30', '-i', HT + '/zone.png', '-loop', '1', '-framerate', '30', '-i', HT + '/kill.png', '-ss', S, '-t', T, '-i', B + '/matte-full-comp.mp4',
                    '-filter_complex', fc, '-map', '[o]', '-frames:v', str(n)] + (['-update', '1', out] if still else ['-c:v', 'qtrle', '-r', '30', out]), check=True)
os.makedirs('out/heads', exist_ok=True); os.makedirs('film/heads', exist_ok=True)
cells = []
for x in json.load(open('out/s08-edl.json'))['edl']:
    f = f"out/heads/{x['id']}.mov"; key(x['src_in'], x['frames'], f); cells.append(os.path.abspath(f)); print(x['id'], x['frames'], flush=True)
open('out/heads/list.txt', 'w').write(''.join(f"file '{c}'\n" for c in cells))
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'out/heads/list.txt', '-c', 'copy', 'out/heads/all.mov'], check=True)
for f in os.listdir('film/heads'):
    if f.startswith('s08-head-'): os.remove('film/heads/' + f)
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', 'out/heads/all.mov', '-vf', f'tile={COLS}x{ROWS}:padding=0:margin=0:color=0x00000000,format=rgba', '-f', 'image2', '-start_number', '0', 'film/heads/s08-head-%02d.png'], check=True)
n = int(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', 'out/heads/all.mov'], capture_output=True, text=True).stdout.strip())
print('head frames', n, sorted(f for f in os.listdir('film/heads') if f.startswith('s08-')))
