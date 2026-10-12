"""Executable custody specification. This is a host model, never SVM evidence.

Values are integer base units. Runtime rollback is modeled by committing a copied
ledger only after execution. Native source in src/lib.rs implements actual custody.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import copy
import hashlib
import struct
from typing import Callable

ARRAY, MERKLE, XMSS = 1, 2, 3
SOL, TOKEN, BURN, ROTATE = 1, 2, 3, 4
MAGIC = b'BUNKER\x00\x01'
TOKEN_PROGRAM = bytes.fromhex('06ddf6e1d765a193d9cbe146ceeb79ac1cb485ed5f5b37913a8cf5857eff00a9')
MAX_LEAVES = 1024
MAX_BURNS = 32

class Rejected(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def require(condition: bool, code: str):
    if not condition:
        raise Rejected(code)


def sha(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _on_curve(encoded: bytes) -> bool:
    # Solana's PDA rule uses Edwards point decompression, not subgroup membership.
    p = 2**255 - 19
    y = int.from_bytes(encoded, 'little') & ((1 << 255) - 1)
    if y >= p:
        return False
    d = (-121665 * pow(121666, -1, p)) % p
    x2 = ((y*y - 1) * pow((d*y*y + 1) % p, -1, p)) % p
    return x2 == 0 or pow(x2, (p-1)//2, p) == 1


def pda(program: bytes, seeds: list[bytes]) -> tuple[bytes, int]:
    require(len(program) == 32 and all(len(s) <= 32 for s in seeds), 'invalid_seeds')
    for bump in range(255, -1, -1):
        key = sha(b''.join(seeds) + bytes([bump]) + program + b'ProgramDerivedAddress')
        if not _on_curve(key):
            return key, bump
    raise Rejected('no_pda')


@dataclass(frozen=True)
class Intent:
    program: bytes
    namespace: bytes
    vault_id: bytes
    state: bytes
    treasury: bytes
    mode: int
    epoch: int
    nonce: int
    index: int
    action: int
    fields: dict
    wire: bytes


def parse_intent(data: bytes) -> Intent:
    require(len(data) >= 190 and data[:8] == MAGIC, 'malformed_intent')
    program, namespace, vault, state, treasury = (data[i:i+32] for i in range(8,168,32))
    mode, epoch, nonce, index, action = struct.unpack_from('<BQQIB', data, 168)
    require(mode in (ARRAY,MERKLE,XMSS), 'unknown_mode')
    payload = data[190:]
    f = {}
    if action == SOL:
        require(len(payload) == 40, 'malformed_intent')
        f = {'destination': payload[:32], 'amount': struct.unpack_from('<Q', payload, 32)[0]}
    elif action == TOKEN:
        require(len(payload) == 137, 'malformed_intent')
        f = dict(zip(('token_program','mint','source','destination'), (payload[i:i+32] for i in range(0,128,32))))
        f.update(amount=struct.unpack_from('<Q', payload,128)[0], decimals=payload[136])
    elif action == BURN:
        require(bool(payload) and 1 <= payload[0] <= MAX_BURNS and len(payload) == 1+4*payload[0], 'malformed_intent')
        targets = list(struct.unpack_from('<'+'I'*payload[0], payload, 1))
        require(targets == sorted(set(targets)), 'burn_list_not_canonical')
        f = {'targets': targets}
    elif action == ROTATE:
        require(len(payload) == 69, 'malformed_intent')
        f = {'new_mode':payload[0], 'parameter':struct.unpack_from('<I', payload,1)[0], 'authority':payload[5:69]}
    else:
        raise Rejected('unknown_action')
    return Intent(program, namespace, vault, state, treasury, mode, epoch, nonce, index, action, f, bytes(data))


@dataclass
class TokenAccount:
    mint: bytes
    authority: bytes
    amount: int = 0
    token_program: bytes = TOKEN_PROGRAM
    delegate: bytes | None = None
    close_authority: bytes | None = None
    frozen: bool = False


@dataclass
class State:
    vault_id: bytes
    address: bytes
    treasury: bytes
    namespace: bytes
    admin: bytes
    mint: bytes
    token_source: bytes
    mode: int
    authority: bytes
    leaf_count: int
    epoch: int = 0
    nonce: int = 0
    consumed: set[int] = field(default_factory=set)
    rent: int = 1
    state_bump: int = 0
    treasury_bump: int = 0

    @property
    def authority_bytes(self):
        return len(self.authority)


class BunkerLedger:
    """Model with explicit account ownership and an injectable RFC XMSS verifier."""
    def __init__(self, program_id: bytes, xmss_verify: Callable | None = None):
        require(len(program_id) == 32, 'invalid_program')
        self.program_id = program_id
        self.states: dict[bytes, State] = {}
        self.sol: dict[bytes, int] = {}
        self.owners: dict[bytes, bytes] = {}
        self.tokens: dict[bytes, TokenAccount] = {}
        self.xmss_verify = xmss_verify

    @staticmethod
    def validate_authority(mode: int, authority: bytes, count: int):
        require(1 <= count <= MAX_LEAVES and count & (count-1) == 0, 'invalid_leaf_count')
        require(mode in (ARRAY, MERKLE, XMSS), 'invalid_mode')
        require(len(authority) == {ARRAY:32*count, MERKLE:32, XMSS:64}[mode], 'invalid_authority')
        if mode == XMSS:
            require(count == 1024, 'wrong_xmss_parameter')

    def initialize(self, vault_id: bytes, namespace: bytes, admin: bytes, mint: bytes,
                   token_source: bytes, mode: int, authority: bytes, leaf_count: int,
                   rent: int = 1) -> State:
        require(all(len(x)==32 for x in (vault_id,namespace,admin,mint,token_source)), 'invalid_key')
        self.validate_authority(mode, authority, leaf_count)
        addr, sb = pda(self.program_id,[b'bunker_state',vault_id])
        treasury, tb = pda(self.program_id,[b'bunker_treasury',addr])
        require(addr not in self.states and treasury not in self.owners, 'already_initialized')
        require(token_source not in self.tokens and token_source not in (addr,treasury), 'invalid_source')
        s = State(vault_id,addr,treasury,namespace,admin,mint,token_source,mode,authority,leaf_count,
                  rent=rent,state_bump=sb,treasury_bump=tb)
        self.states[addr] = s
        self.sol[addr] = rent
        self.sol[treasury] = rent
        self.owners[addr] = self.owners[treasury] = self.program_id
        self.tokens[token_source] = TokenAccount(mint,treasury)
        return s

    def deposit_sol(self, state: bytes, amount: int):
        require(0 < amount < 2**64, 'invalid_amount')
        treasury = self.states[state].treasury
        require(self.sol[treasury] + amount < 2**64, 'overflow')
        self.sol[treasury] += amount

    def deposit_mock(self, state: bytes, amount: int):
        require(0 < amount < 2**64, 'invalid_amount')
        source = self.tokens[self.states[state].token_source]
        require(source.amount+amount < 2**64, 'overflow')
        source.amount += amount

    def _authorize(self, s: State, intent: Intent, witness: bytes):
        require(intent.index < s.leaf_count, 'index_out_of_range')
        require(intent.index not in s.consumed, 'leaf_consumed')
        if s.mode == ARRAY:
            require(len(witness)==36, 'invalid_witness_length')
            require(int.from_bytes(witness[:4],'little')==intent.index, 'witness_index_mismatch')
            require(sha(witness[4:])==s.authority[intent.index*32:(intent.index+1)*32], 'invalid_secret')
        elif s.mode == MERKLE:
            depth = s.leaf_count.bit_length()-1
            require(len(witness)==36+32*depth, 'invalid_witness_length')
            require(int.from_bytes(witness[:4],'little')==intent.index, 'witness_index_mismatch')
            node = sha(b'BUNKER-LEAF-V1\0'+witness[:4]+sha(witness[4:36]))
            for level in range(depth):
                sibling = witness[36+32*level:36+32*(level+1)]
                node = sha(b'BUNKER-NODE-V1\0'+(sibling+node if intent.index & (1<<level) else node+sibling))
            require(node==s.authority, 'invalid_merkle_proof')
        elif s.mode == XMSS:
            require(len(witness)==2500, 'invalid_witness_length')
            require(self.xmss_verify is not None, 'xmss_verifier_unavailable')
            try:
                result = self.xmss_verify(s.authority, intent.wire, witness)
            except Exception as exc:
                raise Rejected('invalid_xmss_signature') from exc
            require(result == intent.index, 'xmss_index_mismatch')
        else:
            raise Rejected('inactive_mode')

    def execute(self, intent: bytes, witness: bytes) -> dict:
        # A failed operation discards all program/token changes, including leaf/nonce.
        trial = copy.deepcopy(self)
        event = trial._execute(parse_intent(intent),bytes(witness))
        self.states, self.sol, self.owners, self.tokens = trial.states,trial.sol,trial.owners,trial.tokens
        return event

    def _execute(self, i: Intent, witness: bytes) -> dict:
        require(i.program == self.program_id, 'wrong_program')
        require(i.state in self.states, 'unknown_state')
        s = self.states[i.state]
        require(self.owners.get(s.address)==self.program_id and self.owners.get(s.treasury)==self.program_id, 'wrong_account_owner')
        require((i.namespace,i.vault_id,i.treasury)==(s.namespace,s.vault_id,s.treasury), 'wrong_vault_domain')
        require(i.mode==s.mode, 'inactive_mode')
        require(i.epoch==s.epoch and i.nonce==s.nonce, 'stale_epoch_or_nonce')
        require(s.nonce < 2**64-1, 'nonce_exhausted')
        f = i.fields
        # Account/payload checks run cheaply before hash-intensive verifier.
        if i.action == SOL:
            require(f['amount'] > 0 and f['destination'] not in (s.address,s.treasury,s.token_source), 'invalid_destination_or_amount')
            require(self.sol.get(f['destination'],0)+f['amount'] < 2**64, 'overflow')
        elif i.action == TOKEN:
            require((f['token_program'],f['mint'],f['source'],f['decimals']) == (TOKEN_PROGRAM,s.mint,s.token_source,6), 'token_intent_mismatch')
            require(f['destination'] in self.tokens and f['destination'] != s.token_source, 'invalid_token_destination')
            src, dst = self.tokens[s.token_source], self.tokens[f['destination']]
            require(src.mint==dst.mint==s.mint and src.token_program==dst.token_program==TOKEN_PROGRAM, 'wrong_token_mint_or_program')
            require(src.authority==s.treasury and src.delegate is None and src.close_authority is None, 'unexpected_source_authority')
            require(not src.frozen and not dst.frozen, 'frozen_token_account')
            require(f['amount'] > 0 and dst.amount+f['amount'] < 2**64, 'invalid_amount_or_overflow')
        elif i.action == BURN:
            require(all(x<s.leaf_count and x not in s.consumed and x!=i.index for x in f['targets']), 'invalid_burn_target')
        elif i.action == ROTATE:
            require(s.mode == XMSS and f['new_mode']==XMSS and f['parameter']==1, 'invalid_rotation_mode')
            require(f['authority']!=s.authority, 'authority_reuse')
            require(s.epoch < 2**64-1, 'epoch_exhausted')
        self._authorize(s,i,witness)
        s.consumed.add(i.index)
        s.nonce += 1
        if i.action == SOL:
            require(self.sol[s.treasury]-f['amount'] >= s.rent, 'insufficient_sol_preserving_rent')
            self.sol[s.treasury] -= f['amount']
            self.sol[f['destination']] = self.sol.get(f['destination'],0)+f['amount']
        elif i.action == TOKEN:
            require(src.amount >= f['amount'], 'insufficient_tokens')
            src.amount -= f['amount']
            dst.amount += f['amount']
        elif i.action == BURN:
            s.consumed.update(f['targets'])
        elif i.action == ROTATE:
            s.authority = f['authority']
            s.epoch += 1
            s.leaf_count = 1024
            s.consumed = set()
        return {'evidence_level':'host_reference','action':i.action,'state':s.address.hex(),
                'treasury':s.treasury.hex(),'epoch':s.epoch,'nonce':s.nonce,'index':i.index}

    def demo_mode(self, state: bytes, admin: bytes, mode: int, authority: bytes, leaf_count: int):
        s = self.states[state]
        require(admin == s.admin, 'unauthorized_admin')
        self.validate_authority(mode,authority,leaf_count)
        require(s.epoch < 2**64-1 and s.nonce < 2**64-1, 'counter_exhausted')
        require(authority != s.authority, 'authority_reuse')
        s.mode,s.authority,s.leaf_count = mode,authority,leaf_count
        s.epoch += 1
        s.nonce += 1
        s.consumed = set()
