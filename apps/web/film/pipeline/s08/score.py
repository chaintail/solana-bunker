#!/usr/bin/env python3
"""Scene 8 v5: the whole arcade scene scored with our own chiptune (chiptune.py tracker; Liam 16499). Reads the EDL (data/s08-edl.js: edl rows, word times T,
markers, tag cue times sfx), so a re-time re-renders the score: every section's tempo and bar line come from the markers, every sting starts on its marker.
usage (dev-mac, from ~/video-work/solana-bunker/s08, system python):
  python3 film/pipeline/s08/score.py [--voice out/voice-ln.wav] [--out film/audio/s08/score.wav] [--table]
One key (C major / A minor). Tempo map (beats per minute from the markers, so the bar grid lands on them):
  A attract    LAMPORT_LAND - 2 beats .. SLOT_OPEN    beat = (SLOT_OPEN - LAMPORT_LAND) / 12   (~123.7)  two voices: 12.5 % lead + triangle
  B tension    SLOT_OPEN .. WEDGE                     beat = (GAME_OVER - SLOT_OPEN) / 6       (~117.6)  A pedal 16ths, chromatic creep
  C game over  GAME_OVER, then silence under the sigh
  D workaround TRUCK_1 - 14 beats .. C1 starts        beat = (TRUCK_3 - TRUCK_1) / 4           (~133.3)  2-step: triangle on 1 and 3, chord stabs on 2 and 4
  E rescue     BANNER .. BANNER + 16 beats (= WIN)    beat = (BLOCK_DROP - BANNER) / 13        (~127.0)
  F win        WIN_1 .. CHECK                         beat = (CHECK - WIN_1) / 16              (~125.3)  C Dm Em F-G, then the full chord on CHECK
  tag          v4's cues at the sfx times. v7 (Liam 16702, tag cut to the proof table): the jingle from the tag start (LEVEL_COMPLETE, first note), its
               arpeggio under the table's scroll, the held C major chord as the table lands, ending 0.1 s before the scene (x11); no row ticks
Levels (absolute, mixed after the voice loudnorm like v4): beds -33 dBFS RMS and stings -27 dBFS peak where they sit under speech, stings -12 dBFS peak in the
clear (GAME OVER, INSERT COIN). With --voice (the loudnormed voice alone, build.sh writes it) a dialogue guard then trims the score so that in every 200 ms
window where the voice is active (RMS >= -30 dBFS) the score sits at least GUARD_DB under it (fast attack with 100 ms look-ahead;
release 40 dB/s while the voice is active, 120 dB/s once it stops), and a peak guard keeps voice + score under 0.85 on the loudest syllables, so the
final mix peaks where v4 did.
Writes score.wav (44.1 kHz mono 16 bit, scene length) and out/score-events.json (marker -> event onset, sections, levels) for score-check.py."""
import sys, os, json, argparse, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chiptune as C
from chiptune import SR, inst, Pattern
FILM = os.path.dirname(os.path.dirname(HERE))
BED_UNDER, STING_UNDER, STING_CLEAR, GUARD_DB, VOICE_ACTIVE, REL_SPEECH, REL_FREE = -33.0, -27.0, -12.0, 16.0, -30.0, 40.0, 120.0
PEAK_SUM = .85   # voice + score sample peak ceiling. The voice alone peaks at 0.842 (-1.5 dBTP loudnorm); build.sh's alimiter (limit 0.95, auto level) adds
                 # +0.46 dB make-up, so the final mix peaks about where v4 did (-1.0 dBFS) and the limiter never limits

ap = argparse.ArgumentParser(); ap.add_argument('--edl', default=os.path.join(FILM, 'data/s08-edl.js')); ap.add_argument('--out', default=os.path.join(FILM, 'audio/s08/score.wav'))
ap.add_argument('--voice'); ap.add_argument('--events', default='out/score-events.json'); ap.add_argument('--table', action='store_true'); A = ap.parse_args()
src = open(A.edl).read(); D = json.loads(src[src.index('{'):src.rindex('}') + 1])
T, M, TOTAL = D['T'], {m['id']: m['t'] for m in D['markers']}, D['total']
SPEECH = [(e['out_in'], e['out_out']) for e in D['edl']]
N = int(round(TOTAL * SR)); score = np.zeros(N); beds = np.zeros(N); bed_gain = np.ones(N); EVENTS = []; SECTIONS = []

def overlap(t0, t1): return sum(max(0, min(t1, b) - max(t0, a)) for a, b in SPEECH) / max(t1 - t0, 1e-9)
def place(x, t, buf=None):
    buf = score if buf is None else buf; i0 = int(round(t * SR)); n = min(len(x), N - i0); buf[i0:i0 + n] += x[:n]
def duck(t0, t1, db=-6.0, ramp=.02):
    """the beds step aside (db) while a sting plays, so the sting reads without being louder"""
    i = np.arange(max(0, int((t0 - ramp) * SR)), min(N, int((t1 + ramp) * SR))); tt = i / SR
    w = np.clip(np.minimum((tt - (t0 - ramp)) / ramp, ((t1 + ramp) - tt) / ramp), 0, 1); bed_gain[i] = np.minimum(bed_gain[i], 10 ** (db * w / 20))
class Grid:
    """a section's bar grid: bar 1 beat 1 at `t1`, 4 beats a bar"""
    def __init__(self, name, t1, beat, start): self.name, self.t1, self.beat, self.start = name, t1, beat, start
    def at(self, t):
        b = (t - self.t1) / self.beat; bar = int(np.floor(b / 4)); return '%s %d:%.2f' % (self.name, bar + 1, b - 4 * bar + 1)
GRIDS = []
def grid_of(t):
    g = [x for x in GRIDS if x.start <= t + 1e-6] or GRIDS[:1]; return g[-1]   # the section running at t (or the last one that ran)
def sting(marker, p, desc, t=None, level=None, length=None, offset=0.0, step_down=None):
    """render pattern p alone at a peak level and place it so that its event (offset s into the pattern) lands on the marker.
    step_down=(t, dB): the sting itself steps down by dB from t on (20 ms ramp ending 12 ms before t), so a sting starting at t reads over its tail"""
    tm = M[marker] if t is None else t; t0 = tm - offset; L = length or p.length + .25
    lev = level if level is not None else (STING_UNDER if overlap(t0, t0 + p.length) >= .2 else STING_CLEAR)   # in the clear = under 20 % of its notes under speech
    x = C.cue(p, L, ('peak', lev), fade_ms=3)
    if step_down:
        ts, sdb = step_down; tt = t0 + np.arange(len(x)) / SR; x = x * 10 ** (sdb * np.clip((tt - (ts - .032)) / .02, 0, 1) / 20)
    place(x, t0); duck(tm, t0 + p.length)
    EVENTS.append(dict(marker=marker, t=M.get(marker, tm), event=round(tm, 4), level='peak %.0f' % lev, what=desc))
def bed(name, p, t0, t1, desc, level=BED_UNDER, grid=None):
    """a looped pattern from t0 to t1, RMS-normalised over its span, 30 ms fade at the cut"""
    n = int(round((t1 - t0) * SR)); x = p.render(np.zeros(n + int(.3 * SR)), 0.0, loops=int(np.ceil((t1 - t0) / p.length)) + 1, until=t1 - t0)
    x = C.fades(x[:n], 30); x = C.rms_to(x, level); place(x, t0, beds)
    SECTIONS.append(dict(section=name, t0=round(t0, 3), t1=round(t1, 3), bpm=round(60 / grid.beat, 1) if grid else None, rms=level, what=desc))

# ---------------- instruments (NES palette)
I = dict(
  lead12=inst(duty=.125, gate=.8, a=.002, d=.06, s=.35, r=.03), lead25=inst(duty=.25, gate=.85, a=.002, d=.08, s=.5, r=.03),
  sq50=inst(duty=.5, gate=.9, a=.002, d=.1, s=.6, r=.03), blip=inst(duty=.125, gate=.75, a=.001, d=.03, s=.25, r=.008),
  blip25=inst(duty=.25, gate=.8, a=.001, d=.05, s=.3, r=.01), blip50=inst(duty=.5, gate=.8, a=.001, d=.04, s=.3, r=.008), tri=inst(wave='tri', gate=.9, a=.003, d=1, s=1, r=.02),
  triS=inst(wave='tri', gate=.8, a=.003, d=.35, s=.7, r=.04), kick=inst(wave='tri', gate=1, a=.001, d=.08, s=0, r=.02),
  hat=inst(wave='hat', vol=.7), snare=inst(wave='noise', gate=1, a=.001, d=.045, s=0, r=.01), boom=inst(wave='noise', gate=1, a=.001, d=.22, s=.05, r=.12),
  grit=inst(wave='noise', gate=.7, a=.001, d=.02, s=.4, r=.005), hold50=inst(duty=.5, gate=1, a=.002, d=.25, s=.45, r=.15, vib=(6.0, .3, .12)),
  hold25=inst(duty=.25, gate=1, a=.002, d=.25, s=.45, r=.15, vib=(6.0, .3, .12)), whistle=inst(duty=.125, gate=1, a=.01, d=1, s=1, r=.01),
  rasp=inst(duty=.125, gate=1, a=.003, d=.3, s=.7, r=.06, vib=(28.0, 1.2, 0.0)), rasp2=inst(duty=.25, gate=1, a=.003, d=.3, s=.6, r=.06, vib=(23.0, 1.0, 0.0)),
  putt=inst(duty=.125, gate=.55, a=.001, d=.025, s=.3, r=.01), chord=inst(duty=.125, gate=.6, a=.001, d=.06, s=.4, r=.02, arp=60.0))
def P(tracks, **kw): return Pattern(tracks, instruments=I, **kw)

# ---------------- A: attract mode (under the load, E1-E2, on to the slot)
bA = (M['SFX_SLOT_OPEN'] - M['SFX_LAMPORT_LAND']) / 12; gA = Grid('A', M['SFX_LAMPORT_LAND'], bA, M['SFX_LAMPORT_LAND'] - 2 * bA); GRIDS.append(gA); tA = gA.start
pA = P([(I['lead12'], '| G4 A4 B4 D5 | C5 - E5 G5 C6 - G5 E5 | A4 - C5 E5 A5 - E5 C5 | F4 - A4 C5 G4 - B4 D5', .6),
        (I['tri'], '| - - G2 - | C3 - G2 - C3 - G2 - | A2 - E2 - A2 - E2 - | F2 - C3 - G2 - D3 -', .5)], bpm=60 / bA, spb=2)
bed('A attract', pA, tA, M['SFX_SLOT_OPEN'], 'attract mode, two voices (12.5 % lead arpeggio-melody, triangle root-fifth): pickup, C | Am | F G', grid=gA)
pLand = lambda pre, w, th, nz, v: P([(I['whistle'], '%s=%.3f' % (w, pre - .05), .25 * v), (I['kick'], '- ' + th, 1.0), (I['boom'], '- ' + nz, .6 * v)], step=pre)   # whistle stops 50 ms before the land
pre = M['SFX_LAMPORT_LAND'] - T['xmss']
sting('SFX_LAMPORT_LAND', pLand(pre, 'C7>C5', 'C3>C1=.28', 'N9>N14=.24', 1.0), 'falling whistle from "XMSS", triangle thud C3 to C1 + low noise', offset=pre)
pre = M['SFX_XMSS_LAND'] - T['awesome']
sting('SFX_XMSS_LAND', P([(I['whistle'], 'G7>G6=%.3f' % (pre - .05), .08), (I['sq50'], '- G5>G4=.06', 1.0), (I['snare'], '- N1=.02', .5)], step=pre),
      'tiny: short whistle, then a "tink" (50 % square G5 to G4, 60 ms) + noise click', offset=pre)
sting('SFX_EXPLODE', P([(I['boom'], 'N3>N13=.65', 1.0), (I['kick'], 'C3>C1=.3', .8), (I['sq50'], 'G3>C2=.22', .25)], step=.65),
      'explosion: long-mode noise burst sweeping down (period 3 to 13), triangle drop, square growl; steps down 9 dB for the score tick', level=STING_UNDER - 2,
      step_down=(M['SFX_SCORE_TICK'], -9.0))   # x11: the tick starts 91 ms into the burst (1x: 100 ms) and only read +2.4 dB over it
tones = ['G4', 'C5', 'E5', 'G5', 'C6', 'E6', 'G6', 'C7', 'E7', 'G7']
sting('SFX_SCORE_TICK', P([(I['blip50'], ' '.join(tones[1 + k // 3 + k % 3] for k in range(21)), 1.0)], step=.7 / 21),
      'score tick-up: 21 square blips (one per counter step, 1/30 s), rolling C major arpeggio C5 to G7')

# ---------------- B: tension (slot opens, block hops, wedges)
bB = (M['SFX_GAME_OVER'] - M['SFX_SLOT_OPEN']) / 6; gB = Grid('B', M['SFX_SLOT_OPEN'], bB, M['SFX_SLOT_OPEN']); GRIDS.append(gB)
pB = P([(I['triS'], ' '.join(['A2 A3'] * 12), .5), (I['lead25'], '| E5 . F5 . E5 . F5 . E5 . F5 . F#5 . G5 . | G#5 . A5 . G#5 . A5 .', .35),
        (I['hat'], ' '.join(['- - C4 -'] * 6), .1)], bpm=60 / bB, spb=4)
bed('B tension', pB, M['SFX_SLOT_OPEN'], M['SFX_WEDGE'], 'tension: A minor, triangle octave pedal in 16ths, 25 % lead creeping E-F to G#-A, off-beat hat', grid=gB)
sting('SFX_SLOT_OPEN', P([(I['blip25'], 'G4>D4 E4>B3 C4>G3', 1.0)], step=.1), 'three bricks drop: three falling blips G4, E4, C4')
sting('SFX_BLOCK_HOP', P([(I['blip25'], 'E4>E6=.22', 1.0)], step=.22), 'jump: 25 % square slide E4 up to E6')
pre = M['SFX_WEDGE'] - T['transaction']; k = max(1, int(round(pre / .04))); rest = ' '.join(['-'] * k)   # 40 ms steps, the crunch starts on step k
sting('SFX_WEDGE', P([(I['whistle'], 'E6>E4=%.3f' % pre, .2), (I['grit'], rest + ' M2 N6 M3 N7 M2 N6 M3 N7 M2 N6', .7), (I['sq50'], rest + ' B2=.25', .35),
                      (I['lead25'], rest + ' F3=.25', .3)], step=pre / k),
      'wedge: drop whistle from "transaction", then the crunch: metallic short-mode noise grinding (40 ms), B2 + F3 tritone', offset=pre)

sting('SFX_SAW', P([(I['rasp'], 'E3>A3 A3>E3 E3>A3 A3>E3 E3>A3 A3>E3', .5), (I['grit'], 'N5 N7 N5 N7 N5 N7', .5)], step=.135),
      'saw: three back-and-forth strokes (0.27 s each, with the sprite), buzzing 12.5 % square E3-A3 + noise')
sting('SFX_BREAK', P([(I['snare'], 'M1=.03', 1.0), (I['boom'], 'N4>N10=.25', .6), (I['blip25'], 'C5>C4 A4>A3 F4>F3 D4>D3', .8)], step=.1),
      'the block falls apart: metallic crack + noise, four falling blips, one per chunk')

# ---------------- C: game over, then silence under the sigh
sting('SFX_GAME_OVER', P([(I['sq50'], 'C5 B4 Bb4 {hold50} A4~=.62', .5), (I['lead25'], 'A4 G#4 G4 {hold25} E4~=.62', .35),
                          (I['tri'], 'A2 . . A2>A1=.6', .55), (I['snare'], 'N3', .3)], step=.17),
      'GAME OVER: the minor fall, C5 B4 Bb4 A4 over A4 G#4 G4 E4, held with vibrato; triangle A2 sliding to A1; then nothing until "I guess"')

# ---------------- D: workaround level (plodding 2-step), trucks, the stamp
bD = (M['SFX_TRUCK_3'] - M['SFX_TRUCK_1']) / 4; gD = Grid('D', M['SFX_TRUCK_1'] - 12 * bD, bD, M['SFX_TRUCK_1'] - 14 * bD); GRIDS.append(gD); tD = gD.start
c1 = next(e['out_in'] for e in D['edl'] if e['id'] == 'C1')
two = lambda r, f, ch, ar: ('%s . - - %s . - -' % (r, f), '- - %s^%s - - - %s^%s -' % (ch, ar, ch, ar))
bars = [two('A2', 'E2', 'A3', '037'), two('F2', 'C3', 'F3', '047'), two('G2', 'D3', 'G3', '047'), two('A2', 'E2', 'A3', '037'), two('F2', 'C3', 'F3', '047'), two('G2', 'D3', 'G3', '047')]
pD = P([(I['tri'], 'E2 . - - | ' + ' | '.join(b[0] for b in bars), .55), (I['chord'], '- - E3^037 - | ' + ' | '.join(b[1] for b in bars), .22),
        (I['snare'], '- - N5 - | ' + ' | '.join(['- - N5 - - - N5 -'] * len(bars)), .12)], bpm=60 / bD, spb=2)
bed('D workaround', pD, tD, c1, 'workaround: plodding 2-step, slow triangle on 1 and 3 (Am F G Am F), 12.5 % arpeggiated chord stabs and soft snare on 2 and 4; stops as the lab coat speaks', grid=gD)
for i, n in enumerate(['A3', 'B3', 'C4', 'D4', 'E4']):
    sting('SFX_TRUCK_%d' % (i + 1), P([(I['putt'], '%s %s' % (n, n), 1.0), (I['grit'], 'M9 M9', .5)], step=bD / 4), 'truck %d putt-putt on %s' % (i + 1, n),
          level=STING_UNDER - (2 if i < 3 else 5))
sting('SFX_STAMP', P([(I['rasp'], 'A2>E2~=.32', .6), (I['rasp2'], 'Bb2>F2~=.32', .4), (I['grit'], 'N10=.3', .25)], step=.32), 'thumbs-down raspberry: two low squares a semitone apart, 28 Hz flutter, sliding down')

# ---------------- E: insert coin, rescue (banner, odometer, flip, swaps, block drop)
sting('SFX_INSERT_COIN', P([(I['blip25'], 'G5 C6 - - G5 C6', 1.0)], step=1 / 12), 'INSERT COIN chime: G5-C6 on the first two blinks of the text (6 Hz flash); the third blink is left clear for "Solana" and the coin')
CL = STING_UNDER - 10; p = C.coin(); place(p * 10 ** ((CL + 18) / 20), M['SFX_COIN_DROP'])   # small: 30 ms later the fanfare starts
EVENTS.append(dict(marker='SFX_COIN_DROP', t=M['SFX_COIN_DROP'], event=M['SFX_COIN_DROP'], level='peak %.0f' % CL, what="v4's coin pattern (B5 to E6) as the coin hits the slot"))
bE = (M['SFX_BLOCK_DROP'] - M['SFX_BANNER']) / 13; gE = Grid('E', M['SFX_BANNER'], bE, M['SFX_BANNER']); GRIDS.append(gE)
pE = P([(I['tri'], '| C2 . C3 . C2 . C3 . C2 . C3 . C2 . C3 . | F2 . F3 . F2 . F3 . G2 . G3 . G2 . G3 . | A2 . A3 . A2 . A3 . F2 . F3 . F2 . F3 . '
                   '| G2 . G3 . G2 . G3 . G2 A2 B2 C3 D3 E3 F3 G3', .5),
        (I['lead12'], '| C5 . E5 . G5 . E5 . C5 . E5 . G5 . E5 . | C5 . F5 . A5 . F5 . D5 . G5 . B5 . G5 . | C5 . E5 . A5 . E5 . C5 . F5 . A5 . F5 . '
                      '| D5 . G5 . B5 . G5 . D5 . G5 . B5 . D6 .', .25),
        (I['hat'], ' '.join(['- - C4 -'] * 14), .08), (I['snare'], ' '.join(['-'] * 56) + ' N6@.5 N6@.6 N5@.7 N5@.8 N4@.9 N4 N3 N3', .12)], bpm=60 / bE, spb=4)
tE1 = min(gE.t1 + 16 * bE, D['edl'][-1]['out_in'] - .05)
bed('E rescue', pE, gE.t1, tE1, 'rescue: C | F G | Am F | G, triangle octave bounce, 12.5 % eighth arpeggio, hat; snare roll + triangle run up into the win screen', grid=gE)
sting('SFX_BANNER', P([(I['sq50'], 'G4 C5 E5 G5 . . {hold50} C6~=.6', .5), (I['lead25'], 'E4 G4 C5 E5 . . {hold25} G5~=.6', .3), (I['tri'], 'C3=.6 - - - - - C3=.6', .5), (I['snare'], 'N3 - - - - - N3', .45)], step=bE / 4),
      'banner fanfare: rising G4 C5 E5 G5 to a held C6 (with E, G a third below), triangle C, noise hits')
sting('SFX_NEW', P([(I['blip25'], 'E6 C7', 1.0)], step=bE / 4), 'NEW!: two bright blips E6, C7', level=STING_UNDER - 2)
sting('SFX_SLOT_WIDEN', P([(I['blip25'], ' '.join(tones[k // 3 + k % 3] for k in range(16)), 1.0)], step=1.2 / 16),
      'odometer 1,232 to 4,096: 16 blips over 1.2 s, rolling C major arpeggio rising G4 to G6')
sting('SFX_SPIN', P([(I['blip25'], 'G5 . . B5 . . D6 . . ' + 'D6 . G5 . ' * 4 + 'D6 . {hold25} C6~=.45', 1.0), (I['tri'], '- ' * 27 + 'C3=.45', .5)], step=1 / 30),
      'the ">" grows (G5 B5 D6), spins (D6/G5 at 15 Hz with the frames), resolves to C6 as the green "<" settles')
sting('SFX_SWAP_A', P([(I['blip25'], 'C6>C5=.15', 1.0)], step=.15), '"-A" tumbles off: falling blip C6 to C5', level=STING_UNDER - 2)
sting('SFX_SWAP_B', P([(I['blip25'], 'C5>C6=.15', 1.0)], step=.15), '"-B" flies in: rising blip C5 to C6', level=STING_UNDER - 2)
sting('SFX_BLOCK_DROP', P([(I['sq50'], 'G5>G3=.4', 1.0), (I['kick'], '- - - - C3>C1=.2', .6)], step=.1), 'the block drops through: falling note G5 to G3')

# ---------------- F: win screen
bF = (M['SFX_CHECK'] - M['SFX_WIN_1']) / 16; gF = Grid('F', M['SFX_WIN_1'], bF, M['SFX_WIN_1']); GRIDS.append(gF)
pF = P([(I['tri'], '| C2 . . . C3 . . . G2 . . . C3 . . . | D2 . . . D3 . . . A2 . . . D3 . . . | E2 . . . E3 . . . B2 . . . E3 . . . '
                   '| F2 . . . F3 . . . G2 . . . G3 . . .', .5),
        (I['lead12'], '| C5 . G4 . E5 . G4 . C5 . G4 . E5 . G4 . | D5 . A4 . F5 . A4 . D5 . A4 . F5 . A4 . | E5 . B4 . G5 . B4 . E5 . B4 . G5 . B4 . '
                      '| F5 . C5 . A5 . C5 . G5 . D5 . B5 . D5 .', .22),
        (I['hat'], ' '.join(['- - C4 -'] * 16), .08), (I['snare'], ' '.join(['- - - - N5 - - -'] * 8), .1)], bpm=60 / bF, spb=4)
bed('F win', pF, gF.t1, M['SFX_CHECK'], 'win screen: C | Dm | Em | F G, triangle half notes, 12.5 % broken chords, hat and snare on 2 and 4', grid=gF)
for i, notes in enumerate(['C5 E5 G5 C6', 'D5 F5 A5 D6', 'E5 G5 B5 E6', 'F5 A5 C6 F6']):
    sting('SFX_WIN_%d' % (i + 1), P([(I['blip25'], notes, 1.0)], step=bF / 4), 'four-note ascending motif ' + notes.replace(' ', '-'))
sting('SFX_CHECK', P([(I['hold50'], 'C6~=.7', .45), (I['chord'], 'C5^047c=.7', .4), (I['tri'], 'C3=.7', .55), (I['boom'], 'N3>N8=.45', .35)], step=.7),
      'full C major chord: C6 + an arpeggiated C-E-G-C voice + triangle C3, noise crash')
sting('SFX_JOE', P([(I['blip'], 'G5 C6 E6 G6 C7 . E7 . .', 1.0)], step=.055), '1-up for Joe: G5 C6 E6 G6 C7 E7', level=STING_UNDER - 3)

# ---------------- tag: v4's cues, v4's times
for x in D['sfx']:
    w = C.jingle(x['hold']) if x['file'] == 'jingle' and 'hold' in x else {'jingle': C.jingle, 'bed': C.bed, 'coin': C.coin, 'tick': C.tick}[x['file']]()
    if x['file'] == 'bed':   # as v4's build: trimmed at the scene end, 0.6 s linear fade-out
        d = TOTAL - x['t']; w = w[:int(round(d * SR))].copy(); k = int(.6 * SR); w[-k:] *= np.linspace(1, 0, k)
    assert x['t'] + len(w) / SR <= TOTAL + 1e-9, ('tag cue runs past the scene end', x)   # nothing is cut off at the end
    place(w, x['t'])
jt = next(x['t'] for x in D['sfx'] if x['file'] == 'jingle'); v7 = 'hold' in D['sfx'][0]
EVENTS.append(dict(marker='SFX_LEVEL_COMPLETE', t=M['SFX_LEVEL_COMPLETE'], event=round(jt + (0 if v7 else 3 * .085), 4), level='peak -12',
                   what="v4's jingle from the tag start, held chord shortened to end before the scene; its first note on the marker as the proof table starts" if v7 else
                        "v4's jingle from the LEVEL COMPLETE flash (tag); its top C6 lands on the marker"))
SECTIONS.append(dict(section='tag', t0=T['tag'], t1=TOTAL, bpm=None, rms=None, what="v7: jingle only (arpeggio under the table's scroll, held chord as it lands)") if v7 else
                dict(section='tag', t0=T['tag'], t1=TOTAL, bpm=124, rms=-30, what="v4: jingle, bed from tag + 1 s, coin on ROTATE, 18 credits ticks"))

score += beds * bed_gain

# ---------------- dialogue guard
def rms_env(x, sr, hop=.01, win=.2):
    """RMS (dB) of the window [t - win/2, t + win/2] at t = 0, hop, 2 hop, ... (scene seconds)"""
    c = np.concatenate([[0.0], np.cumsum(x.astype(float) ** 2)]); h = np.arange(0, TOTAL + 1e-9, hop)
    a = np.clip(np.round((h - win / 2) * sr).astype(int), 0, len(x)); b = np.clip(np.round((h + win / 2) * sr).astype(int), 0, len(x))
    return h, 10 * np.log10(np.maximum((c[b] - c[a]) / max(1, int(win * sr)), 1e-12))
def read_wav(p):
    w = wave.open(p); ch = w.getnchannels(); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float) / 32768
    return x.reshape(-1, ch).mean(1), w.getframerate()
GUARD = None
if A.voice:
    v, vsr = read_wav(A.voice); h, vdb = rms_env(v, vsr); hop = h[1] - h[0]; W = int(round(.1 / hop))
    g = np.ones(len(h))
    for it in range(8):
        k = np.interp(np.arange(N) / SR, h, g); _, sdb = rms_env(score * k, SR)
        need = np.where(vdb >= VOICE_ACTIVE, np.minimum(0, vdb - GUARD_DB - sdb), 0.0)      # dB to take off, per window centre
        if need.min() > -.05: break
        req = 10 ** (need / 20); held = np.array([req[max(0, i - W):i + W + 1].min() for i in range(len(h))])   # the whole window gets the cut
        g = g * held
        for i in range(1, len(g)): g[i] = min(g[i], g[i - 1] * 10 ** ((REL_SPEECH if vdb[i] >= VOICE_ACTIVE else REL_FREE) * hop / 20))   # release dB/s
        for i in range(len(g) - 2, -1, -1): g[i] = min(g[i], g[i + 1] * 10 ** (200 * hop / 20))                # attack ramp 200 dB/s (no clicks)
    k = np.interp(np.arange(N) / SR, h, g); score *= k; GUARD = dict(max_cut_db=round(float(20 * np.log10(g.min())), 1), iterations=it + 1,
                                                                       seconds_cut_over_3db=round(float((g < 10 ** (-3 / 20)).sum() * hop), 2))
    print('guard: max cut %.1f dB, %.2f s cut by more than 3 dB (%d passes)' % (GUARD['max_cut_db'], GUARD['seconds_cut_over_3db'], GUARD['iterations']))
    # peak guard: on the voice's loudest syllables the score steps aside so voice + score stays under PEAK_SUM (v4's chain is unchanged, so the final
    # peak stays v4's). 5 ms blocks, +-1 block for the resampling, 400 dB/s attack, 120 dB/s release.
    B = .005; nb = int(np.ceil(TOTAL / B)); bt = (np.arange(nb) + .5) * B
    def bmax(x, sr):   # per 5 ms block (edges on the scene clock, not a whole number of samples), then the max with both neighbours
        e = np.minimum(np.round(np.arange(nb) * B * sr).astype(int), len(x) - 1); m = np.maximum.reduceat(np.abs(x), e)
        return np.maximum(m, np.maximum(np.concatenate([[0], m[:-1]]), np.concatenate([m[1:], [0]])))
    vpk, spk = bmax(v, vsr), bmax(score, SR); gp = np.minimum(1, np.maximum(0, PEAK_SUM - vpk) / np.maximum(spk, 1e-9))
    for i in range(len(gp) - 2, -1, -1): gp[i] = min(gp[i], gp[i + 1] * 10 ** (400 * B / 20))
    for i in range(1, len(gp)): gp[i] = min(gp[i], gp[i - 1] * 10 ** (120 * B / 20))
    score *= np.interp(np.arange(N) / SR, bt, np.minimum(gp, np.minimum(np.concatenate([[1], gp[:-1]]), np.concatenate([gp[1:], [1]]))))
    GUARD['peak_cut_max_db'] = round(float(20 * np.log10(max(gp.min(), 1e-6))), 1); GUARD['peak_cut_ms'] = int(round((gp < .99).sum() * B * 1000))
    print('peak guard: max cut %.1f dB over %d ms' % (GUARD['peak_cut_max_db'], GUARD['peak_cut_ms']))

assert np.abs(score).max() < 10 ** (-11 / 20), 20 * np.log10(np.abs(score).max())
os.makedirs(os.path.dirname(os.path.abspath(A.out)), exist_ok=True); C.save(A.out, score)
EVENTS.sort(key=lambda e: (e['t'], e['marker']))
for e in EVENTS: e['grid'] = grid_of(e['event']).at(e['event']) if e['marker'] != 'SFX_LEVEL_COMPLETE' else 'tag'
os.makedirs(os.path.dirname(os.path.abspath(A.events)), exist_ok=True)
json.dump(dict(events=EVENTS, sections=SECTIONS, guard=GUARD, levels=dict(bed_under=BED_UNDER, sting_under=STING_UNDER, sting_clear=STING_CLEAR, guard_db=GUARD_DB,
               voice_active=VOICE_ACTIVE)), open(A.events, 'w'), indent=1)
if A.table:
    print('| marker | time (s) | bar:beat | what plays |\n|---|---|---|---|')
    for e in EVENTS: print('| %s | %.2f | %s | %s (%s dBFS) |' % (e['marker'][4:], e['t'], e['grid'], e['what'], e['level']))
    print('\n| section | from-to (s) | BPM | bed level |\n|---|---|---|---|')
    for s in SECTIONS: print('| %s | %.2f-%.2f | %s | %s dBFS RMS |' % (s['section'], s['t0'], s['t1'], s['bpm'], s['rms']))
