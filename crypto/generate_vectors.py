"""Disposable independent C-reference known answers, never fund these keys."""
import json,time,hashlib
from pathlib import Path
from datetime import datetime,timezone
from crypto import xmss
out=Path(__file__).resolve().parents[1]/'artifacts/public-vectors/xmss'
out.mkdir(parents=True,exist_ok=True)
seed=bytes(range(96));started=time.monotonic();pk,sk=xmss.keygen(seed)
(out/'public.bin').write_bytes(pk)
manifest={'schema_version':1,'parameter':'XMSS-SHA2_10_256','reference_commit':xmss.REF_COMMIT,'reference_license':'CC0-1.0','public_seed_input_hex':seed.hex(),'disposable_test_only':True,'public_key_sha256':hashlib.sha256(pk).hexdigest(),'created_at_utc':datetime.now(timezone.utc).isoformat(),'vectors':[]}
for idx in [0,1,511,512,1022,1023]:
 msg=f'Bunker disposable RFC8391 reference vector index={idx}'.encode();sig=xmss.sign_at(sk,idx,msg)
 assert xmss.reference_verify(pk,msg,sig);assert xmss.verify(pk,msg,sig)==idx
 if idx!=1023:assert xmss.sign_at(sk,idx,msg,original=True)==sig
 (out/f'{idx}.msg').write_bytes(msg);(out/f'{idx}.sig').write_bytes(sig)
 manifest['vectors'].append({'index':idx,'message':f'{idx}.msg','signature':f'{idx}.sig','signature_bytes':len(sig),'sha256':hashlib.sha256(sig).hexdigest(),'reference_signer':'original' if idx!=1023 else 'max-index control-flow patch','reference_verify':True,'python_verify':True})
 print('vector',idx,'passed',flush=True)
# Explicitly record upstream defect without accepting its bad result.
original_last=xmss.sign_at(sk,1023,(out/'1023.msg').read_bytes(),original=True)
manifest['upstream_last_index_original_verifies']=xmss.reference_verify(pk,(out/'1023.msg').read_bytes(),original_last)
assert manifest['upstream_last_index_original_verifies'] is False
manifest['wall_seconds']=time.monotonic()-started
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('wrote',out,flush=True)
