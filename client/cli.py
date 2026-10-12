"""Research CLI: explicit host model or actual local-SBF LiteSVM demos.

--adapter svm supports isolated demo and benchmark commands with real SPL CPIs
and measured runtime metadata. Host persistence is separate. No adapter claims
network confirmation; the public devnet deployment has its own infra workflow.
"""
import argparse
import fcntl
import hashlib
import json
import os
import tempfile
import time
import uuid
from pathlib import Path
from . import actions, host
from .journal import SigningJournal, AuthorityHistory
from .merkle import SecretTree, commitment
from .kdf import fixture_secrets

def emit(value):
    print(json.dumps(value,sort_keys=True))

def event(name,ledger,private,message=None,witness=None,**extra):
    state=ledger.states[private["state"]]
    return dict(event_version=1,event=name,evidence_level="host_reference",origin="client_host_model",
                run_id=private["fixture"],operation_id=extra.pop("operation_id",str(uuid.uuid4())),mode=state.mode,
                public_addresses={"state":state.address.hex(),"treasury":state.treasury.hex()},epoch=str(state.epoch),
                nonce=str(state.nonce),message_commitment=hashlib.sha256(message).hexdigest() if message else None,
                witness_bytes=len(witness) if witness else None,compute_units=None,transaction_signature=None,**extra)

def authorize(ledger,private,intent,journal_dir,operation_id):
    message=actions.encode_intent(intent)
    state=ledger.states[private["state"]]
    if state.mode in (1,2): return message,host.primitive_witness(ledger,private,intent["leaf_index"])
    from crypto import xmss
    keyset=hashlib.sha256(state.authority).hexdigest()
    with SigningJournal(Path(journal_dir)/keyset,keyset) as journal:
        signed=journal.sign(operation_id,message,lambda i,m:xmss.sign_at(private["xmss_secret"],i,m),intent["leaf_index"])
    return signed["message"],signed["signature"]

def next_index(ledger,private,journal_dir):
    state=ledger.states[private["state"]];used=set(state.consumed)
    if state.mode==3:
        keyset=hashlib.sha256(state.authority).hexdigest()
        with SigningJournal(Path(journal_dir)/keyset,keyset) as journal:
            used.update(row["leaf_index"] for row in journal.public_status())
    return next(i for i in range(state.leaf_count) if i not in used)

def demo(mode):
    fixture="demo-"+{1:"array",2:"merkle",3:"xmss"}[mode]+"-"+uuid.uuid4().hex[:8]
    ledger,private=host.initialize(mode,16,fixture)
    state=ledger.states[private["state"]]
    events=[event("vault_initialized",ledger,private)]
    ledger.deposit_sol(state.address,10000);ledger.deposit_mock(state.address,10000)
    events.append(event("deposit_observed",ledger,private,before_balances={"sol":"1","mock_usdc":"0"},after_balances={"sol":"10001","mock_usdc":"10000"}))
    with tempfile.TemporaryDirectory(prefix="bunker-disposable-") as directory:
        for action in (1,2):
            index=next_index(ledger,private,directory)
            fields={"destination":host.key("owner-sol"),"amount":100}
            if action==2: fields.update(token_program=host.TOKEN_PROGRAM,mint=state.mint,source=state.token_source,destination=private["token_destination"],decimals=6)
            intent=host.context(ledger,private,index,action,**fields)
            message,witness=authorize(ledger,private,intent,directory,f"withdraw-{action}")
            altered=dict(intent,destination=host.key("attacker-sol") if action==1 else host.key("attacker-token"))
            if action==2: ledger.tokens[altered["destination"]]=host.TokenAccount(state.mint,host.key("attacker"))
            try:
                ledger.execute(actions.encode_intent(altered),witness)
                attack="attacker_redirected"
            except ValueError as exc:
                attack="rejected";reason=str(exc)
            expected="rejected" if mode==3 else "attacker_redirected"
            events.append(event("attack_result",ledger,private,message,witness,asset="SOL" if action==1 else "MOCK_USDC",observed=attack,expected=expected,test_passed=attack==expected,attacker_privileges="ordinary relayer/funding fixtures only; no admin or hash seeds"))
            if attack=="rejected": ledger.execute(message,witness)
            try:
                ledger.execute(message,witness);replay=False
            except ValueError: replay=True
            events.append(event("withdrawal_rejected",ledger,private,message,witness,scenario="replay",test_passed=replay))
            state=ledger.states[private["state"]]
        index=next_index(ledger,private,directory)
        targets=[i for i in (8,9) if i!=index]
        intent=host.context(ledger,private,index,3,targets=targets)
        message,witness=authorize(ledger,private,intent,directory,"burn")
        ledger.execute(message,witness)
        events.append(event("leaves_burned",ledger,private,message,witness,authorizing_leaf=index,targets=targets))
        if mode==3:
            state=ledger.states[private["state"]]
            before=(state.treasury,dict(ledger.sol),{k:v.amount for k,v in ledger.tokens.items()})
            public,secret=host.authority(private["seed"],state.vault_id,3,1,1024)
            history=AuthorityHistory(directory);history.install(state.authority,0);history.install(public,1);history.close()
            index=next_index(ledger,private,directory)
            intent=host.context(ledger,private,index,4,new_mode=3,parameter_id=1,root=public[:32],public_seed=public[32:])
            message,witness=authorize(ledger,private,intent,directory,"rotate")
            ledger.execute(message,witness);private.update(generation=1,xmss_secret=secret)
            state=ledger.states[private["state"]]
            preserved=before==(state.treasury,dict(ledger.sol),{k:v.amount for k,v in ledger.tokens.items()})
            events.append(event("authority_rotated",ledger,private,message,witness,treasury_and_balances_preserved=preserved))
            intent=host.context(ledger,private,0,1,destination=host.key("owner-sol"),amount=100)
            message,witness=authorize(ledger,private,intent,directory,"post-rotate")
            ledger.execute(message,witness)
            events.append(event("withdrawal_confirmed",ledger,private,message,witness,scenario="post_rotation",asset="SOL"))
    return {"schema_version":1,"evidence_level":"host_reference","explicitly_disposable":True,"events":events,"final":host.inspect(ledger,private),"all_assertions_passed":all(e.get("test_passed",True) for e in events)}

def benchmark():
    rows=[]
    for count in (16,256,1024):
        secrets=fixture_secrets(host.key("benchmark"),host.key("benchmark-vault"),0,count)
        t=time.perf_counter_ns();commitments=[commitment(x) for x in secrets];array_ns=time.perf_counter_ns()-t
        t=time.perf_counter_ns();tree=SecretTree(secrets);merkle_ns=time.perf_counter_ns()-t
        rows.append({"leaf_count":count,"evidence_level":"host_reference","array_build_ns":array_ns,"merkle_build_ns":merkle_ns,
                     "measured_serialized_array_commitment_bytes":len(b"".join(commitments)),"measured_serialized_merkle_root_bytes":len(tree.root),
                     "measured_merkle_witness_bytes":len(tree.witness(0)),"measured_merkle_sibling_bytes":len(b"".join(tree.proof(0))),
                     "actual_allocated_account_bytes":None,"rent_lamports":None,"compute_units":None,"transaction_bytes":None})
    return {"schema_version":1,"description":"Host construction timings and measured raw serialized commitments/proofs; no SVM/account/rent/transaction measurements", "rows":rows}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter",choices=("host","svm"),default="host")
    parser.add_argument("--xmss-transport",choices=("inline-v1","staged"),default="inline-v1",help="SVM XMSS transport; default is one inline v1 transaction")
    parser.add_argument("--state-file",default=".private/client/host-fixture.json")
    parser.add_argument("--journal-dir",default=".private/client/journals")
    subs=parser.add_subparsers(dest="command",required=True)
    init=subs.add_parser("init");init.add_argument("--mode",choices=("array","merkle","xmss"),default="array");init.add_argument("--leaves",type=int,default=16);init.add_argument("--fixture",default="default")
    subs.add_parser("inspect")
    for name in ("deposit-sol","deposit-mock-usdc"):
        sub=subs.add_parser(name);sub.add_argument("--amount",type=int,required=True)
    retry=subs.add_parser("retry");retry.add_argument("--operation-id",required=True);retry.add_argument("--keyset-id")
    for name in ("withdraw","burn-leaves","rotate-root"):
        sub=subs.add_parser(name);sub.add_argument("--index",type=int);sub.add_argument("--operation-id",default=None)
        if name=="withdraw":
            sub.add_argument("--asset",choices=("sol","mock-usdc"),default="sol");sub.add_argument("--amount",type=int,required=True);sub.add_argument("--destination")
        if name=="burn-leaves": sub.add_argument("--targets",type=int,nargs="+",required=True)
    for name in ("demo-array","demo-merkle","demo-xmss","benchmark"):
        sub=subs.add_parser(name);sub.add_argument("--samples",type=int,default=20 if name=="benchmark" else 1)
    args=parser.parse_args()
    if args.adapter=="svm":
        from . import svm
        if args.command.startswith("demo-"):
            emit(svm.run({"demo-array":1,"demo-merkle":2,"demo-xmss":3}[args.command],args.samples,xmss_transport=args.xmss_transport));return
        if args.command=="benchmark":emit(svm.benchmark(args.samples,xmss_transport=args.xmss_transport));return
        parser.error("SVM adapter currently supports isolated demo and benchmark commands; persistent commands use --adapter host")
    if args.command.startswith("demo-"):
        result=demo({"demo-array":1,"demo-merkle":2,"demo-xmss":3}[args.command]);emit(result);return
    if args.command=="benchmark":emit(benchmark());return
    path=Path(args.state_file);path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    with open(path.with_suffix(".lock"),"a+b") as lock:
        os.chmod(path.with_suffix(".lock"),0o600);fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if args.command=="init":
            if path.exists():raise ValueError("refusing to replace existing fixture; use a fresh --state-file")
            ledger,private=host.initialize({"array":1,"merkle":2,"xmss":3}[args.mode],args.leaves,args.fixture)
            if args.mode=="xmss":
                with_history=AuthorityHistory(Path(args.journal_dir)/args.fixture)
                with_history.install(ledger.states[private["state"]].authority,0);with_history.close()
            output=event("vault_initialized",ledger,private)
        else:
            ledger,private=host.load(path);state=ledger.states[private["state"]]
            if args.command=="inspect":emit(host.inspect(ledger,private));return
            if args.command in ("deposit-sol","deposit-mock-usdc"):
                method=ledger.deposit_sol if args.command=="deposit-sol" else ledger.deposit_mock
                method(state.address,args.amount);output=event("deposit_observed",ledger,private,asset="SOL" if args.command=="deposit-sol" else "MOCK_USDC",amount=str(args.amount))
            elif args.command=="retry":
                keyset=args.keyset_id or hashlib.sha256(state.authority).hexdigest()
                with SigningJournal(Path(args.journal_dir)/keyset,keyset) as journal:
                    signed=journal.retry(args.operation_id)
                message,witness=signed["message"],signed["signature"]
                decoded=actions.parse_intent(message)
                ledger.execute(message,witness)
                if decoded["action"]==4:
                    history=AuthorityHistory(Path(args.journal_dir)/private["fixture"])
                    generation=history.generation_for(decoded["root"]+decoded["public_seed"]);history.close()
                    public,secret=host.authority(private["seed"],state.vault_id,3,generation,1024)
                    if public!=decoded["root"]+decoded["public_seed"]:raise ValueError("replacement seed unavailable for retry")
                    private.update(generation=generation,xmss_secret=secret)
                output=event("authorization_retry_executed",ledger,private,message,witness,operation_id=args.operation_id)
            else:
                index=args.index if args.index is not None else next_index(ledger,private,args.journal_dir)
                operation_id=args.operation_id or str(uuid.uuid4())
                if args.command=="withdraw":
                    destination=bytes.fromhex(args.destination) if args.destination else (host.key("recipient-sol") if args.asset=="sol" else private["token_destination"])
                    fields=dict(destination=destination,amount=args.amount);action=1 if args.asset=="sol" else 2
                    if action==2: fields.update(token_program=host.TOKEN_PROGRAM,mint=state.mint,source=state.token_source,decimals=6)
                elif args.command=="burn-leaves":action=3;fields=dict(targets=args.targets)
                else:
                    if state.mode!=3:raise ValueError("rotation requires XMSS mode")
                    history=AuthorityHistory(Path(args.journal_dir)/private["fixture"])
                    generation=history.next_generation(private["generation"])
                    public,secret=host.authority(private["seed"],state.vault_id,3,generation,1024)
                    history.install(public,generation);history.close()
                    action=4;fields=dict(new_mode=3,parameter_id=1,root=public[:32],public_seed=public[32:])
                intent=host.context(ledger,private,index,action,**fields)
                message,witness=authorize(ledger,private,intent,args.journal_dir,operation_id)
                try: ledger.execute(message,witness)
                except ValueError as exc:
                    emit(event("withdrawal_rejected",ledger,private,message,witness,operation_id=operation_id,error=str(exc)));raise
                if action==4:private.update(generation=generation,xmss_secret=secret)
                output=event({1:"withdrawal_confirmed",2:"withdrawal_confirmed",3:"leaves_burned",4:"authority_rotated"}[action],ledger,private,message,witness,operation_id=operation_id)
        host.save(path,ledger,private);emit(output)

if __name__=="__main__":
    main()
