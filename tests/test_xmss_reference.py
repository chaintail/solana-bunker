"""Differential verification of explicitly disposable, never funded reference vectors."""
from pathlib import Path
import unittest
from crypto.xmss import verify, reference_verify

VECTORS = Path(__file__).resolve().parents[1] / "artifacts/public-vectors/xmss"


class XMSSReferenceTests(unittest.TestCase):
    def test_reference_valid_boundary_indices(self):
        public = (VECTORS / "public.bin").read_bytes()
        for index in (0, 1, 511, 512, 1022, 1023):
            message = (VECTORS / f"{index}.msg").read_bytes()
            signature = (VECTORS / f"{index}.sig").read_bytes()
            self.assertEqual(len(signature), 2500)
            self.assertEqual(verify(public, message, signature), index)
            self.assertTrue(reference_verify(public, message, signature))

    def test_chain_authentication_randomness_and_index_mutations(self):
        public = (VECTORS / "public.bin").read_bytes()
        message = (VECTORS / "511.msg").read_bytes()
        signature = (VECTORS / "511.sig").read_bytes()
        for offset in (0, 3, 4, 35, 36, 67, 500, 2179, 2180, 2499):
            corrupted = bytearray(signature)
            corrupted[offset] ^= 1
            self.assertFalse(reference_verify(public, message, corrupted), f"offset {offset}")
            with self.assertRaises(ValueError, msg=f"offset {offset}"):
                verify(public, message, corrupted)

    def test_message_and_public_root_seed_mutations(self):
        public = (VECTORS / "public.bin").read_bytes()
        message = (VECTORS / "0.msg").read_bytes()
        signature = (VECTORS / "0.sig").read_bytes()
        for altered_public, altered_message in [(public, message+b"\x00"), (public, b"different canonical intent"), (bytes([public[0]^1])+public[1:],message), (public[:32]+bytes([public[32]^1])+public[33:],message)]:
            self.assertFalse(reference_verify(altered_public, altered_message, signature))
            with self.assertRaises(ValueError):
                verify(altered_public, altered_message, signature)

    def test_malformed_lengths_and_out_of_range_index(self):
        public = (VECTORS / "public.bin").read_bytes()
        message = (VECTORS / "0.msg").read_bytes()
        signature = (VECTORS / "0.sig").read_bytes()
        for malformed in (b"", signature[:-1], signature+b"\x00", (1024).to_bytes(4,"big")+signature[4:], (2**32-1).to_bytes(4,"big")+signature[4:]):
            self.assertFalse(reference_verify(public,message,malformed))
            with self.assertRaises(ValueError):
                verify(public,message,malformed)
