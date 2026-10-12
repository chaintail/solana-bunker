"""Persistence tests use a format-only callback; no crypto validity claimed here."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from client.journal import SigningJournal, JournalError, AuthorityHistory


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="validation-unfunded-journal-")
        self.path = Path(self.tmp.name)
        self.calls = []

    def tearDown(self):
        self.tmp.cleanup()

    def format_callback(self, index, message):
        # Independently reopen durable database while callback runs: reservation must exist.
        with sqlite3.connect(self.path / "signing.sqlite") as db:
            self.assertEqual(db.execute("SELECT status,message FROM leaves WHERE idx=?",(index,)).fetchone(),("reserved",message))
        self.calls.append((index,message))
        return index.to_bytes(4,"big") + bytes(2496)

    def test_exact_retry_durable_and_signer_called_once(self):
        with SigningJournal(self.path,"disposable",16) as journal:
            first = journal.sign("operation-1",b"exact canonical bytes",self.format_callback,index=5)
            self.assertEqual(first,journal.sign("operation-1",b"exact canonical bytes",self.format_callback,index=5))
            self.assertEqual(len(self.calls),1)
        with SigningJournal(self.path,"disposable",16) as journal:
            self.assertEqual(first,journal.retry("operation-1"))
            with self.assertRaises(JournalError):
                journal.sign("operation-1",b"changed message",self.format_callback,index=5)
            with self.assertRaises(JournalError):
                journal.sign("operation-2",b"different message",self.format_callback,index=5)

    def test_uncertain_callback_and_crash_reservation_never_reused(self):
        def fail(index,message):
            raise RuntimeError("uncertain signer interruption")
        with SigningJournal(self.path,"disposable",4) as journal:
            with self.assertRaises(RuntimeError):
                journal.sign("failed",b"first",fail,index=0)
            journal.db.execute("INSERT INTO leaves VALUES (1,'crashed',?,'reserved',NULL)",(b"second",))
        with SigningJournal(self.path,"disposable",4) as journal:
            for operation in ("failed","crashed"):
                with self.assertRaises(JournalError):
                    journal.retry(operation)
            signed=journal.sign("next",b"third",self.format_callback)
            self.assertEqual(signed["leaf_index"],2)
            self.assertEqual([x["status"] for x in journal.public_status()],["abandoned","abandoned","signed"])

    def test_single_writer_lock_and_keyset_mismatch(self):
        with SigningJournal(self.path,"disposable",4):
            with self.assertRaises(JournalError):
                SigningJournal(self.path,"disposable",4)
        with self.assertRaises(JournalError):
            SigningJournal(self.path,"different-keyset",4)

    def test_history_rejects_root_or_generation_reuse(self):
        history=AuthorityHistory(self.path)
        try:
            history.install(bytes(64),1)
            for public,generation in [(bytes(64),2),(bytes([1])*64,1)]:
                with self.assertRaises(JournalError):
                    history.install(public,generation)
            history.install(bytes([1])*64,2)
        finally:
            history.close()
