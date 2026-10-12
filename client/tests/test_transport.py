"""Wire-level controls for v1 limits and retry boundaries; no network access."""
import unittest

from solders.compute_budget import set_compute_unit_limit
from solders.hash import Hash
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.message import MessageV1, TransactionConfig
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction

from client.actions import encode_intent
from client.transport import (COMPUTE_UNIT_LIMIT, build_xmss_transaction,
                              config_values, execute_instruction)


class V1TransportTests(unittest.TestCase):
    def setUp(self):
        self.payer = Keypair()
        self.keys = [Pubkey.new_unique() for _ in range(9)]
        self.intent = dict(zip(("program_id", "namespace", "vault_id", "state", "treasury"),
                               map(bytes, self.keys[:5])))
        self.intent.update(mode=3, epoch=0, nonce=0, leaf_index=7)
        self.accounts = [AccountMeta(key, False, i in (0, 1, 3, 4))
                         for i, key in enumerate(self.keys[3:9])]
        self.witness = (7).to_bytes(4, "big") + b"\x01" * 2496

    def transaction(self, instructions, blockhash=None, **kwargs):
        return build_xmss_transaction(self.payer.pubkey(), [self.payer], instructions,
                                      blockhash or Hash.new_unique(), **kwargs)

    def test_all_actions_roundtrip_full_signature_and_inline_limits(self):
        fields = (
            dict(action=1, destination=bytes(self.keys[7]), amount=100),
            dict(action=2, destination=bytes(self.keys[7]), amount=100,
                 token_program=bytes(self.keys[8]), mint=bytes(self.keys[5]),
                 source=bytes(self.keys[6]), decimals=6),
            dict(action=3, targets=list(range(8, 40))),
            dict(action=4, new_mode=3, parameter_id=1, root=b"a" * 32, public_seed=b"b" * 32),
        )
        for action in fields:
            with self.subTest(action=action["action"]):
                intent = dict(self.intent, **action)
                instruction = execute_instruction(intent, self.witness, self.accounts)
                tx = self.transaction([instruction])
                raw = bytes(tx)
                self.assertGreater(len(raw), 1232)
                self.assertLessEqual(len(raw), 4096)
                decoded = VersionedTransaction.from_bytes(raw)
                self.assertIsInstance(decoded.message, MessageV1)
                self.assertEqual(decoded.message.instructions[0].data,
                                 b"\x02" + len(encode_intent(intent)).to_bytes(2, "little")
                                 + encode_intent(intent) + self.witness)
                self.assertEqual(len(decoded.message.instructions), 1)
                self.assertEqual(config_values(decoded.message.config),
                                 dict(compute_unit_limit=COMPUTE_UNIT_LIMIT,
                                      loaded_accounts_data_size_limit=1048576,
                                      heap_size=32768, priority_fee=None))
                self.assertTrue(all(decoded.verify_with_results()))

    def test_retry_changes_only_outer_transport(self):
        intent = dict(self.intent, action=1, destination=bytes(self.keys[7]), amount=100)
        instruction = execute_instruction(intent, self.witness, self.accounts)
        first, second = self.transaction([instruction]), self.transaction([instruction])
        self.assertNotEqual(bytes(first), bytes(second))
        self.assertEqual(first.message.instructions[0].data, second.message.instructions[0].data)
        self.assertNotEqual(first.signatures, second.signatures)

    def test_reject_actual_oversized_envelope(self):
        instruction = Instruction(self.keys[0], b"x" * 4096, self.accounts)
        with self.assertRaisesRegex(ValueError, "maximum is 4096"):
            self.transaction([instruction])

    def test_reject_legacy_budget_instruction(self):
        with self.assertRaisesRegex(ValueError, "TransactionConfig"):
            self.transaction([set_compute_unit_limit(1400000)])

    def test_require_explicit_bounded_resources(self):
        for config in (TransactionConfig(), TransactionConfig(compute_unit_limit=1400001),
                       TransactionConfig(compute_unit_limit=1),
                       TransactionConfig(compute_unit_limit=1, loaded_accounts_data_size_limit=1)):
            with self.subTest(config=str(config)), self.assertRaises(ValueError):
                self.transaction([], config=config)

    def test_allow_explicit_low_limit_for_runtime_control(self):
        config = TransactionConfig(compute_unit_limit=1, loaded_accounts_data_size_limit=1,
                                   heap_size=32768)
        tx = self.transaction([], config=config)
        self.assertEqual(tx.message.config.compute_unit_limit, 1)


if __name__ == "__main__":
    unittest.main()
