"""Bounded supplemental functional tests on the frozen native SBF binary.

This imports the independent harness unchanged. It owns only supplemental
artifacts, and does not rerun the principal benchmark suite. No network use.
"""
from __future__ import annotations
import datetime
import hashlib
import json
from pathlib import Path
import struct
import sys
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tests.svm_harness import Harness, PROGRAM, NAMESPACE, TOKEN, SYSTEM, meta
from solders.instruction import Instruction
from solders.pubkey import Pubkey
from client.actions import encode_intent

BINARY_SHA='8d7435ea6225ef4b09e972cef7ed3d2b99f7f4e1d1b9e9f8aa5124a0848f6e25'
SOURCE_SHA='4e8db919e96074592bfeb1b5021c957f14338393f8cc93b3b826c849e5006816'
NOW=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()

class SupplementalHarness(Harness):
    def send(self,*args,**kwargs):
        result=super().send(*args,**kwargs)
        old=ROOT/f'artifacts/logs/validation-svm/{self.run_id}/{self.seq:05d}.json'
        new=ROOT/f'artifacts/supplemental-program-logs/{self.run_id}/{self.seq:05d}.json'
        new.parent.mkdir(parents=True,exist_ok=True)
        old.replace(new)
        if self.records and self.records[-1]['evidence_paths']==[str(old.relative_to(ROOT))]:
            self.records[-1]['evidence_paths']=[str(new.relative_to(ROOT))]
        self.last_raw=str(new.relative_to(ROOT))
        return result


def main():
    run_id='supplemental-program-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
    h=SupplementalHarness(run_id)
    assert h.binary_digest==BINARY_SHA,'Native binary changed; do not run against an unreviewed build'
    assert hashlib.sha256((ROOT/'program/src/lib.rs').read_bytes()).hexdigest()==SOURCE_SHA,'Native source changed'
    cases=[]

    def archive(case_id,matrix_id,expected_code,result,before,after,verifier_reached):
        assert before==after,'Rejected transaction changed custody account state or balances'
        actual=str(result.err())
        assert f'Custom({expected_code})' in actual,(case_id,actual,expected_code)
        cases.append(dict(case_id=case_id,matrix_ids=matrix_id,passed=True,evidence_level='local_svm',
            expected='rejection',observed='rejection',failure_stage='program_execution',
            actual_error=actual,program_error_code=expected_code,verifier_reached=verifier_reached,
            unchanged_custody_snapshot=True,before=before,after=after,evidence_paths=[h.last_raw]))

    def reject_ix(case_id,matrix_id,ix,code,verifier=False,payer=None,signers=None,extra=()):
        before=h.snapshot_public()
        extra_before={str(key):None if h.svm.get_account(key) is None else json.loads(h.svm.get_account(key).to_json()) for key in extra}
        result=h.send([ix],payer=payer,signers=signers,expected='rejection',
            experiment={'scenario':case_id,'asset':None},verifier_reached=verifier)
        after=h.snapshot_public()
        extra_after={str(key):None if h.svm.get_account(key) is None else json.loads(h.svm.get_account(key).to_json()) for key in extra}
        assert extra_before==extra_after,'Fresh initialization targets persisted mutation'
        archive(case_id,matrix_id,code,result,before,after,verifier)
        cases[-1].update(extra_accounts_before=extra_before,extra_accounts_after=extra_after)

    def reject_execute(case_id,matrix_id,value,witness,code,accounts=None,verifier=False):
        before=h.snapshot_public()
        result,_=h.execute(value,witness,expected='rejection',scenario=case_id,accounts=accounts,verifier_reached=verifier)
        archive(case_id,matrix_id,code,result,before,h.snapshot_public(),verifier)

    h.setup(1)
    # Reinitialization reaches the create guard after correct canonical accounts.
    duplicate=Instruction(PROGRAM,h.init_data,h.init_accounts)
    reject_ix('duplicate_initialization_preserves_existing_custody',['F02'],duplicate,4,payer=h.admin,signers=[h.admin])

    # A fresh vault prevents duplicate-initialization checks hiding missing signer.
    fresh_vault=hashlib.sha256((run_id+'-fresh-init').encode()).digest()
    state,_=Pubkey.find_program_address([b'bunker_state',fresh_vault],PROGRAM)
    treasury,_=Pubkey.find_program_address([b'bunker_treasury',bytes(state)],PROGRAM)
    source,_=Pubkey.find_program_address([b'bunker_token',bytes(state)],PROGRAM)
    unsigned_admin_init=Instruction(PROGRAM,b'\x00'+fresh_vault+NAMESPACE+struct.pack('<BH',1,16),
        [meta(h.admin.pubkey(),True,False),meta(state,True),meta(treasury,True),meta(source,True),
         meta(h.mint.pubkey()),meta(SYSTEM),meta(TOKEN)])
    reject_ix('initialization_missing_required_admin_signer',['F06'],unsigned_admin_init,3,
        payer=h.relayer,signers=[h.relayer],extra=(state,treasury,source))

    value=h.intent(2);witness=h.witness(value)
    accounts=[meta(h.state,True),meta(h.treasury,True),meta(h.mint.pubkey()),meta(h.source,True),meta(h.owner_token.pubkey(),True),meta(TOKEN)]
    replacements=[(0,h.attacker.pubkey(),2,'state'),(2,h.attacker_token.pubkey(),15,'mint'),
                  (3,h.attacker_token.pubkey(),15,'source'),(5,SYSTEM,15,'token_program')]
    for position,key,code,name in replacements:
        wrong=list(accounts);wrong[position]=meta(key,accounts[position].is_writable)
        reject_execute(f'token_{name}_account_binding_mismatch',['F05'],value,witness,code,wrong)
    encoded_wrong_state={**value,'state':bytes(h.attacker.pubkey())}
    reject_execute('signed_state_identity_mismatch',['F05'],encoded_wrong_state,witness,6)
    readonly=list(accounts);readonly[3]=meta(h.source,False)
    reject_execute('token_source_readonly_privilege',['F06'],value,witness,3,readonly)
    outside=h.intent(leaf=h.count)
    reject_execute('array_authorizing_index_out_of_range',['A02'],outside,
        struct.pack('<I',h.count)+h.secrets[0],10)
    reject_execute('array_witness_index_disagrees_with_intent',['A02'],h.intent(),
        struct.pack('<I',1)+h.secrets[0],11)

    h.setup(2)
    valid=h.intent();valid_witness=h.witness(valid)
    reject_execute('merkle_witness_index_disagrees_with_intent',['M02'],h.intent(leaf=1),valid_witness,11)
    # There are no caller-supplied direction flags: traversal derives from index.
    # Changing the declared leaf and traversal while retaining leaf0 material
    # reaches the Merkle root check, which rejects the inconsistent path.
    flipped=struct.pack('<I',1)+valid_witness[4:]
    reject_execute('merkle_wrong_direction_implied_by_changed_index',['M02'],h.intent(leaf=1),flipped,12,verifier=True)
    corrupt=bytearray(valid_witness);corrupt[36]^=1
    reject_execute('merkle_corrupted_sibling_path',['M02'],valid,bytes(corrupt),12,verifier=True)
    reject_execute('merkle_truncated_proof_length',['M02'],valid,valid_witness[:-32],11)
    reject_execute('merkle_extra_proof_length',['M02'],valid,valid_witness+bytes(32),11)

    summary=dict(schema_version=1,run_id=run_id,observed_at_utc=NOW(),commit=h.commit,
        program_binary_sha256=BINARY_SHA,native_program_source_sha256=SOURCE_SHA,
        source_sha256=h.source_sha256,evidence_level='local_svm',cluster='isolated LiteSVM fixtures',
        runtime='solders0.29.0/LiteSVM',passed=len(cases),failed=0,test_cases=cases,
        measured_attempts=len(h.records),raw_transaction_count=h.seq,
        scope='Supplemental functional checks F02/F05/F06/A02/M02. Native source unchanged; no network confirmation. Admin and relayer are separate disposable local keys.',
        limitations=['This is a bounded acceptance supplement, not a general audit. Readonly/account-policy failures occur before verification where recorded. Merkle directions are derived from index; no explicit direction field exists.'])
    (ROOT/'artifacts/supplemental-program-results.json').write_text(json.dumps(summary,indent=2)+'\n')
    (ROOT/'artifacts/supplemental-program-benchmarks.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in h.records))
    print(json.dumps(dict(passed=len(cases),failed=0,measured_attempts=len(h.records),
        binary_sha256=BINARY_SHA,results='artifacts/supplemental-program-results.json')))

if __name__=='__main__':main()
