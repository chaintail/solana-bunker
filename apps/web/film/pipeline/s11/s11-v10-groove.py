#!/usr/bin/env python3
"""Scene 11 v10: the sponsor groove through the whole credits, ducked under the advisory voice (the opening m3 / conspiracy m4c bed treatment).
Runs on do-box with /home/claude/venvs/manim (numpy, scipy); ffmpeg for decoding only (-vn). Uses music-m4.py (read, hp, eq, lufs, sidechain).
usage: s11-v10-groove.py <groove.wav> <voice stem (key)> <out groove stem .wav>
Treatment: mono fold, 100 Hz high-pass, shelves 6 kHz -6 / 11 kHz -8, notch 16.8 kHz -6 Q 8, normalised to -18 LUFS, then -11.3 dB under speech
(-29.3 LUFS) and +5 dB in the pauses (sidechain on the voice: key 10 ms RMS -44..-38 dBFS, 30 ms look-ahead, 300 ms release).
Placement: v9's anchor, the final chord (track 79.1767) at card 2 (36.90 s; 5 ms early for the limiter, as v9). The groove's bars are 2.3193 s
(grid downbeats 63.042 / 65.341 / ... / 79.18); the entry is the nearest bar downbeat before the roll (3.60 s), raised-cosine fade-in 0.5 s.
Out: faded linearly over 0.4 s from the chord (v9), to jingle B's last hit."""
import sys, json, importlib.util, os
import numpy as np
here = os.path.dirname(os.path.abspath(__file__))
s_ = importlib.util.spec_from_file_location('m4', os.path.join(here, 'music-m4.py')); M = importlib.util.module_from_spec(s_); s_.loader.exec_module(M)
SR = M.SR; db = M.db
LAT, CHORD_TRACK, CARD2, ROLL, TOTAL = 0.005, 79.1767, 36.90, 3.60, 41.30
BAR = (79.18 - 63.042) / 7           # bar 28 -> bar 35 (grid downbeats)
FADE_IN, FADE_OUT = 0.5, 0.4
UNDER, DEPTH, NORM = -11.3, 5.0, -18.0
D = {'key_lo_db': -44, 'key_hi_db': -38, 'attack_ms': 30, 'release_ms': 300}
raw = M.read(sys.argv[1]); key = M.read(sys.argv[2]); N = int(round(TOTAL * SR)); assert len(key) >= N; key = key[:N]
det = M.hp(raw, 180)
y = M.hp(raw, 100)
y = M.eq(y, [{'type': 'highshelf', 'f': 6000, 'gain_db': -6, 'q': 0.7071}, {'type': 'highshelf', 'f': 11000, 'gain_db': -8, 'q': 0.7071},
             {'type': 'peak', 'f': 16800, 'gain_db': -6, 'q': 8}])
L = M.lufs(y); y = y * db(NORM - L)
off = (CARD2 - LAT) - CHORD_TRACK                    # scene = track + off
# bar downbeat attacks (flux onsets on the 180 Hz high-passed fold, as v9), counted back from the chord
bars = {35 - k: M.flux_onset(det, CHORD_TRACK - k * BAR, 0.06) for k in range(0, 17)}
cand = [(b, t + off) for b, t in bars.items() if t + off <= ROLL]
b_in, s_in = max(cand, key=lambda c: c[1])           # nearest bar downbeat at or before the roll
t_in = s_in - off
PRE = 0.005
tt = np.arange(N) / SR
j = np.round((tt - off) * SR).astype(np.int64)
ok = (j >= 0) & (j < len(y)) & (tt >= s_in - PRE)
placed = np.zeros(N); placed[ok] = y[j[ok]]
amp = 0.5 - 0.5 * np.cos(np.pi * np.clip((tt - (s_in - PRE)) / FADE_IN, 0, 1))
amp *= np.clip(1 - (tt - (CARD2 - LAT)) / FADE_OUT, 0, 1)
placed *= amp
frac, k = M.sidechain(key, N, D)
mus = placed * db(UNDER + DEPTH * (1 - frac))
M.write(sys.argv[3], mus)
rep = {'cue_lufs_after_eq_before_norm': L, 'norm_gain_db': NORM - L, 'under_lufs': NORM + UNDER, 'open_lufs': NORM + UNDER + DEPTH, 'entry_bar': b_in,
       'entry_scene_s': s_in, 'entry_track_s': t_in, 'fade_in_s': FADE_IN, 'bars_added_vs_v9': 28 - b_in, 'bars_scene': {str(b): round(t + off, 4) for b, t in sorted(bars.items())},
       'chord_scene': CARD2, 'track_end_s': len(raw) / SR, 'ms_ducked_over_half': int((frac > .5).sum() / 48)}
json.dump(rep, open(sys.argv[3] + '.json', 'w'), indent=1, default=float); print(json.dumps(rep, indent=1, default=float))
