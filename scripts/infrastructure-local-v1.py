"""Execute actual >1232-byte v1 bytes on funded local LiteSVM only."""
from pathlib import Path
import json
from datetime import datetime, timezone
from solders.litesvm import LiteSVM
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.instruction import Instruction
from solders.message import MessageV1, TransactionConfig
from solders.transaction import VersionedTransaction
from solders.transaction_metadata import FailedTransactionMetadata

root = Path(__file__).resolve().parents[1]
svm = LiteSVM().with_blockhash_check(False)
keypair = Keypair()  # Dedicated disposable local fixture, never funded publicly.
svm.airdrop(keypair.pubkey(), 1_000_000_000)
data = b'Solana Bunker local harmless v1 transport probe: ' + b'.'*1800
ix = Instruction(Pubkey.from_string('MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr'), data, [])
config = TransactionConfig(compute_unit_limit=1_000_000,loaded_accounts_data_size_limit=1_048_576,heap_size=32_768)
msg = MessageV1.try_compile(keypair.pubkey(), [ix], Hash.default(), config)
tx = VersionedTransaction(msg,[keypair])
raw = bytes(tx)
assert 1232 < len(raw) <= 4096
parsed = VersionedTransaction.from_bytes(raw)
out = svm.send_transaction(parsed)
failed = isinstance(out,FailedTransactionMetadata)
meta = out.meta() if failed else out
result = {'schema_version':1,'observed_at_utc':datetime.now(timezone.utc).isoformat(),'evidence_level':'local_svm','solders_version':'0.29.0','transaction_version':1,'transaction_bytes':len(raw),'instruction_data_bytes':len(data),'configuration':{'compute_unit_limit':1_000_000,'loaded_accounts_data_size_limit':1_048_576,'heap_size':32_768},'success':not failed,'error':str(out.err()) if failed else None,'compute_consumed':meta.compute_units_consumed(),'logs':meta.logs(),'transaction_signature':str(tx.signatures[0]),'network_confirmation':False}
Path(root/'artifacts/v1-local-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
