"""Independent bytes/tree oracles; these do not establish SVM execution."""
import hashlib
import struct
import unittest
from client import actions, merkle


def fixture(action=1, mode=3):
    value = {key: bytes([i+1])*32 for i, key in enumerate(("program_id", "namespace", "vault_id", "state", "treasury"))}
    value.update(mode=mode, epoch=0x0102030405060708, nonce=0x1112131415161718, leaf_index=7, action=action, destination=b"\x06"*32, amount=0x2122232425262728)
    if action == 2:
        value.update(token_program=b"\x07"*32, mint=b"\x08"*32, source=b"\x09"*32, decimals=6)
    if action == 3:
        value.update(targets=[0, 8, 1023])
    if action == 4:
        value.update(new_mode=3, parameter_id=1, root=b"\x0a"*32, public_seed=b"\x0b"*32)
    return value


def independent_encode(value):
    # Explicit concatenation, independent of production struct format/parser.
    encoded = b"BUNKER\x00\x01" + b"".join(value[key] for key in ("program_id", "namespace", "vault_id", "state", "treasury"))
    encoded += bytes([value["mode"]]) + value["epoch"].to_bytes(8, "little") + value["nonce"].to_bytes(8, "little") + value["leaf_index"].to_bytes(4, "little") + bytes([value["action"]])
    action = value["action"]
    if action == 1:
        return encoded + value["destination"] + value["amount"].to_bytes(8, "little")
    if action == 2:
        return encoded + b"".join(value[k] for k in ("token_program", "mint", "source", "destination")) + value["amount"].to_bytes(8, "little") + bytes([value["decimals"]])
    if action == 3:
        return encoded + bytes([len(value["targets"])]) + b"".join(i.to_bytes(4, "little") for i in value["targets"])
    return encoded + bytes([3]) + (1).to_bytes(4, "little") + value["root"] + value["public_seed"]


def independent_tree(secrets):
    sha = lambda b: hashlib.sha256(b).digest()
    layer = [sha(b"BUNKER-LEAF-V1\x00" + i.to_bytes(4, "little") + sha(secret)) for i, secret in enumerate(secrets)]
    layers = [layer]
    while len(layer) > 1:
        layer = [sha(b"BUNKER-NODE-V1\x00" + layer[i] + layer[i+1]) for i in range(0, len(layer), 2)]
        layers.append(layer)
    return layers


class IntentContractTests(unittest.TestCase):
    def test_four_actions_match_independent_layout_and_lengths(self):
        for action, length in [(1, 230), (2, 327), (3, 203), (4, 259)]:
            with self.subTest(action=action):
                expected = independent_encode(fixture(action))
                self.assertEqual(len(expected), length)
                self.assertEqual(actions.encode_intent(fixture(action)), expected)
                self.assertEqual(actions.encode_intent(actions.parse_intent(expected)), expected)

    def test_every_prefix_and_trailing_byte_rejected(self):
        for action in range(1, 5):
            expected = independent_encode(fixture(action))
            for length in range(len(expected)):
                with self.assertRaises(ValueError):
                    actions.parse_intent(expected[:length])
            with self.assertRaises(ValueError):
                actions.parse_intent(expected + b"\x00")

    def test_max_base_unit_integers_preserved(self):
        value = fixture()
        value.update(amount=2**64-1, nonce=2**64-1, epoch=2**64-1, leaf_index=2**32-1)
        decoded = actions.parse_intent(actions.encode_intent(value))
        self.assertEqual(decoded["amount"], 2**64-1)
        self.assertEqual(decoded["leaf_index"], 2**32-1)
        for key in ("amount", "epoch", "nonce"):
            self.assertEqual(actions.json_intent(decoded)[key], str(2**64-1))

    def test_unsigned_integer_and_boolean_rejections(self):
        for key, bits in [("amount", 64), ("epoch", 64), ("nonce", 64), ("leaf_index", 32), ("mode", 8)]:
            for bad in (-1, 2**bits, True, 1.5):
                value = fixture()
                value[key] = bad
                with self.assertRaises(ValueError):
                    actions.encode_intent(value)

    def test_burn_canonical_sorted_unique_bounded_and_distinct(self):
        for targets in ([], [8, 0], [0, 0], [7], list(range(33)), [2**32]):
            value = fixture(3)
            value["targets"] = targets
            with self.assertRaises(ValueError):
                actions.encode_intent(value)

    def test_rotation_requires_specified_mode_and_parameter(self):
        for key, value in [("mode", 1), ("new_mode", 2), ("parameter_id", 0), ("parameter_id", 2)]:
            intent = fixture(4)
            intent[key] = value
            with self.assertRaises(ValueError):
                actions.encode_intent(intent)

    def test_all_identity_and_action_bytes_are_authenticated(self):
        for action in range(1, 5):
            encoded = independent_encode(fixture(action))
            digest = hashlib.sha256(encoded).digest()
            for offset in range(len(encoded)):
                mutated = bytearray(encoded)
                mutated[offset] ^= 1
                self.assertNotEqual(hashlib.sha256(mutated).digest(), digest)


class MerkleContractTests(unittest.TestCase):
    def test_equivalent_trees_and_boundary_proofs(self):
        for count in (16, 256, 1024):
            secrets = [hashlib.sha256(b"validation-disposable-unfunded" + i.to_bytes(4, "little")).digest() for i in range(count)]
            independent = independent_tree(secrets)
            tree = merkle.SecretTree(secrets)
            self.assertEqual(tree.root, independent[-1][0])
            for index in (0, 1, count//2, count-1):
                proof = tree.proof(index)
                self.assertEqual(len(proof)*32, count.bit_length()*32-32)
                self.assertTrue(merkle.verify(tree.root, count, index, secrets[index], proof))
                self.assertEqual(len(tree.witness(index)), 36+len(proof)*32)
                mutated = [bytes([proof[0][0]^1])+proof[0][1:], *proof[1:]]
                self.assertFalse(merkle.verify(tree.root, count, index, secrets[index], mutated))
                self.assertFalse(merkle.verify(tree.root, count, index^1, secrets[index], proof))
                with self.assertRaises(ValueError):
                    merkle.verify(tree.root, count, index, secrets[index], proof[:-1])

    def test_invalid_tree_sizes(self):
        for count in (0, 1, 3, 2048, True):
            with self.assertRaises(ValueError):
                merkle.height(count)
