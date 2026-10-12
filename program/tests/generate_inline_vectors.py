"""Regenerate public host vectors using the pinned C reference, never live keys.

Run from the repository root after `bash crypto/build_reference.sh`.
These deterministic keys and their signatures are disposable, publicly known
test material. Never fund their vault on any shared network.
"""
import hashlib
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from solders.pubkey import Pubkey
from client.actions import encode_intent
from client.journal import SigningJournal
from crypto.xmss import keygen, reference_verify, sign_at

OUT = Path(__file__).parent / "fixtures"
OUT.mkdir(exist_ok=True)
program = Pubkey.from_bytes(b"P" * 32)
state, _ = Pubkey.find_program_address([b"bunker_state", b"V" * 32], program)
treasury, _ = Pubkey.find_program_address([b"bunker_treasury", bytes(state)], program)
source, _ = Pubkey.find_program_address([b"bunker_token", bytes(state)], program)
public, secret = keygen(hashlib.sha256(b"bunker-native-inline-public-test-v1").digest() * 3)
new_public, new_secret = keygen(hashlib.sha256(b"bunker-native-inline-public-test-v1-new").digest() * 3)
(OUT / "public.bin").write_bytes(public)
(OUT / "new-public.bin").write_bytes(new_public)
base = dict(program_id=bytes(program), namespace=b"N" * 32, vault_id=b"V" * 32,
            state=bytes(state), treasury=bytes(treasury), mode=3, epoch=0, nonce=0)
vectors = [
    ("sol", dict(action=1, leaf_index=0, destination=b"D" * 32, amount=100), False),
    ("token", dict(action=2, leaf_index=1, token_program=bytes(Pubkey.from_string(
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")), mint=b"M" * 32,
        source=bytes(source), destination=b"D" * 32, amount=100, decimals=6), False),
    ("burn", dict(action=3, leaf_index=2, targets=[8, 9]), False),
    ("rotate", dict(action=4, leaf_index=3, new_mode=3, parameter_id=1,
        root=new_public[:32], public_seed=new_public[32:]), False),
    ("old-unused", dict(action=3, leaf_index=4, epoch=1, nonce=1, targets=[8, 9]), False),
    ("new-burn", dict(action=3, leaf_index=0, epoch=1, nonce=1, targets=[8, 9]), True),
]
with tempfile.TemporaryDirectory(prefix="bunker-native-public-vectors-") as directory:
    for name, fields, replacement in vectors:
        message = encode_intent(dict(base, **fields))
        pk, sk = (new_public, new_secret) if replacement else (public, secret)
        keyset = hashlib.sha256(pk).hexdigest()
        with SigningJournal(Path(directory) / keyset, keyset) as journal:
            signature = journal.sign(name, message, lambda i, m: sign_at(sk, i, m),
                                     fields["leaf_index"])["signature"]
        assert reference_verify(pk, message, signature)
        (OUT / f"{name}.intent").write_bytes(message)
        (OUT / f"{name}.sig").write_bytes(signature)
