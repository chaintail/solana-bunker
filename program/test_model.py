"""Focused host specification checks. Independent runtime tests live in tests/."""
import unittest
from client.actions import encode_intent
from client.merkle import SecretTree
from program.model import BunkerLedger, TokenAccount, Rejected, ARRAY, MERKLE, TOKEN_PROGRAM

class CustodySpecificationTests(unittest.TestCase):
    def fixture(self,mode=ARRAY):
        self.tree=SecretTree([bytes([n])*32 for n in range(8)])
        self.ledger=BunkerLedger(b'P'*32)
        authority=b''.join(self.tree.commitments) if hasattr(self.tree,'commitments') else b''.join(__import__('hashlib').sha256(s).digest() for s in self.tree.secrets)
        self.state=self.ledger.initialize(b'V'*32,b'N'*32,b'A'*32,b'M'*32,b'S'*32,mode,authority if mode==ARRAY else self.tree.root,8,rent=100)
        self.ledger.deposit_sol(self.state.address,1000)
        self.ledger.deposit_mock(self.state.address,2_000_000)
        self.ledger.tokens[b'D'*32]=TokenAccount(b'M'*32,b'R'*32)
        self.ledger.tokens[b'E'*32]=TokenAccount(b'M'*32,b'T'*32)

    def intent(self,action='sol',index=0,**fields):
        s=self.ledger.states[self.state.address]
        return encode_intent(dict(program_id=b'P'*32,namespace=b'N'*32,vault_id=b'V'*32,
            state=s.address,treasury=s.treasury,mode=s.mode,epoch=s.epoch,nonce=s.nonce,
            leaf_index=index,action={'sol':1,'token':2,'burn':3,'rotate':4}[action],**fields))

    def witness(self,index):
        import struct
        if self.state.mode==ARRAY:
            return struct.pack('<I',index)+self.tree.secrets[index]
        return self.tree.witness(index)

    def test_array_and_merkle_sol_and_token_copied_witness(self):
        for mode in (ARRAY,MERKLE):
            with self.subTest(mode=mode):
                self.fixture(mode)
                # Bearer credential authorizes attacker-changed recipient and amount.
                self.ledger.execute(self.intent(destination=b'X'*32,amount=123),self.witness(0))
                self.assertEqual(self.ledger.sol[b'X'*32],123)
                token=self.intent(action='token',index=1,token_program=TOKEN_PROGRAM,mint=b'M'*32,
                                  source=b'S'*32,destination=b'E'*32,amount=333,decimals=6)
                self.ledger.execute(token,self.witness(1))
                self.assertEqual(self.ledger.tokens[b'E'*32].amount,333)
                self.assertEqual(self.ledger.states[self.state.address].nonce,2)

    def test_failed_transfer_rolls_back_and_exact_retry_succeeds(self):
        self.fixture()
        intent=self.intent(destination=b'X'*32,amount=2000)
        with self.assertRaisesRegex(Rejected,'insufficient_sol'):
            self.ledger.execute(intent,self.witness(0))
        s=self.ledger.states[self.state.address]
        self.assertEqual(s.nonce,0);self.assertEqual(s.consumed,set())
        self.assertEqual(self.ledger.sol[s.treasury],1100)
        self.ledger.deposit_sol(s.address,1000)
        self.ledger.execute(intent,self.witness(0))
        self.assertEqual(self.ledger.sol[s.treasury],100)

    def test_invalid_token_authority_and_mint_reject_before_leaf_consumption(self):
        self.fixture()
        intent=self.intent(action='token',token_program=TOKEN_PROGRAM,mint=b'M'*32,
                           source=b'S'*32,destination=b'D'*32,amount=1,decimals=6)
        self.ledger.tokens[b'S'*32].delegate=b'Q'*32
        with self.assertRaisesRegex(Rejected,'unexpected_source_authority'):
            self.ledger.execute(intent,self.witness(0))
        self.assertEqual(self.ledger.states[self.state.address].consumed,set())

    def test_consumed_leaf_and_global_nonce(self):
        self.fixture()
        old=self.intent(destination=b'X'*32,amount=1)
        self.ledger.execute(old,self.witness(0))
        with self.assertRaisesRegex(Rejected,'stale_epoch_or_nonce'):
            self.ledger.execute(old,self.witness(0))
        with self.assertRaisesRegex(Rejected,'leaf_consumed'):
            self.ledger.execute(self.intent(destination=b'X'*32,amount=1),self.witness(0))

    def test_burn_consumes_auth_leaf_and_targets(self):
        self.fixture(MERKLE)
        self.ledger.execute(self.intent(action='burn',targets=[1,2,7]),self.witness(0))
        self.assertEqual(self.ledger.states[self.state.address].consumed,{0,1,2,7})
        with self.assertRaisesRegex(Rejected,'invalid_burn_target'):
            self.ledger.execute(self.intent(action='burn',index=3,targets=[1]),self.witness(3))

    def test_admin_transition_keeps_receiving_addresses_balances_and_epoch(self):
        self.fixture()
        addr,treasury=self.state.address,self.state.treasury
        before=self.ledger.sol[treasury]
        self.ledger.demo_mode(addr,b'A'*32,MERKLE,self.tree.root,8)
        self.assertEqual(self.ledger.states[addr].treasury,treasury)
        self.assertEqual(self.ledger.sol[treasury],before)
        self.assertEqual(self.ledger.states[addr].epoch,1)
        with self.assertRaisesRegex(Rejected,'inactive_mode'):
            payload=bytearray(self.intent(destination=b'X'*32,amount=1));payload[168]=ARRAY
            self.ledger.execute(bytes(payload),self.witness(0))

if __name__=='__main__':unittest.main()
