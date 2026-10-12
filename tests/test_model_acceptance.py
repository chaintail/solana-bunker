"""Host-only executable specification checks. Real runtime harness is separate.

Disposable crypto seeds are generated in memory, never shared-cluster funded.
Direct signing bypass is solely for isolated adversarial malformed-message tests.
"""
import copy
import hashlib
import struct
import unittest
from client.actions import encode_intent
from client.merkle import SecretTree
from crypto.xmss import keygen, sign_at, verify
from program.model import BunkerLedger, Rejected, TokenAccount, TOKEN_PROGRAM, pda
from solders.pubkey import Pubkey


def key(label):
    return hashlib.sha256(b"independent-validation-unfunded:"+label.encode()).digest()


class ModelAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # No seed/public secret input exported and no live journal used.
        cls.public, cls.secret = keygen(hashlib.sha256(b"unfunded-validation-key-1").digest()*3)
        cls.new_public, cls.new_secret = keygen(hashlib.sha256(b"unfunded-validation-key-2").digest()*3)

    def fixture(self, mode=1, count=16):
        self.ledger=BunkerLedger(key("program"),verify)
        self.secrets=[key(f"secret-{i}") for i in range(count)]
        self.tree=SecretTree(self.secrets)
        authority=b"".join(hashlib.sha256(s).digest() for s in self.secrets) if mode==1 else self.tree.root if mode==2 else self.public
        self.state=self.ledger.initialize(key(self.id()),key("namespace"),key("admin"),key("mint"),key("source"),mode,authority,count if mode!=3 else 1024,rent=890880)
        self.ledger.deposit_sol(self.state.address,10000)
        self.ledger.deposit_mock(self.state.address,10000)
        self.ledger.tokens[key("owner-token")]=TokenAccount(key("mint"),key("owner"))
        self.ledger.tokens[key("attacker-token")]=TokenAccount(key("mint"),key("attacker"))
        return self.state

    def intent(self,action=1,index=0,**fields):
        s=self.ledger.states[self.state.address]
        value=dict(program_id=self.ledger.program_id,namespace=s.namespace,vault_id=s.vault_id,state=s.address,treasury=s.treasury,mode=s.mode,epoch=s.epoch,nonce=s.nonce,leaf_index=index,action=action)
        if action==1:
            value.update(destination=key("owner"),amount=100)
        elif action==2:
            value.update(token_program=TOKEN_PROGRAM,mint=s.mint,source=s.token_source,destination=key("owner-token"),amount=100,decimals=6)
        elif action==3:
            value.update(targets=[1,3])
        else:
            value.update(new_mode=3,parameter_id=1,root=self.new_public[:32],public_seed=self.new_public[32:])
        value.update(fields)
        return value

    def witness(self,intent):
        index=intent["leaf_index"]
        if intent["mode"]==1:
            return struct.pack("<I",index)+self.secrets[index]
        if intent["mode"]==2:
            return self.tree.witness(index)
        return sign_at(self.secret,index,encode_intent(intent))

    def snapshot(self):
        return copy.deepcopy((self.ledger.states,self.ledger.sol,self.ledger.owners,self.ledger.tokens))

    def rejected(self,intent,witness,code=None):
        before=self.snapshot()
        with self.assertRaises(Rejected) as error:
            self.ledger.execute(encode_intent(intent),witness)
        if code:
            self.assertEqual(error.exception.code,code)
        self.assertEqual(self.snapshot(),before)

    def test_F01_F02_deterministic_pd_as_and_duplicate_init(self):
        s=self.fixture()
        address,bump=Pubkey.find_program_address([b"bunker_state",s.vault_id],Pubkey.from_bytes(self.ledger.program_id))
        self.assertEqual((bytes(address),bump),(s.address,s.state_bump))
        address,bump=Pubkey.find_program_address([b"bunker_treasury",s.address],Pubkey.from_bytes(self.ledger.program_id))
        self.assertEqual((bytes(address),bump),(s.treasury,s.treasury_bump))
        before=self.snapshot()
        with self.assertRaises(Rejected):
            self.ledger.initialize(s.vault_id,s.namespace,s.admin,s.mint,s.token_source,s.mode,s.authority,s.leaf_count)
        self.assertEqual(before,self.snapshot())

    def test_F03_F04_A01_M01_both_assets_and_exact_movements(self):
        for mode in (1,2,3):
            for action in (1,2):
                with self.subTest(mode=mode,action=action):
                    s=self.fixture(mode)
                    value=self.intent(action)
                    self.ledger.execute(encode_intent(value),self.witness(value))
                    current=self.ledger.states[s.address]
                    self.assertEqual((current.nonce,current.consumed),(1,{0}))
                    if action==1:
                        self.assertEqual(self.ledger.sol[s.treasury],s.rent+9900)
                        self.assertEqual(self.ledger.sol[key("owner")],100)
                    else:
                        self.assertEqual(self.ledger.tokens[s.token_source].amount,9900)
                        self.assertEqual(self.ledger.tokens[key("owner-token")].amount,100)

    def test_F05_wrong_domains_and_token_accounts(self):
        self.fixture()
        value=self.intent()
        witness=self.witness(value)
        for field in ("program_id","namespace","vault_id","state","treasury"):
            altered={**value,field:key("substitution")}
            self.rejected(altered,witness)
        value=self.intent(2)
        for field in ("token_program","mint","source","destination"):
            self.rejected({**value,field:key("substitution")},witness)
        self.rejected({**value,"decimals":9},witness)
        for field,val in [("delegate",key("attacker")),("authority",key("attacker")),("close_authority",key("attacker"))]:
            source=self.ledger.tokens[self.state.token_source]
            previous=getattr(source,field)
            setattr(source,field,val)
            self.rejected(value,witness,"unexpected_source_authority")
            setattr(source,field,previous)

    def test_F06_model_aliases_without_claiming_runtime_privileges(self):
        self.fixture()
        value=self.intent()
        for destination in (self.state.address,self.state.treasury,self.state.token_source):
            self.rejected({**value,"destination":destination},self.witness(value),"invalid_destination_or_amount")

    def test_A02_A04_M02_invalid_witness_index_and_replay(self):
        for mode in (1,2):
            self.fixture(mode)
            value=self.intent()
            witness=self.witness(value)
            self.rejected(value,witness[:-1])
            self.rejected(value,bytes([witness[0]^1])+witness[1:],"witness_index_mismatch")
            self.rejected(value,witness[:4]+bytes([witness[4]^1])+witness[5:])
            self.rejected({**value,"leaf_index":16},witness,"index_out_of_range")
            self.ledger.execute(encode_intent(value),witness)
            self.rejected(value,witness,"stale_epoch_or_nonce")
            self.rejected(self.intent(index=0),witness,"leaf_consumed")

    def test_A03_M03_copied_bearer_redirects_both_assets_attacker_first(self):
        # Attacker's only capabilities are ordinary fixture relaying and copied witness.
        for mode in (1,2):
            for action in (1,2):
                self.fixture(mode)
                value=self.intent(action)
                witness=self.witness(value)
                attacker={**value,"destination":key("attacker") if action==1 else key("attacker-token")}
                self.ledger.execute(encode_intent(attacker),witness)
                self.assertEqual(self.ledger.sol.get(key("owner"),0),0)
                self.assertEqual(self.ledger.tokens[key("owner-token")].amount,0)
                received=self.ledger.sol[key("attacker")] if action==1 else self.ledger.tokens[key("attacker-token")].amount
                self.assertEqual(received,100)
                self.rejected(value,witness,"stale_epoch_or_nonce")

    def test_X02_X03_X04_signed_effect_mutation_and_identical_copy(self):
        for action in (1,2):
            self.fixture(3)
            value=self.intent(action)
            witness=self.witness(value)
            self.rejected({**value,"amount":101},witness,"invalid_xmss_signature")
            self.rejected({**value,"destination":key("attacker") if action==1 else key("attacker-token")},witness,"invalid_xmss_signature")
            for offset in (36,2180):
                corrupted=bytearray(witness);corrupted[offset]^=1
                self.rejected(value,corrupted,"invalid_xmss_signature")
            self.ledger.execute(encode_intent(value),witness)
            self.rejected(value,witness,"stale_epoch_or_nonce")
            self.assertEqual(self.ledger.states[self.state.address].nonce,1)

    def test_X05_X06_stale_epoch_nonce_and_no_hash_authorization(self):
        self.fixture(3)
        value=self.intent()
        witness=self.witness(value)
        for field in ("epoch","nonce"):
            self.rejected({**value,field:1},witness,"stale_epoch_or_nonce")
        self.rejected(value,b"","invalid_witness_length")

    def test_B01_B02_B03_fresh_burn_exact_targets(self):
        self.fixture(3)
        value=self.intent(3)
        witness=self.witness(value)
        self.rejected({**value,"targets":[1,4]},witness,"invalid_xmss_signature")
        self.rejected({**value,"targets":[1024]},witness,"invalid_burn_target")
        self.ledger.execute(encode_intent(value),witness)
        self.assertEqual(self.ledger.states[self.state.address].consumed,{0,1,3})
        self.rejected(self.intent(index=1),witness,"leaf_consumed")
        self.rejected(self.intent(3,index=2,targets=[3]),witness,"invalid_burn_target")

    def test_R01_R02_R03_fresh_rotation_stable_treasury_and_new_signer(self):
        s=self.fixture(3)
        previous=(s.treasury,s.token_source,self.ledger.sol[s.treasury],self.ledger.tokens[s.token_source].amount)
        old_unused=self.intent(index=1)
        old_signature=self.witness(old_unused)
        rotation=self.intent(4)
        signature=self.witness(rotation)
        self.rejected({**rotation,"root":key("malicious-replacement")},signature,"invalid_xmss_signature")
        self.ledger.execute(encode_intent(rotation),signature)
        current=self.ledger.states[s.address]
        self.assertEqual((current.epoch,current.nonce,current.authority),(1,1,self.new_public))
        self.assertEqual(previous,(current.treasury,current.token_source,self.ledger.sol[current.treasury],self.ledger.tokens[current.token_source].amount))
        self.rejected(old_unused,old_signature,"stale_epoch_or_nonce")
        new_intent=self.intent(index=0)
        signature=sign_at(self.new_secret,0,encode_intent(new_intent))
        self.ledger.execute(encode_intent(new_intent),signature)
        self.assertEqual(self.ledger.sol[key("owner")],100)

    def test_S01_S02_failed_transfer_rolls_back_then_exact_retry(self):
        self.fixture(3)
        value=self.intent(amount=10001)
        witness=self.witness(value)
        self.rejected(value,witness,"insufficient_sol_preserving_rent")
        self.ledger.deposit_sol(self.state.address,1)
        self.ledger.execute(encode_intent(value),witness)
        self.assertEqual(self.ledger.sol[key("owner")],10001)

    def test_D01_explicit_admin_transition_stable_addresses_inactive_rejected(self):
        s=self.fixture()
        old=self.intent()
        witness=self.witness(old)
        before=(s.address,s.treasury,s.token_source)
        with self.assertRaises(Rejected):
            self.ledger.demo_mode(s.address,key("attacker"),2,self.tree.root,16)
        self.ledger.demo_mode(s.address,s.admin,2,self.tree.root,16)
        current=self.ledger.states[s.address]
        self.assertEqual(before,(current.address,current.treasury,current.token_source))
        self.rejected(old,witness,"inactive_mode")
