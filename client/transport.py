"""Transaction assembly, separate from durable XMSS signing and submission.

The inline v1 default and the explicitly selected staged legacy fallback carry
the same canonical intent and RFC 8391 signature. Transport never signs an XMSS
message or modifies a signing journal.
"""
import struct

from solders.instruction import Instruction
from solders.message import MessageV1, TransactionConfig
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction

from .actions import encode_intent

XMSS_TRANSPORTS = ("inline-v1", "staged")
COMPUTE_UNIT_LIMIT = 1_400_000
LOADED_ACCOUNTS_DATA_SIZE_LIMIT = 1_048_576
HEAP_SIZE = 32_768
MAX_V1_TRANSACTION_BYTES = 4096
COMPUTE_BUDGET_PROGRAM = Pubkey.from_string("ComputeBudget111111111111111111111111111111")


def inline_config():
    return TransactionConfig(
        compute_unit_limit=COMPUTE_UNIT_LIMIT,
        loaded_accounts_data_size_limit=LOADED_ACCOUNTS_DATA_SIZE_LIMIT,
        heap_size=HEAP_SIZE,
    )


def config_values(config):
    return {name: getattr(config, name) for name in (
        "compute_unit_limit", "loaded_accounts_data_size_limit", "heap_size", "priority_fee"
    )}


def execute_instruction(intent, witness, accounts, *, program_id=None):
    """Opcode 2: intent length u16LE, canonical intent, inline raw witness.

Accounts are state W, treasury W, mint, source W for tokens, destination W
for withdrawals, Token Program. They remain explicit so substitution tests
exercise the onchain account checks instead of silently rebuilding accounts.
    """
    wire = encode_intent(intent)
    return Instruction(program_id or Pubkey.from_bytes(intent["program_id"]),
                       b"\x02" + struct.pack("<H", len(wire)) + wire + witness,
                       accounts)


def build_xmss_transaction(payer, signers, instructions, blockhash, *, config=None):
    """Build and sign the outer v1 envelope, enforcing its actual wire limit.

The caller supplies an already journaled XMSS authorization in the instruction.
Passing an explicit smaller config supports resource enforcement controls.
    """
    config = inline_config() if config is None else config
    if config.compute_unit_limit is None or not 1 <= config.compute_unit_limit <= COMPUTE_UNIT_LIMIT:
        raise ValueError("v1 compute_unit_limit must be explicitly set to 1..1400000")
    if config.loaded_accounts_data_size_limit is None or config.loaded_accounts_data_size_limit <= 0:
        raise ValueError("v1 loaded account data limit must be explicitly positive")
    if config.heap_size is None or not 32768 <= config.heap_size <= 262144 or config.heap_size % 1024:
        raise ValueError("v1 heap size must be an explicit 1024-byte multiple in 32768..262144")
    if any(ix.program_id == COMPUTE_BUDGET_PROGRAM for ix in instructions):
        raise ValueError("v1 resource limits belong in TransactionConfig")
    message = MessageV1.try_compile(payer, instructions, blockhash, config)
    transaction = VersionedTransaction(message, signers)
    size = len(bytes(transaction))
    if size > MAX_V1_TRANSACTION_BYTES:
        raise ValueError(f"serialized v1 transaction is {size} bytes; maximum is 4096")
    return transaction
