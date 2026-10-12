"""Paced official upgradeable-loader deployment after a partial CLI upload.

Wire/account ordering follows solana-program 2.1.0 bpf_loader_upgradeable.rs
and loader_upgradeable_instruction.rs (the locked program dependency).
Only the dedicated private program/buffer and authorized developer are used.
"""
import base64
import hashlib
import json
import struct
from solders.compute_budget import set_compute_unit_limit
from solders.instruction import Instruction, AccountMeta
from solders.pubkey import Pubkey
from solders.sysvar import RENT, CLOCK
from solders.system_program import create_account, CreateAccountParams
from solders.transaction import Transaction, VersionedTransaction
from client.transport import build_xmss_transaction
from infrastructure_devnet import ROOT, PRIVATE, keypair, private_json, account, rpc, blockhash, send, write_json

LOADER = Pubkey.from_string('BPFLoaderUpgradeab1e11111111111111111111111')


def meta(key, writable=False, signer=False):
    return AccountMeta(key, signer, writable)


def submit(instructions, name, signers, *, v1=False):
    payer = signers[0]
    path = PRIVATE / 'prepared-deployment' / (name + '.json')
    tx = None
    if path.exists():
        previous = json.loads(path.read_text())
        data = base64.b64decode(previous['transaction_base64'])
        tx = VersionedTransaction.from_bytes(data) if previous['v1'] else Transaction.from_bytes(data)
        status = rpc('getSignatureStatuses', [[str(tx.signatures[0])], {'searchTransactionHistory': True}])['value'][0]
        if status is None and not rpc('isBlockhashValid', [str(tx.message.recent_blockhash), {'commitment': 'confirmed'}])['value']:
            status = rpc('getSignatureStatuses', [[str(tx.signatures[0])], {'searchTransactionHistory': True}])['value'][0]
            if status is None:
                tx = None
    if tx is None:
        tx = build_xmss_transaction(payer.pubkey(), signers, instructions, blockhash()) if v1 else Transaction.new_signed_with_payer(
            [set_compute_unit_limit(1_400_000), *instructions], payer.pubkey(), signers, blockhash())
        private_json(path, {'transaction_base64': base64.b64encode(bytes(tx)).decode(), 'v1': v1})
    return send(tx, name, metadata={'purpose': 'paced_official_upgradeable_loader_deployment'})


def paced_deploy(binary):
    developer, program, buffer = keypair(), keypair('program'), keypair('deployment-buffer')
    programdata, _ = Pubkey.find_program_address([bytes(program.pubkey())], LOADER)
    deployed = account(program.pubkey())
    if deployed:
        assert deployed['owner'] == str(LOADER) and deployed['executable']
        program_bytes = base64.b64decode(deployed['data'][0])
        assert program_bytes == struct.pack('<I', 2) + bytes(programdata)
        data_account = account(programdata)
        data = base64.b64decode(data_account['data'][0])
        assert data_account['owner'] == str(LOADER) and data[:4] == struct.pack('<I', 3)
        assert data[12] == 1 and data[13:45] == bytes(developer.pubkey())
        assert data[45:] == binary
        return {'programId': str(program.pubkey()), 'alreadyDeployed': True}
    receipt_path = ROOT / 'artifacts/v1-paced-deployment-receipts.json'
    receipts = json.loads(receipt_path.read_text()) if receipt_path.exists() else []
    existing = account(buffer.pubkey())
    if existing is None:
        rent = rpc('getMinimumBalanceForRentExemption', [37 + len(binary)])
        create = create_account(CreateAccountParams(from_pubkey=developer.pubkey(), to_pubkey=buffer.pubkey(), lamports=rent, space=37 + len(binary), owner=LOADER))
        initialize = Instruction(LOADER, struct.pack('<I', 0), [meta(buffer.pubkey(), True), meta(developer.pubkey())])
        receipts.append(submit([create, initialize], 'paced-create-deployment-buffer', [developer, buffer]))
        existing = account(buffer.pubkey())
    data = base64.b64decode(existing['data'][0])
    assert existing['owner'] == str(LOADER) and not existing['executable']
    assert len(data) == 37 + len(binary) and data[:5] == struct.pack('<IB', 1, 1)
    assert data[5:37] == bytes(developer.pubkey()), 'Buffer authority differs from dedicated developer'
    for offset in range(0, len(binary), 3500):
        chunk = binary[offset:offset + 3500]
        if data[37 + offset:37 + offset + len(chunk)] == chunk:
            continue
        # bincode enum discriminant u32, offset u32, Vec<u8> length u64.
        instruction = Instruction(LOADER, struct.pack('<IIQ', 1, offset, len(chunk)) + chunk,
                                  [meta(buffer.pubkey(), True), meta(developer.pubkey(), False, True)])
        receipts.append(submit([instruction], f'paced-write-buffer-{offset:06d}', [developer], v1=True))
        write_json(ROOT / 'artifacts/v1-paced-deployment-receipts.json', receipts)
    uploaded = base64.b64decode(account(buffer.pubkey())['data'][0])
    assert uploaded[37:] == binary, 'Buffer payload differs before final deployment'
    rent = rpc('getMinimumBalanceForRentExemption', [36])
    create = create_account(CreateAccountParams(from_pubkey=developer.pubkey(), to_pubkey=program.pubkey(), lamports=rent, space=36, owner=LOADER))
    deploy = Instruction(LOADER, struct.pack('<IQ', 2, len(binary)), [
        meta(developer.pubkey(), True, True), meta(programdata, True), meta(program.pubkey(), True), meta(buffer.pubkey(), True),
        meta(RENT), meta(CLOCK), meta(Pubkey.default()), meta(developer.pubkey(), False, True)])
    final = submit([create, deploy], 'paced-final-program-deployment', [developer, program])
    receipts.append(final)
    write_json(ROOT / 'artifacts/v1-paced-deployment-receipts.json', receipts)
    return {'programId': str(program.pubkey()), 'signature': final['transaction_signature'], 'deployment_method': 'paced_official_loader',
            'programdata_address': str(programdata), 'binary_sha256': hashlib.sha256(binary).hexdigest()}
