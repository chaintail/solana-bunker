"""Collect public receipts and check completed devnet custody demonstrations."""
import base64
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from solders.transaction import VersionedTransaction
from infrastructure_devnet import ROOT, write_json
from tests.evidence_schema import validate


def main():
    artifact = ROOT / 'artifacts'
    manifest = json.loads((artifact / 'devnet-deployment.json').read_text())
    assert manifest['status'] == 'deployed_and_demonstrated'
    assert manifest['program_binary_sha256'] == manifest['deployed_binary_sha256']
    attempts = []
    receipts = {}
    for path in sorted((artifact / 'devnet-transactions').glob('*.json')):
        receipt = json.loads(path.read_text())
        signature = receipt['transaction_signature']
        compact = {key: value for key, value in receipt.items()
                   if key not in ('simulation', 'network_transaction')}
        compact['evidence_path'] = str(path.relative_to(ROOT))
        if receipt.get('confirmed'):
            fetched = receipt['network_transaction']
            raw = base64.b64decode(fetched['transaction'][0])
            transaction = VersionedTransaction.from_bytes(raw)
            assert str(transaction.signatures[0]) == signature
            assert len(raw) == receipt['transaction_bytes']
            assert (fetched['meta']['err'] is None) == receipt['success']
            assert fetched['meta']['computeUnitsConsumed'] == receipt['compute_units']
            compact['wire_sha256'] = hashlib.sha256(raw).hexdigest()
            if receipt.get('mode') == 'xmss':
                assert transaction.version() == 1
                message = transaction.message
                assert len(message.instructions) == 1
                instruction = message.instructions[0]
                assert str(message.account_keys[instruction.program_id_index]) == manifest['program_id']
                assert instruction.data[0] == 2
                resources = {key: getattr(message.config, key) for key in
                             ('compute_unit_limit', 'loaded_accounts_data_size_limit', 'heap_size')}
                assert resources == receipt['inline_resources']
                compact['network_decoded_inline_resources'] = resources
                compact['network_custody_instruction_count'] = 1
            receipts[signature] = compact
        attempts.append(compact)
    # Retain CLI-discovered signatures and enrich them with exact wire receipts
    # where available; a preflight rejection remains an unconfirmed attempt.
    for row in manifest['confirmed_transactions']:
        if row['transaction_signature'] in receipts:
            receipt = receipts[row['transaction_signature']]
            for key in ('transaction_bytes', 'compute_units', 'transaction_version',
                        'network_decoded_version', 'wire_sha256', 'evidence_path'):
                if key in receipt:
                    row[key] = receipt[key]
            for key in ('network_decoded_inline_resources', 'network_custody_instruction_count'):
                if key in receipt:
                    row[key] = receipt[key]
    manifest['transaction_attempts'] = attempts
    manifest['known_unconfirmed_attempts'] = [row for row in attempts if not row.get('confirmed')]
    address_link = lambda address: f'https://explorer.solana.com/address/{address}?cluster=devnet'
    manifest['explorer_links'] = {key: address_link(manifest[key]) for key in
                                  ('program_id', 'mock_mint', 'developer_public_address')}
    for vault in manifest['vaults']:
        vault['explorer_links'] = {key: address_link(vault[key]) for key in
                                   ('state', 'treasury', 'token_source', 'recipient_sol', 'recipient_token')}
    manifest['validation_artifacts'] = {
        'devnet_summary': 'artifacts/v1-devnet-validation-summary.json',
        'local_summary': 'artifacts/canonical-v1-validation-summary.json',
        'native_tests': 'artifacts/v1-native-program-test-results.json',
        'build_environment': 'artifacts/v1-integration-environment.json',
        'initial_cli_failure': 'artifacts/logs/v1-cli-deploy-failure.log',
        'devnet_benchmarks': 'artifacts/v1-devnet-benchmarks.jsonl',
    }
    operations = [row for row in manifest['confirmed_transactions'] if row.get('mode')]
    assert len(operations) == 10
    assert all(row['confirmed'] and row['success'] and row['balance_assertions_passed'] for row in operations)
    xmss = [row for row in operations if row['mode'] == 'xmss']
    assert len(xmss) == 6
    assert all(row['transaction_version'] == row['network_decoded_version'] == 1 for row in xmss)
    assert all(row['transaction_count_for_operation'] == 1 and row['transaction_bytes'] <= 4096 for row in xmss)
    controls = {row['operation'].removeprefix(manifest['demo_run_id'] + '-'): row for row in manifest['simulations']}
    low = controls['xmss-inline-compute-limit-1']
    loaded = controls['xmss-inline-loaded-limit-1']
    assert low['expected_error_verified'] == 'compute_budget_exhausted'
    assert loaded['expected_error_verified'] == 'MaxLoadedAccountsDataSizeExceeded'
    first = next(row for row in xmss if row['operation'].endswith('-xmss-withdraw-sol'))
    assert first['message_commitment'] == low['message_commitment'] == loaded['message_commitment']
    assert first['witness_sha256'] == low['witness_sha256'] == loaded['witness_sha256']
    assert first['compute_units'] > 200_000
    benchmarks = []
    for row in operations:
        mode, action = row['mode'], row['action']
        vault = next(value for value in manifest['vaults'] if value['mode'] == mode)
        benchmark = {
            'schema_version': 1, 'run_id': manifest['demo_run_id'], 'operation_id': row['operation'],
            'observed_at_utc': row['observed_at_utc'], 'commit': manifest['demo_environment']['commit'],
            'program_binary_sha256': manifest['deployed_binary_sha256'], 'evidence_paths': [row['evidence_path']],
            'environment': {'evidence_level': 'devnet_confirmed', 'cluster': 'devnet',
                'genesis_hash': manifest['genesis_hash'], 'runtime_version': manifest['demo_environment']['rpc_version']['solana-core'],
                'toolchain_manifest': 'artifacts/v1-integration-environment.json'},
            'experiment': {'mode': {'array': 'SECRET_ARRAY_V1', 'merkle': 'MERKLE_SECRET_V1', 'xmss': 'XMSS_SHA2_10_256_V1'}[mode],
                'parameter_set': 'XMSS-SHA2_10_256' if mode == 'xmss' else None,
                'asset': 'SOL' if action == 1 else 'MOCK_USDC' if action == 2 else None,
                'mint': manifest['mock_mint'], 'leaf_count': vault['leaf_capacity'],
                'scenario': row['operation'].removeprefix(manifest['demo_run_id'] + '-'), 'fixture_id': vault['state'],
                'command': 'python scripts/infrastructure-devnet-demo.py --run-id ' + manifest['demo_run_id']},
            'outcome': {'expected': 'success', 'observed': 'success', 'test_passed': True,
                'error_code': None, 'failure_stage': None, 'verifier_reached': True},
            'transport': {'version': 'v1' if mode == 'xmss' else 'legacy', 'transaction_index': 0,
                'transaction_count_for_operation': 1, 'transaction_bytes': row['transaction_bytes'],
                'instruction_data_bytes': row['instruction_data_bytes'], 'signature_or_witness_bytes': row['witness_bytes'],
                'merkle_proof_bytes': 32 * vault['merkle_authentication_path_height'] if mode == 'merkle' else None,
                'transaction_signature': row['transaction_signature'], 'confirmation_status': row['confirmation_status'],
                'inline_configuration': row.get('network_decoded_inline_resources')},
            'resources': {'compute_limit': 1_400_000, 'compute_consumed': row['compute_units'],
                'sha256_syscall_count': None, 'allocated_account_bytes': None,
                'logical_authority_bytes': len(bytes.fromhex(row['before']['authority_hex'])),
                'storage_deposit_lamports': None, 'storage_refund_lamports': None,
                'actual_transaction_fee_lamports': str(row['fee_lamports']),
                'inline_limits_enforced': True if mode == 'xmss' else None,
                'temporary_account_bytes': 0, 'usage_bitmap_bytes': 128},
        }
        assert not validate(benchmark, ROOT), validate(benchmark, ROOT)
        benchmarks.append(benchmark)
    (artifact / 'v1-devnet-benchmarks.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in benchmarks))
    summary = {
        'status': manifest['status'], 'cluster': 'devnet',
        'deployment_environment': {key: manifest[key] for key in ('commit', 'rpc_version', 'genesis_hash')},
        'demonstration_environment': manifest['demo_environment'],
        'program_id': manifest['program_id'], 'mock_mint': manifest['mock_mint'],
        'binary_sha256': manifest['deployed_binary_sha256'],
        'vaults': manifest['vaults'],
        'confirmed_transaction_count': len({row['transaction_signature'] for row in manifest['confirmed_transactions']}),
        'unconfirmed_attempt_count': len(manifest['known_unconfirmed_attempts']),
        'custody_operations': [{key: row[key] for key in ('operation', 'mode', 'action', 'transaction_bytes',
            'transaction_version', 'compute_units', 'transaction_signature', 'explorer_url', 'evidence_path',
            'balance_assertions_passed')} for row in operations],
        'inline_resource_enforcement': {
            'evidence_level': 'devnet_simulation_and_confirmed_execution',
            'same_canonical_intent_verified': True,
            'same_xmss_witness_verified': True,
            'low_cu_error': low['result']['value']['err'],
            'low_cu_units_consumed': low['result']['value']['unitsConsumed'],
            'low_loaded_data_error': loaded['result']['value']['err'],
            'accepted_signature': first['transaction_signature'],
            'accepted_compute_units': first['compute_units'],
            'accepted_requested_limits': first['inline_resources'],
        },
        'local_runtime_caveat': 'LiteSVM uses a 1,400,000-CU runtime override; inline limits are not enforced locally.',
    }
    for filename in ('devnet-deployment.json', 'public-deployment.json'):
        write_json(artifact / filename, manifest)
    write_json(artifact / 'v1-devnet-validation-summary.json', summary)
    print(json.dumps({key: summary[key] for key in ('status', 'confirmed_transaction_count', 'unconfirmed_attempt_count')}))


if __name__ == '__main__':
    main()
