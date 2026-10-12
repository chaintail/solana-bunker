import fs from 'node:fs';
import { spawnSync } from 'node:child_process';
import {
  address, createKeyPairFromBytes, createTransactionMessage, setTransactionMessageFeePayer,
  setTransactionMessageLifetimeUsingBlockhash, setTransactionMessageConfig,
  appendTransactionMessageInstruction, compileTransaction, signTransaction,
  getTransactionEncoder, getTransactionDecoder, getSignatureFromTransaction,
} from '@solana/kit';

// Only public RPC responses are emitted. Secret key bytes remain local.
const rpcUrl = process.env.BUNKER_RPC_URL ?? 'https://api.devnet.solana.com';
function rpc(method, params) {
  const py = 'import sys,json,urllib.request\nx=json.load(sys.stdin)\nr=urllib.request.Request(x["url"],data=json.dumps({"jsonrpc":"2.0","id":1,"method":x["method"],"params":x["params"]}).encode(),headers={"Content-Type":"application/json"})\ntry:\n with urllib.request.urlopen(r,timeout=20) as s: print(s.read().decode())\nexcept Exception as e: print(json.dumps({"transport_error":str(e)}))';
  const p = spawnSync('python', ['-c', py], {input: JSON.stringify({url: rpcUrl, method, params}), encoding:'utf8'});
  if (p.status !== 0) throw new Error('RPC helper failed');
  return JSON.parse(p.stdout);
}
const publicEnv = JSON.parse(fs.readFileSync('reports/environment.json'));
const pub = address(publicEnv.developer_public_address);
const result = {schema_version:1, observed_at_utc:new Date().toISOString(), sdk:'@solana/kit 8.4.0', cluster:'devnet', rpc_url:rpcUrl, public_address:pub, resource_config:{computeUnitLimit:1000000,loadedAccountsDataSizeLimit:1048576,heapSize:32768}, stage:'rpc_blockhash'};
try {
  result.runtime = rpc('getVersion', []);
  result.balance = rpc('getBalance',[pub,{commitment:'confirmed'}]);
  const bh = rpc('getLatestBlockhash',[{commitment:'confirmed'}]);
  result.blockhash_response = bh;
  if (!bh.result) throw new Error('getLatestBlockhash unavailable');
  let msg = createTransactionMessage({version:1});
  msg = setTransactionMessageFeePayer(pub,msg);
  msg = setTransactionMessageLifetimeUsingBlockhash({...bh.result.value,lastValidBlockHeight:BigInt(bh.result.value.lastValidBlockHeight)},msg);
  msg = setTransactionMessageConfig(result.resource_config,msg);
  // A real UTF-8 memo is tested rather than assumed to accept its payload.
  const data = new TextEncoder().encode('Solana Bunker harmless v1 transport probe: '+'.'.repeat(1800));
  msg = appendTransactionMessageInstruction({programAddress:address('MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr'),accounts:[],data},msg);
  result.stage='sdk_sign_serialize';
  const kp = await createKeyPairFromBytes(Uint8Array.from(JSON.parse(fs.readFileSync('.private/developer-keypair.json'))));
  const tx = await signTransaction([kp],compileTransaction(msg));
  const raw = getTransactionEncoder().encode(tx);
  result.transaction_bytes=raw.length;
  result.instruction_data_bytes=data.length;
  result.transaction_signature=getSignatureFromTransaction(tx);
  result.local_decode_success=!!getTransactionDecoder().decode(raw);
  if (!(raw.length>1232 && raw.length<=4096)) throw new Error('Probe size outside required range');
  fs.writeFileSync('artifacts/v1-probe-transaction.bin',raw);
  const b64=Buffer.from(raw).toString('base64');
  result.stage='rpc_simulate';
  result.simulation=rpc('simulateTransaction',[b64,{encoding:'base64',sigVerify:true,commitment:'confirmed'}]);
  // Even unfunded submission yields an exact RPC/transport failure stage.
  result.stage='rpc_submit';
  result.submission=rpc('sendTransaction',[b64,{encoding:'base64',skipPreflight:false,preflightCommitment:'confirmed',maxRetries:0}]);
  if (result.submission.result) {
    result.stage='rpc_retrieve';
    result.retrieval=rpc('getTransaction',[result.submission.result,{encoding:'base64',commitment:'confirmed',maxSupportedTransactionVersion:1}]);
    result.status=result.retrieval.result?'network_retrieved':'submission_returned_pending_retrieval';
  } else result.status='blocked';
} catch(e) {result.status='blocked';result.error=e.message;}
fs.writeFileSync('artifacts/v1-probe-result.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
