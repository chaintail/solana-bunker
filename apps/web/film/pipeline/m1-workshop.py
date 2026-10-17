#!/usr/bin/env python3
"""m1 (music) for the bunker (s04) and the whiteboard (s05): one workshop cue across both scenes, sound effects, picture copied (-c:v copy).
Same file on film/s04 and film/s05; the placements are in pipeline/m1-workshop.json.

Runs on do-box with /home/claude/venvs/manim/bin/python3 (numpy, scipy, matplotlib):  python3 m1-workshop.py m1-workshop.json
Every ffmpeg call runs on dev-mac over ssh (ffmpeg is banned on do-box). Spec paths are relative to ~/video-work/solana-bunker on dev-mac.

Timeline: film time F = s04 time for F < L4 (46.5 s), F = L4 + s05 time after it. The music is rendered once on F and split at sample L4 x 48000;
s04's mix carries the part before, s05's the part after. The stitch is a straight concatenation, so the music is continuous to the sample.

Music: the Suno file as (L+R)/2, gained to -16 LUFS (so a level of -20 dB is gain on a -16 LUFS cue), 180 Hz high-pass (2-pole), then cut into
  segments that start and end on measured downbeats (spectral-flux attack within -60..+40 ms of each analysis.json downbeat; the attacks run 20-45 ms
  BEFORE the analysis times on this track). A segment's position comes from an anchor (a track attack on a picture frame) or from its neighbour
  (segments that touch share the splice point). Splice edges: 20 ms equal-power ramps ending 5 ms before the attack, so the incoming downbeat plays
  at full gain. A segment may end with a tail (the downbeat sounds, then a raised-cosine fade).
Levels (dB gain on the -16 LUFS cue): -20 under speech, -14 in speech gaps of 0.8 s or more (speech = 20 ms RMS >= -40 dBFS on the dialogue, holes
  under 0.15 s bridged), ramps linear in dB: 300 ms release after the last word, 100 ms attack ending on the next word. Gap overrides (a named swell)
  set one gap's level; automation windows (dip, stop, final chord) replace the level between their first and last point.
  Dialogue guard: in every 100 ms AND every 200 ms window (10 ms hop) where the dialogue is active (RMS >= -30 dBFS) the music is held 16 dB under it
  by a smooth gain trim (each window's shortfall applied across that window, attack 150 dB/s ahead of the word, release 50 dB/s after it, i.e. about 15 dB in 100 ms / 300 ms;
  trimmed from -32 dBFS, since the loudnorm gain that follows can lift the dialogue).
SFX: each file as (L+R)/2, gained to -20 LUFS event loudness (ebur128, 1 s of padded silence, as film/sfx master.py), then the spec gain
  (0 in the clear, -6 under speech); its hit (spec 'hit', seconds into the file) lands on the picture frame.
Per scene: dialogue (the delivered audio-final.wav, unchanged) + music part + sfx -> loudnorm pass 1 (measure) -> one linear gain -> the scene's limiter
  (alimiter=limit=0.95, latency=1 so the lookahead is compensated); the gain is corrected until ebur128 reads the limited file at -16.0 LUFS
  (loudnorm's own meter reads these mixes off ebur128, so pass 2 is a corrected linear gain, checked by ebur128 after).
Outputs (dev-mac out/): <scene>-m1.mp4, -phone.mp4 (video copied), -audio.wav, stems -dialogue/-music/-sfx.wav (48 kHz float, after the scene gain,
  before the limiter; they sum to the pre-limiter mix), -report.json, -levels.png, -event-frames.png; s04-s05-m1-music-unsplit.wav (the one render, before
  the scene gains). Checks: video md5 vs the source; every music attack and SFX hit measured in the stems vs its frame; continuity across the join;
  guard minimum (100 and 200 ms); loudness of the muxed file."""
import json, os, re, shlex, subprocess, sys
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
FFDIR = '/opt/homebrew/opt/ffmpeg-full/bin/'
FF = FFDIR + 'ffmpeg -nostdin -hide_banner'
RAW = f'-f f32le -ar {SR} -ac 1'
WORK = os.environ.get('M1_WORK', '/tmp')
D = '~/video-work/solana-bunker'


def sh(cmd, inp=None):
    r = subprocess.run(['ssh', 'dev-mac', f'cd {D} && {cmd}'], input=inp, capture_output=True)
    if r.returncode: raise RuntimeError(f'{cmd}\n{r.stderr.decode()[-2000:]}')
    return r.stdout, r.stderr.decode()


def q(p): return '~/' + shlex.quote(p[2:]) if p.startswith('~/') else shlex.quote(p)


def dec(path, ch=1):
    out, _ = sh(f'{FF} -v error -i {q(path)} -ar {SR} -f f32le -')
    x = np.frombuffer(out, dtype=np.float32)
    return x.reshape(-1, 2).mean(1) if ch == 2 else x.copy()


def lufs(x, pad=0.0):
    if pad: x = np.concatenate([x, np.zeros(int(pad * SR), np.float32)])
    _, err = sh(f'{FF} -nostats {RAW} -i - -af ebur128=peak=true -f null -', inp=x.astype(np.float32).tobytes())
    s = err[err.rfind('Summary'):]
    return dict(I=float(re.search(r'I:\s+(-?[\d.]+) LUFS', s).group(1)), LRA=float(re.search(r'LRA:\s+(-?[\d.]+) LU', s).group(1)),
                TP=float(re.search(r'Peak:\s+(-?[\d.inf]+) dBFS', s).group(1)))


def wav(x, path, codec='pcm_f32le'):
    sh(f'{FF} -v error -y {RAW} -i - -c:a {codec} {q(path)}', inp=x.astype(np.float32).tobytes())


def ffilter(x, af):
    out, err = sh(f'{FF} -nostats {RAW} -i - -af {shlex.quote(af)} -ar {SR} -ac 1 -f f32le -', inp=x.astype(np.float32).tobytes())
    return np.frombuffer(out, dtype=np.float32).copy(), err


def rms_db(x, win, hop, n_out):
    c = np.concatenate([[0.0], np.cumsum(x.astype(np.float64) ** 2)]); w = int(win * SR); h = int(hop * SR)
    ctr = np.arange(n_out) * h; a = np.clip(ctr - w // 2, 0, len(x)); b = np.clip(ctr + w // 2, 0, len(x))
    return 10 * np.log10((c[b] - c[a]) / np.maximum(b - a, 1) + 1e-12)


def speech_runs(d, thr=-40.0, bridge=.15, min_run=.04):
    act = rms_db(d, .02, .01, len(d) // 480 + 1) >= thr; runs = []; i = 0
    while i < len(act):
        if act[i]:
            j = i
            while j < len(act) and act[j]: j += 1
            runs.append([i * .01, j * .01]); i = j
        else: i += 1
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] < bridge: merged[-1][1] = r[1]
        else: merged.append(r)
    return [r for r in merged if r[1] - r[0] >= min_run]


def flux_attack(x, t0, t1, hop=96, N=512):
    """time where the largest spectral-flux rise in [t0, t1] enters (the window's trailing quarter)"""
    a = int(t0 * SR); w = np.hanning(N); S = []
    for i in range(a - N, int(t1 * SR), hop):
        seg = x[max(0, i):i + N]
        if len(seg) < N: seg = np.pad(seg, (N - len(seg), 0))
        S.append(np.log1p(np.abs(np.fft.rfft(seg * w)) * 10))
    f = np.maximum(np.diff(np.array(S), axis=0), 0).sum(1)
    return (a - N) / SR + (int(np.argmax(f)) + 1) * hop / SR + .75 * N / SR


def onset_env(x, t0, t1, rel=-12.0):
    a, b = max(0, int(t0 * SR)), int(t1 * SR); n = 48; s = np.abs(x[a:b]); k = len(s) // n; e = s[:k * n].reshape(k, n).max(1)
    return a / SR + int(np.argmax(e >= e.max() * 10 ** (rel / 20))) * n / SR


def main():
    spec = json.load(open(sys.argv[1])); FPS = spec['fps']; SC = spec['scenes']; names = list(SC)
    L = {s: SC[s]['frames'] / FPS for s in names}; NS = {s: int(round(L[s] * SR)) for s in names}
    OFF = {}; acc = 0.0
    for s in names: OFF[s] = acc; acc += L[s]
    TT = acc; N = sum(NS.values()); JOIN = NS[names[0]]
    F = lambda s, t: OFF[s] + t                       # scene time -> film time
    Ff = lambda s, f: OFF[s] + f / FPS                # scene frame -> film time
    t = np.arange(N) / SR
    rep = dict(name=spec['name'], scenes={s: dict(length_s=L[s], frames=SC[s]['frames'], film_offset_s=OFF[s]) for s in names}, join_sample=JOIN)
    # ---------------- dialogue (both scenes on the film timeline)
    d = {}
    for s in names:
        x = dec(SC[s]['dialogue']); assert abs(len(x) - NS[s]) <= 2, (s, len(x), NS[s]); d[s] = np.pad(x, (0, max(0, NS[s] - len(x))))[:NS[s]]
    dd = np.concatenate([d[s] for s in names])
    runs = speech_runs(dd); rep['speech_runs_film'] = [[round(a, 3), round(b, 3)] for a, b in runs]
    # ---------------- music source: mono, -16 LUFS, high-pass, measured downbeat attacks
    M = spec['music']; m2 = dec(M['file'], ch=2); I0 = lufs(m2)['I']; m2 *= 10 ** ((M['ref_lufs'] - I0) / 20)
    m2 = sosfilt(butter(2, M['highpass'], 'highpass', fs=SR, output='sos'), m2).astype(np.float32)
    an = json.load(open(os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), M['analysis']))) if not M['analysis'].startswith('~') else \
        json.loads(sh(f'cat {q(M["analysis"])}')[0])
    DB = an['downbeats_s']
    att = {k + 1: flux_attack(m2, db - .06, db + .04) for k, db in enumerate(DB)}
    rep['music_source'] = dict(file=M['file'], mono_lufs=I0, gain_to_ref_db=round(M['ref_lufs'] - I0, 2),
                               attacks={b: dict(analysis=DB[b - 1], measured=round(att[b], 4), diff_ms=round(1000 * (att[b] - DB[b - 1]), 1)) for b in att})
    # ---------------- segments: place on the film timeline
    segs = [dict(s) for s in M['segments']]
    for g in segs:
        g['tin'] = att[g['bar_in']]; g['tout'] = att[g['bar_out']] if g.get('bar_out') else len(m2) / SR
        if g.get('anchor'):
            a = g['anchor']; g['off'] = Ff(a['scene'], a['frame']) - att[a['bar']]
    for _ in range(len(segs)):   # chain: a segment without an anchor touches its anchored neighbour at the splice
        for i, g in enumerate(segs):
            if 'off' in g: continue
            if g.get('chain') == 'next' and 'off' in segs[i + 1]: g['off'] = segs[i + 1]['off'] + segs[i + 1]['tin'] - g['tout']
            if g.get('chain') == 'prev' and 'off' in segs[i - 1]: g['off'] = segs[i - 1]['off'] + segs[i - 1]['tout'] - g['tin']
    E, LEAD = M['edge'], M['edge_lead']; music = np.zeros(N, np.float64); seg_rows = []
    for i, g in enumerate(segs):
        fa, fb = g['tin'] + g['off'], g['tout'] + g['off']; a0 = fa - LEAD - E
        tail = g.get('tail', 0.0); end = fb + tail if tail else (fb - LEAD if g.get('bar_out') else fb)
        i0, i1 = max(0, int(round(a0 * SR))), min(N, int(round(end * SR)))
        tt = t[i0:i1]; src = np.round((tt - g['off']) * SR).astype(np.int64); ok = (src >= 0) & (src < len(m2))
        w = np.ones(len(tt))
        u = np.clip((tt - a0) / E, 0, 1); w *= np.sin(.5 * np.pi * u)                        # head: 20 ms equal-power ramp ending 5 ms before the attack
        if tail:                                                                               # tail: the downbeat sounds, then a raised-cosine fade
            h = fb + .05; v = np.clip((tt - h) / (end - h), 0, 1); w *= .5 + .5 * np.cos(np.pi * v)
        elif g.get('bar_out'):
            v = np.clip((tt - (fb - LEAD - E)) / E, 0, 1); w *= np.cos(.5 * np.pi * v)       # out: 20 ms equal-power ramp ending 5 ms before the next attack
        else:
            v = np.clip((tt - (fb - .02)) / .02, 0, 1); w *= 1 - v                            # file end
        seg = np.zeros(len(tt)); seg[ok] = m2[src[ok]]; music[i0:i1] += seg * w
        loc = lambda x: (names[0], x) if x < OFF[names[1]] else (names[1], x - OFF[names[1]])
        seg_rows.append(dict(id=g['id'], bars=f"{g['bar_in']}-{g.get('bar_out', 'end')}", track_in=round(g['tin'], 4), track_out=round(g['tout'], 4),
                             film_in=round(fa, 4), film_out=round(fb, 4), scene_in=[loc(fa)[0], round(loc(fa)[1], 4)], scene_out=[loc(fb)[0], round(loc(fb)[1], 4)],
                             tail_s=tail, anchor=g.get('anchor'), note=g.get('note', '')))
    for a, b in zip(seg_rows, seg_rows[1:]):
        a['gap_to_next_s'] = round(b['film_in'] - a['film_out'], 4)
    rep['segments'] = seg_rows
    # ---------------- level automation
    Lv = spec['levels']; U, G = Lv['under'], Lv['gap']; lev = np.full(N, float(U))
    gaps = [[runs[i][1], runs[i + 1][0]] for i in range(len(runs) - 1)] + [[runs[-1][1], TT]]
    gaps = [g for g in gaps if g[1] - g[0] >= Lv['gap_min']]
    ovr = {}
    for o in Lv.get('gap_overrides', []):
        x = F(o['scene'], o['t']); hit = [g for g in gaps if g[0] - .05 <= x <= g[1] + .05]; assert hit, o; ovr[tuple(hit[0])] = o['db']
    gap_rows = []
    for g0, g1 in gaps:
        lv = ovr.get((g0, g1), G); end = g1 >= TT - 1e-6
        pts = [(g0, U), (g0 + Lv['release'], lv)] + ([(TT + 1, lv)] if end else [(g1 - Lv['attack'], lv), (g1, U)])
        m = (t >= g0) & (t < (TT + 1 if end else g1)); lev[m] = np.maximum(lev[m], np.interp(t[m], [p[0] for p in pts], [p[1] for p in pts]))
        gap_rows.append(dict(film=[round(g0, 3), round(g1, 3)], db=lv))
    for w in Lv.get('automation', []):
        px = [F(p[0], p[1]) for p in w['points']]; py = [p[2] for p in w['points']]; m = (t >= px[0]) & (t <= px[-1]); lev[m] = np.interp(t[m], px, py)
    music *= 10 ** (lev / 20)
    # ---------------- dialogue guard (100 and 200 ms windows, 10 ms hop)
    hop = .01; nh = int(TT / hop) + 1; GD, VA = spec['guard_db'], spec['voice_active_db']; trim = np.ones(N)
    GATT, GREL = spec.get('guard_attack_db_s', 150), spec.get('guard_release_db_s', 50)
    vdb = {w: rms_db(dd, w, hop, nh) for w in (.1, .2)}
    for it in range(40):
        need = np.zeros(nh); worst = 0.0
        for w in (.1, .2):   # each window's shortfall is spread over that window (+-w/2), so the trim lowers the whole window
            mdb = rms_db(music * trim, w, hop, nh); act = (vdb[w] >= VA - 2) & (mdb > -90)
            nw = np.where(act, np.minimum(0, vdb[w] - (GD + .3) - mdb), 0.0); worst = min(worst, nw.min()); h = int(round(w / 2 / hop))
            need = np.minimum(need, np.array([nw[max(0, i - h):i + h + 1].min() for i in range(nh)]))
        if worst > -.05: break
        g = 10 ** (need / 20)
        for i in range(1, nh): g[i] = min(g[i], g[i - 1] * 10 ** (GREL * hop / 20))          # release after the word
        for i in range(nh - 2, -1, -1): g[i] = min(g[i], g[i + 1] * 10 ** (GATT * hop / 20))  # attack ahead of the word
        trim *= np.interp(t, np.arange(nh) * hop, g)
    music = (music * trim).astype(np.float32)
    mon = np.abs(music) > 0
    rep['levels'] = dict(guard_iterations=it + 1, guard_worst_before_last_db=round(float(worst), 2), gaps=gap_rows, automation=Lv.get('automation', []), guard_trim_max_db=round(float(20 * np.log10(trim[mon].min())), 1),
                         guard_trim_s_over_3db=round(float(((trim < 10 ** (-3 / 20)) & mon).sum() / SR), 2))
    wav(music, spec['music_unsplit'])
    # ---------------- per scene: sfx, mix, gain, limiter, remux, checks
    parts = {names[0]: music[:JOIN], names[1]: music[JOIN:]}
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    for s in names:
        S = SC[s]; n = NS[s]; T = L[s]; OUT = S['out']; ft = lambda k: k / FPS; R = rep['scenes'][s]
        sruns = [[a - OFF[s], b - OFF[s]] for a, b in runs if b > OFF[s] and a < OFF[s] + T]
        sfx = np.zeros(n, np.float32); R['sfx'] = []
        for e in S['sfx']:
            x = dec(e['file'], ch=2); I = lufs(x, pad=1.0)['I']; x = x * 10 ** ((spec['sfx_ref_lufs'] - I + e['gain']) / 20)
            at = ft(e['frame']) - e['hit']; i0 = int(round(at * SR)); a = max(0, -i0); b = min(len(x), n - i0); sfx[i0 + a:i0 + b] += x[a:b]
            R['sfx'].append(dict(id=e['id'], file=os.path.basename(e['file']), frame=e['frame'], frame_t=round(ft(e['frame']), 4), hit_in_file=e['hit'],
                                 event_lufs_raw=I, gain_db=e['gain'], under_speech=any(r[0] - .05 <= ft(e['frame']) <= r[1] + .05 for r in sruns)))
        mus = parts[s]; mix = d[s] + mus + sfx
        _, err = ffilter(mix, 'loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json')
        m1 = json.loads(err[err.rfind('{'):err.rfind('}') + 1]); gdb = -16.0 - float(m1['input_i']); hist = []
        for it in range(5):
            k = 10 ** (gdb / 20); fin, _ = ffilter(mix * k, S['limiter']); fin = np.pad(fin, (0, max(0, n - len(fin))))[:n]
            If = lufs(fin)['I']; hist.append([round(gdb, 3), If])
            if abs(If + 16.0) <= .05: break
            gdb += -16.0 - If
        R['loudnorm'] = dict(pass1_input_i=float(m1['input_i']), pass1_input_tp=float(m1['input_tp']), linear_gain_db=round(gdb, 3), gain_then_ebur128=hist)
        R['gain_lin'] = k
        stems = dict(dialogue=d[s] * k, music=mus * k, sfx=sfx * k)
        for nm, x in stems.items(): wav(x, f'{OUT}-{nm}.wav')
        wav(fin, f'{OUT}-audio.wav', 'pcm_s24le')
        for src, dst, br in [(S['master'], f'{OUT}.mp4', S['abr']), (S['phone'], f'{OUT}-phone.mp4', S['abr_phone'])]:
            sh(f'{FF} -v error -y -i {q(src)} -i {q(OUT + "-audio.wav")} -map 0:v -map 1:a -c:v copy -c:a aac -b:a {br} -ac 1 -movflags +faststart -shortest {q(dst)}')
        vmd5 = lambda p: re.search(r'MD5=(\w+)', sh(f'{FF} -v error -i {q(p)} -map 0:v -c copy -f md5 -')[0].decode()).group(1)
        R['video_md5'] = {p: vmd5(p) for p in [S['master'], f'{OUT}.mp4', S['phone'], f'{OUT}-phone.mp4']}
        R['video_identical'] = dict(master=R['video_md5'][S['master']] == R['video_md5'][f'{OUT}.mp4'], phone=R['video_md5'][S['phone']] == R['video_md5'][f'{OUT}-phone.mp4'])
        R['probe'] = {p: sh(f'{FFDIR}ffprobe -v error -count_frames -show_entries stream=codec_type,nb_read_frames,duration -of compact {q(p)}')[0].decode().strip()
                      for p in [f'{OUT}.mp4', f'{OUT}-phone.mp4']}
        dm = dec(f'{OUT}.mp4'); dm = np.pad(dm, (0, max(0, n - len(dm))))[:n]
        def lag(a, b, Lg=600, w=(2, 12)):
            A = a[int(w[0] * SR):int(w[1] * SR)]; return max(range(-Lg, Lg + 1), key=lambda l: float(np.dot(A, b[int(w[0] * SR) + l:int(w[1] * SR) + l])))
        R['lag_samples'] = dict(final_vs_dialogue=lag(d[s], fin), mp4_vs_final=lag(fin, dm))
        R['loudness_mp4'] = lufs(dm); R['loudness_final_wav'] = lufs(fin)
        dmp = dec(f'{OUT}-phone.mp4'); R['loudness_phone'] = lufs(dmp)
        # guard on the final stems, 100 and 200 ms windows
        nhs = int(T / hop) + 1; R['guard'] = {}
        for w in (.1, .2):
            v = rms_db(stems['dialogue'], w, hop, nhs); mm = rms_db(stems['music'], w, hop, nhs); xx = rms_db(stems['sfx'], w, hop, nhs)
            act = (v >= VA) & (mm > -90); ax = (v >= VA) & (xx > -90)
            R['guard'][f'{int(w * 1000)}ms'] = dict(windows=int(act.sum()), min_db=round(float((v - mm)[act].min()), 2) if act.any() else None,
                                                    min_at_s=round(float(np.arange(nhs)[act][np.argmin((v - mm)[act])] * hop), 2) if act.any() else None,
                                                    median_db=round(float(np.median((v - mm)[act])), 1) if act.any() else None,
                                                    sfx_min_db=round(float((v - xx)[ax].min()), 2) if ax.any() else None,
                                                    sfx_min_at_s=round(float(np.arange(nhs)[ax][np.argmin((v - xx)[ax])] * hop), 2) if ax.any() else None)
        # SFX hits in the stem vs frames
        for r in R['sfx']:
            tf = r['frame_t']; r['measured_hit'] = round(onset_env(stems['sfx'], tf - .04, tf + .04), 4); r['err_ms'] = round((r['measured_hit'] - tf) * 1000, 1)
        # picture metrics around each check frame
        raw, _ = sh(f'{FF} -v error -i {q(S["master"])} -vf scale=160:90,format=gray -f rawvideo -')
        V = np.frombuffer(raw, np.uint8).reshape(-1, 90, 160).astype(np.float32); dif = np.r_[0, np.abs(np.diff(V, axis=0)).mean((1, 2))]
        R['picture'] = [dict(id=c['id'], frame=c['frame'], argmax_diff_frame=int(max(range(max(1, c['frame'] - 4), min(len(V), c['frame'] + 5)), key=lambda i: dif[i])),
                             diff={i: round(float(dif[i]), 2) for i in range(max(1, c['frame'] - 4), min(len(V), c['frame'] + 5))}) for c in S['picture_checks']]
        R['video_frames_decoded'] = len(V)
        sel = '+'.join(f'between(n,{c["frame"] - 3},{c["frame"] + 2})' for c in S['picture_checks'])
        vf = (f"drawtext=text='f%{{n}}':x=8:y=8:fontsize=40:fontcolor=yellow:box=1:boxcolor=black@0.7,select='{sel}',scale=320:180,"
              f"tile=6x{len(S['picture_checks'])}:padding=4:color=white")
        sh(f'{FF} -v error -y -i {q(S["master"])} -vf {shlex.quote(vf)} -frames:v 1 {q(OUT + "-event-frames.png")}')
        subprocess.run(['scp', '-q', f'dev-mac:video-work/solana-bunker/{OUT}-event-frames.png', f'{WORK}/{s}-m1-event-frames.png'], check=True)
        R['stems'] = {nm: f'{OUT}-{nm}.wav' for nm in stems}
        # level plot
        tt = np.arange(nhs) * hop; v1 = rms_db(stems['dialogue'], .1, hop, nhs); mm1 = rms_db(stems['music'], .1, hop, nhs); xx1 = rms_db(stems['sfx'], .1, hop, nhs)
        v2 = rms_db(stems['dialogue'], .2, hop, nhs); mm2 = rms_db(stems['music'], .2, hop, nhs)
        fig, (a1, a2) = plt.subplots(2, 1, figsize=(18, 8.5), sharex=True, gridspec_kw=dict(height_ratios=[3, 1.3]))
        for x, c, lb in [(v1, '#2a6fdb', 'dialogue'), (mm1, '#d9822b', 'music'), (xx1, '#1a9e5a', 'sfx')]: a1.plot(tt, np.maximum(x, -70), color=c, lw=1.0, label=lb + ' (100 ms RMS)')
        for a, b in sruns: a1.axvspan(max(a, 0), min(b, T), color='#2a6fdb', alpha=.06, lw=0)
        for r in R['sfx']:
            a1.axvline(r['frame_t'], color='#1a9e5a', ls=':', lw=1); a1.text(r['frame_t'], -3, f" {r['id']}\n f{r['frame']}", fontsize=7.5, color='#1a6e3a', va='top')
        for g in seg_rows:
            for key, lb in (('film_in', 'in'), ('film_out', 'out')):
                x = g[key] - OFF[s]
                if 0 <= x <= T: a1.axvline(x, color='#d9822b', ls='--', lw=1); a1.text(x, -62, f" {g['id']} {lb}\n bar {g['bars']}", fontsize=7, color='#a0561b')
        a1.set_ylim(-70, 0); a1.set_ylabel('dBFS'); a1.legend(loc='lower right', fontsize=8); a1.grid(alpha=.25)
        a1.set_title(f"{s}-m1: levels after the scene gain (shaded = speech; dotted green = SFX frames; dashed orange = music segment in/out)", fontsize=10)
        act1 = (v1 >= VA) & (mm1 > -90); act2 = (v2 >= VA) & (mm2 > -90)
        a2.plot(tt[act1], (v1 - mm1)[act1], '.', ms=2.5, color='#7a3fb0', label='dialogue minus music, 100 ms')
        a2.plot(tt[act2], (v2 - mm2)[act2], '.', ms=1.8, color='#2a9d8f', label='dialogue minus music, 200 ms')
        a2.axhline(GD, color='#c0392b', lw=1, label=f'{GD:.0f} dB guard'); a2.set_ylim(0, 60); a2.set_ylabel('dB'); a2.set_xlabel(f'{s} seconds'); a2.grid(alpha=.25); a2.legend(loc='upper right', fontsize=8)
        a2.set_xlim(0, T); fig.tight_layout(); png = f'{WORK}/{s}-m1-levels.png'; fig.savefig(png, dpi=105); plt.close(fig)
        subprocess.run(['scp', '-q', png, f'dev-mac:video-work/solana-bunker/{OUT}-levels.png'], check=True)
        R['stem_arrays'] = None
        rep['scenes'][s] = R
        globals().setdefault('_stems', {})[s] = stems
    # ---------------- music attacks in the rendered film-timeline music vs the intended times
    mu = np.concatenate([_stems[s]['music'] / rep['scenes'][s]['gain_lin'] for s in names])   # read below from disk too
    ev = []
    for g in seg_rows:
        for key, bar in (('film_in', g['bars'].split('-')[0]),):
            x = g[key]; m = flux_attack(mu, x - .06, x + .06)
            ev.append(dict(event=f"{g['id']} in (bar {bar})", intended_film=round(x, 4), measured_film=round(m, 4), err_ms=round(1000 * (m - x), 1)))
    for c in M.get('checks', []):
        x = Ff(c['scene'], c['frame']) if 'frame' in c else F(c['scene'], c['t']); g = [r for r in seg_rows if r['film_in'] - .1 <= x <= r['film_out'] + .6][0]
        m = flux_attack(mu, x - .06, x + .06); ev.append(dict(event=c['id'], intended_film=round(x, 4), measured_film=round(m, 4), err_ms=round(1000 * (m - x), 1), segment=g['id']))
    rep['music_attacks'] = ev
    # ---------------- continuity across the join (files read back from disk)
    un = dec(spec['music_unsplit']); p4 = dec(f"{SC[names[0]]['out']}-music.wav"); p5 = dec(f"{SC[names[1]]['out']}-music.wav")
    k4, k5 = rep['scenes'][names[0]]['gain_lin'], rep['scenes'][names[1]]['gain_lin']
    cat = np.concatenate([p4.astype(np.float64) / k4, p5.astype(np.float64) / k5])
    rep['continuity'] = dict(unsplit_samples=len(un), part_samples=[len(p4), len(p5)], join_sample=JOIN,
                             max_abs_diff_concat_vs_unsplit=float(np.abs(cat[:len(un)] - un).max()) if len(cat) == len(un) else 'length mismatch',
                             scene_gain_db=[round(20 * np.log10(k4), 3), round(20 * np.log10(k5), 3)], level_step_at_join_db=round(20 * np.log10(k5 / k4), 3),
                             samples_around_join=[float(x) for x in un[JOIN - 3:JOIN + 3]])
    for s in names: rep['scenes'][s].pop('stem_arrays', None)
    out = json.dumps(rep, indent=1, default=float)
    sh(f'cat > {q(spec["report"])}', inp=out.encode()); open(f'{WORK}/{spec["name"]}-report.json', 'w').write(out)
    print(json.dumps(dict(segments=seg_rows, music_attacks=ev, continuity=rep['continuity'], levels={k: v for k, v in rep['levels'].items() if k != 'automation'}), indent=1, default=float))
    for s in names:
        R = rep['scenes'][s]
        print(s, json.dumps({k: R[k] for k in ['loudnorm', 'video_identical', 'lag_samples', 'loudness_mp4', 'loudness_phone', 'guard']}, default=float))
        for r in R['sfx']: print(' ', r['id'], 'frame', r['frame'], r['frame_t'], 'hit', r['measured_hit'], 'err_ms', r['err_ms'], 'gain', r['gain_db'], 'under_speech', r['under_speech'])
        for p in R['picture']: print('  picture', p['id'], p['frame'], 'argmax', p['argmax_diff_frame'], p['diff'])


if __name__ == '__main__':
    main()
