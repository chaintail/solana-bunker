#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s11 (system python). Scene 11 timing (film-plan-ending.md part C, composer rulings: roll at 6 px a frame,
the closing lines on two cards on black, voice only) -> out/s11-edl.json, film/data/s11-edl.js (window.S11: T), out/s11-audio.filter.
One segment of the denoised take: C1 583.62-586.00 ("Feel free to reach out with any questions.") at scene 3.90; "Feel" 583.84 -> 4.12.
The roll starts below its window (472 px) at 3.60 and moves 6 px a frame; ROLL_H is the roll's measured height (4525 px in the v2 typography,
s11-cnn.html); it ends when the last line has left the window."""
import json, math
FPS = 30
SEG = (583.62, 586.00, 3.90)
ROLL_H, WIN, PXF = 4525, 472, 6        # measured in s11-cnn.html (v2 spacing, two-line bracket credits): roll offsetHeight 4525, window 471.67 -> 472
T = {'bars': 0.0, 'ident': .35, 'logo_in': .35, 'net_in': 1.15, 'cnn_in': 1.80, 'streak': 2.20, 'split': 3.00, 'split_end': 3.60, 'roll': 3.60, 'pxf': PXF,
     'voice': SEG[2], 'feel': round(SEG[2] + 583.84 - SEG[0], 3)}
roll_frames = math.ceil((WIN + ROLL_H) / PXF)
T['roll_end'] = round(T['roll'] + roll_frames / FPS, 4)
T['card1'] = T['roll_end']                       # 0.5 s crossfade in, held 4.0 s
T['card2'] = round(T['card1'] + 4.5, 4)          # 0.4 s crossfade, held 3.0 s
T['fade'] = round(T['card2'] + 3.4, 4)           # 1.0 s to black
frames = round((T['fade'] + 1.0) * FPS); TOTAL = round(frames / FPS, 4); T['total'] = TOTAL
doc = {'total': TOTAL, 'frames': frames, 'fps': FPS, 'seg': SEG, 'T': T}
json.dump(doc, open('out/s11-edl.json', 'w'), indent=1)
open('film/data/s11-edl.js', 'w').write('window.S11 = ' + json.dumps(doc) + ';\n')
a, b, si = SEG; d = b - a; ms = int(round(si * 1000))
open('out/s11-audio.filter', 'w').write(
    f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={d - 0.02:.4f}:d=0.02,adelay={ms}|{ms}[a0];\n"
    f"anullsrc=r=48000:cl=mono,atrim=0:{TOTAL},asetpts=PTS-STARTPTS[base];\n"
    f"[base][a0]amix=inputs=2:normalize=0:duration=longest,pan=mono|c0=c0,apad=whole_dur={TOTAL},atrim=0:{TOTAL},asetpts=PTS-STARTPTS[mix]\n")
print('roll frames', roll_frames, 'total', TOTAL, 'frames', frames); print(T)
