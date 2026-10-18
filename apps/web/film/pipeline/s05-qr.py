#!/usr/bin/env python3
"""Writes data/s05-qr.js: QR matrices (rows of 0/1 strings, 1 px quiet zone added by the scene) for the see-the-code and proof boxes of slide 5.
v1 = array/hash vault, v2 = Merkle vault; code boxes point at program/src/lib.rs on main (line 113 = ARRAY arm, 114 = MERKLE arm), proof boxes at the Solscan devnet
withdrawal transactions in artifacts/public-deployment.json (v1-live-20261012-array-withdraw-sol 5mHxtbGL..., v1-live-20261012-merkle-withdraw-sol 5XPHXjBK...)."""
import json, qrcode
GH = 'https://github.com/chaintail/solana-bunker/blob/main/program/src/lib.rs#L'
SOL = 'https://solscan.io/tx/%s?cluster=devnet'
S1 = '5mHxtbGLuEhxVCDhRRc6A1pdpQzn3KgQyfvzSoUS4GzySBZ2AkDJQgKbwb3UrNaZ4rMEzJ2syQb3yvWw35TMhwjr'
S2 = '5XPHXjBKRvZJ5vNkEqDF5TXtk88ZZd96R92MuSxf7uAYRXTVER6AnYgDyqZoqEMe8Tn8zwez3hSRme1VZv9BaKBw'
def m(u):
    q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_M); q.add_data(u); q.make(fit=True)
    return [''.join('1' if c else '0' for c in row) for row in q.get_matrix()]
d = {'code1': m(GH + '113'), 'code2': m(GH + '114'), 'proof1': m(SOL % S1), 'proof2': m(SOL % S2)}
open('data/s05-qr.js', 'w').write('window.QR = ' + json.dumps(d) + ';\n'); print({k: len(v) for k, v in d.items()})
