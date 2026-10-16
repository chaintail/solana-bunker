#!/usr/bin/env python3
"""Scene 8 v5 score checks, by waveform (dev-mac, from ~/video-work/solana-bunker/s08, system python):
  python3 film/pipeline/s08/score-check.py [--score film/audio/s08/score.wav] [--voice out/voice-ln.wav] [--final out/audio-final.wav]
1. every marker has an onset in the score: the level jump (RMS of the next 8 ms over the 10 ms before, with a 2 ms gap) nearest the marker in +-20 ms (local
   maxima of at least 3 dB). LEVEL_COMPLETE is checked on the jingle note that lands on it. v8 bar: the onset within MAX_MS (10 ms) of the marker and the jump
   at least MIN_DB (6 dB), so every hit reads over the tail before it (v5-v7: 20 ms and 3 dB). v8 also checks the jingle's held chord against the table stop.
2. the voice is never masked: in every 200 ms window (50 ms hop) where the loudnormed voice is active (RMS >= -30 dBFS) the score is at least 15 dB under it.
3. levels: score RMS per section where someone speaks, sting peaks, the score's peak; the final mix's peak and the score's offset in it (cross-correlation over the tag)."""
import sys, os, json, argparse, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); FILM = os.path.dirname(os.path.dirname(HERE))
ap = argparse.ArgumentParser(); ap.add_argument('--edl', default=os.path.join(FILM, 'data/s08-edl.js')); ap.add_argument('--score', default=os.path.join(FILM, 'audio/s08/score.wav'))
ap.add_argument('--voice', default='out/voice-ln.wav'); ap.add_argument('--final'); ap.add_argument('--events', default='out/score-events.json'); A = ap.parse_args()
src = open(A.edl).read(); D = json.loads(src[src.index('{'):src.rindex('}') + 1]); TOTAL = D['total']
def rd(p):
    w = wave.open(p); ch = w.getnchannels(); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float) / 32768; return x.reshape(-1, ch).mean(1), w.getframerate()
def db(v): return 20 * np.log10(max(float(v), 1e-9))
def rms(x, sr, a, b): s = x[max(0, int(round(a * sr))):max(0, int(round(b * sr)))]; return np.sqrt((s ** 2).mean()) if len(s) else 0.0
s, ssr = rd(A.score); v, vsr = rd(A.voice); ok = True; MIN_DB, MAX_MS = 6.0, 10.0
ev = {e['marker']: e for e in json.load(open(A.events))['events']} if os.path.exists(A.events) else {}
print('1. markers (score onset - marker, ms; level jump dB)')
worst = 0
for m in D['markers']:
    t = ev.get(m['id'], {}).get('event', m['t']) if m['id'] == 'SFX_LEVEL_COMPLETE' else m['t']
    taus = np.arange(t - .02, t + .0201, .0005); J = np.array([db(rms(s, ssr, u, u + .008)) - db(rms(s, ssr, u - .012, u - .002)) for u in taus])
    pk = [i for i in range(1, len(J) - 1) if J[i] >= 3 and J[i] >= J[i - 1] and J[i] >= J[i + 1]]   # onsets: local maxima of the jump, >= 3 dB (not at the window edge)
    i = min(pk, key=lambda i: abs(taus[i] - t)) if pk else int(np.argmax(J)); best = (taus[i], J[i])   # the onset nearest the marker
    d = (best[0] - m['t']) * 1000; good = best[1] >= MIN_DB and abs(d) <= MAX_MS; ok &= good; worst = max(worst, abs(d))
    print('  %-20s %6.2f s  %+6.1f ms  %+5.1f dB %s' % (m['id'], m['t'], d, best[1], '' if good else '  FAIL'))
print('  worst offset %.1f ms' % worst)
lc = ev.get('SFX_LEVEL_COMPLETE', {})
if 'chord' in lc:   # v8: the held chord (after the 7-note arpeggio) lands as the proof table stops (T.proof)
    t = lc['chord']; taus = np.arange(t - .02, t + .0201, .0005); J = np.array([db(rms(s, ssr, u, u + .008)) - db(rms(s, ssr, u - .012, u - .002)) for u in taus])
    i = int(np.argmax(J)); d = (taus[i] - D['T']['proof']) * 1000; good = abs(d) <= MAX_MS; ok &= good
    print('  %-20s %6.2f s  %+6.1f ms  %+5.1f dB %s  (jingle chord vs T.proof, the table stops)' % ('JINGLE_CHORD', D['T']['proof'], d, J[i], '' if good else '  FAIL'))
print('2. masking (200 ms windows, 50 ms hop, voice active >= -30 dBFS): score must be >= 15 dB under the voice')
h = np.arange(0, TOTAL - .2 + 1e-9, .05); vw = np.array([db(rms(v, vsr, a, a + .2)) for a in h]); sw = np.array([db(rms(s, ssr, a, a + .2)) for a in h])
act = vw >= -30; mg = (vw - sw)[act]
print('  %d active windows, margin min %.1f dB, median %.1f dB, %d under 15 dB' % (act.sum(), mg.min(), np.median(mg), (mg < 15).sum()))
for a in h[act][mg < 15]: print('    window %.2f-%.2f s: voice %.1f, score %.1f' % (a, a + .2, vw[h == a][0], sw[h == a][0]))
ok &= bool((mg >= 15).all())
h2 = np.arange(0, TOTAL - .2 + 1e-9, .2); v2 = np.array([db(rms(v, vsr, a, a + .2)) for a in h2]); s2 = np.array([db(rms(s, ssr, a, a + .2)) for a in h2]); a2 = v2 >= -30
print('  (non-overlapping 200 ms grid: %d active windows, margin min %.1f dB)' % (a2.sum(), (v2 - s2)[a2].min()))
print('3. levels')
print('  score peak %.1f dBFS, score RMS over the whole scene %.1f dBFS' % (db(np.abs(s).max()), db(np.sqrt((s ** 2).mean()))))
speech = [(e['out_in'], e['out_out']) for e in D['edl']]
if os.path.exists(A.events):
    for sec in json.load(open(A.events))['sections']:
        segs = [(max(a, sec['t0']), min(b, sec['t1'])) for a, b in speech if min(b, sec['t1']) > max(a, sec['t0'])]
        if segs:
            e2 = sum(rms(s, ssr, a, b) ** 2 * (b - a) for a, b in segs) / sum(b - a for a, b in segs)
            print('  %-13s score RMS while someone speaks %.1f dBFS (%.1f s of speech); voice RMS there %.1f dBFS' % (sec['section'], db(np.sqrt(e2)), sum(b - a for a, b in segs),
                  db(np.sqrt(sum(rms(v, vsr, a, b) ** 2 * (b - a) for a, b in segs) / sum(b - a for a, b in segs)))))
for name, a, b in [('silence under the sigh', D['T']['sigh'] - .06, D['T']['sighEnd']), ('C1 "Not really cool"', D['edl'][6]['out_in'], D['edl'][6]['out_out'])]:
    print('  %-24s score RMS %.1f dBFS, voice %.1f dBFS' % (name, db(rms(s, ssr, a, b)), db(rms(v, vsr, a, b))))
if A.final:
    f, fsr = rd(A.final); t0 = D['T']['tag']; tt = np.arange(t0, TOTAL - .1, 1 / 4000)
    fs = np.interp(tt, np.arange(len(f)) / fsr, f); ss = np.interp(tt, np.arange(len(s)) / ssr, s)
    lags = np.arange(-120, 121); c = [np.dot(fs[120:-120], np.roll(ss, k)[120:-120]) for k in lags]
    print('  final mix: peak %.2f dBFS; score offset in the mix %+.2f ms (cross-correlation over the tag)' % (db(np.abs(f).max()), lags[int(np.argmax(c))] / 4))
print('ALL OK' if ok else 'CHECK FAILED'); sys.exit(0 if ok else 1)
