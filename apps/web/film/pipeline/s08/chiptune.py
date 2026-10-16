#!/usr/bin/env python3
"""Scene 8: a small 8-bit tracker, synthesised from scratch (NES-like palette: pulse 12.5 / 25 / 50 / 75 % duty, 4-bit triangle, 15-bit LFSR noise in long and
short mode; 44.1 kHz mono 16 bit; numpy only, no samples, deterministic). score.py builds the whole scene's score with it; v4's tag cues are patterns here too.
usage (dev-mac, system python): python3 film/pipeline/s08/chiptune.py [outdir=film/audio/s08]   -> the four v4 tag cues (bit-identical to v4):
  jingle.wav  ~2.1 s level-complete success: rising C major arpeggio, two square voices (50 % and 25 % duty) + triangle bass, held chord; peak -12 dBFS
  bed.wav     8 bars at 124 BPM (15.48 s, seamless loop): C  Am  F  G  C  Am  F  G, thin 12.5 % square lead, triangle bass, noise hat; RMS -30 dBFS
  coin.wav    1-up / coin blip (B5 -> E6 square); peak -18 dBFS
  tick.wav    soft score tick (30 ms square, fast decay); peak -18 dBFS
Every file has 20 ms fades at both ends. Levels are absolute: build.sh mixes the score after the speech loudnorm (it is not renormalised).

Tracker. A Pattern has a step length (bpm + steps per beat, or seconds) and tracks; a track is (instrument, token string, mix weight). Tokens, one per step,
whitespace separated ('|' is a bar line and is ignored):
  C5  F#4  Bb3   note (midi 60 = C4)            N7  noise, long mode, period index 0-15 (0 = brightest)     M7  noise, short (metallic) mode
  .   hold the previous note one more step       -   rest       <   step back one step (the next note overlaps the previous one)
  {name}         switch the track's instrument (no step)
suffixes on a note: ^047 arpeggio (semitone offsets 0-9 a=10 b=11 c=12, cycled at the instrument's arp rate, 60 Hz like the NES frame)
  >G4 / >N12 slide to that pitch over the note    ~ vibrato (instrument's vib, default 6 Hz +-0.25 st after 80 ms)    @0.5 volume    =1.35 length in seconds
An instrument is a dict: wave ('sq' pulse / 'tri' / 'noise' / 'hat' = v4's 1-bit hat), duty, vol, gate (fraction of the step length that sounds),
ADSR a/d/s/r (attack, exponential decay to sustain, release inside the note), vib (rate Hz, depth st, delay s), arp (Hz), v4 (True: v4's constant-pitch
note with the pulse's DC left in, for the tag cues; otherwise pulses are AC-coupled like the console's output)."""
import sys, os, re, wave, numpy as np
SR = 44100
def hz(n): return 440.0 * 2 ** ((n - 69) / 12)          # midi note -> Hz
NAMES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
def midi(name):
    """'C4' -> 60, 'F#3' -> 54, 'Bb2' -> 46"""
    m = re.fullmatch(r'([A-G])([#b]?)(-?\d)', name)
    if not m: raise ValueError(name)
    return 12 * (int(m.group(3)) + 1) + NAMES[m.group(1)] + {'#': 1, 'b': -1, '': 0}[m.group(2)]
def osc(kind, f, n, duty=.5):
    ph = (np.arange(n) * f / SR) % 1.0
    if kind == 'sq': return np.where(ph < duty, 1.0, -1.0)
    if kind == 'tri': return np.round((4 * np.abs(ph - .5) - 1) * 15) / 15      # 4-bit triangle, like the real thing
    raise ValueError(kind)
def env(n, a=.004, d=.08, s=.6, r=.05, hold=None):
    """attack / decay-to-sustain / release envelope over n samples (release inside the note)"""
    t = np.arange(n) / SR; T = n / SR; e = np.minimum(1, t / a) * (s + (1 - s) * np.exp(-t / d)); rr = min(r, T)
    return e * np.clip((T - t) / rr, 0, 1)
def note(buf, t0, dur, midi, kind='sq', duty=.5, vol=1.0, **kw):
    i0 = int(round(t0 * SR)); n = int(round(dur * SR)); n = min(n, len(buf) - i0)
    if n <= 0: return
    buf[i0:i0 + n] += vol * osc(kind, hz(midi), n, duty) * env(n, **kw)
def fades(x, ms=20):
    k = int(SR * ms / 1000); x[:k] *= np.linspace(0, 1, k); x[-k:] *= np.linspace(1, 0, k); return x
def peak_to(x, dbfs): return x * (10 ** (dbfs / 20) / np.abs(x).max())
def rms_to(x, dbfs): return x * (10 ** (dbfs / 20) / np.sqrt((x ** 2).mean()))
def db(v): return 20 * np.log10(max(float(v), 1e-12))
def save(path, x):
    with wave.open(path, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())
    print('%-28s %.3f s  peak %.1f dBFS  rms %.1f dBFS' % (os.path.basename(path), len(x) / SR, 20 * np.log10(np.abs(x).max()), 20 * np.log10(np.sqrt((x ** 2).mean()))))
def noise_hat(buf, t0, dur=.035, vol=1.0, rng=None):
    i0 = int(round(t0 * SR)); n = int(dur * SR); n = min(n, len(buf) - i0)
    if n <= 0: return
    z = rng.choice([-1.0, 1.0], n); z = np.diff(np.concatenate([[0], z])) / 2          # differenced white noise = bright 1-bit hat
    buf[i0:i0 + n] += vol * z * np.exp(-np.arange(n) / (SR * .008))

# ---- NES noise: 15-bit LFSR clocked at CPU / period; long mode taps bits 0^1 (32767 steps), short mode bits 0^6 (93 steps, metallic)
CPU = 1789773
NOISE_PERIODS = [4, 8, 16, 32, 64, 96, 128, 160, 202, 254, 380, 508, 762, 1016, 2034, 4068]
_LFSR = {}
def lfsr(short):
    if short not in _LFSR:
        r = 1; out = []; tap = 6 if short else 1
        for _ in range(93 if short else 32767):
            out.append(1.0 if r & 1 == 0 else -1.0); fb = (r ^ (r >> tap)) & 1; r = (r >> 1) | (fb << 14)
        _LFSR[short] = np.array(out)
    return _LFSR[short]

# ---- the general voice: per-sample pitch (arpeggio, slide, vibrato), phase accumulated so pitch moves are click free
DEF = dict(wave='sq', duty=.5, vol=1.0, gate=1.0, a=.004, d=.08, s=.6, r=.05, vib=(6.0, .25, .08), arp=60.0, v4=False)
def inst(**kw):
    d = dict(DEF); d.update(kw); return d
def voice(buf, t0, dur, ins, pitch, arp=None, slide=None, vib=False, vol=1.0, rng=None):
    """one note of an instrument into buf. pitch: midi number, or ('N'|'M', period index) for noise. slide: target pitch (same kind)."""
    w = ins['wave']
    if w == 'hat': return noise_hat(buf, t0, vol=ins['vol'] * vol, rng=rng)
    if ins['v4']:                                 # v4 path (constant pitch, pulse with its DC), sample-exact with v4's cues
        return note(buf, t0, dur, pitch, w, ins['duty'] if w == 'sq' else 1, ins['vol'] * vol, a=ins['a'], d=ins['d'], s=ins['s'], r=ins['r'])
    i0 = int(round(t0 * SR)); n = int(round(dur * SR)); n = min(n, len(buf) - i0)
    if n <= 0: return
    t = np.arange(n) / SR; u = t / (n / SR)
    if w == 'noise':
        mode, p0 = pitch; p1 = slide[1] if slide else p0
        idx = np.clip(np.round(p0 + (p1 - p0) * u).astype(int), 0, 15)
        rate = CPU / np.array(NOISE_PERIODS, float)[idx]
        seq = lfsr(mode == 'M'); pos = np.floor(np.cumsum(rate / SR)).astype(np.int64) % len(seq)
        x = seq[pos]
    else:
        semi = np.full(n, float(pitch))
        if slide is not None: semi += (slide - pitch) * u
        if arp: semi += np.array(arp, float)[np.floor(t * ins['arp']).astype(int) % len(arp)]
        if vib:
            rate, depth, delay = ins['vib']; semi += depth * np.sin(2 * np.pi * rate * np.maximum(0, t - delay)) * (t > delay)
        ph = np.concatenate([[0.0], np.cumsum(hz(semi) / SR)[:-1]]) % 1.0
        x = np.where(ph < ins['duty'], 1.0, -1.0) - (2 * ins['duty'] - 1) if w == 'sq' else np.round((4 * np.abs(ph - .5) - 1) * 15) / 15   # pulse AC-coupled (no DC), as after the console's output high-pass
    buf[i0:i0 + n] += ins['vol'] * vol * x * env(n, a=ins['a'], d=ins['d'], s=ins['s'], r=ins['r'])

TOK = re.compile(r'^([A-G][#b]?-?\d|[NM]\d+)(.*)$')
SUF = re.compile(r'\^([0-9a-c]+)|>([A-G][#b]?-?\d|[NM]\d+)|(~)|@([0-9.]+)|=([0-9.]+)')
def pitch_of(s): return (s[0], int(s[1:])) if s[0] in 'NM' else midi(s)
def parse(text, instruments, ins0):
    """token string -> events [step, n_steps, instrument, pitch, fx dict]"""
    ev = []; step = 0; ins = ins0
    for tok in text.split():
        if tok == '|': continue
        if tok.startswith('{'): ins = instruments[tok.strip('{}')]; continue
        if tok == '.':
            if ev and ev[-1][0] + ev[-1][1] == step: ev[-1][1] += 1
            step += 1; continue
        if tok == '-': step += 1; continue
        if tok == '<': step -= 1; continue
        m = TOK.match(tok)
        if not m: raise ValueError(tok)
        fx = {}
        for a in SUF.finditer(m.group(2)):
            if a.group(1): fx['arp'] = [int(c, 16) for c in a.group(1)]
            if a.group(2): fx['slide'] = pitch_of(a.group(2))
            if a.group(3): fx['vib'] = True
            if a.group(4): fx['vol'] = float(a.group(4))
            if a.group(5): fx['len'] = float(a.group(5))
        if ''.join(a.group(0) for a in SUF.finditer(m.group(2))) != m.group(2): raise ValueError('bad suffix ' + tok)
        ev.append([step, 1, ins, pitch_of(m.group(1)), fx]); step += 1
    return ev, step
class Pattern:
    """tracks: list of (instrument, token string, mix weight). step = seconds per step, or bpm + spb (steps per beat)."""
    def __init__(self, tracks, step=None, bpm=None, spb=4, instruments=None, seed=8):
        self.step = step if step is not None else 60.0 / bpm / spb
        self.instruments = instruments or {}; self.seed = seed
        self.tracks = []
        for ins, text, wgt in tracks:
            ev, n = parse(text, self.instruments, ins); self.tracks.append((ev, wgt))
        self.length = max(max(e[0] * self.step + e[4].get('len', e[1] * self.step) for e in ev) if ev else 0 for ev, _ in self.tracks)   # '=' lengths count
    def render(self, buf, t0=0.0, loops=1, until=None, gain=1.0):
        """add the pattern into buf from t0 (seconds), looped; notes that start at or after `until` are dropped, notes running past it are cut there"""
        rng = np.random.default_rng(self.seed); L = self.length
        for ev, wgt in self.tracks:
            tmp = np.zeros(len(buf))
            for k in range(loops):
                for st, ns, ins, p, fx in ev:
                    t = t0 + k * L + st * self.step
                    if until is not None and t >= until - 1e-9: continue
                    dur = fx.get('len', ns * self.step * ins['gate'])
                    if until is not None: dur = min(dur, until - t)
                    voice(tmp, t, dur, ins, p, fx.get('arp'), fx.get('slide'), fx.get('vib', False), fx.get('vol', 1.0), rng)
            buf += tmp * wgt * gain
        return buf
def cue(pattern, length, level, fade_ms=20):
    """render a pattern alone into its own buffer of `length` s, with fades and an absolute level: ('peak', dBFS) or ('rms', dBFS)"""
    x = pattern.render(np.zeros(int(round(length * SR)))); x = fades(x, fade_ms)
    return peak_to(x, level[1]) if level[0] == 'peak' else rms_to(x, level[1])

# ---- v4's tag cues as patterns (bit-identical to the v4 wavs)
def jingle(hold=1.35, length=2.1):
    """v4: hold 1.35 s, 2.1 s buffer. v7 passes a shorter hold; the buffer then ends 50 ms after the bass (release inside the note, so nothing is cut)"""
    st = .085   # one arpeggio note = 2 steps of 42.5 ms, the harmony enters half a note late
    I = dict(lead=inst(v4=True, wave='sq', duty=.5, vol=1, gate=.95, a=.002, d=.1, s=.8, r=.01), harm=inst(v4=True, wave='sq', duty=.25, vol=.7, gate=.95, a=.002, d=.1, s=.8, r=.01),
             bass=inst(v4=True, wave='tri', vol=1, a=.002, d=1, s=1, r=.01), leadH=inst(v4=True, wave='sq', duty=.5, vol=1, a=.002, d=.5, s=.35, r=.35),
             harmH=inst(v4=True, wave='sq', duty=.25, vol=.8, a=.002, d=.5, s=.35, r=.35), bassH=inst(v4=True, wave='tri', vol=1, a=.002, d=.8, s=.7, r=.4))
    p = Pattern([(I['lead'], 'C5 . E5 . G5 . C6 . G5 . C6 . E6 . {leadH} E6=%g' % hold, .5),                 # voice 1: 50 % square, C5 E5 G5 C6 G5 C6 E6, held E6
                 (I['harm'], '- G4 . B4 . D5 . G5 . D5 . G5 . B5 . < {harmH} C6=%g' % hold, .38),             # voice 2: 25 % square a fourth below, half a step late; held C6
                 (I['bass'], 'C2 . E2 . G2 . C3 . G2 . C3 . E3 . {bassH} C3=%g' % (hold + .05), .6)],               # triangle two octaves down; held C3
                step=st / 2, instruments=I)
    return cue(p, length if hold == 1.35 else p.length + .05, ('peak', -12))
def bed():
    BPM = 124; I = dict(bass=inst(v4=True, wave='tri', vol=1, gate=.9, a=.003, d=1, s=1, r=.02), lead=inst(v4=True, wave='sq', duty=.125, vol=1, gate=.8, a=.002, d=.06, s=.35, r=.03),
                        hat=inst(v4=True, wave='hat', vol=.7))
    lead = '| C4 E4 G4 - C4 E4 G4 - | A3 C4 E4 - A3 C4 E4 - | A3 C4 F4 - A3 C4 F4 - | G3 B3 D4 - G3 B3 D4 - ' \
           '| C4 E4 G4 E5 C4 E4 G4 E5 | A3 C4 E4 C5 A3 C4 E4 C5 | A3 C4 F4 C5 A3 C4 F4 C5 | G3 B3 D4 B4 G3 B3 D4 B4'      # thin 12.5 % eighth arpeggio, octave pops in bars 5-8
    bass = ' '.join(['| C2 - G2 - C2 - G2 -', '| A1 - E2 - A1 - E2 -', '| F1 - C2 - F1 - C2 -', '| G1 - D2 - G1 - D2 -'] * 2)   # root on 1 and 3, fifth on 2 and 4
    hat = ' '.join(['- N0 - N0 - N0 - N0'] * 8)                                                                       # off-beat hat
    p = Pattern([(I['bass'], bass, .5), (I['lead'], lead, .22), (I['hat'], hat, .08)], bpm=BPM, spb=2, instruments=I)
    x = cue(p, 8 * 4 * 60 / BPM, ('rms', -30)); assert np.abs(x).max() < 10 ** (-12 / 20); return x
def coin():
    I = inst(v4=True, wave='sq', duty=.5, a=.001, d=1, s=1, r=.005); J = inst(v4=True, wave='sq', duty=.5, a=.001, d=.12, s=.25, r=.2)
    return cue(Pattern([(I, 'B5=.075 {J} E6=.34', 1)], step=.075, instruments=dict(J=J)), .42, ('peak', -18))   # B5, E6
def tick():
    return cue(Pattern([(inst(v4=True, wave='sq', duty=.5, a=.001, d=.01, s=.1, r=.006), 'G6=.03', 1)], step=.03), .03, ('peak', -18), fade_ms=5)   # G6, 30 ms
if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'film/audio/s08'; os.makedirs(out, exist_ok=True)
    for name, fn in (('jingle', jingle), ('bed', bed), ('coin', coin), ('tick', tick)): save(os.path.join(out, name + '.wav'), fn())
