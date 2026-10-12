"""Measured SHA256 syscall loops and deliberately distinct loop-only baselines."""
import json,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
from solders.litesvm import LiteSVM
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction
from solders.transaction import Transaction
from solders.compute_budget import set_compute_unit_limit
from solders.transaction_metadata import FailedTransactionMetadata
ROOT=Path(__file__).resolve().parents[1];binary=ROOT/'target/deploy/bunker_xmss_probe.so'
svm=LiteSVM();pid=Pubkey.new_unique();payer=Keypair();svm.add_program_from_file(pid,binary);svm.airdrop(payer.pubkey(),1_000_000_000);rows=[]
for length in [64,96,128]:
 for repetitions in [1,512,1024,2048]:
  for slices in [1,3]:
   for kind in ['sha256','loop_baseline']:
    data=bytes([1 if kind=='sha256' else 2])+length.to_bytes(2,'big')+repetitions.to_bytes(4,'big')+bytes([slices])
    ix=Instruction(pid,data,[]);tx=Transaction.new_signed_with_payer([set_compute_unit_limit(1_400_000),ix],payer.pubkey(),[payer],svm.latest_blockhash())
    result=svm.send_transaction(tx);failed=isinstance(result,FailedTransactionMetadata);meta=result.meta() if failed else result
    rows.append({'kind':kind,'input_bytes':length,'slices':slices,'repetitions':repetitions,'sha256_syscall_count':repetitions if kind=='sha256' else 0,'compute_units':meta.compute_units_consumed(),'success':not failed,'error':str(result.err()) if failed else None,'return_data':str(meta.return_data()),'transaction_bytes':len(bytes(tx))})
    print(kind,length,repetitions,slices,rows[-1]['compute_units'],flush=True)
evidence={'schema_version':1,'evidence_level':'local_svm','observed_at_utc':datetime.now(timezone.utc).isoformat(),'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'program_binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'runtime':'solders0.29.0 LiteSVM','compute_limit':1_400_000,'rows':rows,'caveat':'Chained syscall loop includes dispatch, copy, iteration and return-data overhead. Loop baseline uses integer accumulator work to avoid optimizer removal and is not a pure syscall cost subtraction model.'}
(ROOT/'artifacts/crypto-hash-microbench.json').write_text(json.dumps(evidence,indent=2)+'\n')
