#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s08 (system python, numpy). Scene 8 edit list (film-plan-s08.md section 1) -> out/s08-edl.json,
film/data/s08-edl.js (window.S08: edl, beat times T, SFX markers), out/s08-audio.filter. Needs out/take-dn.wav (build.sh audio).
Liam's only read of this passage (456.2-495.7 s), used as recorded. In/out points sit in the pauses of silencedetect (n=-38dB, d=0.12) on the denoised take.
E5/C1 ("withdrawal" | "Not") has almost no pause (plan R2): the cut is the quietest 10 ms frame in 477.00-477.15 s, snapped to the nearest zero crossing.
v4: E5 and C1 are one continuous stretch of the take (no inserted gap; the natural pause is 477.04-477.14 s), E6 starts at "Solana" (the "Oh, but" groan
is cut at 479.60 s), E8 is split at the comma into E8a (engineer) and E8b (lab coat, from "and"); rows that touch in the take play as ONE audio segment (no fade at the join).
One real time shift: +0.60 s after E8 (the block drops through the slot). The tag gets 8-bit chiptune (pipeline/s08/chiptune.py -> audio/s08/*.wav), mixed in build.sh. Beat times are take times of the key
words (transcript tokens rechecked with a 50 ms energy scan), mapped through the edit list, so the scene never hard-codes a time twice.
v5: the whole scene is scored (pipeline/s08/score.py reads markers, T and sfx from data/s08-edl.js and renders audio/s08/score.wav, tag cues included);
the mix takes that one file at 0 s (out/s08-sfx.args/.filter).
v7 (Liam 16702): the tag is cut to the proof table. LEVEL COMPLETE, the rotation text box, the spent-leaf bitmap, the NEXT LEVEL tree and the ROTATE stamp are gone
(with their cues: the tag bed and the ROTATE coin; the row ticks are dropped). From the tag start the table scrolls in over 0.6545 s (0.595 s at 1.1x, the jingle's 7-note arpeggio) and holds
to the end; TAG = 2.01 s gives 1270 scene frames (x11: 1155 frames, 38.50 s, 2.09 s from the end of the last word), and the scene's last frame is v6's last frame
moved 10.0 s earlier (same table, same Joe pose: his cheer has 1 s and 1/3 s periods), so scene 9's hand-off frame is unchanged."""
import json, subprocess, numpy as np
SR = 48000
def pcm(a, b):
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-ss', str(a), '-t', str(b - a), '-i', 'out/take-dn.wav', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32)
a0, a1 = 477.00, 477.15; x = pcm(a0, a1); W = int(.01 * SR)
rms = [np.sqrt((x[i:i + W] ** 2).mean()) for i in range(0, len(x) - W, W // 2)]
m = int(np.argmin(rms)) * (W // 2) + W // 2
zc = np.nonzero(np.diff(np.signbit(x)))[0]
m = int(zc[np.argmin(abs(zc - m))]) if len(zc) else m
CUT = round(a0 + m / SR, 4); print('E5/C1 head split at %.4f s (audio is not cut here)' % CUT)
E6IN, E8SPLIT = 479.60, 485.58   # E6 head cut in the silence before "Solana" (onset 479.65); E8 comma pause is 485.30-485.60
TAG = 2.01   # v7: was 12.0
PROOF_IN = .6545   # v7: the proof table scrolls 244 -> 8 px over this (v6: 3.9 s from tag + 7.0 s)
lines = [  # id, speaker, text, src_in, src_out, extra gap before this line (s)
    ('E1', 'eng', 'XMSS signatures seem awesome.', 456.40, 458.66, 0),
    ('E2', 'eng', "They're way smaller.", 458.76, 459.76, 0),
    ('E3', 'eng', 'Only 2500 bytes. Ah, damn it, that 1232 byte transaction limit.', 460.06, 465.86, 0),
    ('S1', 'lab', '(sigh)', 466.90, 467.99, 0),
    ('E4', 'eng', 'I guess we could use temporary data accounts to upload signatures in pieces.', 468.10, 471.95, 0),
    ('E5', 'eng', 'But from our research, that took five transactions just to do a simple withdrawal.', 472.86, CUT, 0),
    ('C1', 'lab', 'Not really cool.', CUT, 478.30, 0),
    ('E6', 'eng', 'Solana Transactions V1 to the rescue.', E6IN, 481.95, -0.45),   # gap: Solana onset lands 0.93 s after C1 ends
    ('E7', 'eng', '4,096 bytes.', 482.30, 484.05, 0),
    ('E8a', 'eng', 'So we built that,', 484.40, E8SPLIT, 0),
    ('E8b', 'lab', 'and it worked.', E8SPLIT, 486.62, 0),
    ('E9', 'eng', 'One transaction, 3100 bytes, about half a million compute units, and the full signature verifies on-chain in a single shot.', 486.68, 495.10, 0.60),
]
START = 1.20
edl = []; shift = START - lines[0][3]
for id_, sp, text, si, so, gap in lines:
    shift += gap; oi = round(si + shift, 4); d = so - si
    edl.append({'id': id_, 'speaker': sp, 'text': text, 'src_in': si, 'src_out': so, 'out_in': oi, 'out_out': round(oi + d, 4), 'frames': int(round(d * 30))})
for i in range(1, len(edl)): assert edl[i]['out_in'] >= edl[i - 1]['out_out'] - 1e-6, edl[i]['id']
def S(src):   # take time -> scene time (the line containing it)
    for e in edl:
        if e['src_in'] - .05 <= src <= e['src_out'] + .05: return round(src - e['src_in'] + e['out_in'], 3)
    raise ValueError(src)
END_SPEECH = edl[-1]['out_out']; TAG0 = round(END_SPEECH + .27, 3); TOTAL = round(TAG0 + TAG, 2)
T = {  # beat cues, scene seconds
 'load': 0.0, 'xmss': S(456.48), 'awesome': S(458.10), 'smaller': S(459.30), 'only': S(460.12), 'bytes1': S(461.84), 'ah': S(462.72), 'n1232': S(463.76),
 'transaction': S(465.04), 'limit': S(465.68), 'e3end': S(465.80), 'sigh': S(466.96), 'sighEnd': S(467.96), 'iguess': S(468.14), 'tempacct': S(469.28),
 'upload': S(470.56), 'pieces': S(471.68), 'but': S(472.91), 'research': S(473.68), 'five': S(474.64), 'e5end': edl[5]['out_out'],
 'not': S(477.16), 'cool': S(478.00), 'c1end': edl[6]['out_out'], 'oh': 0, 'solana': S(479.68), 'v1': S(480.96), 'rescue': S(481.60),
 'n4096': S(482.38), 'bytes2': S(483.60), 'so': S(484.46), 'that': S(485.20), 'worked': S(485.62), 'e8end': edl[10]['out_out'],
 'one': S(486.74), 'n3100': S(488.33), 'halfmil': S(489.92), 'compute': S(490.56), 'signature': S(492.32), 'verifies': S(492.88), 'onchain': S(493.52),
 'single': S(494.40), 'shot': S(494.88), 'end': END_SPEECH, 'tag': TAG0, 'proof': round(TAG0 + PROOF_IN, 4), 'total': TOTAL,
}
T['oh'] = round(T['solana'] - .48, 3)   # coin drop (oh + .45) lands just before the banner
trucks = [round(T['research'] + .6 + i * .9, 3) for i in range(3)] + [round(T['not'] + .04, 3), round(T['not'] + .64, 3)]   # arrival times at TEMP ACCT; 4 and 5 arrive under C1
T['trucks'] = trucks
markers = [{'id': k, 't': v} for k, v in [
    ('SFX_LAMPORT_LAND', T['xmss'] + .42), ('SFX_XMSS_LAND', T['awesome'] + .42), ('SFX_EXPLODE', T['smaller']), ('SFX_SCORE_TICK', T['smaller'] + .1),
    ('SFX_SLOT_OPEN', T['ah']), ('SFX_BLOCK_HOP', T['n1232'] + .3), ('SFX_WEDGE', T['transaction'] + .2), ('SFX_GAME_OVER', T['limit'] + .1),
    ('SFX_SAW', T['upload']), ('SFX_BREAK', T['pieces'])] + [(f'SFX_TRUCK_{i + 1}', a) for i, a in enumerate(trucks)] + [
    ('SFX_STAMP', T['cool']), ('SFX_INSERT_COIN', T['c1end'] + .05), ('SFX_COIN_DROP', T['oh'] + .45), ('SFX_BANNER', T['solana']), ('SFX_NEW', T['v1']),
    ('SFX_SLOT_WIDEN', T['n4096']), ('SFX_SPIN', T['n4096'] + .6), ('SFX_SWAP_A', T['so']), ('SFX_SWAP_B', T['so'] + .35), ('SFX_BLOCK_DROP', T['worked'] + .2),
    ('SFX_WIN_1', T['one']), ('SFX_WIN_2', T['n3100']), ('SFX_WIN_3', T['compute']), ('SFX_WIN_4', T['verifies']), ('SFX_CHECK', T['single']),
    ('SFX_JOE', T['single']), ('SFX_LEVEL_COMPLETE', T['tag'])]]   # v7: the jingle's first note, as the table starts
for mk in markers: mk['t'] = round(mk['t'], 3)
# chiptune cues of the tag (chiptune.py patterns, rendered by score.py). v7: only the jingle, from the tag start: its 7-note arpeggio (0.595 s) runs while the table
# scrolls in, the held C major chord lands as it stops and is held `hold` s, release included, so it ends 0.1 s before the x11 end. Cut with their pictures: v6's
# tag bed (from the text box) and ROTATE coin. The 18 row ticks are dropped too: at this scroll speed they would come every 25-30 ms on top of the arpeggio
# (and the sum peaks over the score's -11 dBFS ceiling); the arpeggio is the scroll's sound.
SFX = [{'file': 'jingle', 't': TAG0, 'hold': 1.10}]
doc = {'total': TOTAL, 'fps': 30, 'edl': edl, 'T': T, 'markers': markers, 'note': 'v7: tag cut to the proof table (Liam 16702). v5: score.py renders the whole chiptune score (audio/s08/score.wav) from markers, T and the tag cue times (sfx); the mix plays that one file', 'sfx': SFX}
json.dump(doc, open('out/s08-edl.json', 'w'), indent=1)
open('film/data/s08-edl.js', 'w').write('window.S08 = ' + json.dumps(doc) + ';\n')
f = []; runs = []   # rows that touch in the take AND in the scene play as one segment (no fade, no dip at the join)
for e in edl:
    if runs and abs(runs[-1]['src_out'] - e['src_in']) < 1e-3 and abs(runs[-1]['out_out'] - e['out_in']) < 1e-3: runs[-1]['src_out'] = e['src_out']; runs[-1]['out_out'] = e['out_out']
    else: runs.append(dict(src_in=e['src_in'], src_out=e['src_out'], out_in=e['out_in'], out_out=e['out_out']))
for i, e in enumerate(runs):
    d = e['src_out'] - e['src_in']; ms = int(round(e['out_in'] * 1000))
    f.append(f"[0:a]atrim=start={e['src_in']}:end={e['src_out']},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={d - 0.02:.4f}:d=0.02,adelay={ms}|{ms}[a{i}];")
f.append(f"anullsrc=r=48000:cl=mono,atrim=0:{TOTAL},asetpts=PTS-STARTPTS[base];")
f.append('[base]' + ''.join(f'[a{i}]' for i in range(len(runs))) + f"amix=inputs={len(runs) + 1}:normalize=0:duration=longest,pan=mono|c0=c0,apad=whole_dur={TOTAL},atrim=0:{TOTAL},asetpts=PTS-STARTPTS[mix]")
open('out/s08-audio.filter', 'w').write('\n'.join(f) + '\n')
for e in edl: print(e['id'], e['speaker'], e['src_in'], e['src_out'], '->', e['out_in'], e['out_out'], e['frames'])
print('total', TOTAL, 'tag', TAG0)
# score input for build.sh: input 2 is the whole score (score.py, scene length, levels baked in, tag cues included), from 0 s, into [sfx]
open('out/s08-sfx.args', 'w').write('-i film/audio/s08/score.wav')
open('out/s08-sfx.filter', 'w').write(f"[2:a]aresample=48000,apad=whole_dur={TOTAL},atrim=0:{TOTAL}[sfx]")
