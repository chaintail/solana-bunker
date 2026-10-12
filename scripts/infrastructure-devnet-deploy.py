"""Single-writer devnet deployment and six-decimal mock-mint bootstrap.

Requires explicit devnet genesis, funded fresh developer, and private keys.
Never changes CLI global config; no mainnet path exists here.
"""
import hashlib,json,os,subprocess,urllib.request
from pathlib import Path
from datetime import datetime,timezone
from solders.keypair import Keypair

ROOT=Path(__file__).resolve().parents[1]
RPC='https://api.devnet.solana.com'
DEVNET_GENESIS='EtWTRABZaYq6iMfeYKouRu166VU2xqa1wcaWoxPkrZBG'
TOKEN='TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'
BIN=Path(os.getenv('BUNKER_SOLANA_BIN','/workspace/scratch/1a48031fefb9/toolchains/solana-release/bin'))
def rpc(method,params):
    q=urllib.request.Request(RPC,data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(q,timeout=25) as r:
        d=json.load(r)
    if 'error' in d: raise RuntimeError(str(d['error']))
    return d['result']
def address(role):
    return str(Keypair.from_bytes(bytes(json.loads((ROOT/'.private'/f'{role}-keypair.json').read_text()))).pubkey())
def run(command):
    # All keys are pre-created; the CLI never creates a recoverable random buffer.
    p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=240)
    if p.returncode: raise RuntimeError('CLI failed; exit='+str(p.returncode)+'; '+p.stderr[-1500:])
    try:return json.loads(p.stdout)
    except json.JSONDecodeError:return {'cli_output':p.stdout[-1500:]}

env=json.loads((ROOT/'reports/environment.json').read_text())
developer=env['developer_public_address'];program=address('program');mint=address('mint')
binary=ROOT/'program/target/deploy/bunker_program.so';raw=binary.read_bytes()
manifest={'schema_version':1,'observed_at_utc':datetime.now(timezone.utc).isoformat(),'cluster':'devnet','rpc_url':RPC,'genesis_hash':rpc('getGenesisHash',[]),'developer_public_address':developer,'program_id':program,'program_deployed':False,'program_binary_bytes':len(raw),'program_binary_sha256':hashlib.sha256(raw).hexdigest(),'upgrade_authority':developer,'mock_mint':mint,'mock_mint_created':False,'mock_token_label':'Mock USDC — test token, no real value','decimals':6,'token_program':TOKEN,'mint_authority':developer,'freeze_authority':None,'status':'preparing','confirmed_transactions':[]}
assert manifest['genesis_hash']==DEVNET_GENESIS,'Wrong development cluster'
manifest['developer_balance_lamports']=rpc('getBalance',[developer,{'commitment':'confirmed'}])['value']
output=ROOT/'artifacts/public-deployment.json'
try:
    if manifest['developer_balance_lamports'] < 1_300_000_000:
        raise RuntimeError('Funding pending: estimated peak deployment needs about1.3devnet SOL; recommend2SOL')
    key=str(ROOT/'.private/developer-keypair.json')
    if rpc('getAccountInfo',[program,{'encoding':'base64'}])['value'] is None:
        manifest['program_deployment_result']=run([str(BIN/'solana'),'program','deploy',str(binary),'--url',RPC,'--keypair',key,'--fee-payer',key,'--upgrade-authority',key,'--program-id',str(ROOT/'.private/program-keypair.json'),'--buffer',str(ROOT/'.private/deployment-buffer-keypair.json'),'--max-len',str(len(raw)),'--use-rpc','--max-sign-attempts','2','--output','json'])
    manifest['program_deployed']=rpc('getAccountInfo',[program,{'encoding':'base64'}])['value'] is not None
    if rpc('getAccountInfo',[mint,{'encoding':'base64'}])['value'] is None:
        manifest['mint_creation_result']=run([str(BIN/'spl-token'),'--url',RPC,'--owner',key,'--fee-payer',key,'--program-id',TOKEN,'--output','json','create-token','--decimals','6',str(ROOT/'.private/mint-keypair.json')])
    manifest['mock_mint_created']=rpc('getAccountInfo',[mint,{'encoding':'base64'}])['value'] is not None
    manifest['status']='deployed_and_mint_created'
except Exception as e:
    manifest['status']='blocked';manifest['blocker']=str(e)
finally:
    output.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))
