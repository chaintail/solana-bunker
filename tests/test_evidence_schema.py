import copy
import unittest
from evidence_schema import FIELDS, validate


def actual_record():
    record = {"schema_version": 1, "run_id": "schema-unit-fixture", "operation_id": "fixture", "observed_at_utc": "2026-10-12T13:00:00Z", "commit": "disposable-test", "program_binary_sha256": None, "evidence_paths": ["tests/test_evidence_schema.py"]}
    record.update({section: {key: None for key in keys} for section, keys in FIELDS.items()})
    record["environment"].update(evidence_level="host_reference", cluster="host")
    record["outcome"].update(expected="success", observed="success", test_passed=True)
    return record


class EvidenceSchemaTests(unittest.TestCase):
    def test_actual_host_record_allows_unmeasured_nulls(self):
        self.assertEqual(validate(actual_record()), [])

    def test_missing_field_is_not_implicitly_zero(self):
        r = actual_record()
        del r["resources"]["compute_consumed"]
        self.assertTrue(validate(r))

    def test_host_cannot_become_onchain_compute(self):
        r = actual_record()
        r["resources"]["compute_consumed"] = 100
        self.assertTrue(validate(r))

    def test_claimed_network_confirmation_requires_observed_identifier(self):
        r = actual_record()
        r["environment"].update(evidence_level="devnet_confirmed", cluster="devnet")
        r["program_binary_sha256"] = "0" * 64
        self.assertTrue(validate(r))
        r["transport"].update(transaction_signature="disposable-unit-fixture", confirmation_status="confirmed")
        self.assertEqual(validate(r), [])

    def test_simulated_transaction_cannot_be_called_confirmed(self):
        r = actual_record()
        r["environment"].update(evidence_level="devnet_simulation", cluster="devnet")
        r["program_binary_sha256"] = "0" * 64
        r["transport"]["confirmation_status"] = "confirmed"
        self.assertTrue(validate(r))

    def test_large_monetary_value_must_preserve_decimal_precision(self):
        r = actual_record()
        r["environment"]["evidence_level"] = "local_svm"
        r["program_binary_sha256"] = "0" * 64
        r["resources"]["storage_deposit_lamports"] = 2**64 - 1
        self.assertTrue(validate(r))
        r["resources"]["storage_deposit_lamports"] = str(2**64 - 1)
        self.assertEqual(validate(r), [])

    def test_negative_and_boolean_sizes_invalid(self):
        for bad in [-1, True, "123"]:
            r = actual_record()
            r["transport"]["transaction_bytes"] = bad
            self.assertTrue(validate(r))

    def test_measurement_requires_raw_evidence(self):
        r = actual_record()
        r["evidence_paths"] = []
        self.assertTrue(validate(r))
