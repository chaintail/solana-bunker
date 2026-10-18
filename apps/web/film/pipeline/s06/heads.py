#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s06. Head sprites for slide 6 (same key as pipeline/head-test/key.sh: RVM alpha minus a luma key of the
black shirt below the chin, zone / kill masks recentred on the jaw (JX below), 760x1100 crop; adapted from the slide 5 heads script).
  narrator: lip-synced head, every line of out/s06-edl.json cut at the audio in/out and concatenated, tiled 16 x 12 per sheet -> film/heads/s06-narr-NN.png
            (frame i of the run = sheet i // 192, cell i % 192; the scene holds a line's last frame through the pauses that follow it)
  bouncer:  one closed-mouth frame (never speaks)                         -> film/heads/s06-bouncer.png
  devil:    one closed-mouth frame, red monochrome (horns/mask are SVG)    -> film/heads/s06-devil.png
Sprite size 152x220 (760x1100 / 5): 2x the bouncer's on-screen head."""
import json, os, subprocess, sys
os.environ['PATH'] = '/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:' + os.environ['PATH']
B = os.path.expanduser('~/video-work/bunker')
W, H, COLS, ROWS = 152, 220, 16, 12
LO, HI = 28, 58
# zone / kill masks (1080x1440, as pipeline/head-test/zone.sh) recentred on Liam's jaw in this scene's lines: zone.sh centres both on x 625 and hard-kills
# x < 453 below y 950, which cut a rectangle out of the left jaw (sprite x < 39, y > 161). Here the jaw spans x 361..771 on rows 930-1080, centre JX.
# kill: outside JX +- 265 below y 950; zone (where the shirt luma key may act): outside the jaw ellipse (JX, 870) 255 x 245 below y 925, or outside JX +- 200 below y 955
JX = 566
ZONE, KILL = 'out/heads/zone-jaw.png', 'out/heads/kill-jaw.png'
def masks():
    for e, f in ((f"255*max(clip((hypot((X-{JX})/255,(Y-870)/245)-1)*12,0,1)*clip((Y-925)/40,0,1),clip((abs(X-{JX})-200)/20,0,1)*clip((Y-955)/15,0,1))", ZONE),
                 (f"255*clip((abs(X-{JX})-265)/18,0,1)*clip((Y-950)/12,0,1)", KILL)):
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=1080x1440,format=gray', '-vf', f"geq=lum='{e}'", '-frames:v', '1', f], check=True)
BOUNCER_T, DEVIL_T = float(os.environ.get('BOUNCER_T', 360.90)), float(os.environ.get('DEVIL_T', 353.00))
def key(src_in, n, out, post='', still=False):
    fc = (f"[0:v]fps=30,format=gray,gblur=sigma=1.5,lut=y='clip(({HI}-val)*255/({HI}-{LO}),0,255)'[s];[2:v]format=gray[z];[3:v]format=gray[kl];"
          f"[s][z]blend=all_mode=multiply,dilation,dilation[sd];[sd][kl]blend=all_mode=lighten,negate,gblur=sigma=1.2[k];"
          f"[1:v]fps=30,format=gray[a];[a][k]blend=all_mode=multiply,gblur=sigma=0.8[am];"
          f"[4:v]fps=30,format=rgb24,despill=type=green:mix=0.6:expand=0.2,format=gbrp[rgb];[rgb][am]alphamerge,crop=760:1100:250:150,"
          f"scale={W}:{H}:flags=lanczos,format=rgba{post},trim=end_frame={n},setpts=PTS-STARTPTS[o]")
    S, T = str(src_in), str(n / 30 + 0.2)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', S, '-t', T, '-i', B + '/matte-full-comp.mp4', '-ss', S, '-t', T, '-i', B + '/matte-full-alpha.mp4',
                    '-loop', '1', '-framerate', '30', '-i', ZONE, '-loop', '1', '-framerate', '30', '-i', KILL, '-ss', S, '-t', T, '-i', B + '/matte-full-comp.mp4',
                    '-filter_complex', fc, '-map', '[o]', '-frames:v', str(n)] + (['-update', '1', out] if still else ['-c:v', 'qtrle', '-r', '30', out]), check=True)
os.makedirs('out/heads', exist_ok=True); os.makedirs('film/heads', exist_ok=True)
masks()
key(BOUNCER_T, 1, 'film/heads/s06-bouncer.png', still=True)
# red monochrome: luma -> deep red..hot red, alpha kept
key(DEVIL_T, 1, 'film/heads/s06-devil.png', post=",colorchannelmixer=rr=.42:rg=.42:rb=.16:gr=.08:gg=.08:gb=.03:br=.07:bg=.07:bb=.03,eq=contrast=1.15:brightness=.02", still=True)
if 'stills' in sys.argv: sys.exit(0)
cells = []
for x in json.load(open('out/s06-edl.json'))['edl']:
    f = f"out/heads/{x['id']}.mov"; key(x['src_in'], x['frames'], f); cells.append(os.path.abspath(f)); print(x['id'], x['frames'], flush=True)
open('out/heads/list.txt', 'w').write(''.join(f"file '{c}'\n" for c in cells))
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'out/heads/list.txt', '-c', 'copy', 'out/heads/all.mov'], check=True)
for f in os.listdir('film/heads'):
    if f.startswith('s06-narr-'): os.remove('film/heads/' + f)
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', 'out/heads/all.mov', '-vf', f'tile={COLS}x{ROWS}:padding=0:margin=0:color=0x00000000,format=rgba', '-f', 'image2', '-start_number', '0', 'film/heads/s06-narr-%02d.png'], check=True)
n = int(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', 'out/heads/all.mov'], capture_output=True, text=True).stdout.strip())
print('narrator frames', n, sorted(f for f in os.listdir('film/heads') if f.startswith('s06-')))
