"""Shared devnet-only RPC, private key loading, and confirmed evidence helpers."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from solders.hash import Hash
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction, Transaction

ROOT = Path(__file__).resolve().parents[1]
RPC = 'https://api.devnet.solana.com'
GENESIS = 'EtWTRABZaYq6iMfeYKouRu166VU2xqa1wcaWoxPkrZBG'
DEVELOPER_PATH = Path(os.environ.get('BUNKER_DEVNET_KEYPAIR', '/srv/world/secrets/agents/composer-dobot/solana/bunker-devnet.json'))
DEVELOPER_ADDRESS = 'N4FZnqmfXWoGhofuJAYnDdnYF8ows635ZAw2omFCtW1'
PRIVATE = ROOT / '.private' / 'devnet-v1'
NOW = lambda: datetime.now(timezone.utc).isoformat()


def rpc(method, params=()):
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': list(params)}).encode()
    for attempt in range(5):
        try:
            request = urllib.request.Request(RPC, data=body, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(request, timeout=45) as response:
                result = json.load(response)
            if 'error' in result:
                raise RuntimeError(json.dumps(result['error']))
            return result['result']
        except (urllib.error.URLError, TimeoutError):
            if attempt == 4:
                raise
            time.sleep(min(2 ** attempt, 10))


def private_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path.parent, 0o700)
    temporary = path.with_suffix('.tmp')
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, 'w') as output:
        json.dump(value, output)
        output.flush()
        os.fsync(output.fileno())
    temporary.replace(path)
    os.chmod(path, 0o600)


def keypair(role=None):
    path = PRIVATE / f'{role}.json' if role else DEVELOPER_PATH
    if not path.exists():
        if role is None:
            raise RuntimeError('Dedicated developer keypair is unavailable')
        private_json(path, list(bytes(Keypair())))
    pair = Keypair.from_bytes(bytes(json.loads(path.read_text())))
    if role is None and str(pair.pubkey()) != DEVELOPER_ADDRESS:
        raise RuntimeError('Developer public address differs from the authorized wallet')
    return pair


def account(address):
    return rpc('getAccountInfo', [str(address), {'encoding': 'base64', 'commitment': 'confirmed'}])['value']


def blockhash():
    return Hash.from_string(rpc('getLatestBlockhash', [{'commitment': 'confirmed'}])['value']['blockhash'])


def explorer(signature):
    return f'https://explorer.solana.com/tx/{signature}?cluster=devnet'


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def environment():
    assert rpc('getGenesisHash') == GENESIS, 'Wrong development cluster'
    return {'observed_at_utc': NOW(), 'cluster': 'devnet', 'rpc_url': RPC,
            'genesis_hash': GENESIS, 'rpc_version': rpc('getVersion'),
            'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}


def send(tx, operation, *, allow_failure=False, skip_preflight=False, metadata=None):
    raw = bytes(tx)
    if len(raw) > (4096 if isinstance(tx, VersionedTransaction) and tx.version() == 1 else 1232):
        raise ValueError('Serialized transaction exceeds its transport limit')
    row = {'operation': operation, 'observed_at_utc': NOW(), 'transaction_bytes': len(raw),
           'transaction_version': int(tx.version()) if isinstance(tx, VersionedTransaction) and isinstance(tx.version(), int) else 'legacy',
           'transaction_signature': str(tx.signatures[0]), 'confirmed': False, **(metadata or {})}
    encoded = base64.b64encode(raw).decode()
    path = ROOT / 'artifacts' / 'devnet-transactions' / f'{operation}.json'
    try:
        signature = row['transaction_signature']
        status = rpc('getSignatureStatuses', [[signature], {'searchTransactionHistory': True}])['value'][0]
        if status is None:
            row['simulation'] = rpc('simulateTransaction', [encoded, {'encoding': 'base64', 'sigVerify': True, 'commitment': 'confirmed'}])
            submitted = rpc('sendTransaction', [encoded, {'encoding': 'base64', 'skipPreflight': skip_preflight, 'preflightCommitment': 'confirmed', 'maxRetries': 5}])
            assert submitted == signature
        deadline = time.monotonic() + 100
        while time.monotonic() < deadline:
            status = rpc('getSignatureStatuses', [[signature], {'searchTransactionHistory': True}])['value'][0]
            if status and status.get('confirmationStatus') in ('confirmed', 'finalized'):
                break
            time.sleep(1)
        if not status or status.get('confirmationStatus') not in ('confirmed', 'finalized'):
            raise RuntimeError('Submission outcome uncertain; retain exact authorization and inspect signature before retry')
        row.update(confirmed=True, confirmation_status=status['confirmationStatus'], slot=status['slot'], error=status['err'], explorer_url=explorer(signature))
        for _ in range(25):
            fetched = rpc('getTransaction', [signature, {'encoding': 'base64', 'commitment': 'confirmed', 'maxSupportedTransactionVersion': 1}])
            if fetched:
                break
            time.sleep(1)
        if fetched is None:
            raise RuntimeError('Confirmed transaction retrieval not yet available')
        row['network_transaction'] = fetched
        returned = base64.b64decode(fetched['transaction'][0])
        assert returned == raw, 'Network transaction differs from submitted bytes'
        decoded = VersionedTransaction.from_bytes(returned)
        row['network_decoded_version'] = int(decoded.version()) if isinstance(decoded.version(), int) else 'legacy'
        row['compute_units'] = fetched['meta'].get('computeUnitsConsumed')
        row['fee_lamports'] = fetched['meta'].get('fee')
        row['success'] = fetched['meta']['err'] is None
        if not allow_failure and not row['success']:
            raise RuntimeError(f"Confirmed execution failed: {row['error']}")
    except Exception as error:
        row['failure'] = str(error)
        write_json(path, row)
        raise
    write_json(path, row)
    print(json.dumps({key: row.get(key) for key in ('operation', 'transaction_bytes', 'compute_units', 'transaction_signature', 'confirmed', 'success')}), flush=True)
    return {key: value for key, value in row.items() if key not in ('simulation', 'network_transaction')} | {'evidence_path': str(path.relative_to(ROOT))}
