#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s07. Slide 7 edit list (film-plan-s07.md section 1) -> out/s07-edl.json, film/data/s07-edl.js,
out/s07-audio.filter. Lines come from the take's second read-through of this passage (413-457 s); in/out points sit in the pauses found with
silencedetect (n=-38dB, d=0.12) on the denoised take,
with each out point pushed 0.06-0.12 s later so word tails decay inside the 20 ms fade. "Eight kilobytes each." (431.92-433.84) is not in the script and is left out.
v6 (Liam 16718): 0.55 s of the bed-only pause after "massive" (M5 ends 17.47, M6 starts 18.70) is cut at scene 17.49: every line from M6 on starts 0.55 s
earlier and the scene is 41.4667 s (1244 frames). 0.55 s = 15 frames of the x11 output (15 x 1.1 / 30), so the x11 picture after the cut is v5's shifted by
exactly 15 frames; the pause after "massive" goes from 1.48 to 0.93 s of scene time. The trim is written into the EDL (trim) for the scene.
v7 (Liam 16819): "Then Merkle put thousands of those one-time keys into a tree" -> "and Merkle put those into a tree": M7 is three pieces cut at word boundaries on the
denoised take (faster_whisper word times, quiet spots checked at 20 ms RMS): M7 438.05-439.0167 (to "put", quiet 439.00-439.06), M7b 439.48-439.9133 ("those", its tail, quiet 439.90-439.94),
M7c 440.9533-441.82 ("into a tree", quiet 440.94-440.98 before "into"); "thousands of" (439.0167-439.48) and "one-time keys" (439.9133-440.9533) are gone, 1.5033 s = 41 frames
of the x11 output (41 x 1.1 / 30), all later lines start 1.5033 s earlier. Piece lengths are whole frames so the lip-synced head cells stay on the audio. Cuts are in the EDL (trims, uncut v5 clock)."""
import json
lines = [  # id, text, src_in, src_out, out_in
    ('M1', 'And lucky for us, it turns out you can build a signature out of nothing but hash functions.', 413.95, 418.30, 0.70),
    ('M2', 'No curves at all.', 418.59, 419.68, 5.28),
    ('M3', 'Shout out to Leslie Lamport, who figured this out in 1979.', 420.30, 423.95, 6.64),
    ('M4', 'Yeah, that Lamport. The namesake for the smallest unit of Solana.', 424.15, 427.95, 10.45),
    ('M5', 'Unfortunately, Lamport signatures are massive.', 428.80, 431.75, 14.52),
    ('M6', 'But Winternitz came along and made these smaller using hash chains.', 434.33, 437.45, 18.70),
    ('M7', 'and Merkle put', 438.05, 439.0167, 22.06),
    ('M7b', 'those', 439.48, 439.9133, 22.06 + 29 / 30),
    ('M7c', 'into a tree.', 440.9533, 441.82, 22.06 + 42 / 30),
    ('M8', "The whole thing is called XMSS, and it's a NIST standard.", 442.54, 446.25, 26.09),
    ('M9', "It's what we built for version three.", 446.66, 448.12, 29.95),
    ('M10', "So when the attacker copies our transaction and swaps the destination, the signature doesn't match anymore.", 448.77, 454.00, 33.10),
    ('M11', 'The program throws it out.', 454.42, 455.55, 38.45),
]
TRIM_AT, TRIM_D = 17.49, 0.55   # v6
CUT7 = 1.5033                   # v7: 0.4633 + 1.04 s out of M7 (41 x 1.1 / 30)
TOTAL = round(1244 / 30 - CUT7, 4)  # 39.9634 (v6 41.4667 s, 1244 frames; x11: 1131 frames -> 1090)
edl = []
for id_, text, si, so, oi in lines:
    d = so - si
    if oi >= TRIM_AT: oi = round(oi - TRIM_D, 6)
    if id_ in ('M8', 'M9', 'M10', 'M11'): oi = round(oi - CUT7, 6)
    edl.append({'id': id_, 'text': text, 'src_in': si, 'src_out': so, 'out_in': oi, 'out_out': round(oi + d, 4), 'frames': int(round(d * 30))})
for i in range(1, len(edl)): assert edl[i]['out_in'] >= edl[i - 1]['out_out'] - 1e-3, edl[i]['id']
# trims on the uncut (v5) clock: after "massive" (v6), then the two cuts in M7 (v7: at 23.0267 and 23.9233); see sh()/amb() in s07-xmss.html
A, B = 439.0167, 439.9133
trims = [{'at': TRIM_AT, 'd': TRIM_D}, {'at': round(22.06 + 29 / 30, 4), 'd': round(439.48 - A, 4)}, {'at': round(22.06 + 29 / 30 + (439.48 - A) + 13 / 30, 4), 'd': round(440.9533 - B, 4)}]
assert abs(sum(t['d'] for t in trims[1:]) - CUT7) < 1e-3
doc = {'total': TOTAL, 'fps': 30, 'edl': edl, 'trim': {'at': TRIM_AT, 'd': TRIM_D}, 'trims': trims}
json.dump(doc, open('out/s07-edl.json', 'w'), indent=1)
open('film/data/s07-edl.js', 'w').write('window.S07 = ' + json.dumps(doc) + ';\n')
f = []
for i, e in enumerate(edl):
    d = e['src_out'] - e['src_in']; ms = int(round(e['out_in'] * 1000))
    f.append(f"[0:a]atrim=start={e['src_in']}:end={e['src_out']},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={d - 0.02:.4f}:d=0.02,adelay={ms}|{ms}[a{i}];")
f.append(f"anullsrc=r=48000:cl=mono,atrim=0:{TOTAL},asetpts=PTS-STARTPTS[base];")
f.append('[base]' + ''.join(f'[a{i}]' for i in range(len(edl))) + f"amix=inputs={len(edl) + 1}:normalize=0:duration=longest,pan=mono|c0=c0,apad=whole_dur={TOTAL},atrim=0:{TOTAL},asetpts=PTS-STARTPTS[mix]")
open('out/s07-audio.filter', 'w').write('\n'.join(f) + '\n')
for e in edl: print(e['id'], e['src_in'], e['src_out'], '->', e['out_in'], e['out_out'], e['frames'])
