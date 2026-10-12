"""Single-writer durable leaf reservations; signing exposure is independent of chain use.

Crash after reservation permanently retires the leaf. Never restore only a seed and
resume signing. Back up this journal together with the dedicated mnemonic.
"""
import fcntl
import hashlib
import os
import sqlite3
from pathlib import Path

class JournalError(ValueError):
    pass

class SigningJournal:
    def __init__(self, directory, keyset_id, leaf_count=1024):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.directory, 0o700)
        self.lock = open(self.directory / "writer.lock", "a+b")
        os.chmod(self.directory / "writer.lock", 0o600)
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.lock.close()
            raise JournalError("another signer owns this keyset journal")
        self.db = sqlite3.connect(self.directory / "signing.sqlite", isolation_level=None)
        os.chmod(self.directory / "signing.sqlite", 0o600)
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("PRAGMA journal_mode=DELETE")
        self.db.execute("CREATE TABLE IF NOT EXISTS meta (name TEXT PRIMARY KEY,value TEXT NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS leaves (idx INTEGER PRIMARY KEY,operation_id TEXT UNIQUE NOT NULL,message BLOB NOT NULL,status TEXT NOT NULL,signature BLOB)")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            existing = dict(self.db.execute("SELECT name,value FROM meta"))
            if existing and (existing.get("keyset_id") != keyset_id or existing.get("leaf_count") != str(leaf_count)):
                raise JournalError("journal belongs to a different keyset")
            if not existing:
                self.db.executemany("INSERT INTO meta VALUES (?,?)", [("keyset_id",keyset_id),("leaf_count",str(leaf_count))])
            # A previous process may have exposed a signature before persisting it.
            self.db.execute("UPDATE leaves SET status='abandoned' WHERE status='reserved'")
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            self.close()
            raise
        self.leaf_count = leaf_count

    def close(self):
        if getattr(self, "db", None):
            self.db.close(); self.db = None
        if getattr(self, "lock", None) and not self.lock.closed:
            fcntl.flock(self.lock, fcntl.LOCK_UN); self.lock.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def sign(self, operation_id, message, signer, index=None):
        if not isinstance(message,bytes) or not operation_id:
            raise JournalError("operation ID and exact message bytes required")
        old = self.db.execute("SELECT idx,message,status,signature FROM leaves WHERE operation_id=?",(operation_id,)).fetchone()
        if old:
            if old[1] != message or index is not None and old[0] != index:
                raise JournalError("operation/leaf cannot be rebound to a different message")
            if old[2] != "signed":
                raise JournalError("uncertain signing leaf abandoned; use fresh operation/leaf")
            return {"leaf_index":old[0], "message":old[1], "signature":old[3]}
        used = {row[0] for row in self.db.execute("SELECT idx FROM leaves")}
        if index is None:
            index = next((i for i in range(self.leaf_count) if i not in used),None)
        if type(index) is not int or index not in range(self.leaf_count) or index in used:
            raise JournalError("leaf unavailable or exhausted")
        self.db.execute("BEGIN IMMEDIATE")
        self.db.execute("INSERT INTO leaves VALUES (?,?,?,'reserved',NULL)",(index,operation_id,message))
        self.db.execute("COMMIT")  # durable reservation BEFORE signer invocation
        try:
            signature = signer(index,message)
            if not isinstance(signature,bytes) or len(signature)!=2500 or int.from_bytes(signature[:4],"big")!=index:
                raise JournalError("signer returned malformed XMSS authorization")
            self.db.execute("BEGIN IMMEDIATE")
            self.db.execute("UPDATE leaves SET status='signed',signature=? WHERE idx=?",(signature,index))
            self.db.execute("COMMIT")  # exact authorization durable BEFORE release
        except BaseException:
            if self.db.in_transaction:
                self.db.execute("ROLLBACK")
            self.db.execute("UPDATE leaves SET status='abandoned' WHERE idx=?",(index,))
            raise
        return {"leaf_index":index,"message":message,"signature":signature}

    def retry(self, operation_id):
        row = self.db.execute("SELECT idx,message,status,signature FROM leaves WHERE operation_id=?",(operation_id,)).fetchone()
        if not row or row[2] != "signed":
            raise JournalError("no durable authorization for retry")
        return {"leaf_index":row[0],"message":row[1],"signature":row[3]}

    def retire(self, index, reason="onchain_burn"):
        if type(index) is not int or index not in range(self.leaf_count):
            raise JournalError("invalid leaf")
        if self.db.execute("SELECT 1 FROM leaves WHERE idx=?",(index,)).fetchone():
            raise JournalError("leaf already locally retired")
        self.db.execute("INSERT INTO leaves VALUES (?,?,?,'abandoned',NULL)",(index,f"retired:{reason}:{index}",b""))

    def public_status(self):
        return [{"leaf_index":r[0],"status":r[1],"message_commitment":hashlib.sha256(r[2]).hexdigest()} for r in self.db.execute("SELECT idx,status,message FROM leaves ORDER BY idx")]

class AuthorityHistory:
    """Local signer history protects against intentionally reinstalling old keysets."""
    def __init__(self, directory):
        path = Path(directory); path.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.db = sqlite3.connect(path/"authority-history.sqlite")
        os.chmod(path/"authority-history.sqlite",0o600)
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("CREATE TABLE IF NOT EXISTS keysets (public BLOB PRIMARY KEY,generation TEXT UNIQUE NOT NULL)")

    def install(self, public, generation):
        if not isinstance(public,bytes) or len(public)!=64:
            raise JournalError("expected XMSS root/public-seed64")
        try:
            self.db.execute("INSERT INTO keysets VALUES (?,?)",(public,str(generation))); self.db.commit()
        except sqlite3.IntegrityError as exc:
            raise JournalError("historical authority/generation reuse refused") from exc

    def close(self):
        self.db.close()
