#!/usr/bin/env python3
"""Masters the Solana Bunker film's sound effects from cues.tsv. A port of clan-world's
apps/android/tools/audio/master.py (same layering, EQ, event-loudness measurement, limiter and
re-render loop) for film use: stereo output, MP3 128 kbps instead of Ogg, no beds, true peak
checked against -3 dBTP.

Runs on dev-mac (encoding is banned on do-box). Standard library only. Needs Homebrew's ffmpeg-full.

    python3 master.py --src ~/audio-work/solana-bunker/src --out ~/audio-work/solana-bunker/out

--src holds freesound/fs<ID>-hq.ogg (HQ previews: stand-ins until originals are downloaded with a
freesound account) and kenney/kenney_<pack>/Audio/*.ogg. Outputs OUT/audition/<out>.mp3 and
OUT/work/ (intermediate WAVs). Each cue is rendered, measured (1 s of silence padded) and re-rendered
with a corrected gain until it lands within 0.3 LU of its target. Encoded files must read <= -3 dBTP
or the run fails.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FFMPEG = os.environ.get("FFMPEG") or next(
    (p for p in ("/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg",) if os.path.exists(p)), "ffmpeg")
RATE = 48000
TP_MAX = -3.0
MAX_GR = 8.0

MACROS = {
    "@SHELF": "treble=g=-4:f=7000,equalizer=f=3500:t=q:w=1.2:g=-2",
    "@MID": "equalizer=f=1500:t=q:w=1:g=3",
}
# High-pass and low-pass of each class.
CLASS = {
    "sting": (60, 16000), "sfx": (60, 14000),
}
KENNEY = {"casino": "kenney_casino-audio", "impact": "kenney_impact-sounds", "rpg": "kenney_rpg-audio"}


def macros(f):
    for k, v in MACROS.items():
        f = f.replace(k, v)
    return f


def run(args, **kw):
    return subprocess.run(args, check=True, capture_output=True, text=True, **kw)


def resolve(src_root, key):
    """(path, kind) for a source key; kind is 'original', 'preview' or 'pack'."""
    scheme, name = key.split(":", 1)
    if scheme == "fs":
        for ext in ("wav", "flac", "aif", "aiff", "mp3", "ogg"):
            p = os.path.join(src_root, "freesound", f"fs{name}.{ext}")
            if os.path.exists(p):
                return p, "original"
        p = os.path.join(src_root, "freesound", f"fs{name}-hq.ogg")
        if os.path.exists(p):
            return p, "preview"
        raise SystemExit(f"missing freesound source {name}")
    if scheme == "k":
        pack, stem = name.split("/", 1)
        p = os.path.join(src_root, "kenney", KENNEY[pack], "Audio", f"{stem}.ogg")
        if not os.path.exists(p):
            raise SystemExit(f"missing Kenney source {name}")
        return p, "pack"
    raise SystemExit(f"unknown source scheme {key}")


def parse_layers(spec):
    layers = []
    for chunk in spec.split("+"):
        parts = chunk.split("|")
        segs = []
        for s in parts[0].split("~"):
            src, rng = s.rsplit("@", 1)
            a, b = rng.split("-")
            segs.append((src, float(a), float(b)))
        opts = {"delay": 0.0, "gain": 0.0, "af": ""}
        for o in parts[1:]:
            k, v = o.split("=", 1)
            opts[k] = v if k == "af" else float(v)
        layers.append((segs, opts))
    return layers


def read_manifest(path):
    rows = []
    with open(path) as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            c = line.rstrip("\n").split("\t")
            if len(c) != 11:
                raise SystemExit(f"bad row ({len(c)} columns): {line!r}")
            rows.append(dict(zip(
                ["out", "cue", "cand", "ship", "class", "target", "fade_ms", "maxlen", "ceiling", "layers", "post"], c)))
    return rows


def graph(row, src_root, channels):
    """-i inputs and the filter graph that yields [pre]: layered, trimmed, EQ'd, before gain."""
    layers = parse_layers(row["layers"])
    inputs, idx, chains, labels = [], {}, [], []
    layout = "mono" if channels == 1 else "stereo"  # film: always stereo (channels=2)
    for li, (segs, opts) in enumerate(layers):
        seg_labels = []
        for si, (src, a, b) in enumerate(segs):
            path, _ = resolve(src_root, src)
            if path not in idx:
                idx[path] = len(idx)
                inputs += ["-i", path]
            lab = f"s{li}_{si}"
            chains.append(f"[{idx[path]}:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,aresample={RATE},"
                          f"aformat=sample_fmts=fltp:channel_layouts={layout}[{lab}]")
            seg_labels.append(lab)
        cur = seg_labels[0]
        for si, nxt in enumerate(seg_labels[1:], 1):
            out = f"x{li}_{si}"
            chains.append(f"[{cur}][{nxt}]acrossfade=d=0.25:c1=qsin:c2=qsin[{out}]")
            cur = out
        f = []
        if opts["af"]:
            f.append(macros(opts["af"]))
        if opts["gain"]:
            f.append(f"volume={opts['gain']}dB")
        if opts["delay"]:
            f.append(f"adelay=delays={int(opts['delay'])}:all=1")
        lab = f"l{li}"
        chains.append(f"[{cur}]{','.join(f) if f else 'anull'}[{lab}]")
        labels.append(lab)
    if len(labels) > 1:
        chains.append("".join(f"[{l}]" for l in labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest[mix]")
    else:
        chains.append(f"[{labels[0]}]anull[mix]")
    hp, lp = CLASS[row["class"]]
    pre = []
    pre += ["silenceremove=start_periods=1:start_threshold=-60dB",
            "areverse,silenceremove=start_periods=1:start_threshold=-65dB,areverse"]
    if row["maxlen"] != "-":
        pre.append(f"atrim=end={row['maxlen']},asetpts=PTS-STARTPTS")
    pre += [f"highpass=f={hp}:poles=2", f"lowpass=f={lp}:poles=2"]
    if row["post"] != "-":
        pre.append(macros(row["post"]))
    chains.append(f"[mix]{','.join(pre)}[pre]")
    return inputs, ";".join(chains)


def sample_peak(path):
    err = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=sample", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.search(r"Sample peak:\s+Peak:\s+(-?[\d.]+|-inf)", err[err.rfind("Summary:"):], re.S)
    return float(m.group(1))


def measure(path_or_args, pad=True):
    """(I, true peak) by ebur128; one-shots padded with 1 s of silence."""
    args = path_or_args if isinstance(path_or_args, list) else ["-i", path_or_args]
    af = ("apad=pad_dur=1," if pad else "") + "ebur128=peak=true"
    err = subprocess.run([FFMPEG, "-hide_banner", "-nostats", *args, "-af", af, "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summary = err[err.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+|-inf)", summary).group(1))
    tp = re.search(r"True peak:\s+Peak:\s+(-?[\d.]+|-inf)", summary, re.S)
    return i, float(tp.group(1)) if tp else float("nan")


def duration(path):
    ffprobe = os.path.join(os.path.dirname(FFMPEG), "ffprobe") if os.path.dirname(FFMPEG) else "ffprobe"
    out = run([ffprobe, "-v", "error",
               "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout
    return float(out.strip())


def oneshot(row, src_root, out_path, work):
    inputs, g = graph(row, src_root, 2)
    target = float(row["target"])
    ceiling = float(row["ceiling"]) if row["ceiling"] != "-" else -4.0
    limit = 10 ** (ceiling / 20)
    fade = int(row["fade_ms"]) / 1000
    pre_wav = os.path.join(work, row["out"] + ".pre.wav")
    run([FFMPEG, "-hide_banner", "-y", *inputs, "-filter_complex", g, "-map", "[pre]",
         "-c:a", "pcm_f32le", "-ar", str(RATE), "-ac", "2", pre_wav])
    i0, _ = measure(pre_wav)
    # A short knock can have more than 17 dB between its peak and its event loudness; reaching the
    # target under the ceiling would crush its attack. The limiter may take at most MAX_GR dB: a cue
    # that still falls short stays quieter (it is reported) rather than squashed.
    cap = ceiling - sample_peak(pre_wav) + MAX_GR
    gain = min(target - i0, cap)
    final_wav = os.path.join(work, row["out"] + ".wav")
    for _ in range(4):
        chain = (f"volume={gain:.2f}dB,alimiter=limit={limit:.4f}:attack=1:release=40:level=false:latency=true,"
                 f"afade=t=in:d=0.002,areverse,afade=t=in:d={fade}:curve=exp,areverse")
        run([FFMPEG, "-hide_banner", "-y", "-i", pre_wav, "-af", chain, "-c:a", "pcm_f32le", "-ar", str(RATE), final_wav])
        i1, _ = measure(final_wav)
        if abs(i1 - target) <= 0.3 or (gain >= cap and i1 < target):
            break
        gain = min(gain + target - i1, cap)
    run([FFMPEG, "-hide_banner", "-y", "-i", final_wav, "-c:a", "libmp3lame", "-b:a", "128k", "-ac", "2", "-ar", str(RATE),
         "-map_metadata", "-1", out_path])
    return {"pre_I": i0, "gain_db": round(gain, 2), "filters": g + " | " + chain + " | libmp3lame 128k stereo 48 kHz"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", help="comma-separated output stems")
    a = ap.parse_args()
    src_root, out_root = os.path.expanduser(a.src), os.path.expanduser(a.out)
    for d in ("audition", "work"):
        os.makedirs(os.path.join(out_root, d), exist_ok=True)
    work = os.path.join(out_root, "work")
    sources = {}
    with open(os.path.join(HERE, "SOURCES.tsv")) as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            c = line.rstrip("\n").split("\t")
            sources[c[0]] = {"url": c[1], "licence": c[3]}
    rows = read_manifest(os.path.join(HERE, "cues.tsv"))
    only = set(a.only.split(",")) if a.only else None
    prov = []
    failed = []
    for row in rows:
        if only and row["out"] not in only:
            continue
        out_path = os.path.join(out_root, "audition", f"{row['out']}.mp3")
        info = oneshot(row, src_root, out_path, work)
        i, tp = measure(out_path)
        dur = duration(out_path)
        keys = sorted({s for segs, _ in parse_layers(row["layers"]) for (s, _, _) in segs})
        used = [resolve(src_root, k) for k in keys]
        standins = [k for k, (_, kind) in zip(keys, used) if kind == "preview"]
        ok = tp <= TP_MAX
        if not ok:
            failed.append(row["out"])
        print(f"{'ok  ' if ok else 'FAIL'} {row['out']:24s} I={i:6.1f} LUFS (target {row['target']})  TP={tp:5.1f} dBTP  "
              f"{dur:5.2f}s  {os.path.getsize(out_path):7d} B" + (f"  stand-in: {','.join(standins)}" if standins else ""))
        prov.append([
            os.path.relpath(out_path, out_root), row["cue"], row["cand"], row["ship"],
            "; ".join(f"{k} <{sources.get(k, {}).get('url', '?')}> sha256:{sha256(p)[:16]}"
                      + (" (freesound HQ preview stand-in)" if kind == "preview" else "") for k, (p, kind) in zip(keys, used)),
            "; ".join(sorted({sources.get(k, {}).get("licence", "?") for k in keys})),
            f"{row['class']} target {row['target']} LUFS; measured I {i:.1f} LUFS, TP {tp:.1f} dBTP; {dur:.2f} s; "
            f"gain {info['gain_db']:+.2f} dB",
            info["filters"],
        ])
    if only:
        print("--only: PROVENANCE.tsv left as it was")
    else:
        with open(os.path.join(HERE, "PROVENANCE.tsv"), "w") as fh:
            fh.write("# Generated by master.py: one row per output file. Do not edit by hand.\n")
            fh.write("# file\tcue\tcandidate\tship\tsources (key <url> sha256 of the file used)\tlicence\tloudness\tprocessing\n")
            for p in prov:
                fh.write("\t".join(p) + "\n")
    if failed:
        raise SystemExit(f"true peak above {TP_MAX} dBTP: {', '.join(failed)}")


if __name__ == "__main__":
    main()
