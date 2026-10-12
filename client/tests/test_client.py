import hashlib
import json
import tempfile
import unittest
from client import actions, kdf, host
from client.merkle import SecretTree, verify
from client.journal import SigningJournal, JournalError, AuthorityHistory

def base(action=1):
    return dict(program_id=b"p"*32,namespace=b"n"*32,vault_id=b"v"*32,state=b"s"*32,treasury=b"t"*32,
                mode=3,epoch=7,nonce=9,leaf_index=2,action=action,destination=b"d"*32,amount=123)

class ClientTests(unittest.TestCase):
    def test_actions_roundtrip(self):
        cases=[base(),dict(base(2),token_program=b"a"*32,mint=b"m"*32,source=b"x"*32,decimals=6),
               dict(base(3),targets=[3,8,1023]),dict(base(4),new_mode=3,parameter_id=1,root=b"r"*32,public_seed=b"u"*32)]
        for case,size in zip(cases,[230,327,203,259]):
            wire=actions.encode_intent(case);self.assertEqual(len(wire),size)
            self.assertEqual(actions.encode_intent(actions.parse_intent(wire)),wire)
            with self.assertRaises(ValueError):actions.parse_intent(wire+b"\0")
    def test_burn_policy(self):
        for targets in ([2],[8,8],[8,3],[],list(range(33))):
            with self.assertRaises(ValueError):actions.encode_intent(dict(base(3),targets=targets))
    def test_numeric_bounds(self):
        for amount in (-1,2**64,True,1.2):
            with self.assertRaises(ValueError):actions.encode_intent(dict(base(),amount=amount))
    def test_merkle_sizes_and_negatives(self):
        for count in (16,256,1024):
            secrets=kdf.fixture_secrets(b"z"*32,b"v"*32,0,count);tree=SecretTree(secrets)
            for index in (0,count-1):
                proof=tree.proof(index)
                self.assertTrue(verify(tree.root,count,index,secrets[index],proof))
                self.assertEqual(len(tree.witness(index)),36+32*(count.bit_length()-1))
                altered=proof.copy();altered[0]=bytes([altered[0][0]^1])+altered[0][1:]
                self.assertFalse(verify(tree.root,count,index,secrets[index],altered))
                self.assertFalse(verify(tree.root,count,index^1,secrets[index],proof))
                with self.assertRaises(ValueError):verify(tree.root,count,index,secrets[index],proof[:-1])
                with self.assertRaises(ValueError):verify(tree.root,count,count,secrets[index],proof)
    def test_bip39_seed_vector(self):
        mnemonic="abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        self.assertEqual(kdf.bip39_seed(mnemonic,"TREZOR").hex(),"c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04")
    def test_kdf_separation(self):
        seeds=kdf.xmss_seeds(b"z"*64,b"v"*32,0)
        self.assertEqual(len(set(seeds)),3)
        self.assertNotEqual(seeds,kdf.xmss_seeds(b"z"*64,b"v"*32,1))
        self.assertNotEqual(seeds[0],kdf.fixture_secrets(b"z"*64,b"v"*32,0,16)[0])
    def test_journal_reserve_retry_reuse_and_crash(self):
        with tempfile.TemporaryDirectory() as directory:
            calls=[]
            def signer(i,m):calls.append((i,m));return i.to_bytes(4,"big")+b"s"*2496
            with SigningJournal(directory,"key") as journal:
                signed=journal.sign("op",b"intent",signer,index=0)
                self.assertEqual(journal.retry("op"),signed)
                self.assertEqual(journal.sign("op",b"intent",signer,index=0),signed)
                self.assertEqual(len(calls),1)
                with self.assertRaises(JournalError):journal.sign("changed",b"other",signer,index=0)
                with self.assertRaises(JournalError):journal.sign("op",b"other",signer,index=0)
                with self.assertRaises(JournalError):SigningJournal(directory,"key")
                def uncertain(i,m):raise RuntimeError("lost signer response")
                with self.assertRaises(RuntimeError):journal.sign("uncertain",b"message",uncertain,index=1)
                with self.assertRaises(JournalError):journal.sign("reuse",b"message",signer,index=1)
                journal.db.execute("INSERT INTO leaves VALUES (2,'crash',?,'reserved',NULL)",(b"crash",))
            with SigningJournal(directory,"key") as journal:
                self.assertEqual(journal.public_status()[2]["status"],"abandoned")
                self.assertEqual(journal.retry("op"),signed)
                self.assertEqual(journal.sign("fresh",b"new",signer)["leaf_index"],3)
            with self.assertRaises(JournalError):SigningJournal(directory,"different")
    def test_authority_history(self):
        with tempfile.TemporaryDirectory() as directory:
            history=AuthorityHistory(directory);history.install(b"r"*64,0)
            with self.assertRaises(JournalError):history.install(b"r"*64,1)
            with self.assertRaises(JournalError):history.install(b"s"*64,0)
            history.install(b"s"*64,1);history.close()
    def test_host_persistence(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger,private=host.initialize(2,16,"test-only")
            ledger.deposit_sol(private["state"],123)
            host.save(directory+"/state.json",ledger,private)
            restored,private2=host.load(directory+"/state.json")
            self.assertEqual(host.inspect(ledger,private),host.inspect(restored,private2))

if __name__=="__main__":unittest.main()
