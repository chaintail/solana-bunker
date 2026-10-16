#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s11 (system python). Scene 11 timing (film-plan-ending.md part C, composer rulings: roll at 6 px a frame,
the closing lines on two cards on black, voice only) -> out/s11-edl.json, film/data/s11-edl.js (window.S11: T), out/s11-audio.filter.
v3: the voice is the generated outro read (no take segment), starting at 4.60; the printed ask line still fades in at 4.12.
The roll starts below its window (472 px) at 3.60 and moves 6 px a frame; ROLL_H is the roll's measured height (4851 px in v3; 4525 in v2,
s11-cnn.html); it ends when the last line has left the window."""
import json, math
FPS = 30
VOICE_AT = 4.60     # generated outro read (Google en-GB-Studio-C, voices/outro/outro.wav), 1.0 s after the split lands (3.60)
ROLL_H, WIN, PXF = 4851, 472, 6        # measured in s11-cnn.html (v3: + AUDIO ENGINEERS and ASSOCIATE PRODUCER blocks): roll offsetHeight 4851, window 471.67 -> 472
T = {'bars': 0.0, 'ident': .35, 'logo_in': .35, 'net_in': 1.15, 'cnn_in': 1.80, 'streak': 2.20, 'split': 3.00, 'split_end': 3.60, 'roll': 3.60, 'pxf': PXF,
     'voice': VOICE_AT, 'feel': 4.12}   # the printed ask line keeps its v1/v2 time
roll_frames = math.ceil((WIN + ROLL_H) / PXF)
T['roll_end'] = round(T['roll'] + roll_frames / FPS, 4)
T['card1'] = T['roll_end']                       # 0.5 s crossfade in, held 4.0 s
T['card2'] = round(T['card1'] + 4.5, 4)          # 0.4 s crossfade, held 3.0 s
T['fade'] = round(T['card2'] + 3.4, 4)           # 1.0 s to black
frames = round((T['fade'] + 1.0) * FPS); TOTAL = round(frames / FPS, 4); T['total'] = TOTAL
doc = {'total': TOTAL, 'frames': frames, 'fps': FPS, 'voice_at': VOICE_AT, 'T': T}
json.dump(doc, open('out/s11-edl.json', 'w'), indent=1)
open('film/data/s11-edl.js', 'w').write('window.S11 = ' + json.dumps(doc) + ';\n')
ms = int(round(VOICE_AT * 1000))
open('out/s11-audio.filter', 'w').write(
    f"[0:a]silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02,aresample=48000,afade=t=in:d=0.02,adelay={ms},apad=whole_dur={TOTAL},atrim=0:{TOTAL},asetpts=PTS-STARTPTS[mix]\n")
print('roll frames', roll_frames, 'total', TOTAL, 'frames', frames); print(T)
