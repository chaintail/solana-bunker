"""Actual SBF execution in LiteSVM; fixtures installed directly (not custody or upload evidence)."""
import json,hashlib,subprocess,platform
from pathlib import Path
from datetime import datetime,timezone
from solders.litesvm import LiteSVM
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.account import Account
from solders.instruction import Instruction,AccountMeta
from solders.transaction import Transaction
from solders.compute_budget import set_compute_unit_limit
from solders.transaction_metadata import FailedTransactionMetadata
ROOT=Path(__file__).resolve().parents[1]
BINARY=ROOT/'target/deploy/bunker_xmss_probe.so'
VECTORS=ROOT/'artifacts/public-vectors/xmss'
OUT=ROOT/'artifacts/crypto-svm-probe.json'
def run():
    pid=Pubkey.new_unique();payer=Keypair();svm=LiteSVM();svm.add_program_from_file(pid,BINARY)
    svm.airdrop(payer.pubkey(),10_000_000_000)
    pk=(VECTORS/'public.bin').read_bytes();rows=[]
    for index in [0,1,511,512,1022,1023]:
        msg=(VECTORS/f'{index}.msg').read_bytes();sig=(VECTORS/f'{index}.sig').read_bytes()
        for scenario in ['valid','message_corrupted','auth_path_corrupted','public_seed_corrupted','wots_corrupted','index_out_of_range','short_signature']:
            p=pk;m=msg;s=sig
            if scenario=='message_corrupted':m=msg+b'!'
            if scenario=='auth_path_corrupted':s=sig[:-1]+bytes([sig[-1]^1])
            if scenario=='public_seed_corrupted':p=pk[:-1]+bytes([pk[-1]^1])
            if scenario=='wots_corrupted':s=sig[:100]+bytes([sig[100]^1])+sig[101:]
            if scenario=='index_out_of_range':s=(1024).to_bytes(4,'big')+sig[4:]
            if scenario=='short_signature':s=sig[:-1];m=b'' # total length rejected by probe
            fixture=Pubkey.new_unique();data=p+s+m
            svm.set_account(fixture,Account(10_000_000,data,pid,False,0))
            ix=Instruction(pid,b'', [AccountMeta(fixture,False,False)])
            tx=Transaction.new_signed_with_payer([set_compute_unit_limit(1_400_000),ix],payer.pubkey(),[payer],svm.latest_blockhash())
            result=svm.send_transaction(tx);failed=isinstance(result,FailedTransactionMetadata);meta=result.meta() if failed else result
            expected=scenario=='valid'
            row={'index':index,'scenario':scenario,'expected_success':expected,'success':not failed,'passed':(not failed)==expected,'compute_units':meta.compute_units_consumed(),'fee_lamports':meta.fee(),'error':str(result.err()) if failed else None,'transaction_bytes':len(bytes(tx)),'fixture_account_bytes':len(data),'logs':meta.logs(),'evidence_level':'local_svm','transport':'legacy transaction with preinstalled fixture account; not a large-data transport test'}
            rows.append(row);print(index,scenario,'success',not failed,'CU',row['compute_units'],flush=True)
    evidence={'schema_version':1,'observed_at_utc':datetime.now(timezone.utc).isoformat(),'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'program_binary_sha256':hashlib.sha256(BINARY.read_bytes()).hexdigest(),'binary_path':str(BINARY.relative_to(ROOT)),'runtime':'solders0.29.0 LiteSVM native binding','sbf_toolchain':'Agave4.3.0 platform-tools1.57','compute_limit':1_400_000,'reference_commit':'171ccbd26f098542a67eb5d2b128281c80bd71a6','rows':rows,'all_passed':all(x['passed'] for x in rows),'limitations':['Fixture account is installed via LiteSVM set_account, so these runs verify cryptography execution only. No upload, public-cluster transport, custody transfer, nonce/epoch or account rules proved.','Zeroized original reference final-index signing differs; index1023 uses explicitly recorded control-flow patch.']}
    OUT.write_text(json.dumps(evidence,indent=2)+'\n')
    if not evidence['all_passed']:raise SystemExit(1)
if __name__=='__main__':run()
