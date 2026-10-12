"""Actual LiteSVM CLI adapter using the independent custody harness.

The harness is validator-owned. This adapter emits separately named client
evidence and always signs through the durable client journal. Every run gets
fresh disposable key material; journals are local temporary signing state.
"""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import uuid
from .actions import encode_intent
from .journal import SigningJournal, AuthorityHistory
from .transport import XMSS_TRANSPORTS
from crypto.xmss import keygen, sign_at

ROOT=Path(__file__).resolve().parents[1]

def harness_class():
    spec=importlib.util.spec_from_file_location("bunker_independent_svm_harness",ROOT/"tests/svm_harness.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.Harness

def token_amount(snapshot,name):
    return int.from_bytes(bytes.fromhex(snapshot[name]["data_hex"])[64:72],"little")

def summary(h):
    snapshot=h.snapshot_public();state=h.state_values()
    return {"treasury":snapshot["treasury"]["address"],"token_source":snapshot["source"]["address"],
            "treasury_lamports":snapshot["treasury"]["lamports"],"token_base_units":str(token_amount(snapshot,"source")),
            "owner_sol":snapshot["owner"]["lamports"],"owner_tokens":str(token_amount(snapshot,"owner_token")),
            "attacker_sol":snapshot["attacker"]["lamports"],"attacker_tokens":str(token_amount(snapshot,"attacker_token")),
            "epoch":str(state["epoch"]),"nonce":str(state["nonce"]),"consumed":sorted(state["consumed"])}

def run(mode=1,samples=1,count=16,xmss_transport="inline-v1"):
    if xmss_transport not in XMSS_TRANSPORTS:raise ValueError("unknown XMSS transport")
    if type(samples) is not int or not 1<=samples<=20:raise ValueError("samples must be 1..20")
    run_id="client-svm-"+datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")+"-"+uuid.uuid4().hex[:6]
    h=harness_class()(run_id,xmss_transport=xmss_transport)
    # Validator fixtures are intentionally reproducible; client signing tests
    # use fresh random keysets to avoid sharing mutable signing state.
    if mode==3:
        h.public,h.secret=keygen(os.urandom(96));h.new_public,h.new_secret=keygen(os.urandom(96))
    h.setup(mode,count)
    events=[]
    def narrate(name,before=None,message=None,witness=None,**extra):
        event={"event_version":1,"event":name,"evidence_level":"local_svm","origin":"client_verified_runtime_result",
               "run_id":run_id,"operation_id":h.results[-1]["operation_id"] if h.results else run_id+"-init",
               "mode":mode,"public_addresses":{"state":str(h.state),"treasury":str(h.treasury),"mint":str(h.mint.pubkey()),"source":str(h.source)},
               "before":before,"after":summary(h),"message_commitment":hashlib.sha256(message).hexdigest() if message else None,
               "witness_bytes":len(witness) if witness else None,"transaction_evidence":h.records[-1]["evidence_paths"] if h.records else [],
               "transaction_signature":h.records[-1]["transport"]["transaction_signature"] if h.records else None,
               "compute_units":h.records[-1]["resources"]["compute_consumed"] if h.records else None,
               "transport":h.records[-1]["transport"] if h.records else None,
               "resources":h.records[-1]["resources"] if h.records else None,**extra}
        events.append(event)
    narrate("vault_initialized",attacker_scope="distinct relayer/funding credentials and disclosed witness only; no admin, mint authority, upgrade credential or hash seeds")
    try:
        with tempfile.TemporaryDirectory(prefix="bunker-client-svm-") as directory:
            history=AuthorityHistory(directory)
            if mode==3:history.install(h.public,0)
            def sign(value,operation,new=False):
                if mode!=3:return h.witness(value)
                public=h.new_public if new else h.public;secret=h.new_secret if new else h.secret
                keyset=hashlib.sha256(public).hexdigest()
                with SigningJournal(Path(directory)/keyset,keyset) as journal:
                    signed=journal.sign(operation,encode_intent(value),lambda index,message:sign_at(secret,index,message),value["leaf_index"])
                return signed["signature"]
            def index():
                used=set(h.state_values()["consumed"])
                if mode==3:
                    keyset=hashlib.sha256(h.public).hexdigest()
                    with SigningJournal(Path(directory)/keyset,keyset) as journal:
                        used.update(x["leaf_index"] for x in journal.public_status())
                return next(i for i in range(h.count) if i not in used)
            for action in (1,2):
                for sample in range(samples):
                    value=h.intent(action,index());message=encode_intent(value);witness=sign(value,f"principal-{action}-{sample}")
                    before=summary(h);h.execute(value,witness,scenario="client_principal_success",verifier_reached=True)
                    after=summary(h)
                    asset="SOL" if action==1 else "MOCK_USDC"
                    if action==1:assert int(before["treasury_lamports"])-int(after["treasury_lamports"])==100 and int(after["owner_sol"])-int(before["owner_sol"])==100
                    else:assert int(before["token_base_units"])-int(after["token_base_units"])==100 and int(after["owner_tokens"])-int(before["owner_tokens"])==100
                    narrate("withdrawal_confirmed",before,message,witness,asset=asset,sample=sample)
                    h.execute(value,witness,expected="rejection",scenario="client_exact_replay",verifier_reached=False)
                    narrate("withdrawal_rejected",after,message,witness,asset=asset,scenario="replay",test_passed=True)
                value=h.intent(action,index());message=encode_intent(value);witness=sign(value,f"attack-{action}")
                changed=dict(value,destination=bytes(h.attacker.pubkey() if action==1 else h.attacker_token.pubkey()))
                before=summary(h);expected="rejection" if mode==3 else "success"
                h.execute(changed,witness,expected=expected,scenario="client_copied_witness_destination",verifier_reached=True)
                after=summary(h)
                if mode==3:assert before==after
                elif action==1:assert int(after["attacker_sol"])-int(before["attacker_sol"])==100
                else:assert int(after["attacker_tokens"])-int(before["attacker_tokens"])==100
                narrate("attack_result",before,message,witness,asset=asset,expected=expected,observed=expected,test_passed=True)
                if mode==3:
                    h.execute(dict(value,amount=value["amount"]+1),witness,expected="rejection",scenario="client_signed_amount_mutation",verifier_reached=True)
                    narrate("withdrawal_rejected",after,message,witness,asset=asset,scenario="changed_amount",test_passed=True)
                    h.execute(value,witness,scenario="client_copy_preserves_intended_effect",verifier_reached=True)
                    narrate("withdrawal_confirmed",after,message,witness,asset=asset,scenario="unchanged_authorization")
            signer_index=index();targets=[h.count-2,h.count-1]
            value=h.intent(3,signer_index,targets=targets);message=encode_intent(value);witness=sign(value,"burn")
            before=summary(h)
            if mode==3:
                h.execute(dict(value,targets=[h.count-3,h.count-1]),witness,expected="rejection",scenario="client_signed_burn_mutation",verifier_reached=True)
                narrate("burn_rejected",before,message,witness,scenario="changed_targets",test_passed=True)
            h.execute(value,witness,scenario="client_authenticated_burn",verifier_reached=True)
            assert set(targets+[signer_index])<=h.state_values()["consumed"]
            narrate("leaves_burned",before,message,witness,authorizing_leaf=signer_index,targets=targets)
            if mode==3:
                burned=h.intent(1,targets[0]);burned_witness=sign(burned,"burned-leaf")
                h.execute(burned,burned_witness,expected="rejection",scenario="client_burned_leaf_rejected",verifier_reached=False)
                narrate("withdrawal_rejected",summary(h),encode_intent(burned),burned_witness,scenario="burned_leaf",test_passed=True)
                # Expose one old-root authorization that rotation will invalidate.
                rotation_index=index();old_index=rotation_index+1
                old=h.intent(1,old_index);old_witness=sign(old,"old-unused")
                value=h.intent(4,rotation_index);message=encode_intent(value);witness=sign(value,"rotate")
                history.install(h.new_public,1)
                before=summary(h)
                for field in ("root","public_seed"):
                    changed=dict(value,**{field:bytes([value[field][0]^1])+value[field][1:]})
                    h.execute(changed,witness,expected="rejection",scenario="client_rotation_"+field+"_mutation",verifier_reached=True)
                    narrate("rotation_rejected",before,message,witness,scenario="changed_"+field,test_passed=True)
                h.execute(value,witness,scenario="client_authorized_rotation",verifier_reached=True)
                after=summary(h)
                for field in ("treasury","token_source","treasury_lamports","token_base_units"):assert before[field]==after[field]
                assert after["epoch"]=="1" and after["consumed"]==[]
                narrate("authority_rotated",before,message,witness,treasury_and_balances_preserved=True)
                h.execute(old,old_witness,expected="rejection",scenario="client_old_unused_authority",verifier_reached=False)
                narrate("withdrawal_rejected",after,encode_intent(old),old_witness,scenario="old_root_authorization",test_passed=True)
                current_old=h.intent(1,old_index+1);current_old_witness=sign(current_old,"old-root-current-epoch")
                h.execute(current_old,current_old_witness,expected="rejection",scenario="client_old_root_current_epoch",verifier_reached=True)
                narrate("withdrawal_rejected",after,encode_intent(current_old),current_old_witness,scenario="old_root_current_epoch",test_passed=True)
                # New tree leaf0; old tree leaf0 was consumed, as expected.
                for action in (1,2):
                    value=h.intent(action,action-1);message=encode_intent(value);witness=sign(value,f"new-{action}",new=True)
                    before=summary(h);h.execute(value,witness,scenario="client_new_root_withdrawal",verifier_reached=True)
                    narrate("withdrawal_confirmed",before,message,witness,asset="SOL" if action==1 else "MOCK_USDC",scenario="post_rotation")
                value=h.intent(1,2,amount=1000000);message=encode_intent(value);witness=sign(value,"insufficient-exact-retry",new=True)
                before=summary(h)
                h.execute(value,witness,expected="rejection",scenario="client_insufficient_balance_signed",verifier_reached=True)
                assert before==summary(h)
                narrate("withdrawal_rejected",before,message,witness,scenario="insufficient_balance_after_signing",test_passed=True)
                keyset=hashlib.sha256(h.new_public).hexdigest()
                with SigningJournal(Path(directory)/keyset,keyset) as journal:
                    exact=journal.retry("insufficient-exact-retry")
                assert exact["message"]==message and exact["signature"]==witness
                h.deposit(sol=1000000)
                before=summary(h)
                h.execute(value,exact["signature"],scenario="client_exact_retry_funded",verifier_reached=True)
                narrate("authorization_retry_executed",before,message,witness,exact_bytes_preserved=True,asset="SOL")
            history.close()
    finally:
        root=ROOT/"artifacts";root.mkdir(exist_ok=True)
        records_path=root/(run_id+"-benchmarks.jsonl")
        records_path.write_text("".join(json.dumps(row)+"\n" for row in h.records))
        events_path=root/(run_id+"-events.jsonl")
        events_path.write_text("".join(json.dumps(row)+"\n" for row in events))
    return {"schema_version":1,"run_id":run_id,"evidence_level":"local_svm","runtime":"solders0.29.0/LiteSVM",
            "mode":mode,"xmss_transport":xmss_transport,"samples_per_asset":samples,"program_binary_sha256":h.binary_digest,"commit":h.commit,
            "all_assertions_passed":True,"test_cases":len(h.results),"measured_transactions":len(h.records),
            "events":events,"evidence_paths":[str(records_path.relative_to(ROOT)),str(events_path.relative_to(ROOT))],
            "limitations":"Local SBF runtime execution; no devnet confirmation. " + ("XMSS uses one inline v1 transaction with a local 1.4M CU runtime override; LiteSVM does not enforce inline resource limits." if xmss_transport=="inline-v1" else "XMSS uses five-transaction sealed staging; temporary accounts retained, no refunds.")}

def benchmark(samples=20,xmss_transport="inline-v1"):
    results=[]
    for count in (16,256,1024):
        for mode in (1,2):results.append(run(mode,min(samples,(count-6)//2),count,xmss_transport))
    results.append(run(3,samples,1024,xmss_transport))
    return {"schema_version":1,"evidence_level":"local_svm","runs":results}
