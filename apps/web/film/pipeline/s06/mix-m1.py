#!/usr/bin/env python3
"""m1 (music): lays a music cue and sound effects under a finished scene and remuxes it with the picture copied (-c:v copy).
Shared by the scenes (pipeline/s06, s07, s09); the scene's placements are in its spec, pipeline/sNN/sNN-m1.json.
s06 additions: music.downbeat_in_track (the in downbeat's attack when the cut starts before it, so the check looks at the downbeat, not the cut) and a 200 ms guard window.

Runs on do-box with /home/claude/venvs/manim/bin/python3 (numpy, scipy, matplotlib):  python3 mix-m1.py pipeline/s07/s07-m1.json
Every ffmpeg call runs on dev-mac over ssh (ffmpeg is banned on do-box); on dev-mac itself (Darwin) the same calls run locally.
Paths in the spec are relative to the scene directory on dev-mac (~/video-work/solana-bunker/sNN) unless they start with ~ or /.

Audio (mono 48 kHz, as every scene mix):
  dialogue  the scene's delivered mix (out/.../audio-final.wav: voice, brown bed, the scene's limiter), unchanged.
  music     the cue as (L+R)/2, gained to -16 LUFS (so the plan's dB figures are gain on a -16 LUFS cue), 180 Hz high-pass (2-pole),
            cut in at a measured downbeat (spec music.track_in -> music.scene_in, 5 ms head fade).
            Level: -20 dB under speech, -14 dB in speech gaps of 0.8 s or more (speech = 20 ms RMS >= -40 dBFS on the dialogue,
            sub-0.15 s holes bridged); ramps linear in dB, 300 ms release after the last word, 100 ms attack ending on the next word.
            Dialogue guard (as s08 score.py): in every 100 ms window (10 ms hop) where the dialogue is active (RMS >= -30 dBFS) the music
            is held 16 dB under it by a gain trim (attack 60 dB/s, release 20 dB/s; the trim treats windows from -32 dBFS as active, since
            the loudnorm gain that follows can lift the dialogue by up to 2 dB). Out: a raised-cosine fade (spec music.fade).
  sfx       each file as (L+R)/2, gained to -20 LUFS event loudness (ebur128 with 1 s of padded silence, as film/sfx master.py),
            then the spec gain (0 in the clear, -6 under speech); its hit (spec 'hit', seconds into the file) lands on the picture frame.
  mix       dialogue + music + sfx -> loudnorm pass 1 (measure) -> pass 2 as one linear gain -> the scene's limiter with latency=1 (the
            lookahead is compensated, so the dialogue stays where the delivered mix had it); the gain is corrected until the limited file
            reads -16.0 LUFS -> out/<name>-audio.wav. (loudnorm's own pass 2 falls back to dynamic mode on these mixes, because the delivered
            dialogue's limiter peaks already sit above its true-peak target.)
  stems     out/<name>-dialogue.wav, -music.wav, -sfx.wav (float, after the loudnorm gain, before the limiter; they sum to the mix).
Video: out/<name>.mp4 and out/<name>-phone.mp4 copy the source master's and phone cut's video streams; audio AAC 192k / 128k.
Checks (out/<name>-report.json, out/<name>-levels.png, out/<name>-event-frames.png: frames f-3..f+2 of every picture check): video stream md5 = source; music in/out and every SFX hit vs its frame (20 ms);
dialogue guard minimum; dialogue lag vs the delivered mix; AAC lag; loudness of the muxed file; picture frame metrics per event."""
import json, os, platform, re, shlex, subprocess, sys
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
LOCAL = platform.system() == 'Darwin'
WORK = os.environ.get('M1_WORK', '/tmp')   # local scratch for the plot and the report copy
FFDIR = '/opt/homebrew/opt/ffmpeg-full/bin/'


def sh(cmd, inp=None, cwd=None):
    """run a shell command on dev-mac (ffmpeg lives there); returns (stdout bytes, stderr str)"""
    if cwd: cmd = f'cd {cwd} && {cmd}'
    full = ['bash', '-c', cmd] if LOCAL else ['ssh', 'dev-mac', cmd]
    r = subprocess.run(full, input=inp, capture_output=True)
    if r.returncode: raise RuntimeError(f'{cmd}\n{r.stderr.decode()[-2000:]}')
    return r.stdout, r.stderr.decode()


def q(p):  # quote a dev-mac path, keeping a leading ~ expandable
    return '~/' + shlex.quote(p[2:]) if p.startswith('~/') else shlex.quote(p)


FF = FFDIR + 'ffmpeg -nostdin -hide_banner'
RAW = f'-f f32le -ar {SR} -ac 1'


def dec(path, ch=1):
    out, _ = sh(f'{FF} -v error -i {q(path)} -ar {SR} -f f32le -', cwd=D)
    x = np.frombuffer(out, dtype=np.float32)
    return x.reshape(-1, 2).mean(1) if ch == 2 else x.copy()


def lufs(x, pad=0.0):
    if pad: x = np.concatenate([x, np.zeros(int(pad * SR), np.float32)])
    _, err = sh(f'{FF} -nostats {RAW} -i - -af ebur128=peak=true -f null -', inp=x.astype(np.float32).tobytes())
    s = err[err.rfind('Summary'):]
    return dict(I=float(re.search(r'I:\s+(-?[\d.]+) LUFS', s).group(1)), LRA=float(re.search(r'LRA:\s+(-?[\d.]+) LU', s).group(1)),
                TP=float(re.search(r'Peak:\s+(-?[\d.inf]+) dBFS', s).group(1)))


def wav(x, path, codec='pcm_f32le'):
    sh(f'{FF} -v error -y {RAW} -i - -c:a {codec} {q(path)}', inp=x.astype(np.float32).tobytes(), cwd=D)


def ffilter(x, af):
    out, err = sh(f'{FF} -nostats {RAW} -i - -af {shlex.quote(af)} -ar {SR} -ac 1 -f f32le -', inp=x.astype(np.float32).tobytes())
    return np.frombuffer(out, dtype=np.float32).copy(), err


def rms_db(x, win, hop, n_out=None):
    """RMS in dB of windows of `win` s centred on 0, hop, 2 hop, ..."""
    c = np.concatenate([[0.0], np.cumsum(x.astype(np.float64) ** 2)]); w = int(win * SR); h = int(hop * SR)
    n = n_out or len(x) // h + 1; ctr = np.arange(n) * h; a = np.clip(ctr - w // 2, 0, len(x)); b = np.clip(ctr + w // 2, 0, len(x))
    e = (c[b] - c[a]) / np.maximum(b - a, 1); return 10 * np.log10(e + 1e-12)


def speech_runs(d, thr=-40.0, bridge=.15, min_run=.04):
    act = rms_db(d, .02, .01) >= thr; runs = []; i = 0
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


def onset_env(x, t0, t1, rel=-12.0):
    """first 1 ms block in [t0, t1] whose peak is within `rel` dB of the window's peak (the transient)"""
    a, b = max(0, int(t0 * SR)), int(t1 * SR); n = 48; s = np.abs(x[a:b]); k = len(s) // n; e = s[:k * n].reshape(k, n).max(1)
    return a / SR + int(np.argmax(e >= e.max() * 10 ** (rel / 20))) * n / SR


def flux_peak(x, t0, t1, hop=240, N=2048):
    """time of the largest spectral-flux frame in [t0, t1] (a downbeat on legato material)"""
    a = int(t0 * SR) - N // 2; w = np.hanning(N); S = []
    for i in range(a, int(t1 * SR) - N // 2, hop):
        seg = x[max(0, i):i + N]
        if len(seg) < N: seg = np.pad(seg, (N - len(seg), 0))
        S.append(np.log1p(np.abs(np.fft.rfft(seg * w)) * 10))
    S = np.array(S); f = np.maximum(np.diff(S, axis=0), 0).sum(1)
    return (a + N // 2) / SR + (int(np.argmax(f)) + 1) * hop / SR


def rms_peak(x, t0, t1, win=.05):
    a, b = int(t0 * SR), int(t1 * SR); n = int(win * SR); r = np.convolve(x[a:b] ** 2, np.ones(n) / n, 'same'); return t0 + int(np.argmax(r)) / SR


def ramp_db(t, pts):
    return np.interp(t, [p[0] for p in pts], [p[1] for p in pts])


def main():
    global D
    spec = json.load(open(sys.argv[1])); D = spec['dir']; FPS = spec['fps']; NF = spec['frames']; T = NF / FPS; N = int(round(T * SR))
    name = spec['name']; OUT = f'out/{name}'; ft = lambda k: k / FPS
    rep = dict(scene=spec['scene'], name=name, length_s=T, frames=NF)
    # ---------------- dialogue
    d = dec(spec['dialogue']); assert abs(len(d) - N) <= 2, (len(d), N); d = np.pad(d, (0, max(0, N - len(d))))[:N]
    runs = speech_runs(d); rep['speech_runs'] = [[round(a, 2), round(b, 2)] for a, b in runs]
    gaps = [[runs[i][1], runs[i + 1][0]] for i in range(len(runs) - 1)] + [[runs[-1][1], T]]
    gaps = [g for g in gaps if g[1] - g[0] >= spec['music']['gap_min']]
    # ---------------- music
    M = spec['music']; m2 = dec(M['file'], ch=2); mono_I = lufs(m2)['I']; m2 *= 10 ** ((M['ref_lufs'] - mono_I) / 20)
    m2 = sosfilt(butter(2, M['highpass'], 'highpass', fs=SR, output='sos'), m2).astype(np.float32)
    s0 = int(round(M['scene_in'] * SR)); a0 = int(round(M['track_in'] * SR)); music = np.zeros(N, np.float32)
    seg = m2[a0:a0 + (N - s0)]; music[s0:s0 + len(seg)] = seg
    t = np.arange(N) / SR; U, G = M['under'], M['gap']
    lev = np.full(N, U, np.float64)
    for g0, g1 in gaps:
        if g1 <= M['scene_in']: continue
        end = g1 >= T - 1e-6; pts = [(g0, U), (g0 + M['release'], G)] + ([(T + 1, G)] if end else [(g1 - M['attack'], G), (g1, U)])
        m = (t >= g0) & (t < (T + 1 if end else g1)); lev[m] = np.maximum(lev[m], ramp_db(t[m], pts))
    gain = 10 ** (lev / 20)
    head = int(M['head_fade'] * SR); gain[s0:s0 + head] *= .5 - .5 * np.cos(np.pi * np.arange(head) / head)
    f0, f1 = M['fade']; fm = (t >= f0); gain[fm] *= np.where(t[fm] < f1, .5 + .5 * np.cos(np.pi * (t[fm] - f0) / (f1 - f0)), 0)
    gain[:s0] = 0; music = music * gain
    # dialogue guard (100 ms windows, 10 ms hop): music >= GUARD dB under the active dialogue, trimmed with a smooth gain
    hop = .01; nh = int(T / hop) + 1; vdb = rms_db(d, .1, hop, nh); GD, VA = spec['guard_db'], spec['voice_active_db']; trim = np.ones(N)
    vdb2 = rms_db(d, .2, hop, nh)   # s06: the guard holds in 200 ms windows too
    for it in range(8):
        mdb = rms_db(music * trim, .1, hop, nh); act = (vdb >= VA - 2) & (mdb > -90)   # 2 dB below the check's threshold: the loudnorm gain comes later
        need = np.where(act, np.minimum(0, vdb - (GD + .3) - mdb), 0.0)
        mdb2 = rms_db(music * trim, .2, hop, nh); act2 = (vdb2 >= VA - 2) & (mdb2 > -90)
        need = np.minimum(need, np.where(act2, np.minimum(0, vdb2 - (GD + .3) - mdb2), 0.0))
        if need.min() > -.05: break
        g = 10 ** (np.array([need[max(0, i - 10):i + 11].min() for i in range(nh)]) / 20)
        for i in range(1, nh): g[i] = min(g[i], g[i - 1] * 10 ** (20 * hop / 20))
        for i in range(nh - 2, -1, -1): g[i] = min(g[i], g[i + 1] * 10 ** (60 * hop / 20))
        trim *= np.interp(t, np.arange(nh) * hop, g)
    music_placed = music.astype(np.float32)   # s06: before the guard trim, for the placement check of the in/out downbeats
    music = (music * trim).astype(np.float32); sp = np.zeros(N, bool)
    for a, b in runs: sp[int(a * SR):int(b * SR)] = True
    sp[:s0] = False
    rep['music'] = dict(file=M['file'], mono_lufs=mono_I, gain_to_ref_db=round(M['ref_lufs'] - mono_I, 2), track_in=M['track_in'], scene_in=M['scene_in'],
                        gaps_at_gap_level=[[round(a, 2), round(b, 2)] for a, b in gaps if b > M['scene_in']], guard_trim_max_db=round(float(20 * np.log10(trim[s0:].min())), 1),
                        guard_trim_s_over_3db=round(float((trim[s0:] < 10 ** (-3 / 20)).sum() / SR), 2),
                        guard_trim_median_db_under_speech=round(float(20 * np.log10(np.median(trim[sp]))), 1) if sp.any() else None)
    # ---------------- sfx
    sfx = np.zeros(N, np.float32); rep['sfx'] = []
    for e in spec['sfx']:
        x = dec(e['file'], ch=2); I0 = lufs(x, pad=1.0)['I']; x = x * 10 ** ((spec['sfx_ref_lufs'] - I0 + e['gain']) / 20)
        at = ft(e['frame']) - e['hit']; i0 = int(round(at * SR)); a = max(0, -i0); b = min(len(x), N - i0)
        sfx[i0 + a:i0 + b] += x[a:b]
        rep['sfx'].append(dict(id=e['id'], file=e['file'], frame=e['frame'], frame_t=round(ft(e['frame']), 4), hit_in_file=e['hit'], file_start=round(at, 4),
                               mono_event_lufs_raw=I0, gain_db=e['gain'], under_speech=any(r[0] - .05 <= ft(e['frame']) <= r[1] + .05 for r in runs)))
    # ---------------- mix, loudnorm (two pass, linear), limiter
    mix = d + music + sfx
    # pass 1: loudnorm measures the mix; pass 2: that linear gain, then the scene's limiter; the gain is corrected until the limited file
    # reads -16.0 LUFS (loudnorm's own pass 2 drops to dynamic mode here, because the delivered dialogue's limiter peaks already sit above
    # its true-peak target, and the s07 limiter's auto level adds 20 log(1/limit) dB after it)
    _, err = ffilter(mix, 'loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json')
    m1 = json.loads(err[err.rfind('{'):err.rfind('}') + 1]); gdb = -16.0 - float(m1['input_i']); hist = []
    for it in range(4):
        k = 10 ** (gdb / 20); fin, _ = ffilter(mix * k, spec['limiter']); fin = np.pad(fin, (0, max(0, N - len(fin))))[:N]
        If = lufs(fin)['I']; hist.append([round(gdb, 3), If])
        if abs(If + 16.0) <= .05: break
        gdb += -16.0 - If
    rep['loudnorm'] = dict(pass1_input_i=float(m1['input_i']), pass1_input_tp=float(m1['input_tp']), linear_gain_db=round(gdb, 3), gain_then_final_lufs=hist)
    stems = dict(dialogue=d * k, music=music * k, sfx=sfx * k)
    for s, x in stems.items(): wav(x, f'{OUT}-{s}.wav')
    wav(fin, f'{OUT}-audio.wav', 'pcm_s24le')
    # ---------------- remux, picture copied
    for src, dst, br in [(spec['master'], f'{OUT}.mp4', '192k'), (spec['phone'], f'{OUT}-phone.mp4', '128k')]:
        sh(f'{FF} -v error -y -i {q(src)} -i {q(OUT + "-audio.wav")} -map 0:v -map 1:a -c:v copy -c:a aac -b:a {br} -ac 1 -movflags +faststart -shortest {q(dst)}', cwd=D)
    # ---------------- checks
    vmd5 = lambda p: re.search(r'MD5=(\w+)', sh(f'{FF} -v error -i {q(p)} -map 0:v -c copy -f md5 -', cwd=D)[0].decode()).group(1)
    rep['video_md5'] = {p: vmd5(p) for p in [spec['master'], f'{OUT}.mp4', spec['phone'], f'{OUT}-phone.mp4']}
    rep['video_identical'] = dict(master=rep['video_md5'][spec['master']] == rep['video_md5'][f'{OUT}.mp4'], phone=rep['video_md5'][spec['phone']] == rep['video_md5'][f'{OUT}-phone.mp4'])
    probe = lambda p: sh(f'{FFDIR}ffprobe -v error -count_frames -show_entries stream=codec_type,nb_read_frames,duration -of compact {q(p)}', cwd=D)[0].decode().strip()
    rep['probe'] = {p: probe(p) for p in [f'{OUT}.mp4', f'{OUT}-phone.mp4']}
    dm = dec(f'{OUT}.mp4'); dm = np.pad(dm, (0, max(0, N - len(dm))))[:N]
    def lag(a, b, L=600, w=(2, 12)):  # samples b lags a
        A = a[int(w[0] * SR):int(w[1] * SR)]; return max(range(-L, L + 1), key=lambda l: float(np.dot(A, b[int(w[0] * SR) + l:int(w[1] * SR) + l])))
    rep['lag_samples'] = dict(final_vs_dialogue=lag(d, fin), mp4_vs_final=lag(fin, dm))
    rep['loudness_mp4'] = lufs(dm); rep['loudness_final_wav'] = lufs(fin)
    # dialogue guard on the final stems (100 ms windows, 10 ms hop, dialogue active >= -30 dBFS after the loudnorm gain)
    vdb = rms_db(stems['dialogue'], .1, hop, nh); mdb = rms_db(stems['music'], .1, hop, nh); xdb = rms_db(stems['sfx'], .1, hop, nh)
    act = (vdb >= VA) & (mdb > -90); mg = (vdb - mdb)[act]
    nb = int(T / .1); vb = rms_db(stems['dialogue'], .1, .1, nb)[1:]; mb = rms_db(stems['music'], .1, .1, nb)[1:]  # non-overlapping grid (centres .1, .2 ...)
    ab = (vb >= VA) & (mb > -90)
    ax = (vdb >= VA) & (xdb > -90)
    v2 = rms_db(stems['dialogue'], .2, hop, nh); m2w = rms_db(stems['music'], .2, hop, nh); a2 = (v2 >= VA) & (m2w > -90)
    rep['guard'] = dict(windows_hop10ms=int(act.sum()), min_db=round(float(mg.min()), 2) if act.any() else None, median_db=round(float(np.median(mg)), 1) if act.any() else None,
                        min_at_s=round(float(np.arange(nh)[act][np.argmin(mg)] * hop), 2) if act.any() else None,
                        windows_grid100ms=int(ab.sum()), min_grid_db=round(float((vb - mb)[ab].min()), 2) if ab.any() else None,
                        windows200_hop10ms=int(a2.sum()), min200_db=round(float((v2 - m2w)[a2].min()), 2) if a2.any() else None,
                        min200_at_s=round(float(np.arange(nh)[a2][np.argmin((v2 - m2w)[a2])] * hop), 2) if a2.any() else None,
                        sfx_vs_dialogue_min_db=round(float((vdb - xdb)[ax].min()), 2) if ax.any() else None,
                        sfx_vs_dialogue_min_at_s=round(float(np.arange(nh)[ax][np.argmin((vdb - xdb)[ax])] * hop), 2) if ax.any() else None)
    # onsets in the stems vs the picture frames
    ms = stems['music']; nz = np.nonzero(np.abs(ms) > 1e-7)[0]
    on = dict(music_first_sample=round(nz[0] / SR, 4), music_last_sample=round(nz[-1] / SR, 4), music_in_frame=M['frame_in'], music_in_frame_t=round(ft(M['frame_in']), 4))
    xi = M['scene_in'] + M.get('downbeat_in_track', M['track_in']) - M['track_in']; on['music_in_downbeat_expected'] = round(xi, 4)
    on['music_in_downbeat'] = round(flux_peak(ms, xi - .05, xi + .05) if 'downbeat_in_track' in M else flux_peak(ms, M['scene_in'] - .02, M['scene_in'] + .08), 4)
    on['music_in_err_ms'] = round((on['music_in_downbeat'] - ft(M['frame_in'])) * 1000, 1)
    if M.get('out_downbeat_track') is not None:
        xo = M['scene_in'] + M['out_downbeat_track'] - M['track_in']; on['music_out_downbeat_expected'] = round(xo, 4)
        on['music_out_downbeat_measured'] = round(flux_peak(ms, xo - .08, xo + .08), 4)
    on['music_in_downbeat_untrimmed'] = round(flux_peak(music_placed, on['music_in_downbeat_expected'] - .05, on['music_in_downbeat_expected'] + .05), 4) if 'downbeat_in_track' in M else None
    if M.get('out_downbeat_track') is not None: on['music_out_downbeat_untrimmed'] = round(flux_peak(music_placed, xo - .08, xo + .08), 4)
    on['music_fade'] = M['fade']; on['next_downbeat_after_end'] = M.get('next_downbeat_note')
    on['music_out_last_frame_t'] = round(ft(NF - 1), 4)
    ss = stems['sfx']
    for r, e in zip(rep['sfx'], spec['sfx']):
        tf = ft(e['frame'])
        r['measured_hit'] = round(rms_peak(ss, tf - .35, tf + .35) if e.get('swell') else onset_env(ss, tf - .04, tf + .04), 4)
        r['err_ms'] = round((r['measured_hit'] - tf) * 1000, 1)
    rep['onsets'] = on
    # picture: per event, mean |diff| and mean luma rise frame-to-frame around the frame (gray 160x90 of the master)
    raw, _ = sh(f'{FF} -v error -i {q(spec["master"])} -vf scale=160:90,format=gray -f rawvideo -', cwd=D)
    V = np.frombuffer(raw, np.uint8).reshape(-1, 90, 160).astype(np.float32); dif = np.r_[0, np.abs(np.diff(V, axis=0)).mean((1, 2))]; up = np.r_[0, np.diff(V.mean((1, 2)))]
    pic = []
    for ev in spec['picture_checks']:
        f = ev['frame']; rng = range(max(1, f - 4), min(len(V), f + 5)); met = dif if ev['metric'] == 'diff' else up
        pic.append(dict(id=ev['id'], frame=f, metric=ev['metric'], argmax_frame=int(max(rng, key=lambda i: met[i])), values={i: round(float(met[i]), 2) for i in rng}))
    rep['picture'] = pic; rep['video_frames_decoded'] = len(V)
    # contact sheet: frames f-3 .. f+2 of every picture check, one row each, labelled with the frame number (out/<name>-event-frames.png)
    sel = '+'.join(f'between(n,{c["frame"] - 3},{c["frame"] + 2})' for c in spec['picture_checks'])
    vf = (f"drawtext=text='f%{{n}}':x=8:y=8:fontsize=40:fontcolor=yellow:box=1:boxcolor=black@0.7,select='{sel}',scale=320:180,"
          f"tile=6x{len(spec['picture_checks'])}:padding=4:color=white")
    sh(f'{FF} -v error -y -i {q(spec["master"])} -vf {shlex.quote(vf)} -frames:v 1 {q(OUT + "-event-frames.png")}', cwd=D)
    if not LOCAL: subprocess.run(['scp', '-q', f'dev-mac:{D[2:]}/{OUT}-event-frames.png', f'{WORK}/{name}-event-frames.png'], check=True)
    # ---------------- level plot
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    tt = np.arange(nh) * hop
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(16, 8.5), sharex=True, gridspec_kw=dict(height_ratios=[3, 1.3]))
    for x, c, lb in [(vdb, '#2a6fdb', 'dialogue'), (mdb, '#d9822b', 'music'), (xdb, '#1a9e5a', 'sfx')]:
        a1.plot(tt, np.maximum(x, -70), color=c, lw=1.1, label=lb + ' (100 ms RMS)')
    for a, b in runs: a1.axvspan(a, b, color='#2a6fdb', alpha=.06, lw=0)
    for r in rep['sfx']:
        a1.axvline(r['frame_t'], color='#1a9e5a', ls=':', lw=1); a1.text(r['frame_t'], -12, f" {r['id']}\n f{r['frame']}", fontsize=7.5, color='#1a6e3a', va='top')
    a1.axvline(ft(M['frame_in']), color='#d9822b', ls='--', lw=1.2); a1.text(ft(M['frame_in']), -4, f" music in f{M['frame_in']}", fontsize=8, color='#a0561b', va='top')
    if M.get('out_downbeat_track') is not None: a1.axvline(M['scene_in'] + M['out_downbeat_track'] - M['track_in'], color='#d9822b', ls=':', lw=1)
    a1.axvspan(f0, f1, color='#d9822b', alpha=.08, lw=0)
    a1.set_ylim(-70, 0); a1.set_ylabel('dBFS'); a1.legend(loc='lower left', fontsize=8); a1.grid(alpha=.25)
    a1.set_title(f"{name}: levels after the loudnorm gain (shaded blue = speech; dotted green = SFX frames; dashed orange = music in)", fontsize=10)
    a2.plot(tt[act], (vdb - mdb)[act], '.', ms=2.5, color='#7a3fb0', label='dialogue minus music, active windows')
    a2.axhline(GD, color='#c0392b', lw=1, label=f'{GD:.0f} dB guard'); a2.set_ylim(0, 60); a2.set_ylabel('dB'); a2.set_xlabel('scene seconds'); a2.grid(alpha=.25); a2.legend(loc='upper left', fontsize=8)
    a2.set_xlim(0, T); fig.tight_layout(); png = f'{WORK}/{name}-levels.png'; fig.savefig(png, dpi=110)
    if LOCAL: os.replace(png, os.path.expanduser(f'{D}/{OUT}-levels.png'))
    else: subprocess.run(['scp', '-q', png, f'dev-mac:{D[2:] if D.startswith("~/") else D}/{OUT}-levels.png'], check=True)
    rep['levels_png_local'] = png
    _, _ = sh(f'cat > {q(OUT + "-report.json")}', inp=json.dumps(rep, indent=1).encode(), cwd=D)
    json.dump(rep, open(f'{WORK}/{name}-report.json', 'w'), indent=1)
    print(json.dumps({k: rep[k] for k in ['music', 'loudnorm', 'video_identical', 'lag_samples', 'loudness_mp4', 'guard', 'onsets']}, indent=1))
    for r in rep['sfx']: print(r['id'], 'frame', r['frame'], r['frame_t'], 'hit', r['measured_hit'], 'err_ms', r['err_ms'], 'gain', r['gain_db'], 'under_speech', r['under_speech'])
    for p in pic: print('picture', p['id'], 'frame', p['frame'], p['metric'], 'argmax', p['argmax_frame'], p['values'])


if __name__ == '__main__':
    main()
