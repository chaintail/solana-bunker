"""Single writer: deploy pinned custody SBF and create a six-decimal devnet mint."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from solders.compute_budget import set_compute_unit_limit
from solders.instruction import Instruction, AccountMeta
from solders.pubkey import Pubkey
from solders.system_program import create_account, CreateAccountParams
from solders.transaction import Transaction
from infrastructure_devnet import ROOT, RPC, PRIVATE, DEVELOPER_PATH, keypair, account, rpc, environment, blockhash, send, write_json, explorer

BIN = Path(os.environ.get('BUNKER_SOLANA_BIN', str(Path.home() / '.local/share/solana/install/releases/4.3.0/solana-release/bin')))
TOKEN = Pubkey.from_string('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')


def main(paced=False):
    manifest = environment()
    developer, program, mint = keypair(), keypair('program'), keypair('mint')
    binary = ROOT / 'program/target/deploy/bunker_program.so'
    raw = binary.read_bytes()
    manifest.update(schema_version=2, developer_public_address=str(developer.pubkey()), program_id=str(program.pubkey()), program_deployed=False,
        program_binary_bytes=len(raw), program_binary_sha256=hashlib.sha256(raw).hexdigest(), upgrade_authority=str(developer.pubkey()),
        mock_mint=str(mint.pubkey()), mock_mint_created=False, mock_token_label='Mock USDC — test token, no real value',
        decimals=6, token_program=str(TOKEN), mint_authority=str(developer.pubkey()), freeze_authority=None,
        status='preparing', confirmed_transactions=[], vaults=[])
    probe = ROOT / 'artifacts/v1-devnet-transport-result.json'
    if probe.exists():
        manifest['confirmed_transactions'].append(json.loads(probe.read_text())['result'])
    try:
        manifest['developer_balance_lamports'] = rpc('getBalance', [str(developer.pubkey()), {'commitment': 'confirmed'}])['value']
        if manifest['developer_balance_lamports'] < 2_000_000_000:
            raise RuntimeError('Funding pending: require at least 2 devnet SOL before bootstrap')
        keypair('deployment-buffer')
        command = [str(BIN / 'solana'), 'program', 'deploy', str(binary), '--url', RPC,
                   '--keypair', str(DEVELOPER_PATH), '--fee-payer', str(DEVELOPER_PATH), '--upgrade-authority', str(DEVELOPER_PATH),
                   '--program-id', str(PRIVATE / 'program.json'), '--buffer', str(PRIVATE / 'deployment-buffer.json'),
                   '--max-len', str(len(raw)), '--use-rpc', '--max-sign-attempts', '5', '--output', 'json']
        if paced:
            from infrastructure_devnet_loader import paced_deploy
            deployed = paced_deploy(raw)
        else:
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=600)
            if result.returncode:
                # CLI recovery phrases must never enter public artifacts. The
                # explicit private buffer avoids them; retain only error lines.
                errors = [line for line in result.stderr.splitlines() if line.startswith('Error:') and not any(word in line.lower() for word in ('mnemonic', 'seed phrase', 'recovery'))]
                raise RuntimeError('Deployment failed: ' + '\n'.join(errors)[-1500:])
            deployed = json.loads(result.stdout)
        manifest['program_deployment_result'] = deployed
        manifest['program_deployed'] = bool(account(program.pubkey())['executable'])
        dump = PRIVATE / 'deployed-program.so'
        subprocess.run([str(BIN / 'solana'), 'program', 'dump', str(program.pubkey()), str(dump), '--url', RPC], check=True, capture_output=True, timeout=120)
        manifest['deployed_binary_sha256'] = hashlib.sha256(dump.read_bytes()).hexdigest()
        assert manifest['deployed_binary_sha256'] == manifest['program_binary_sha256']
        signature = deployed.get('signature')
        deployment_signatures = {}
        for address in (program.pubkey(), keypair('deployment-buffer').pubkey()):
            for entry in rpc('getSignaturesForAddress', [str(address), {'commitment': 'confirmed', 'limit': 1000}]):
                deployment_signatures[entry['signature']] = entry
        if signature and signature not in deployment_signatures:
            status = rpc('getSignatureStatuses', [[signature], {'searchTransactionHistory': True}])['value'][0]
            assert status and status['confirmationStatus'] in ('confirmed', 'finalized') and status['err'] is None
            deployment_signatures[signature] = {'signature': signature, **status}
        for index, (txid, status) in enumerate(deployment_signatures.items()):
            manifest['confirmed_transactions'].append({'operation': 'deploy_program' if txid == signature else f'deployment_buffer_{index:04d}',
                'transaction_signature': txid, 'explorer_url': explorer(txid), 'confirmed': True, 'slot': status['slot'], 'success': status['err'] is None})
        manifest['deployment_buffer_address'] = str(keypair('deployment-buffer').pubkey())
        if account(mint.pubkey()) is None:
            rent = rpc('getMinimumBalanceForRentExemption', [82])
            create = create_account(CreateAccountParams(from_pubkey=developer.pubkey(), to_pubkey=mint.pubkey(), lamports=rent, space=82, owner=TOKEN))
            initialize = Instruction(TOKEN, b'\x14\x06' + bytes(developer.pubkey()) + b'\x00', [AccountMeta(mint.pubkey(), False, True)])
            tx = Transaction.new_signed_with_payer([set_compute_unit_limit(100_000), create, initialize], developer.pubkey(), [developer, mint], blockhash())
            manifest['confirmed_transactions'].append(send(tx, 'create_mock_mint'))
        mint_account = account(mint.pubkey())
        assert mint_account and mint_account['owner'] == str(TOKEN)
        import base64
        mint_data = base64.b64decode(mint_account['data'][0])
        assert mint_data[44] == 6 and mint_data[45] == 1 and mint_data[46:50] == b'\0' * 4
        manifest.update(mock_mint_created=True, status='deployed_and_mint_created')
    except Exception as error:
        manifest.update(status='blocked', blocker=str(error))
        raise
    finally:
        for filename in ('devnet-deployment.json', 'public-deployment.json'):
            write_json(ROOT / 'artifacts' / filename, manifest)
        print(json.dumps({key: manifest.get(key) for key in ('status', 'program_id', 'mock_mint', 'blocker')}, indent=2))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--paced', action='store_true', help='Resume exact buffer with paced official loader instructions')
    main(paced=parser.parse_args().paced)
