"""Pedagogical SHA-256 commitments, deliberately bearer authorization; not XMSS."""
import hashlib
import struct
from .actions import octets, number

LEAF_DOMAIN = b"BUNKER-LEAF-V1\x00"
NODE_DOMAIN = b"BUNKER-NODE-V1\x00"

def sha(data):
    return hashlib.sha256(data).digest()

def commitment(secret):
    return sha(octets(secret))

def leaf_hash(index, secret):
    return sha(LEAF_DOMAIN + struct.pack("<I", number(index, 32)) + commitment(secret))

def node_hash(left, right):
    return sha(NODE_DOMAIN + octets(left) + octets(right))

def height(count):
    if type(count) is not int or count < 2 or count > 1024 or count & (count-1):
        raise ValueError("leaf count must be power of two in 2..1024")
    return count.bit_length()-1

class SecretTree:
    def __init__(self, secrets):
        height(len(secrets))
        self.secrets = [octets(s) for s in secrets]
        self.levels = [[leaf_hash(i,s) for i,s in enumerate(self.secrets)]]
        while len(self.levels[-1]) > 1:
            layer = self.levels[-1]
            self.levels.append([node_hash(layer[i], layer[i+1]) for i in range(0,len(layer),2)])
        self.root = self.levels[-1][0]

    def proof(self, index):
        index = number(index,32)
        if index >= len(self.secrets):
            raise ValueError("leaf out of range")
        result = []
        for layer in self.levels[:-1]:
            result.append(layer[index ^ 1]); index >>= 1
        return result

    def witness(self, index):
        proof = self.proof(index)
        return struct.pack("<I", index) + self.secrets[index] + b"".join(proof)

def verify(root, count, index, secret, siblings):
    depth = height(count)
    index = number(index,32)
    if index >= count or len(siblings) != depth:
        raise ValueError("invalid index/proof height")
    current = leaf_hash(index, secret)
    for sibling in siblings:
        sibling = octets(sibling)
        current = node_hash(sibling,current) if index & 1 else node_hash(current,sibling)
        index >>= 1
    return current == octets(root)
