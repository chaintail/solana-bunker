"""20 repetitions of six independent fixtures; stable per-case CU evidence."""
import hashlib,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
from solders.litesvm import LiteSVM
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.account import Account
from solders.instruction import AccountMeta,Instruction
from solders.transaction import Transaction
from solders.compute_budget import set_compute_unit_limit
from solders.transaction_metadata import FailedTransactionMetadata
root=Path(__file__).resolve().parents[1];v=root/'artifacts/public-vectors/xmss';binary=root/'target/deploy/bunker_xmss_probe.so'
svm=LiteSVM();pid=Pubkey.new_unique();payer=Keypair();svm.add_program_from_file(pid,binary);svm.airdrop(payer.pubkey(),1_000_000_000);public=(v/'public.bin').read_bytes();rows=[]
for index in [0,1,511,512,1022,1023]:
 for repetition in range(20):
  fixture=Pubkey.new_unique();data=public+(v/f'{index}.sig').read_bytes()+(v/f'{index}.msg').read_bytes();svm.set_account(fixture,Account(10_000_000,data,pid,False,0))
  tx=Transaction.new_signed_with_payer([set_compute_unit_limit(1_400_000),Instruction(pid,b'',[AccountMeta(fixture,False,False)])],payer.pubkey(),[payer],svm.latest_blockhash())
  r=svm.send_transaction(tx);bad=isinstance(r,FailedTransactionMetadata);meta=r.meta() if bad else r
  rows.append({'index':index,'repetition':repetition,'success':not bad,'compute_units':meta.compute_units_consumed(),'error':str(r.err()) if bad else None})
e={'schema_version':1,'evidence_level':'local_svm','created_at_utc':datetime.now(timezone.utc).isoformat(),'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'program_binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'runtime':'solders0.29.0 LiteSVM','repetitions_per_fixture':20,'rows':rows,'summary':{str(i):{'min':min(x['compute_units'] for x in rows if x['index']==i),'max':max(x['compute_units'] for x in rows if x['index']==i)} for i in [0,1,511,512,1022,1023]},'all_passed':all(x['success'] for x in rows)}
(root/'artifacts/crypto-svm-repeat-profile.json').write_text(json.dumps(e,indent=2)+'\n');print(json.dumps(e['summary'],indent=2));assert e['all_passed']
