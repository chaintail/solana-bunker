"""Explicit host-model adapter and JSON persistence for disposable demo fixtures."""
import hashlib
import json
import os
from dataclasses import asdict
from pathlib import Path
from program.model import BunkerLedger, State, TokenAccount, TOKEN_PROGRAM
from . import kdf
from .merkle import SecretTree, commitment

def key(label):
    return hashlib.sha256(("bunker-disposable-host:"+label).encode()).digest()

def pack(value):
    if isinstance(value,bytes): return {"$bytes":value.hex()}
    if isinstance(value,set): return {"$set":sorted(value)}
    if isinstance(value,dict): return {k:pack(v) for k,v in value.items()}
    if isinstance(value,list): return [pack(v) for v in value]
    return value

def unpack(value):
    if isinstance(value,dict):
        if "$bytes" in value: return bytes.fromhex(value["$bytes"])
        if "$set" in value: return set(value["$set"])
        return {k:unpack(v) for k,v in value.items()}
    if isinstance(value,list): return [unpack(v) for v in value]
    return value

def save(path, ledger, private):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    document={"schema_version":1,"evidence_level":"host_reference","explicitly_disposable":True,
              "program_id":ledger.program_id,"private":private,
              "states":{k.hex():asdict(v) for k,v in ledger.states.items()},
              "sol":{k.hex():v for k,v in ledger.sol.items()},
              "owners":{k.hex():v for k,v in ledger.owners.items()},
              "tokens":{k.hex():asdict(v) for k,v in ledger.tokens.items()}}
    temp=path.with_suffix(".tmp")
    fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    with os.fdopen(fd,"w") as stream:
        json.dump(pack(document),stream,sort_keys=True);stream.flush();os.fsync(stream.fileno())
    os.replace(temp,path)
    directory=os.open(path.parent,os.O_RDONLY);os.fsync(directory);os.close(directory)

def load(path):
    document=unpack(json.loads(Path(path).read_text()))
    if document.get("evidence_level")!="host_reference" or not document.get("explicitly_disposable"):
        raise ValueError("host adapter accepts only explicit disposable fixtures")
    try:
        from crypto.xmss import verify
    except ImportError:
        verify=None
    ledger=BunkerLedger(document["program_id"],verify)
    ledger.states={bytes.fromhex(k):State(**v) for k,v in document["states"].items()}
    ledger.sol={bytes.fromhex(k):v for k,v in document["sol"].items()}
    ledger.owners={bytes.fromhex(k):v for k,v in document["owners"].items()}
    ledger.tokens={bytes.fromhex(k):TokenAccount(**v) for k,v in document["tokens"].items()}
    return ledger,document["private"]

def authority(seed,vault,mode,generation,count):
    if mode in (1,2):
        secrets=kdf.fixture_secrets(seed,vault,generation,count)
        return (b"".join(commitment(s) for s in secrets) if mode==1 else SecretTree(secrets).root),None
    from crypto import xmss
    public,secret=xmss.keygen(b"".join(kdf.xmss_seeds(seed,vault,generation)))
    return public,secret

def initialize(mode=1,count=16,fixture="default"):
    if mode==3: count=1024
    seed=key("seed:"+fixture);vault=key("vault:"+fixture)
    public,secret=authority(seed,vault,mode,0,count)
    from crypto.xmss import verify
    ledger=BunkerLedger(key("program"),verify)
    state=ledger.initialize(vault,key("namespace"),key("trusted-admin"),key("mock-mint"),key("source:"+fixture),mode,public,count)
    destination=key("recipient-token:"+fixture)
    ledger.tokens[destination]=TokenAccount(state.mint,key("recipient"))
    return ledger,{"seed":seed,"generation":0,"xmss_secret":secret,"state":state.address,"token_destination":destination,"fixture":fixture}

def context(ledger,private,index,action,**fields):
    state=ledger.states[private["state"]]
    return dict(program_id=ledger.program_id,namespace=state.namespace,vault_id=state.vault_id,state=state.address,
                treasury=state.treasury,mode=state.mode,epoch=state.epoch,nonce=state.nonce,leaf_index=index,action=action,**fields)

def primitive_witness(ledger,private,index):
    state=ledger.states[private["state"]]
    secrets=kdf.fixture_secrets(private["seed"],state.vault_id,private["generation"],state.leaf_count)
    if state.mode==1: return index.to_bytes(4,"little")+secrets[index]
    return SecretTree(secrets).witness(index)

def inspect(ledger,private):
    state=ledger.states[private["state"]]
    return {"evidence_level":"host_reference","explicitly_disposable":True,"fixture_id":private["fixture"],
            "state":state.address.hex(),"treasury":state.treasury.hex(),"mock_mint":state.mint.hex(),
            "token_source":state.token_source.hex(),"token_destination":private["token_destination"].hex(),
            "mode":state.mode,"epoch":str(state.epoch),"nonce":str(state.nonce),"leaf_count":state.leaf_count,
            "used_leaves":sorted(state.consumed),"sol_base_units":str(ledger.sol[state.treasury]),
            "token_base_units":str(ledger.tokens[state.token_source].amount),"authority_sha256":hashlib.sha256(state.authority).hexdigest()}
