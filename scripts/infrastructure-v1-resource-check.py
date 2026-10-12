"""Bounded local runtime check: does LiteSVM enforce inline v1 limits?"""
import json
from pathlib import Path
from datetime import datetime,timezone
from solders.litesvm import LiteSVM
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction
from solders.compute_budget import set_compute_unit_limit
from solders.message import MessageV1,TransactionConfig
from solders.transaction import VersionedTransaction,Transaction
from solders.transaction_metadata import FailedTransactionMetadata

root=Path(__file__).resolve().parents[1]
key=Keypair()
ix=Instruction(Pubkey.from_string('MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr'),b'Harmless inline-resource enforcement check',[])
rows=[]
for case,compute,loaded in [('v1_normal',200_000,1_048_576),('v1_compute_1',1,1_048_576),('v1_loaded_bytes_1',200_000,1)]:
    svm=LiteSVM();svm.airdrop(key.pubkey(),1_000_000_000)
    config=TransactionConfig(compute_unit_limit=compute,loaded_accounts_data_size_limit=loaded)
    msg=MessageV1.try_compile(key.pubkey(),[ix],svm.latest_blockhash(),config)
    tx=VersionedTransaction(msg,[key]);result=svm.send_transaction(tx)
    failed=isinstance(result,FailedTransactionMetadata);meta=result.meta() if failed else result
    rows.append({'case':case,'inline_compute_limit':compute,'inline_loaded_bytes_limit':loaded,'success':not failed,'error':str(result.err()) if failed else None,'compute_consumed':meta.compute_units_consumed(),'logs':meta.logs(),'serialized_transaction_bytes':len(bytes(tx))})
svm=LiteSVM();svm.airdrop(key.pubkey(),1_000_000_000)
tx=Transaction.new_signed_with_payer([set_compute_unit_limit(1),ix],key.pubkey(),[key],svm.latest_blockhash())
result=svm.send_transaction(tx);failed=isinstance(result,FailedTransactionMetadata);meta=result.meta() if failed else result
rows.append({'case':'legacy_compute_instruction_1','success':not failed,'error':str(result.err()) if failed else None,'compute_consumed':meta.compute_units_consumed(),'logs':meta.logs(),'serialized_transaction_bytes':len(bytes(tx))})
out={'schema_version':1,'observed_at_utc':datetime.now(timezone.utc).isoformat(),'evidence_level':'local_svm','solders_version':'0.29.0','results':rows,'inline_limits_enforced':not rows[1]['success'] and not rows[2]['success'],'network_confirmation':False}
(root/'artifacts/v1-resource-enforcement.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
