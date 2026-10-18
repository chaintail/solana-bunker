#!/usr/bin/env python3
"""s04/s05 m2: prove the split music stems concatenate to the one render. Runs on do-box (/home/claude/venvs/manim).
usage: continuity-m2.py <unsplit.wav> <s04 prefix> <s05 prefix>   (prefix = music-m2-workshop.py's per-scene prefix; reads <prefix>-loudness.json from
  finish-m3.py and the stems it wrote, <prefix>-music.f32.wav at the scene's final gain)"""
import sys, os, json, importlib.util
import numpy as np

here = os.path.dirname(os.path.abspath(__file__))
s_ = importlib.util.spec_from_file_location('m4', os.path.join(here, 'music-m4.py')); M = importlib.util.module_from_spec(s_); s_.loader.exec_module(M)
un = M.read(sys.argv[1]); parts, gains = [], []
for p in sys.argv[2:4]:
    g = json.load(open(p + '-loudness.json'))['linear_gain_db']; gains.append(g)
    parts.append(M.read(p + '-music.f32.wav') / 10 ** (g / 20))
cat = np.concatenate(parts)
r = {'unsplit_samples': len(un), 'part_samples': [len(x) for x in parts], 'scene_gain_db': gains, 'level_step_at_join_db': round(gains[1] - gains[0], 3),
     'max_abs_diff_concat_vs_unsplit': float(np.abs(cat - un).max()) if len(cat) == len(un) else 'length mismatch', 'unsplit_peak': float(np.abs(un).max())}
print(json.dumps(r))
json.dump(r, open(os.path.join(os.path.dirname(sys.argv[2]), 's04-s05-m2-continuity.json'), 'w'), indent=1)
