#!/usr/bin/env python3
"""Scene 9's on-screen seed phrase (film-brief-s09-seed.md): a valid 24-word BIP-39 English mnemonic, never a funded one.
Entropy = SHA-256 of a fixed public string plus the first counter that gives 24 distinct words (reproducible; nobody holds a key for it), checksum = first 8 bits of SHA-256(entropy), per BIP-39.
Wordlist: pipeline/s09/bip39-english.txt, the canonical BIP-39 English list (checked against its known SHA-256 below).
usage (any box, stdlib only, from apps/web/film): python3 pipeline/s09/mnemonic.py  -> data/s09-mnemonic.js"""
import hashlib, json
WL = 'pipeline/s09/bip39-english.txt'
raw = open(WL, 'rb').read()
assert hashlib.sha256(raw).hexdigest() == '2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda', 'not the canonical BIP-39 English wordlist'
words = raw.decode().split()
assert len(words) == 2048
def phrase(n):   # 256 bits of entropy -> 24 words
    ent = hashlib.sha256(b'solana-bunker film scene 9: the seed card (on-screen prop, never funded) #%d' % n).digest()
    bits = bin(int.from_bytes(ent, 'big'))[2:].zfill(256) + bin(hashlib.sha256(ent).digest()[0])[2:].zfill(8)
    return ent, [words[int(bits[i * 11:(i + 1) * 11], 2)] for i in range(24)]
n = 0
while len(set(phrase(n)[1])) < 24: n += 1   # first counter with 24 distinct words (a repeated word reads as a typo on a backup card)
ent, m = phrase(n)
# round trip: words -> bits -> entropy + checksum
b2 = ''.join(bin(words.index(w))[2:].zfill(11) for w in m); e2 = int(b2[:256], 2).to_bytes(32, 'big')
assert e2 == ent and int(b2[256:], 2) == hashlib.sha256(e2).digest()[0]
open('data/s09-mnemonic.js', 'w').write('window.S09_WORDS = ' + json.dumps(m) + ';\n')
print(' '.join(m))
