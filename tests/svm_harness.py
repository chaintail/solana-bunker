"""Actual SBF custody execution in LiteSVM, with real SPL CPIs and serialized txs.

Local-only fixtures never receive shared-cluster funds. Admin/mint and relayer
are different keypairs; attacks submit as relayer and use no admin instruction.
"""
import datetime
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'tests'))
from solders.litesvm import LiteSVM
from solders.account import Account
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.system_program import create_account, CreateAccountParams, transfer, TransferParams
from solders.compute_budget import set_compute_unit_limit
from solders.transaction import Transaction
from solders.transaction_metadata import FailedTransactionMetadata
from client.actions import encode_intent
from client.merkle import SecretTree
from crypto.xmss import keygen, sign_at
from evidence_schema import FIELDS, validate, summarize

TOKEN=Pubkey.from_string('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')
SYSTEM=Pubkey.default()
BINARY=ROOT/'program/target/deploy/bunker_program.so'
PROGRAM=Pubkey.from_bytes(hashlib.sha256(b'bunker-independent-litesvm-program').digest())
NAMESPACE=hashlib.sha256(b'local-litesvm-no-network-genesis').digest()
NOW=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()


def meta(key,writable=False,signer=False):
    return AccountMeta(key,signer,writable)


class Harness:
    def __init__(self,run_id):
        self.run_id=run_id
        self.binary_bytes=BINARY.read_bytes()
        self.binary_digest=hashlib.sha256(self.binary_bytes).hexdigest()
        archive=ROOT/f'artifacts/binaries/{self.binary_digest}.so'
        archive.parent.mkdir(parents=True,exist_ok=True)
        archive.write_bytes(self.binary_bytes)
        self.source_sha256={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for folder in ('tests','client','program/src','crypto/xmss-verifier/src') for path in sorted((ROOT/folder).rglob('*')) if path.is_file() and path.suffix in {'.py','.rs'} and '__pycache__' not in path.parts}
        try:
            self.commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
        except subprocess.CalledProcessError:
            self.commit='source_snapshot:'+hashlib.sha256(json.dumps(self.source_sha256,sort_keys=True).encode()).hexdigest()
        self.records=[];self.results=[];self.seq=0
        self.public,self.secret=keygen(hashlib.sha256(b'independent-actual-svm-disposable-key1').digest()*3)
        self.new_public,self.new_secret=keygen(hashlib.sha256(b'independent-actual-svm-disposable-key2').digest()*3)

    def send(self,ixs,payer=None,signers=None,experiment=None,expected='success',operation=None,index=0,total=1,witness_bytes=None,proof_bytes=None,verifier_reached=None):
        payer=payer or self.relayer
        signers=signers or [payer]
        self.svm.expire_blockhash()  # Fresh outer envelope for exact inner retries.
        tx=Transaction.new_signed_with_payer([set_compute_unit_limit(1400000),*ixs],payer.pubkey(),signers,self.svm.latest_blockhash())
        storage_before=self.storage_snapshot()
        result=self.svm.send_transaction(tx)
        failed=isinstance(result,FailedTransactionMetadata)
        metadata=result.meta() if failed else result
        observed='rejection' if failed else 'success'
        logs=metadata.logs()
        self.seq+=1
        op=operation or f'{self.run_id}-{self.seq}'
        path=f'artifacts/logs/validation-svm/{self.run_id}/{self.seq:05d}.json'
        raw={'run_id':self.run_id,'operation_id':op,'observed_at_utc':NOW(),'result':json.loads(result.to_json()),'serialized_transaction_hex':bytes(tx).hex(),'transaction_bytes':len(bytes(tx)),'accounts_after':self.snapshot_public(),'attacker_scope':'ordinary dedicated relayer credential plus disclosed bearer witness; admin, upgrade, mint authority, and XMSS seeds excluded'}
        absolute=ROOT/path;absolute.parent.mkdir(parents=True,exist_ok=True);absolute.write_text(json.dumps(raw,indent=2)+'\n')
        if experiment:
            r={'schema_version':1,'run_id':self.run_id,'operation_id':op,'observed_at_utc':NOW(),'commit':self.commit,'source_sha256':self.source_sha256,'program_binary_sha256':self.binary_digest,'evidence_paths':[path]}
            r.update({section:{field:None for field in fields} for section,fields in FIELDS.items()})
            r['environment'].update(evidence_level='local_svm',cluster='LiteSVM isolated fixture',runtime_version='solders0.29.0/litesvm',toolchain_manifest='reports/environment.json')
            r['experiment'].update(mode={1:'SECRET_ARRAY_V1',2:'MERKLE_SECRET_V1',3:'XMSS_SHA2_10_256_V1'}[self.mode],parameter_set='XMSS-SHA2_10_256' if self.mode==3 else None,asset=experiment.get('asset'),mint=str(self.mint.pubkey()),leaf_count=self.count,scenario=experiment['scenario'],fixture_id=self.fixture_id,command='python3 tests/svm_harness.py')
            r['outcome'].update(expected=expected,observed=observed,test_passed=expected==observed,error_code=str(result.err()) if failed else None,failure_stage='program_execution' if failed else None,verifier_reached=verifier_reached)
            r['transport'].update(version='legacy',transaction_index=index,transaction_count_for_operation=total,transaction_bytes=len(bytes(tx)),instruction_data_bytes=sum(len(ix.data) for ix in ixs),signature_or_witness_bytes=witness_bytes,merkle_proof_bytes=proof_bytes,transaction_signature=str(metadata.signature()),confirmation_status=None)
            state=self.svm.get_account(self.state)
            source=self.svm.get_account(self.source)
            treasury=self.svm.get_account(self.treasury)
            storage_after=self.storage_snapshot()
            deposit=sum(max(value-storage_before.get(address,0),0) for address,value in storage_after.items())
            refund=sum(max(value-storage_after.get(address,0),0) for address,value in storage_before.items())
            temporary_bytes=sum(len(self.svm.get_account(address).data) for address in self.stages if self.svm.get_account(address))
            r['resources'].update(compute_limit=1400000,compute_consumed=metadata.compute_units_consumed(),allocated_account_bytes=sum(len(a.data) for a in (state,source,treasury) if a),logical_authority_bytes=self.authority_len,actual_transaction_fee_lamports=str(metadata.fee()),storage_deposit_lamports=str(deposit),storage_refund_lamports=str(refund),temporary_account_bytes=temporary_bytes,usage_bitmap_bytes=128)
            assert not validate(r,ROOT),validate(r,ROOT)
            self.records.append(r)
        if observed!=expected:
            raise AssertionError(f'{experiment} expected{expected}, observed{observed}: {result}')
        return result

    def setup(self,mode,count=16):
        self.mode=mode;self.count=1024 if mode==3 else count
        self.svm=LiteSVM()
        self.stages=[]
        self.svm.add_program(PROGRAM,self.binary_bytes)
        self.admin=Keypair();self.relayer=Keypair();self.mint=Keypair();self.owner=Keypair();self.attacker=Keypair();self.owner_token=Keypair();self.attacker_token=Keypair()
        for pair in (self.admin,self.relayer,self.owner,self.attacker):
            self.svm.airdrop(pair.pubkey(),10000000000)
        self.fixture_id=f'{self.run_id}-mode{mode}-n{self.count}-{uuid.uuid4().hex[:8]}'
        self.vault=hashlib.sha256(self.fixture_id.encode()).digest()
        self.state,_=Pubkey.find_program_address([b'bunker_state',self.vault],PROGRAM)
        self.treasury,_=Pubkey.find_program_address([b'bunker_treasury',bytes(self.state)],PROGRAM)
        self.source,_=Pubkey.find_program_address([b'bunker_token',bytes(self.state)],PROGRAM)
        self.secrets=[hashlib.sha256(b'isolated-validation-bearer'+i.to_bytes(4,'little')).digest() for i in range(self.count)]
        self.tree=SecretTree(self.secrets)
        authority=b''.join(hashlib.sha256(s).digest() for s in self.secrets) if mode==1 else self.tree.root if mode==2 else self.public
        self.authority_len=len(authority)
        create=create_account(CreateAccountParams(from_pubkey=self.admin.pubkey(),to_pubkey=self.mint.pubkey(),lamports=self.svm.minimum_balance_for_rent_exemption(82),space=82,owner=TOKEN))
        init_mint=Instruction(TOKEN,b'\x14\x06'+bytes(self.admin.pubkey())+b'\x00',[meta(self.mint.pubkey(),True)])
        self.send([create,init_mint],self.admin,[self.admin,self.mint])
        data=b'\x00'+self.vault+NAMESPACE+struct.pack('<BH',mode,self.count)
        init=Instruction(PROGRAM,data,[meta(self.admin.pubkey(),True,True),meta(self.state,True),meta(self.treasury,True),meta(self.source,True),meta(self.mint.pubkey()),meta(SYSTEM),meta(TOKEN)])
        self.send([init],self.admin,experiment={'scenario':'initialize','asset':None})
        self.init_data=data;self.init_accounts=init.accounts
        for offset in range(0,len(authority),900):
            write=Instruction(PROGRAM,b'\x01'+struct.pack('<I',offset)+authority[offset:offset+900],[meta(self.admin.pubkey(),True,True),meta(self.state,True),meta(SYSTEM)])
            self.send([write],self.admin,experiment={'scenario':'authority_upload','asset':None},operation=f'{self.fixture_id}-authority',index=offset//900,total=(len(authority)+899)//900)
        for pair,owner in ((self.owner_token,self.owner),(self.attacker_token,self.attacker)):
            create=create_account(CreateAccountParams(from_pubkey=self.admin.pubkey(),to_pubkey=pair.pubkey(),lamports=self.svm.minimum_balance_for_rent_exemption(165),space=165,owner=TOKEN))
            initialize=Instruction(TOKEN,b'\x12'+bytes(owner.pubkey()),[meta(pair.pubkey(),True),meta(self.mint.pubkey())])
            self.send([create,initialize],self.admin,[self.admin,pair])
        self.deposit(100000,100000)

    def deposit(self,sol=0,tokens=0):
        if sol:
            self.send([transfer(TransferParams(from_pubkey=self.relayer.pubkey(),to_pubkey=self.treasury,lamports=sol))])
        if tokens:
            mint=Instruction(TOKEN,b'\x07'+struct.pack('<Q',tokens),[meta(self.mint.pubkey(),True),meta(self.source,True),meta(self.admin.pubkey(),False,True)])
            self.send([mint],self.admin)

    def snapshot_public(self):
        if not hasattr(self,'state'):
            return {}
        out={}
        for name,address in [('state',self.state),('treasury',self.treasury),('source',self.source),('owner',self.owner.pubkey()),('attacker',self.attacker.pubkey()),('owner_token',self.owner_token.pubkey()),('attacker_token',self.attacker_token.pubkey())]:
            account=self.svm.get_account(address)
            out[name]=None if not account else {'address':str(address),'lamports':str(account.lamports),'owner':str(account.owner),'data_hex':account.data.hex(),'allocated_bytes':len(account.data)}
        return out

    def storage_snapshot(self):
        if not hasattr(self,'state'):return {}
        out={}
        for address in (self.state,self.treasury,self.source,*getattr(self,'stages',[])):
            account=self.svm.get_account(address)
            if account and account.data:
                out[str(address)]=min(account.lamports,self.svm.minimum_balance_for_rent_exemption(len(account.data)))
        return out

    def state_values(self):
        data=self.svm.get_account(self.state).data
        return {'epoch':int.from_bytes(data[203:211],'little'),'nonce':int.from_bytes(data[211:219],'little'),'consumed':{i for i in range(self.count) if data[230+i//8]&(1<<(i%8))},'authority':data[358:358+self.authority_len]}

    def intent(self,action=1,leaf=0,**updates):
        state=self.state_values()
        value=dict(program_id=bytes(PROGRAM),namespace=NAMESPACE,vault_id=self.vault,state=bytes(self.state),treasury=bytes(self.treasury),mode=self.mode,epoch=state['epoch'],nonce=state['nonce'],leaf_index=leaf,action=action)
        if action==1:value.update(destination=bytes(self.owner.pubkey()),amount=100)
        elif action==2:value.update(token_program=bytes(TOKEN),mint=bytes(self.mint.pubkey()),source=bytes(self.source),destination=bytes(self.owner_token.pubkey()),amount=100,decimals=6)
        elif action==3:value.update(targets=[1,3])
        else:value.update(new_mode=3,parameter_id=1,root=self.new_public[:32],public_seed=self.new_public[32:])
        value.update(updates)
        return value

    def witness(self,intent,new=False):
        leaf=intent['leaf_index']
        if self.mode==1:return struct.pack('<I',leaf)+self.secrets[leaf]
        if self.mode==2:return self.tree.witness(leaf)
        return sign_at(self.new_secret if new else self.secret,leaf,encode_intent(intent))

    def execute(self,value,witness,expected='success',scenario='withdraw',stage=None,accounts=None,verifier_reached=None):
        wire=encode_intent(value)
        asset='SOL' if value['action']==1 else 'MOCK_USDC' if value['action']==2 else None
        op=f'{self.run_id}-logical-{uuid.uuid4().hex[:12]}'
        staged=self.mode==3 and len(witness)==2500
        if staged and stage is None:
            pair=Keypair();stage=pair.pubkey()
            self.stages.append(stage)
            init=Instruction(PROGRAM,b'\x04'+struct.pack('<H',len(wire))+wire+struct.pack('<I',len(witness)),[meta(self.relayer.pubkey(),True,True),meta(stage,True,True),meta(self.state),meta(SYSTEM)])
            self.send([init],signers=[self.relayer,pair],experiment={'scenario':scenario+'_stage_init','asset':asset},operation=op,index=0,total=5,witness_bytes=len(witness))
            for offset in range(0,len(witness),900):
                write=Instruction(PROGRAM,b'\x05'+struct.pack('<I',offset)+witness[offset:offset+900],[meta(self.relayer.pubkey(),True,True),meta(stage,True)])
                self.send([write],experiment={'scenario':scenario+'_stage_upload','asset':asset},operation=op,index=1+offset//900,total=5,witness_bytes=len(witness))
        destination=Pubkey.from_bytes(value['destination']) if 'destination'in value else self.owner.pubkey()
        metas=accounts or [meta(self.state,True),meta(self.treasury,True),meta(self.mint.pubkey()),meta(self.source,True),meta(destination,True),meta(TOKEN)]
        if staged:metas=[*metas,meta(stage)]
        ix=Instruction(PROGRAM,bytes([3 if staged else 2])+struct.pack('<H',len(wire))+wire+(b''if staged else witness),metas)
        before=self.snapshot_public()
        result=self.send([ix],experiment={'scenario':scenario,'asset':asset},expected=expected,operation=op,index=4 if staged else 0,total=5 if staged else 1,witness_bytes=len(witness),proof_bytes=len(witness)-36 if self.mode==2 else None,verifier_reached=verifier_reached)
        after=self.snapshot_public()
        if expected=='rejection':
            assert before==after,'Failed transaction persisted vault state or movement'
        self.results.append({'scenario':scenario,'mode':self.mode,'asset':asset,'expected':expected,'passed':True,'before':before,'after':after,'operation_id':op,'evidence_level':'local_svm'})
        return result,stage

    def flush(self):
        output=ROOT/'artifacts/validation-benchmarks.jsonl'
        output.write_text(''.join(json.dumps(r)+'\n'for r in self.records))
        summarize(self.records,ROOT/'artifacts/validation-benchmark-summary.csv')
        (ROOT/'artifacts/validation-svm-results.json').write_text(json.dumps({'schema_version':1,'run_id':self.run_id,'commit':self.commit,'source_sha256':self.source_sha256,'program_binary_sha256':self.binary_digest,'evidence_level':'local_svm','test_cases':self.results,'measured_attempts':len(self.records),'scope':'Runtime execution in LiteSVM; no network confirmation. Distinct admin/mint vs relayer. Deterministic test keysets deliberately reset/reused only inside isolated no-value fixtures for adversarial tests; never fund on shared cluster and never emulate this signing bypass with a real key. Exact transaction envelopes/raw runtime metadata in evidence paths. Temporary stage accounts retained and included in logical-operation setup; no refunds implemented.'},indent=2)+'\n')


def full_correctness(h,modes):
    for mode in modes:
        # Actual copied-bearer weakness or exact-message rejection on both assets.
        for action in (1,2):
            h.setup(mode)
            value=h.intent(action)
            witness=h.witness(value)
            altered={**value,'destination':bytes(h.attacker.pubkey() if action==1 else h.attacker_token.pubkey())}
            before=h.snapshot_public()
            h.execute(altered,witness,expected='rejection' if mode==3 else 'success',scenario='copied_destination_substitution',verifier_reached=True)
            after=h.snapshot_public()
            if mode!=3:
                if action==1:assert int(after['attacker']['lamports'])-int(before['attacker']['lamports'])==100
                else:assert int.from_bytes(bytes.fromhex(after['attacker_token']['data_hex'])[64:72],'little')==100
            else:
                h.execute({**value,'amount':101},witness,expected='rejection',scenario='changed_signed_amount',verifier_reached=True)
        h.setup(mode)
        value=h.intent()
        witness=h.witness(value)
        # No state movement for exact account substitution and missing privileges.
        accounts=[meta(h.state,True),meta(h.treasury,True),meta(h.mint.pubkey()),meta(h.source,True),meta(h.owner.pubkey(),True),meta(TOKEN)]
        for position in (0,1,4):
            wrong=list(accounts);wrong[position]=meta(wrong[position].pubkey,False)
            h.execute(value,witness,expected='rejection',scenario=f'readonly_account_{position}',accounts=wrong,verifier_reached=False)
        wrong=list(accounts);wrong[1]=meta(h.attacker.pubkey(),True)
        h.execute(value,witness,expected='rejection',scenario='treasury_account_substitution',accounts=wrong,verifier_reached=False)
        # Invalid witness reaches verifier, with otherwise current, funded fixture.
        for offset in ((4,) if mode==1 else (36,) if mode==2 else (36,2180)):
            corrupt=bytearray(witness);corrupt[offset]^=1
            h.execute(value,bytes(corrupt),expected='rejection',scenario=f'invalid_witness_byte_{offset}',verifier_reached=True)
        h.execute(value,b'',expected='rejection',scenario='missing_hash_authorization',verifier_reached=False)
        # Exact source alias must reject even if caller supplies a decoy unused source.
        alias={**value,'destination':bytes(h.source)}
        wrong=list(accounts);wrong[3]=meta(h.attacker.pubkey());wrong[4]=meta(h.source,True)
        h.execute(alias,h.witness(alias),expected='rejection',scenario='canonical_source_destination_alias_with_decoy',accounts=wrong,verifier_reached=False)
        # Burn strict targets; atomically consume its own authorizing leaf too.
        burn=h.intent(3)
        burn_witness=h.witness(burn)
        if mode==3:
            h.execute({**burn,'targets':[1,4]},burn_witness,expected='rejection',scenario='signed_burn_list_mutation',verifier_reached=True)
        h.execute({**burn,'targets':[h.count]},burn_witness,expected='rejection',scenario='burn_out_of_range',verifier_reached=False)
        h.execute(burn,burn_witness,scenario='burn_exact_leaves',verifier_reached=True)
        assert h.state_values()['consumed']=={0,1,3}
        used=h.intent(leaf=1)
        h.execute(used,h.witness(used),expected='rejection',scenario='burned_leaf_rejected',verifier_reached=False)
        second=h.intent(3,leaf=2,targets=[3])
        h.execute(second,h.witness(second),expected='rejection',scenario='already_burned_target_rejected',verifier_reached=False)
        # Raw malformed burn lists bypass client canonical checks, exercise program checks.
        for tail in (b'\x02'+struct.pack('<II',4,4),b'\x02'+struct.pack('<II',5,4),b'\x01'+struct.pack('<I',2)):
            canonical=encode_intent(h.intent(3,leaf=2,targets=[4]))
            raw=canonical[:190]+tail
            primitive=h.witness(h.intent(3,leaf=2,targets=[4])) if mode!=3 else b''
            ix=Instruction(PROGRAM,b'\x02'+struct.pack('<H',len(raw))+raw+primitive,accounts)
            before=h.snapshot_public()
            rejected=h.send([ix],expected='rejection',experiment={'scenario':'burn_noncanonical_or_signer_target','asset':None},verifier_reached=False)
            assert 'Custom(13)' in str(rejected.err()),str(rejected.err())
            assert before==h.snapshot_public()
        # Failure occurs after authorizer consumption in code, runtime must roll back.
        h.setup(mode)
        value=h.intent(amount=100001)
        witness=h.witness(value)
        _,stage=h.execute(value,witness,expected='rejection',scenario='insufficient_balance_atomic_rollback',verifier_reached=True)
        h.deposit(sol=1)
        h.execute(value,witness,stage=stage,scenario='exact_authorization_retry_after_deposit',verifier_reached=True)
        assert h.state_values()['consumed']=={0}
        print(f'actual SVM mode{mode}: attacks, accounts, burns, exact retry passed',flush=True)
    if 3 in modes:
        h.setup(3)
        rotation=h.intent(4)
        witness=h.witness(rotation)
        before=h.snapshot_public()
        h.execute({**rotation,'root':hashlib.sha256(b'malicious-root').digest()},witness,expected='rejection',scenario='replacement_root_mutation',verifier_reached=True)
        h.execute(rotation,witness,scenario='fresh_xmss_root_rotation',verifier_reached=True)
        after=h.snapshot_public()
        for account in ('treasury','source'):
            assert before[account]==after[account]
        assert h.state_values()['epoch']==1 and h.state_values()['nonce']==1 and h.state_values()['authority']==h.new_public
        old=h.intent(leaf=2)
        h.execute(old,h.witness(old),expected='rejection',scenario='unused_old_root_current_epoch_rejected',verifier_reached=True)
        fresh=h.intent(leaf=0)
        h.execute(fresh,h.witness(fresh,new=True),scenario='new_root_post_rotation_withdrawal',verifier_reached=True)
        print('actual SVM XMSS fresh rotation, stable addresses/balances, old root rejection and new withdrawal passed',flush=True)
    if modes==[1,2,3]:
        # D01: one actual vault progresses across modes; this is trusted setup.
        h.setup(1,16)
        original_state,original_treasury,original_source=h.state,h.treasury,h.source
        for mode,count in ((2,16),(3,1024)):
            before=h.snapshot_public()
            switch=Instruction(PROGRAM,b'\x06'+struct.pack('<BH',mode,count),[meta(h.admin.pubkey(),True,True),meta(h.state,True),meta(SYSTEM)])
            h.send([switch],h.admin)
            h.mode=mode;h.count=count
            authority=h.tree.root if mode==2 else h.public
            h.authority_len=len(authority)
            write=Instruction(PROGRAM,b'\x01'+struct.pack('<I',0)+authority,[meta(h.admin.pubkey(),True,True),meta(h.state,True),meta(SYSTEM)])
            h.send([write],h.admin)
            after=h.snapshot_public()
            assert (h.state,h.treasury,h.source)==(original_state,original_treasury,original_source)
            assert before['treasury']==after['treasury'] and before['source']==after['source']
            h.results.append({'scenario':'trusted_same_vault_mode_transition','mode':mode,'asset':None,'expected':'success','passed':True,'before':before,'after':after,'evidence_level':'local_svm','ordinary_demo_admin_trusted':True})
            value=h.intent(leaf=0)
            h.execute(value,h.witness(value),scenario='same_vault_post_transition_withdrawal',verifier_reached=True)
        print('actual SVM same-vault array->Merkle->XMSS transition preserves receiving accounts and balances',flush=True)
    for mode in (m for m in modes if m in (1,2)):
        for count in (16,256,1024):
            h.setup(mode,count)
            for action in (1,2):
                value=h.intent(action,leaf=action-1)
                h.execute(value,h.witness(value),scenario='size_comparison_success',verifier_reached=True)
            size=len(h.svm.get_account(h.state).data)
            assert size==358+(count*32 if mode==1 else 32)
            print(f'actual SVM mode{mode} leaves{count}: allocated state{size} bytes, both assets passed',flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--demo',choices=['array','merkle','xmss'])
    parser.add_argument('--samples',type=int,default=1)
    parser.add_argument('--full',action='store_true')
    args=parser.parse_args()
    modes=[{'array':1,'merkle':2,'xmss':3}[args.demo]] if args.demo else [1,2,3]
    h=Harness('validation-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S'))
    try:
        for mode in modes:
            for action in (1,2):
                h.setup(mode,256 if args.samples>16 else 16)
                value=h.intent(action)
                witness=h.witness(value)
                before=h.snapshot_public()
                h.execute(value,witness,scenario='principal_success',verifier_reached=True)
                after=h.snapshot_public()
                if action==1:
                    assert int(before['treasury']['lamports'])-int(after['treasury']['lamports'])==100
                    assert int(after['owner']['lamports'])-int(before['owner']['lamports'])==100
                else:
                    amount=lambda snap,name:int.from_bytes(bytes.fromhex(snap[name]['data_hex'])[64:72],'little')
                    assert amount(before,'source')-amount(after,'source')==100
                    assert amount(after,'owner_token')-amount(before,'owner_token')==100
                assert h.state_values()['consumed']=={0}
                h.execute(value,witness,expected='rejection',scenario='exact_replay',verifier_reached=False)
                print(f'actual SVM mode{mode} asset{action} success+replay passed',flush=True)
                for leaf in range(1,args.samples):
                    value=h.intent(action,leaf=leaf)
                    h.execute(value,h.witness(value),scenario='principal_success',verifier_reached=True)
        if args.full:
            full_correctness(h,modes)
    finally:
        h.flush()


if __name__=='__main__':
    main()
