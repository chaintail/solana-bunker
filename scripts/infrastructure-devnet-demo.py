"""Devnet demonstrations using private, single-writer fixtures and inline XMSS v1."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import uuid
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from solders.compute_budget import set_compute_unit_limit
from solders.hash import Hash
from solders.instruction import Instruction, AccountMeta
from solders.message import TransactionConfig
from solders.pubkey import Pubkey
from solders.system_program import create_account, transfer, CreateAccountParams, TransferParams
from solders.transaction import Transaction, VersionedTransaction
from client.actions import encode_intent, parse_intent
from client.journal import SigningJournal, AuthorityHistory
from client.merkle import SecretTree
from client.transport import execute_instruction, build_xmss_transaction
from crypto.xmss import keygen, sign_at
from infrastructure_devnet import ROOT, PRIVATE, GENESIS, NOW, account, rpc, keypair, private_json, blockhash, send, write_json, environment

TOKEN = Pubkey.from_string('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')
SYSTEM = Pubkey.default()
NAMESPACE = bytes(Hash.from_string(GENESIS))


def meta(key, writable=False, signer=False):
    return AccountMeta(key, signer, writable)


class Demonstrations:
    def __init__(self, run_id):
        self.path = PRIVATE / run_id
        self.path.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.run_id = run_id
        self.developer = keypair()
        self.relayer = keypair(run_id + '-relayer')
        self.recipient = keypair(run_id + '-recipient')
        self.attacker = keypair(run_id + '-attacker')
        self.token_recipient = keypair(run_id + '-token-recipient')
        self.token_attacker = keypair(run_id + '-token-attacker')
        self.manifest = json.loads((ROOT / 'artifacts/devnet-deployment.json').read_text())
        assert self.manifest['program_deployed'] and self.manifest['mock_mint_created']
        self.program = Pubkey.from_string(self.manifest['program_id'])
        self.mint = Pubkey.from_string(self.manifest['mock_mint'])
        self.manifest.update(demo_environment=environment(), default_xmss_transport='inline-v1', demo_run_id=run_id)
        self.manifest.setdefault('simulations', [])
        self.completed = {row['operation']: row for row in self.manifest['confirmed_transactions']}
        self.flush()

    def flush(self):
        for name in ('devnet-deployment.json', 'public-deployment.json'):
            write_json(ROOT / 'artifacts' / name, self.manifest)

    def submit(self, instructions, name, payer=None, signers=None, *, v1=False, metadata=None):
        name = self.run_id + '-' + name
        if name in self.completed:
            return self.completed[name]
        payer = payer or self.relayer
        signers = signers or [payer]
        prepared_path = self.path / 'prepared-transactions' / (name + '.json')
        tx = None
        if prepared_path.exists():
            prepared = json.loads(prepared_path.read_text())
            raw = base64.b64decode(prepared['transaction_base64'])
            tx = VersionedTransaction.from_bytes(raw) if prepared['v1'] else Transaction.from_bytes(raw)
            metadata = prepared['metadata']
            # A saved signature is authoritative even when confirmation retrieval
            # failed after broadcast. Never rebuild until its blockhash expired
            # and full-history status lookup still says it was never included.
            status = rpc('getSignatureStatuses', [[str(tx.signatures[0])], {'searchTransactionHistory': True}])['value'][0]
            if status is None and not rpc('isBlockhashValid', [str(tx.message.recent_blockhash), {'commitment': 'confirmed'}])['value']:
                status = rpc('getSignatureStatuses', [[str(tx.signatures[0])], {'searchTransactionHistory': True}])['value'][0]
                if status is None:
                    tx = None
        if tx is None:
            tx = build_xmss_transaction(payer.pubkey(), signers, instructions, blockhash()) if v1 else Transaction.new_signed_with_payer(
                [set_compute_unit_limit(1_400_000), *instructions], payer.pubkey(), signers, blockhash())
            private_json(prepared_path, {'transaction_base64': base64.b64encode(bytes(tx)).decode(), 'v1': v1, 'metadata': metadata})
        row = send(tx, name, metadata=metadata)
        self.manifest['confirmed_transactions'].append(row)
        self.completed[name] = row
        self.flush()
        return row

    def prepare(self):
        for role, pair, amount in [('relayer', self.relayer, 20_000_000), ('recipient', self.recipient, 1_000_000), ('attacker', self.attacker, 1_000_000)]:
            self.submit([transfer(TransferParams(from_pubkey=self.developer.pubkey(), to_pubkey=pair.pubkey(), lamports=amount))], 'fund-' + role, self.developer)
        for role, pair, owner in [('recipient', self.token_recipient, self.recipient), ('attacker', self.token_attacker, self.attacker)]:
            if account(pair.pubkey()) is None:
                create = create_account(CreateAccountParams(from_pubkey=self.developer.pubkey(), to_pubkey=pair.pubkey(), lamports=rpc('getMinimumBalanceForRentExemption', [165]), space=165, owner=TOKEN))
                initialize = Instruction(TOKEN, b'\x12' + bytes(owner.pubkey()), [meta(pair.pubkey(), True), meta(self.mint)])
                self.submit([create, initialize], 'create-token-' + role, self.developer, [self.developer, pair])

    def setup(self, mode):
        self.mode = mode
        self.label = {1: 'array', 2: 'merkle', 3: 'xmss'}[mode]
        path = self.path / (self.label + '.json')
        if path.exists():
            self.private = json.loads(path.read_text())
        else:
            public, secret = keygen(os.urandom(96)) if mode == 3 else (b'', b'')
            new_public, new_secret = keygen(os.urandom(96)) if mode == 3 else (b'', b'')
            self.private = {'vault': os.urandom(32).hex(), 'secrets': [os.urandom(32).hex() for _ in range(16)],
                            'public': public.hex(), 'secret': secret.hex(), 'new_public': new_public.hex(), 'new_secret': new_secret.hex()}
            private_json(path, self.private)
        self.vault = bytes.fromhex(self.private['vault'])
        self.state, _ = Pubkey.find_program_address([b'bunker_state', self.vault], self.program)
        self.treasury, _ = Pubkey.find_program_address([b'bunker_treasury', bytes(self.state)], self.program)
        self.source, _ = Pubkey.find_program_address([b'bunker_token', bytes(self.state)], self.program)
        self.secrets = [bytes.fromhex(s) for s in self.private['secrets']]
        self.tree = SecretTree(self.secrets)
        authority = b''.join(hashlib.sha256(s).digest() for s in self.secrets) if mode == 1 else self.tree.root if mode == 2 else bytes.fromhex(self.private['public'])
        if account(self.state) is None:
            data = b'\x00' + self.vault + NAMESPACE + struct.pack('<BH', mode, 1024 if mode == 3 else 16)
            initialize = Instruction(self.program, data, [meta(self.developer.pubkey(), True, True), meta(self.state, True), meta(self.treasury, True), meta(self.source, True), meta(self.mint), meta(SYSTEM), meta(TOKEN)])
            self.submit([initialize], self.label + '-initialize', self.developer)
        state_data = self.state_data()
        written = int.from_bytes(state_data[226:230], 'little')
        for offset in range(written, len(authority), 900):
            instruction = Instruction(self.program, b'\x01' + struct.pack('<I', offset) + authority[offset:offset + 900], [meta(self.developer.pubkey(), True, True), meta(self.state, True), meta(SYSTEM)])
            self.submit([instruction], self.label + '-authority-' + str(offset), self.developer)
        self.submit([transfer(TransferParams(from_pubkey=self.developer.pubkey(), to_pubkey=self.treasury, lamports=10_000_000))], self.label + '-deposit-sol', self.developer)
        self.submit([Instruction(TOKEN, b'\x07' + struct.pack('<Q', 1_000_000), [meta(self.mint, True), meta(self.source, True), meta(self.developer.pubkey(), False, True)])], self.label + '-mint-mock-usdc', self.developer)
        if not any(v['state'] == str(self.state) for v in self.manifest['vaults']):
            self.manifest['vaults'].append({'mode': self.label, 'vault_id': self.vault.hex(), 'state': str(self.state), 'treasury': str(self.treasury), 'token_source': str(self.source), 'initialized': True,
                'explorer_url': f'https://explorer.solana.com/address/{self.treasury}?cluster=devnet',
                'recipient_sol': str(self.recipient.pubkey()), 'recipient_token': str(self.token_recipient.pubkey())})
        self.flush()

    def state_data(self):
        return base64.b64decode(account(self.state)['data'][0])

    def snapshot(self):
        data = self.state_data()
        token_data = base64.b64decode(account(self.source)['data'][0])
        return {'treasury': str(self.treasury), 'token_source': str(self.source), 'treasury_lamports': account(self.treasury)['lamports'],
                'token_base_units': int.from_bytes(token_data[64:72], 'little'),
                'recipient_lamports': account(self.recipient.pubkey())['lamports'],
                'recipient_token_base_units': int.from_bytes(base64.b64decode(account(self.token_recipient.pubkey())['data'][0])[64:72], 'little'),
                'epoch': int.from_bytes(data[203:211], 'little'),
                'nonce': int.from_bytes(data[211:219], 'little'), 'consumed': [i for i in range(1024 if self.mode == 3 else 16) if data[230 + i // 8] & (1 << (i % 8))]}

    def intent(self, action, leaf, **fields):
        data = self.state_data()
        value = dict(program_id=bytes(self.program), namespace=NAMESPACE, vault_id=self.vault, state=bytes(self.state), treasury=bytes(self.treasury), mode=self.mode,
                     epoch=int.from_bytes(data[203:211], 'little'), nonce=int.from_bytes(data[211:219], 'little'), leaf_index=leaf, action=action)
        if action == 1:
            value.update(destination=bytes(self.recipient.pubkey()), amount=10_000)
        elif action == 2:
            value.update(token_program=bytes(TOKEN), mint=bytes(self.mint), source=bytes(self.source), destination=bytes(self.token_recipient.pubkey()), amount=10_000, decimals=6)
        elif action == 3:
            value.update(targets=[8, 9])
        else:
            public = bytes.fromhex(self.private['new_public'])
            value.update(new_mode=3, parameter_id=1, root=public[:32], public_seed=public[32:])
        return value | fields

    def witness(self, value, operation, new=False):
        leaf = value['leaf_index']
        if self.mode == 1:
            return struct.pack('<I', leaf) + self.secrets[leaf]
        if self.mode == 2:
            return self.tree.witness(leaf)
        public = bytes.fromhex(self.private['new_public' if new else 'public'])
        secret = bytes.fromhex(self.private['new_secret' if new else 'secret'])
        keyset = hashlib.sha256(public).hexdigest()
        with SigningJournal(self.path / 'journals' / keyset, keyset) as journal:
            return journal.sign(operation, encode_intent(value), lambda index, message: sign_at(secret, index, message), leaf)['signature']

    def instruction(self, value, witness):
        destination = Pubkey.from_bytes(value['destination']) if 'destination' in value else self.recipient.pubkey()
        accounts = [meta(self.state, True), meta(self.treasury, True), meta(self.mint), meta(self.source, True), meta(destination, True), meta(TOKEN)]
        return execute_instruction(value, witness, accounts)

    def simulate(self, name, value, witness, config=None, expect_success=False, expected_error=None):
        tx = build_xmss_transaction(self.relayer.pubkey(), [self.relayer], [self.instruction(value, witness)], blockhash(), config=config)
        result = rpc('simulateTransaction', [base64.b64encode(bytes(tx)).decode(), {'encoding': 'base64', 'sigVerify': True, 'commitment': 'confirmed'}])
        row = {'operation': self.run_id + '-' + name, 'observed_at_utc': NOW(), 'evidence_level': 'devnet_simulation', 'network_confirmation': False,
               'transaction_bytes': len(bytes(tx)), 'transaction_version': 1, 'result': result, 'expected_success': expect_success,
               'compute_limit': config.compute_unit_limit if config else 1_400_000,
               'loaded_accounts_bytes_limit': config.loaded_accounts_data_size_limit if config else 1_048_576,
               'message_commitment': hashlib.sha256(encode_intent(value)).hexdigest(), 'witness_sha256': hashlib.sha256(witness).hexdigest()}
        write_json(ROOT / 'artifacts/devnet-simulations' / (row['operation'] + '.json'), row)
        assert (result['value']['err'] is None) == expect_success, row
        if expected_error is not None:
            assert expected_error in json.dumps(result['value']['err']), row
            row['expected_error_verified'] = expected_error
        write_json(ROOT / 'artifacts/devnet-simulations' / (row['operation'] + '.json'), row)
        self.manifest['simulations'].append(row)
        self.flush()
        return row

    def execute(self, action, leaf, name, new=False, controls=False):
        if self.run_id + '-' + name in self.completed and self.completed[self.run_id + '-' + name].get('balance_assertions_passed'):
            return self.completed[self.run_id + '-' + name]
        operation_path = self.path / 'prepared-authorizations' / (name + '.json')
        if operation_path.exists():
            prepared = json.loads(operation_path.read_text())
            value = parse_intent(bytes.fromhex(prepared['intent']))
            witness = bytes.fromhex(prepared['witness'])
            before = prepared['before']
        else:
            value = self.intent(action, leaf)
            witness = self.witness(value, name, new=new)
            before = self.snapshot()
            private_json(operation_path, {'intent': encode_intent(value).hex(), 'witness': witness.hex(), 'before': before})
        # Skip simulations when this exact envelope already landed; the stale
        # nonce is then expected and submit() reconciles its confirmed signature.
        pending = self.path / 'prepared-transactions' / (self.run_id + '-' + name + '.json')
        already_landed = False
        if pending.exists():
            saved = json.loads(pending.read_text())
            saved_tx = VersionedTransaction.from_bytes(base64.b64decode(saved['transaction_base64']))
            already_landed = rpc('getSignatureStatuses', [[str(saved_tx.signatures[0])], {'searchTransactionHistory': True}])['value'][0] is not None
        if controls and not already_landed:
            low = self.simulate('xmss-inline-compute-limit-1', value, witness, TransactionConfig(compute_unit_limit=1, loaded_accounts_data_size_limit=1_048_576, heap_size=32_768), expected_error='ComputationalBudgetExceeded')
            assert 'ComputationalBudgetExceeded' in json.dumps(low['result'])
            self.simulate('xmss-inline-loaded-limit-1', value, witness, TransactionConfig(compute_unit_limit=1_400_000, loaded_accounts_data_size_limit=1, heap_size=32_768), expected_error='MaxLoadedAccountsDataSizeExceeded')
        if self.mode == 3 and action in (1, 2) and not already_landed:
            altered = value | {'destination': bytes(self.attacker.pubkey() if action == 1 else self.token_attacker.pubkey())}
            self.simulate(name + '-destination-substitution', altered, witness, expected_error='"Custom": 12')
        row = self.submit([self.instruction(value, witness)], name, v1=self.mode == 3, metadata={
            'mode': self.label, 'action': action, 'witness_bytes': len(witness), 'instruction_data_bytes': len(self.instruction(value, witness).data),
            'transaction_count_for_operation': 1, 'message_commitment': hashlib.sha256(encode_intent(value)).hexdigest(),
            'inline_resources': {'compute_unit_limit': 1_400_000, 'loaded_accounts_data_size_limit': 1_048_576, 'heap_size': 32_768} if self.mode == 3 else None,
            'before': before})
        after = self.snapshot()
        assert after['nonce'] == before['nonce'] + 1
        if action == 1:
            assert before['treasury_lamports'] - after['treasury_lamports'] == value['amount']
            assert after['recipient_lamports'] - before['recipient_lamports'] == value['amount']
        elif action == 2:
            assert before['token_base_units'] - after['token_base_units'] == value['amount']
            assert after['recipient_token_base_units'] - before['recipient_token_base_units'] == value['amount']
        elif action == 3:
            assert set([leaf, 8, 9]) <= set(after['consumed'])
            if self.mode == 3:
                keyset = hashlib.sha256(bytes.fromhex(self.private['public'])).hexdigest()
                with SigningJournal(self.path / 'journals' / keyset, keyset) as journal:
                    locally_retired = {entry['leaf_index'] for entry in journal.public_status()}
                    for target in (8, 9):
                        if target not in locally_retired:
                            journal.retire(target)
        else:
            assert after['epoch'] == before['epoch'] + 1 and after['consumed'] == []
            for field in ('treasury', 'token_source', 'treasury_lamports', 'token_base_units'):
                assert before[field] == after[field]
        row['after'] = after
        row['balance_assertions_passed'] = True
        self.flush()
        return row

    def run(self):
        self.prepare()
        for mode in (1, 2, 3):
            self.setup(mode)
            self.execute(1, 0, self.label + '-withdraw-sol', controls=mode == 3)
            self.execute(2, 1, self.label + '-withdraw-mock-usdc')
            if mode == 3:
                self.execute(3, 2, 'xmss-burn-leaves')
                old_path = self.path / 'old-unused-authorization.json'
                if not old_path.exists():
                    value = self.intent(1, 4)
                    witness = self.witness(value, 'old-unused-authorization')
                    private_json(old_path, {'value': {k: v.hex() if isinstance(v, bytes) else v for k, v in value.items()}, 'witness': witness.hex()})
                self.execute(4, 3, 'xmss-rotate-root')
                old = json.loads(old_path.read_text())
                value = {k: bytes.fromhex(v) if k in ('program_id', 'namespace', 'vault_id', 'state', 'treasury', 'destination') else v for k, v in old['value'].items()}
                self.simulate('xmss-old-unused-root-after-rotation', value, bytes.fromhex(old['witness']), expected_error='"Custom": 8')
                self.execute(1, 0, 'xmss-post-rotation-withdraw-sol', new=True)
                self.execute(2, 1, 'xmss-post-rotation-withdraw-mock-usdc', new=True)
            current = next(v for v in self.manifest['vaults'] if v['state'] == str(self.state))
            current['final_snapshot'] = self.snapshot()
            self.flush()
        self.manifest.update(status='deployed_and_demonstrated', inline_v1_confirmed=True, inline_v1_resource_enforcement='Low-CU and low-loaded-account-data devnet simulations rejected; identical full-limit XMSS authorization confirmed.',
            trusted_bypasses='Developer retains program upgrade and explicit demo administration; mint authority retained. These are excluded from attacker scope.')
        self.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', default='devnet-v1-' + uuid.uuid4().hex[:8])
    args = parser.parse_args()
    Demonstrations(args.run_id).run()
