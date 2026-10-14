#!/usr/bin/env python3
"""Merge parakeet token timestamps (JSON on stdin) into word timings; writes JSON to stdout.
usage: words.py < parakeet.json > words.json"""
import json, sys, re
d = json.load(sys.stdin)
words = []
for s in d['sentences']:
    for tk in s['tokens']:
        t, a, b = tk['text'], tk['start'], tk['end']
        if t.startswith(' ') or not words:
            words.append({'w': t.strip(), 's': a, 'e': b})
        else:
            words[-1]['w'] += t; words[-1]['e'] = b
# punctuation tokens are glued onto the previous word by the rule above
for w in words:
    w['w'] = re.sub(r'\s+', '', w['w'])
json.dump(words, sys.stdout, indent=1)
