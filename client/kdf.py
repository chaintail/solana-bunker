"""Project seed recipe v1. BIP39 seed derivation is separate from key derivation."""
import hashlib
import hmac
import struct
import unicodedata
from .actions import octets, number

SALT = b"Solana-Bunker-KDF-v1"

def bip39_seed(mnemonic, passphrase=""):
    # Seed conversion only: callers must validate entropy/checksum with their BIP39 wallet.
    password = unicodedata.normalize("NFKD", mnemonic).encode()
    salt = ("mnemonic"+unicodedata.normalize("NFKD", passphrase)).encode()
    return hashlib.pbkdf2_hmac("sha512", password, salt, 2048, 64)

def hkdf(seed, info, length):
    if not 1 <= length <= 255*32:
        raise ValueError("HKDF length out of range")
    prk = hmac.new(SALT, seed, hashlib.sha256).digest()
    result, previous = b"", b""
    for counter in range(1, (length+31)//32+1):
        previous = hmac.new(prk, previous+info+bytes([counter]), hashlib.sha256).digest()
        result += previous
    return result[:length]

def derive(seed, vault_id, mode, generation, label, length=32):
    if not isinstance(seed,bytes) or len(seed) < 32:
        raise ValueError("seed must have at least 32 bytes")
    if not isinstance(label,str) or not label.isascii() or not 1 <= len(label) <= 64:
        raise ValueError("invalid label")
    info = b"BUNKER-SEED\x00\x01" + octets(vault_id) + bytes([number(mode,8)]) + struct.pack("<Q", number(generation,64)) + bytes([len(label)]) + label.encode()
    return hkdf(seed, info, length)

def fixture_secrets(seed, vault_id, generation, count):
    # Mode=0 is an explicit shared disposable ARRAY/MERKLE comparison domain.
    return [derive(seed, vault_id, 0, generation, f"baseline-secret-{i}") for i in range(count)]

def xmss_seeds(seed, vault_id, generation):
    return tuple(derive(seed, vault_id, 3, generation, label) for label in ("xmss-sk-seed", "xmss-sk-prf", "xmss-pub-seed"))
