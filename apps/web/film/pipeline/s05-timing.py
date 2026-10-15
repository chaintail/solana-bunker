#!/usr/bin/env python3
"""Slide 5 audio edit list, word timings and filter graph (runs anywhere, no media tools).
usage: s05-timing.py <bunker-transcript.json> <out-dir>
Writes <out-dir>/s05-edl.json, s05-timing.js (window.S05 = {...}), s05-audio.filter (label [mix]).
Phrase table: id, token window (transcript s), speech bounds e0/e1 (energy, from silencedetect -38 dB on the denoised take), cut in/out (source s, inside the
silences around the phrase), gap after (s of room tone before the next phrase). Token times of the TDT model run 0.0-0.35 s early at phrase onsets, so each
phrase's tokens are mapped linearly onto the energy bounds (same method as conspiracy-timing.py)."""
import json, sys, re
tr = json.load(open(sys.argv[1]))['sentences']; out = sys.argv[2]
toks = sorted((t['s'], t['e'], t['t']) for s in tr for t in s['tokens'])
def words(a, b):
    ws = []
    for s, e, t in toks:
        if s < a or s >= b: continue
        if t.startswith(' ') or not ws: ws.append([t.strip(), s, e])
        elif re.match(r"^[,.?!']$", t): ws[-1][0] += t
        else: ws[-1][0] += t; ws[-1][2] = e
    return [w for w in ws if w[0]]
LEAD = 0.5          # slide-4 end frame held before the first word
TAIL = 2.6          # after the last word: board holds, then hard cut to slide 6
# id, (tok_a, tok_b), e0, e1, cut_in, cut_out, gap_after
P = [
 ('c1',  (217.7, 219.6), 218.12, 219.26, 218.00, 219.38, 0.35),   # So back to Justin's tweet.
 ('c2',  (219.7, 221.9), 219.95, 221.75, 219.85, 221.85, 0.35),   # The first idea was to use a hash.
 ('c3',  (222.2, 226.1), 222.52, 226.01, 222.42, 226.10, 0.30),   # Justin is super smart. So if he likes a hash, we like a hash.
 ('c4',  (226.1, 227.6), 226.46, 227.56, 226.36, 227.64, 0.30),   # And hashing is super simple.
 ('c5',  (227.7, 228.7), 227.88, 228.66, 227.78, 228.76, 0.25),   # So here's the idea.
 ('c6a', (228.7, 230.5), 229.01, 230.44, 228.91, 230.52, 0.55),   # Create a bunch of one-time secrets,
 ('c6b', (230.5, 232.9), 230.65, 232.83, 230.58, 232.92, 1.60),   # hash each of them, and store the hashes in a vault.   (cascade runs through the gap)
 ('c7a', (233.0, 234.9), 233.24, 234.93, 233.10, 235.00, 0.30),   # To spend, reveal one of the secrets.
 ('c7b', (234.9, 236.8), 235.11, 236.57, 235.03, 236.66, 0.25),   # If it matches the vault, lets you in.
 ('c8',  (236.8, 238.2), 237.05, 238.22, 236.95, 238.30, 1.00),   # Cross that one off the list.   (X, coin bounces back in the gap)
 ('c9',  (238.3, 239.5), 238.49, 239.31, 238.40, 239.40, 0.60),   # Pretty simple, right?
 ('c10', (239.9, 243.8), 240.22, 243.61, 240.10, 243.68, 0.30),   # Yeah, keeping track of a thousand one-time passwords is pretty annoying.
 ('c11', (243.9, 248.2), 244.16, 247.82, 244.06, 247.90, 2.60),   # But the real pain in the uh wallet is storing all of that data on chain.  (rent tag runs through the gap)
 ('c12', (254.3, 257.0), 254.39, 256.96, 254.29, 257.03, 0.35),   # But that is why we built version two.
 ('c13', (259.1, 264.9), 259.32, 264.79, 259.22, 264.85, 0.40),   # So, what's the standard ... compress data on chain? A Merkle tree, of course.
 ('c14', (265.1, 271.8), 265.43, 271.66, 265.33, 271.70, 1.20),   # Same thousand secrets. Now we commit them as a Merkle root. 33,000 bytes ... becomes 390.
 ('c15', (288.7, 293.4), 288.73, 292.77, 288.65, 292.85, 0.50),   # And now it's time to celebrate. We have our bunker and our funds are safe.
 ('c16a',(293.4, 294.95),293.65, 294.94, 293.55, 295.00, 5.60),   # So let's spend some   (the race runs through the gap)
 ('c16b',(295.2, 297.6), 295.37, 297.57, 295.30, 297.65, 0.45),   # oh crackers, what the flip happened here?
 ('c17', (297.6, 298.9), 297.78, 298.70, 297.70, 298.78, 0.60),   # We just got robbed.
 ('c18', (299.0, 300.75),299.43, 300.97, 299.35, 301.00, 0.50),   # Ah, here's the theoretical problem
 ('c19', (303.3, 309.0), 303.40, 308.73, 303.30, 308.80, 0.60),   # It is super unlikely ... crazy fast block times on Solana.
 ('c20a',(309.2, 312.5), 309.57, 312.22, 309.47, 312.30, 0.40),   # But if an attacker can see our transaction before it lands,
 ('c20b',(312.6, 316.7), 312.74, 316.51, 312.64, 316.58, 0.55),   # and if they actually broke Ed25519,
 ('c20c',(316.9, 322.6), 317.16, 322.09, 317.06, 322.17, 0.60),   # they could copy our secret, swap the destination, pay a bigger fee, and beat our transaction.
 ('c21', (324.2, 326.0), 324.64, 325.72, 324.55, 325.80, 0.55),   # That's a timing attack.
 ('c22', (326.1, 328.6), 326.44, 327.88, 326.35, 327.95, 0.0),    # And it all works as coded.
]
edl, wl = [], {}
t = LEAD; g = 0
for pid, (ta, tb), e0, e1, ci, co, gap in P:
    ws = words(ta, tb); t0, t1 = ws[0][1], ws[-1][2]; k = (e1 - e0) / (t1 - t0)
    mp = lambda x: e0 + (x - t0) * k
    off = t - ci; n = round((co - ci) * 30)
    edl.append({'id': pid, 'src_in': ci, 'src_out': co, 'out_in': round(t, 3), 'out_out': round(t + co - ci, 3), 'speech': [round(e0 + off, 3), round(e1 + off, 3)], 'frames': n, 'frame0': g})
    wl[pid] = [(w[0], round(mp(w[1]) + off, 3), round(mp(w[2]) + off, 3)) for w in ws]
    g += n; t = t + (co - ci) + gap
total = round(edl[-1]['out_out'] + TAIL, 3)
json.dump({'edl': edl, 'words': wl, 'total': total, 'head_frames': g}, open(out + '/s05-edl.json', 'w'), indent=1)
open(out + '/s05-timing.js', 'w').write('window.S05 = ' + json.dumps({'edl': edl, 'words': wl, 'total': total, 'headFrames': g}) + ';\n')
parts = []
for i, e in enumerate(edl):
    d = int(round(e['out_in'] * 1000)); dur = e['src_out'] - e['src_in']
    parts.append(f"[0:a]atrim=start={e['src_in']}:end={e['src_out']},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={dur-0.02:.3f}:d=0.02,adelay={d}|{d}[a{i}]")
parts.append(f"anullsrc=r=48000:cl=mono,atrim=0:{total},asetpts=PTS-STARTPTS[base]")
parts.append('[base]' + ''.join(f'[a{i}]' for i in range(len(edl))) + f"amix=inputs={len(edl)+1}:normalize=0:duration=longest,pan=mono|c0=c0,apad=whole_dur={total},atrim=0:{total},asetpts=PTS-STARTPTS[mix]")
open(out + '/s05-audio.filter', 'w').write(';\n'.join(parts) + '\n')
print('total', total, 'head frames', g)
for e in edl: print(e['id'], e['out_in'], e['out_out'], e['speech'])
for k, v in wl.items(): print(k, ' '.join(f"{w}@{s:.2f}" for w, s, _ in v))
