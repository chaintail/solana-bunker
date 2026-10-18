#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker. Lip-synced head-and-neck sprites for slide 4, one PNG sequence per character:
film/heads/<character>/h%05d.png (RGBA, 30 fps, index 0 = first output frame of the character's first phrase).
Same key as ~/video-work/head-test/key.sh (RVM alpha minus a luma key of the black shirt below the chin, zone.png / kill.png masks, 760x1100 crop),
but cut with the audio edit list (out/s04/s04-edl.json) and scaled straight to the sprite size: the clip a stand-in body needs is
hair-top-to-chin = body height / 4.7 (body = 6 faces, face = chin to hairline = 665 px of the 760x1100 key), so
physicist (body 800 px) 153x221, others (body 500 px) 95x138. Each phrase runs to the start of the next phrase of the same character
(the gap holds its last frame); the scene clamps to the first/last frame, so the head freezes when the character's part is over."""
import json, os, subprocess, sys
os.environ['PATH'] = '/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin:' + os.environ['PATH']
B = os.path.expanduser('~/video-work/bunker'); HT = os.path.expanduser('~/video-work/head-test')
e = json.load(open('out/s04/s04-edl.json'))['edl']
ONLY_SHEETS = len(sys.argv) > 1 and sys.argv[1] == 'sheets'
SIZE = {'physicist': (153, 221), 'joe': (95, 138), 'engineer': (95, 138)}
LO, HI = 28, 58
for who, (w, h) in ([] if ONLY_SHEETS else SIZE.items()):
    segs = [x for x in e if x['who'] == who]
    d = f'film/heads/{who}'; os.makedirs(d, exist_ok=True)
    f0 = round(segs[0]['out_in'] * 30)
    for i, x in enumerate(segs):
        a = round(x['out_in'] * 30) - f0
        b = (round(segs[i + 1]['out_in'] * 30) - f0) if i + 1 < len(segs) else a + round((x['out_out'] - x['out_in']) * 30) + 3
        n = b - a; dur = x['src_out'] - x['src_in']; nsrc = round(dur * 30)
        S = str(x['src_in']); T = str(dur + 0.1)
        fc = (f"[0:v]fps=30,format=gray,gblur=sigma=1.5,lut=y='clip(({HI}-val)*255/({HI}-{LO}),0,255)'[s];[2:v]format=gray[z];[3:v]format=gray[kl];"
              f"[s][z]blend=all_mode=multiply,dilation,dilation[sd];[sd][kl]blend=all_mode=lighten,negate,gblur=sigma=1.2[k];"
              f"[1:v]fps=30,format=gray[a];[a][k]blend=all_mode=multiply,gblur=sigma=0.8[am];"
              f"[4:v]fps=30,format=rgb24,despill=type=green:mix=0.6:expand=0.2,format=gbrp[rgb];[rgb][am]alphamerge,crop=760:1100:250:150,"
              f"scale={w}:{h}:flags=lanczos,format=rgba,tpad=stop_mode=clone:stop={n},trim=end_frame={n},setpts=PTS-STARTPTS[o]")
        cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', S, '-t', T, '-i', B + '/matte-full-comp.mp4', '-ss', S, '-t', T, '-i', B + '/matte-full-alpha.mp4',
               '-loop', '1', '-framerate', '30', '-i', HT + '/zone.png', '-loop', '1', '-framerate', '30', '-i', HT + '/kill.png', '-ss', S, '-t', T, '-i', B + '/matte-full-comp.mp4',
               '-filter_complex', fc, '-map', '[o]', '-frames:v', str(n), '-start_number', str(a), f'{d}/h%05d.png']
        subprocess.run(cmd, check=True); print(who, x['id'], a, b, n, flush=True)
# sprite sheets (20 columns, rows appended): one image per character, so the scene loads three files instead of ~1100
def sheets():
    for who, (w, h) in SIZE.items():
        d = f'film/heads/{who}'; n = len([f for f in os.listdir(d) if f.startswith('h') and f.endswith('.png')]); rows = []
        for r in range(0, n, 20):
            fs = [f'{d}/h{i:05d}.png' for i in range(r, min(n, r + 20))]
            subprocess.run(['magick'] + fs + ['-background', 'none', '+append', f'{d}/row{r // 20:02d}.png'], check=True); rows.append(f'{d}/row{r // 20:02d}.png')
        subprocess.run(['magick'] + rows + ['-background', 'none', '-append', f'film/heads/{who}.png'], check=True)
        for r in rows: os.remove(r)
        print('sheet', who, n, flush=True)
sheets()
