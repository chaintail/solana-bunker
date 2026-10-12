"""Canonical application intent v1 (XMSS signature encoding remains RFC 8391)."""
import struct

MAGIC = b"BUNKER\x00\x01"
SECRET_ARRAY_V1, MERKLE_SECRET_V1, XMSS_SHA2_10_256_V1 = 1, 2, 3
WITHDRAW_SOL, WITHDRAW_TOKEN, BURN_LEAVES, ROTATE_ROOT = 1, 2, 3, 4
HEADER_BYTES = 190
MAX_BURN = 32
IDENTITIES = ("program_id", "namespace", "vault_id", "state", "treasury")

def octets(value, size=32):
    if isinstance(value, str):
        value = bytes.fromhex(value)
    if not isinstance(value, bytes) or len(value) != size:
        raise ValueError(f"expected {size} bytes")
    return value

def number(value, bits):
    if isinstance(value, str) and value.isascii() and value.isdecimal():
        value = int(value)
    if type(value) is not int or not 0 <= value < (1 << bits):
        raise ValueError(f"expected uint{bits}")
    return value

def burn_targets(targets, leaf_index):
    values = [number(x, 32) for x in targets]
    if not 1 <= len(values) <= MAX_BURN or values != sorted(set(values)):
        raise ValueError("burn targets must be 1..32 sorted unique indices")
    if leaf_index in values:
        raise ValueError("burn signer must be distinct from targets")
    return values

def encode_intent(intent):
    mode = number(intent["mode"], 8)
    action = number(intent["action"], 8)
    if mode not in (1, 2, 3) or action not in (1, 2, 3, 4):
        raise ValueError("unknown mode/action")
    leaf = number(intent["leaf_index"], 32)
    header = MAGIC + b"".join(octets(intent[k]) for k in IDENTITIES)
    header += struct.pack("<BQQIB", mode, number(intent["epoch"], 64), number(intent["nonce"], 64), leaf, action)
    if action == WITHDRAW_SOL:
        payload = octets(intent["destination"]) + struct.pack("<Q", number(intent["amount"], 64))
    elif action == WITHDRAW_TOKEN:
        payload = b"".join(octets(intent[k]) for k in ("token_program", "mint", "source", "destination"))
        payload += struct.pack("<QB", number(intent["amount"], 64), number(intent["decimals"], 8))
    elif action == BURN_LEAVES:
        values = burn_targets(intent["targets"], leaf)
        payload = bytes([len(values)]) + b"".join(struct.pack("<I", x) for x in values)
    else:
        if mode != 3 or number(intent["new_mode"], 8) != 3 or number(intent["parameter_id"], 32) != 1:
            raise ValueError("rotation requires XMSS-SHA2_10_256 parameter 1")
        payload = struct.pack("<BI", 3, 1) + octets(intent["root"]) + octets(intent["public_seed"])
    return header + payload

def parse_intent(data):
    if not isinstance(data, bytes) or len(data) < HEADER_BYTES or data[:8] != MAGIC:
        raise ValueError("invalid intent header")
    out = {k: data[8 + 32*i:40 + 32*i] for i, k in enumerate(IDENTITIES)}
    out.update(zip(("mode", "epoch", "nonce", "leaf_index", "action"), struct.unpack("<BQQIB", data[168:190])))
    body, action = data[190:], out["action"]
    if action == 1 and len(body) == 40:
        out.update(destination=body[:32], amount=struct.unpack("<Q", body[32:])[0])
    elif action == 2 and len(body) == 137:
        out.update({k: body[32*i:32*(i+1)] for i, k in enumerate(("token_program", "mint", "source", "destination"))})
        out.update(amount=struct.unpack("<Q", body[128:136])[0], decimals=body[136])
    elif action == 3 and body and len(body) == 1 + body[0]*4:
        out["targets"] = [struct.unpack("<I", body[1+4*i:5+4*i])[0] for i in range(body[0])]
    elif action == 4 and len(body) == 69:
        out.update(new_mode=body[0], parameter_id=struct.unpack("<I", body[1:5])[0], root=body[5:37], public_seed=body[37:69])
    else:
        raise ValueError("invalid action payload size or action")
    if encode_intent(out) != data:
        raise ValueError("noncanonical intent")
    return out

def json_intent(intent):
    return {k: v.hex() if isinstance(v, bytes) else str(v) if k in ("amount", "epoch", "nonce") else v for k,v in intent.items()}
