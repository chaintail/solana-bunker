"""Focused runtime intent/domain/rotation/staging gaps, frozen SBF binary.

Independent supplemental runner; does not mutate the shared harness or program.
Fresh disposable local XMSS keys, one original signed message per leaf; changed
messages reuse only the original authorization as adversarial witnesses.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from svm_harness import Harness, PROGRAM, TOKEN, SYSTEM, meta
from client.actions import encode_intent
from client.merkle import SecretTree
from crypto.xmss import keygen,sign_at,verify
from solders.instruction import Instruction
from solders.keypair import Keypair
from solders.pubkey import Pubkey

FROZEN_BINARY='8d7435ea6225ef4b09e972cef7ed3d2b99f7f4e1d1b9e9f8aa5124a0848f6e25'

def code(result):
    return json.loads(result.to_json())['err']['InstructionError'][1]['Custom']

def main():
    run_id='supplemental-intent-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:6]
    h=Harness(run_id)
    assert h.binary_digest==FROZEN_BINARY,'Unexpected program binary; do not silently mix results'
    h.public,h.secret=keygen(os.urandom(96));h.new_public,h.new_secret=keygen(os.urandom(96))
    h.setup(3)
    cases=[]
    def record(name,result,expected_code,verifier_reached,before,stage=None,notes=None):
        assert code(result)==expected_code,(name,code(result),expected_code)
        assert h.snapshot_public()==before,'Rejection persisted vault state or movement'
        cases.append(dict(scenario=name,evidence_level='local_svm',expected='rejection',observed='rejection',test_passed=True,
                          custom_error_code=expected_code,verifier_reached=verifier_reached,
                          failure_stage='signature_verifier' if verifier_reached else 'cheap_policy_or_stage_binding',
                          evidence_paths=h.records[-1]['evidence_paths'],notes=notes))

    def reject(value,witness,name,expected_code,deep=False,stage=None,notes=None):
        before=h.snapshot_public()
        result,_=h.execute(value,witness,expected='rejection',scenario=name,stage=stage,verifier_reached=deep)
        if stage is not None:
            h.records[-1]['transport'].update(transaction_index=0,transaction_count_for_operation=1)
        record(name,result,expected_code,deep,before,notes=notes)
        print(name,'PASS',flush=True)

    def stage_wire(wire,witness,name):
        pair=Keypair();stage=pair.pubkey();h.stages.append(stage)
        operation=run_id+'-'+name
        init=Instruction(PROGRAM,b'\x04'+struct.pack('<H',len(wire))+wire+struct.pack('<I',len(witness)),
                         [meta(h.relayer.pubkey(),True,True),meta(stage,True,True),meta(h.state),meta(SYSTEM)])
        h.send([init],signers=[h.relayer,pair],experiment={'scenario':name+'_stage_init','asset':None},operation=operation,index=0,total=5,witness_bytes=len(witness))
        for offset in range(0,len(witness),900):
            ix=Instruction(PROGRAM,b'\x05'+struct.pack('<I',offset)+witness[offset:offset+900],
                           [meta(h.relayer.pubkey(),True,True),meta(stage,True)])
            h.send([ix],experiment={'scenario':name+'_stage_upload','asset':None},operation=operation,index=1+offset//900,total=5,witness_bytes=len(witness))
        return stage

    def reject_raw(wire,witness,name,expected_code):
        stage=stage_wire(wire,witness,name)
        destination=Pubkey.from_bytes(wire[190:222]) if wire[189]==1 else h.owner.pubkey()
        ix=Instruction(PROGRAM,b'\x03'+struct.pack('<H',len(wire))+wire,
                       [meta(h.state,True),meta(h.treasury,True),meta(h.mint.pubkey()),meta(h.source,True),meta(destination,True),meta(TOKEN),meta(stage)])
        before=h.snapshot_public()
        result=h.send([ix],experiment={'scenario':name,'asset':None},expected='rejection',verifier_reached=False,witness_bytes=len(witness),
                      operation=run_id+'-'+name,index=4,total=5)
        record(name,result,expected_code,False,before)
        print(name,'PASS',flush=True)

    try:
        sol=h.intent(1,0);sol_wire=encode_intent(sol);sol_sig=sign_at(h.secret,0,sol_wire)
        # Entirely valid burn context reaches signature verification, not balances.
        burn=h.intent(3,0,targets=[3,4])
        reject(burn,sol_sig,'signed_action_SOL_to_valid_burn',12,True)
        token=h.intent(2,1);token_sig=sign_at(h.secret,1,encode_intent(token))
        reject(dict(token,mint=hashlib.sha256(b'wrong-disposable-mint').digest()),token_sig,'changed_signed_mint_policy',15,False,
               notes='Runtime exact mint/state/source checks intentionally reject before the XMSS verifier.')
        try:
            verify(h.public,encode_intent(dict(token,mint=hashlib.sha256(b'wrong-disposable-mint').digest())),token_sig)
            raise AssertionError('Changed mint passed cryptographic binding')
        except ValueError:
            cases.append(dict(scenario='changed_signed_mint_host_crypto_binding',evidence_level='host_reference',expected='rejection',observed='rejection',test_passed=True,verifier_reached=True,
                              notes='Direct full RFC verifier confirms cryptographic mint binding separately; runtime cheap mint policy is retained.'))
        for field,name,error in [('namespace','wrong_network_namespace',6),('vault_id','wrong_vault_identity',6)]:
            reject(dict(sol,**{field:hashlib.sha256(name.encode()).digest()}),sol_sig,name,error,False)
        reject(dict(sol,epoch=sol['epoch']+1),sol_sig,'stale_authority_epoch',8,False)
        wrong_program=encode_intent(dict(sol,program_id=hashlib.sha256(b'unrelated-local-program').digest()))
        pair=Keypair();ix=Instruction(PROGRAM,b'\x04'+struct.pack('<H',len(wrong_program))+wrong_program+struct.pack('<I',len(sol_sig)),
             [meta(h.relayer.pubkey(),True,True),meta(pair.pubkey(),True,True),meta(h.state),meta(SYSTEM)])
        before=h.snapshot_public();result=h.send([ix],signers=[h.relayer,pair],experiment={'scenario':'wrong_program_namespace_stage_init','asset':'SOL'},expected='rejection',verifier_reached=False)
        record('wrong_program_namespace_stage_init',result,6,False,before,notes='Program identity is checked by staging initialization before allocation; stage account remains absent.')
        assert h.svm.get_account(pair.pubkey()) is None
        rotation=h.intent(4,2);rotation_sig=sign_at(h.secret,2,encode_intent(rotation))
        changed_root=bytes([rotation['root'][0]^1])+rotation['root'][1:]
        reject(dict(rotation,root=changed_root),rotation_sig,'replacement_root_substitution',12,True)
        current=h.intent(4,2,root=h.public[:32],public_seed=h.public[32:])
        reject(current,rotation_sig,'same_current_authority_rotation',14,False)
        malformed=bytearray(encode_intent(rotation));malformed[190]=2
        reject_raw(bytes(malformed),rotation_sig,'replacement_mode_substitution',14)

        stage=stage_wire(sol_wire,sol_sig,'immutable_original_authorization')
        stage_before=h.svm.get_account(stage)
        for name,offset,chunk in [('sealed_stage_overwrite',0,b'\x00'),('sealed_stage_reseal',2500,b'\x00')]:
            ix=Instruction(PROGRAM,b'\x05'+struct.pack('<I',offset)+chunk,[meta(h.relayer.pubkey(),True,True),meta(stage,True)])
            before=h.snapshot_public();result=h.send([ix],experiment={'scenario':name,'asset':None},expected='rejection',verifier_reached=False)
            record(name,result,19,False,before)
            after=h.svm.get_account(stage);assert bytes(after.data)==bytes(stage_before.data) and after.lamports==stage_before.lamports
        reject(dict(sol,amount=101),sol_sig,'sealed_stage_bound_to_different_intent',19,False,stage=stage)
        before=h.snapshot_public();h.execute(sol,sol_sig,scenario='original_sealed_stage_executes',stage=stage,verifier_reached=True)
        h.records[-1]['operation_id']=run_id+'-immutable_original_authorization'
        after=h.snapshot_public();assert int(before['treasury']['lamports'])-int(after['treasury']['lamports'])==100
        cases.append(dict(scenario='original_sealed_stage_executes',evidence_level='local_svm',expected='success',observed='success',test_passed=True,verifier_reached=True,evidence_paths=h.records[-1]['evidence_paths']))

        # Explicit trusted administration changes verifier mode; no admin spends.
        before=h.snapshot_public();treasury_before=before['treasury'];source_before=before['source']
        transition=Instruction(PROGRAM,b'\x06'+struct.pack('<BH',2,16),[meta(h.admin.pubkey(),True,True),meta(h.state,True),meta(SYSTEM)])
        h.send([transition],h.admin,experiment={'scenario':'trusted_transition_xmss_to_merkle','asset':None})
        # Shared harness computes storage reserve deltas; a smaller allocation
        # retains actual account lamports here, so it is not a money refund.
        h.records[-1]['resources']['storage_refund_lamports']='0'
        account=h.svm.get_account(h.state)
        h.records[-1]['resources']['retained_excess_state_rent_lamports']=str(account.lamports-h.svm.minimum_balance_for_rent_exemption(len(account.data)))
        tree=SecretTree(h.secrets[:16])
        upload=Instruction(PROGRAM,b'\x01'+struct.pack('<I',0)+tree.root,[meta(h.admin.pubkey(),True,True),meta(h.state,True),meta(SYSTEM)])
        h.send([upload],h.admin,experiment={'scenario':'trusted_transition_authority_upload','asset':None})
        after=h.snapshot_public();assert treasury_before==after['treasury'] and source_before==after['source']
        assert before['state']['lamports']==after['state']['lamports'],'Reallocation unexpectedly refunded rent'
        inactive=h.intent(1,0) # Requested XMSS header while active account mode is Merkle.
        reject(inactive,sol_sig,'inactive_xmss_after_merkle_transition',7,False)
        h.mode=2;h.count=16;h.tree=tree;h.authority_len=32
        value=h.intent(1,0);before=h.snapshot_public();h.execute(value,h.witness(value),scenario='new_active_merkle_authorizes',verifier_reached=True)
        after=h.snapshot_public();assert int(before['treasury']['lamports'])-int(after['treasury']['lamports'])==100
        cases.append(dict(scenario='new_active_merkle_authorizes',evidence_level='local_svm',expected='success',observed='success',test_passed=True,verifier_reached=True,evidence_paths=h.records[-1]['evidence_paths'],notes='Same treasury/token source preserved across explicit trusted transition. State excess rent retained; no lamport refund.'))
    finally:
        benchmarks=ROOT/'artifacts/supplemental-intent-benchmarks.jsonl'
        benchmarks.write_text(''.join(json.dumps(row)+'\n'for row in h.records))
        results=dict(schema_version=1,run_id=run_id,commit=h.commit,source_sha256=h.source_sha256,program_binary_sha256=h.binary_digest,
                     runtime='solders0.29.0/LiteSVM',evidence_level='local_svm',test_cases=cases,case_count=len(cases),
                     actual_runtime_case_count=sum(c['evidence_level']=='local_svm'for c in cases),host_crypto_case_count=sum(c['evidence_level']=='host_reference'for c in cases),
                     measured_transactions=len(h.records),all_assertions_passed=all(c['test_passed']for c in cases),evidence_paths=['artifacts/supplemental-intent-benchmarks.jsonl'],
                     scope='Fresh isolated local keys/mock assets. Relayer attack excludes trusted admin/mint/upgrade credentials and hash seeds. No public network confirmation. Sealed stage and trusted transition data are real SBF execution. One current-authority signature per source intent; negatives alter submitted effects without signing changed messages.')
        (ROOT/'artifacts/supplemental-intent-results.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({k:results[k]for k in ('case_count','actual_runtime_case_count','host_crypto_case_count','measured_transactions','all_assertions_passed','run_id')}),flush=True)

if __name__=='__main__':main()
