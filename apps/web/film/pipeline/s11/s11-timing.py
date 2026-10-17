#!/usr/bin/env python3
"""Runs ON dev-mac from ~/video-work/solana-bunker/s11 (system python). Scene 11 timing (film-plan-ending.md part C) -> out/s11-edl.json,
film/data/s11-edl.js (window.S11: T), out/s11-audio.filter (the voice) and out/s11-mix.filter (voice + jingles + groove).
v4: the locked read (en-US-Studio-O, stitch-B, voices/outro/outro-v4.wav, 14.52 s) at 4.60; the codes and the ask line are revealed on its words
(onsets measured with faster_whisper small int8 word timestamps, refined on the 10 ms RMS envelope: the stop bursts after the closures).
v7: the roll's speed curve (Liam, 2026-10-16). Phase 1 holds 6 px a frame until the outro voice has ended and the groove starts. Phase 2 eases
(cubic in-out on the speed) up to 10 px a frame, reached when the middle of the crew blocks (WRITTEN BY .. SPECIAL THANKS) is at the window's
centre, and holds. Phase 3 eases back down to 6 px a frame, reached when the closing lines (the Lamport portrait line, the two joke lines) enter
the window, and holds until the last line has left. T.roll_px[n] is the roll's whole-pixel offset at roll frame n. If the groove's bar 27 in-point
would fall before the read's end (19.10), the empty window holds whole frames longer before card 1 (T.roll_end; v7: 4 frames).
Audio adds: jingle A (news-open-1) with its first big hit on the CNN slam (1.80); jingle B (news-open-2) with its last hit on card 2's landing
frame (card2 + 0.4, the crossfade's end); the sponsor groove from the bar 27 downbeat right after the voice, its final chord (bar 35) on card 2 (T.card2),
faded out over the 0.4 s to jingle B's last hit (a downbeat end: the groove's next hit is 0.55 s after the chord)."""
import json, math
FPS = 30
VOICE_AT = 4.60     # v4: the locked read (Google en-US-Studio-O, voices/outro/outro-v4.wav), 1.0 s after the split lands (3.60)
TRIM = 0.030        # the start silence the audio chain's silenceremove takes off outro-v4.wav (14.525 -> 14.495 s)
VOICE_END = 19.10   # the read's file end in scene time (its last sound is at 18.33)
W_GH, W_COLLAB, W_REACH = 8.37, 10.84, 11.87   # word onsets in outro-v4.wav: "GitHub" (whisper 8.28), "collaborate" (10.90), "reach" (11.90, silence ends 11.872)
at = lambda w: round(VOICE_AT - TRIM + w, 2)   # file time -> scene time
# the roll, measured in s11-cnn.html at load (v7: + MUSIC, ARCADE SCORE, NEWS STINGS, the Lamport portrait line; SOUND EFFECTS one line): offsetHeight 5613,
# window 470.69 (the page starts the roll at Math.round(win) = 471). Block tops in roll px: WRITTEN BY 1372, SPECIAL THANKS ends 5199, the Lamport line 5250.
ROLL_H, WIN = 5613, 471
PX1, PX2 = 6, 10                   # px a frame: v1-v6 speed; the phase 2 hold (1.67x, a whole number of px so the hold has no cadence)
CREW_MID = (1372 + 5199) / 2       # the middle of the crew blocks
CLOSE_TOP = 5250                   # the closing lines' first line
N_DN = 60                          # phase 3 ease, frames
PH2 = 19.20                        # phase 2 starts 0.1 s after the read's end (the groove comes in at 19.14)
LAT = 0.005                        # the limiter (alimiter, 5 ms attack, no latency compensation) delays the mix by 5 ms: the new layers go in 5 ms early
# audio sources on dev-mac (attack times from out/onset_at.py: the steepest 2 ms RMS rise; the groove's on its 180 Hz high-passed mono downmix, as played)
JA_HIT = 0.6677     # news-open-1-mini-jingle.wav: first big hit (the 0.02 and 0.34 onsets are pickups at -21 dBFS)
JB_HIT = 1.2915     # news-open-2-minimalist-transition.wav: last hit (-4.2 dBFS peak)
G_IN, G_CHORD = 60.6895, 79.1767   # suno-1-reassuring-groove-a.wav: bar 27 downbeat (grid 60.72), bar 35 final chord (grid 79.18)
JA_MONO, JB_MONO, G_MONO = -24.4, -25.4, -19.6   # integrated LUFS of each file's mono downmix (stereo: -19.9, -20.0, -16.3)
T = {'bars': 0.0, 'ident': .35, 'logo_in': .35, 'net_in': 1.15, 'cnn_in': 1.80, 'streak': 2.20, 'split': 3.00, 'split_end': 3.60, 'roll': 3.60,
     'voice': VOICE_AT,
     'q_gh': at(W_GH), 'q_tg': at(W_COLLAB), 'q_x': round(at(W_COLLAB) + .5, 2), 'pop': .15,   # v4: each code pops in (opacity, 150 ms) on its cue
     'ask': at(W_REACH), 'ask_d': .9}                                                         # the ask line writes in left to right from "reach"
R0 = round(T['roll'] * FPS)
ease = lambda p: 4 * p ** 3 if p < .5 else 1 - (-2 * p + 2) ** 3 / 2

def roll(p2):
    """Roll positions for phase 2 starting at roll frame p2 -> (px list, phase frames)."""
    c, px, v = 0.0, [0], []
    for n in range(p2): c += PX1; px.append(round(c))
    n_up = round((WIN + CREW_MID - WIN / 2 - c) / ((PX1 + PX2) / 2))
    for k in range(n_up): c += PX1 + (PX2 - PX1) * ease((k + .5) / n_up); px.append(round(c))
    hold = len(px) - 1; d0 = CLOSE_TOP - N_DN * (PX1 + PX2) / 2
    while c + PX2 / 2 < d0: c += PX2; px.append(round(c))
    dn = len(px) - 1
    for k in range(N_DN): c += PX2 - (PX2 - PX1) * ease((k + .5) / N_DN); px.append(round(c))
    slow = len(px) - 1
    while px[-1] < WIN + ROLL_H: c += PX1; px.append(round(c))
    return px, {'p2': p2, 'hold': hold, 'dn': dn, 'slow': slow, 'end': len(px) - 1}

px, ph = roll(round(PH2 * FPS) - R0)
hold_n = max(0, math.ceil(round((VOICE_END - (G_IN + (R0 + ph['end']) / FPS + 4.5 - G_CHORD)) * FPS, 6)))   # frames the empty window holds before card 1
card2 = (R0 + ph['end'] + hold_n) / FPS + 4.5
g_start = G_IN + card2 - G_CHORD   # the in-point downbeat whose final chord lands on card 2
assert hold_n <= 6 and VOICE_END <= g_start <= PH2, (hold_n, g_start)
fs = lambda n: round((R0 + n) / FPS, 4)
T.update({'roll_px': px, 'ph2': fs(ph['p2']), 'ph2_hold': fs(ph['hold']), 'ph3': fs(ph['dn']), 'ph3_hold': fs(ph['slow']), 'roll_out': fs(ph['end'])})
T['roll_end'] = fs(ph['end'] + hold_n)
T['card1'] = T['roll_end']                       # 0.5 s crossfade in, held 4.0 s
T['card2'] = round(T['card1'] + 4.5, 4)          # 0.4 s crossfade, held 3.0 s
T['card2_land'] = round(T['card2'] + .4, 4)      # the crossfade's end: card 2 fully in
T['fade'] = round(T['card2'] + 3.4, 4)           # 1.0 s to black
frames = round((T['fade'] + 1.0) * FPS); TOTAL = round(frames / FPS, 4); T['total'] = TOTAL
A = {'ja_start': round(T['cnn_in'] - JA_HIT - LAT, 4), 'jb_start': round(T['card2_land'] - JB_HIT - LAT, 4),
     'g_in': G_IN, 'g_start': round(g_start - LAT, 4), 'g_chord': T['card2'], 'duck': VOICE_AT}   # starts in the pre-limiter mix
doc = {'total': TOTAL, 'frames': frames, 'fps': FPS, 'voice_at': VOICE_AT, 'T': T, 'audio': A}
json.dump(doc, open('out/s11-edl.json', 'w'), indent=1)
open('film/data/s11-edl.js', 'w').write('window.S11 = ' + json.dumps(doc, separators=(',', ':')) + ';\n')
ms = int(round(VOICE_AT * 1000)); S = lambda s: f"{round(s * 48000)}S"
open('out/s11-audio.filter', 'w').write(
    f"[0:a]silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02,aresample=48000,afade=t=in:d=0.02,adelay={ms},apad=whole_dur={TOTAL},atrim=0:{TOTAL},asetpts=PTS-STARTPTS[mix]\n")
# the mix: 0 voice (out/voice.wav, placed; VOICE_GAIN is filled in by build.sh: -16 LUFS for the voice alone), 1 jingle A, 2 jingle B, 3 groove.
# Levels in the mono mix: jingles at their mastered -20 LUFS event loudness (0 dB), the groove -10 dB under the voice's -16 (-26 LUFS), 180 Hz high-pass.
# asetpts=N/SR/TB after each adelay: ffmpeg 9's adelay keeps a trimmed input's timestamps, and the atrim after it then drops the delay.
# Jingle A: ducked -12 dB over 100 ms from the voice's start and faded out over 1.0 s from there (the file ends at 4.43, so both act on silence).
# Jingle B fades with the picture; the groove fades out from its final chord to jingle B's last hit.
mono = 'pan=mono|c0=0.5*c0+0.5*c1'
pad = f"apad=whole_dur={TOTAL},atrim=0:{TOTAL},asetpts=PTS-STARTPTS"
fade = f"afade=t=out:st={T['fade']}:d=1.0"
open('out/s11-mix.filter', 'w').write(';'.join([
    "[0:a]volume=VOICE_GAINdB[v]",
    f"[1:a]{mono},volume={-20 - JA_MONO:.1f}dB,adelay={S(A['ja_start'])},asetpts=N/SR/TB,{pad},asetnsamples=48,"
    f"volume='if(lt(t,{VOICE_AT}),1,pow(10,-12/20*min(1,(t-{VOICE_AT})/0.1)))':eval=frame,afade=t=out:st={VOICE_AT}:d=1.0[ja]",
    f"[2:a]{mono},volume={-20 - JB_MONO:.1f}dB,adelay={S(A['jb_start'])},asetpts=N/SR/TB,{pad},{fade}[jb]",
    f"[3:a]atrim=start={G_IN - .01:.4f},asetpts=PTS-STARTPTS,{mono},volume={-26 - G_MONO:.1f}dB,highpass=f=180,afade=t=in:d=0.01,"
    f"adelay={S(A['g_start'] - .01)},asetpts=N/SR/TB,{pad},afade=t=out:st={A['g_chord'] - LAT:.4f}:d={T['card2_land'] - T['card2']:.1f}[g]",
    "[v][ja][jb][g]amix=inputs=4:normalize=0:duration=first[mix]"]) + "\n")
print('roll frames', ph['end'], 'hold', hold_n, 'total', TOTAL, 'frames', frames)
print({k: v for k, v in T.items() if k != 'roll_px'}); print(A)
