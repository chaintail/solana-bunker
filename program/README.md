# Native custody program

`src/lib.rs` is the actual SBF program. `model.py` is a separate host executable
specification; host results must never be reported as Solana runtime evidence.

Build with pinned `solana-program=2.1.0`, `spl-token=7.0.0`, and the local exact
RFC 8391 verifier:

```sh
cargo check --manifest-path program/Cargo.toml
cargo build-sbf --manifest-path program/Cargo.toml --sbf-out-dir program/target/deploy
python -m unittest program.test_model -v
```

The binary has no embedded program ID: the runtime supplies it. All PDA checks
use canonical bumps and the same runtime program ID. Namespace is a fixed
32-byte deployment identifier configured during trusted bootstrap; clients use
the selected cluster genesis hash. It is authenticated in every action.

## Accounts and state

State seeds: `[b"bunker_state", vault_id32]`.
Treasury seeds: `[b"bunker_treasury", state_pubkey32]`.
Basic SPL source seeds: `[b"bunker_token", state_pubkey32]`.
The treasury is an eight-byte program-owned native account. Its rent minimum
remains after SOL debits. It is the authority of the source token account.

State allocation is 358 bytes plus actual authority bytes. Large arrays start
with at most 10,000 allocated bytes, grow with sequential writes, and cannot
execute until all requested authority bytes are written. Merkle/XMSS do not
allocate a large unused array. Bitmap capacity is fixed 1,024 leaves (128 bytes).
Allocation/rent figures here describe the format; runtime measurements belong
in the generated evidence.

| Offset | Bytes | Field |
|---:|---:|---|
| 0 | 8 | `BUNKST01` |
| 8 | 32 | vault ID |
| 40 | 32 | namespace |
| 72 | 32 | treasury |
| 104 | 32 | trusted demo administrator |
| 136 | 32 | six-decimal mock mint |
| 168 | 32 | exact source token account |
| 200 | 1 | mode 1=array, 2=Merkle, 3=XMSS |
| 201 | 2 | leaf count, little endian |
| 203 | 8 | epoch, little endian |
| 211 | 8 | action nonce, little endian |
| 219 | 1 | canonical state bump |
| 220 | 1 | canonical treasury bump |
| 221 | 4 | authority length, little endian |
| 225 | 1 | initialized authority flag |
| 226 | 4 | sequential authority bytes written |
| 230 | 128 | consumed bitmap; index/8, bit index%8 |
| 358 | variable | commitments / Merkle root / XMSS root and seed |

## Instruction ABI

Every instruction starts with a one-byte opcode. Accounts below are positional.
`W` means writable; `S` means signer. Counts, offsets and intent lengths are
little endian. Authority/signature bytes are passed unchanged.

| Opcode | Payload after opcode | Accounts |
|---:|---|---|
| 0 initialize | vault32, namespace32, mode u8, leaf count u16 | payer WS, state W, treasury W, source W, mint, system program, token program |
| 1 write authority | offset u32, 1..900 authority bytes | admin WS, state W, system program |
| 2 execute inline | intent length u16, exact intent, witness | state W, treasury W, mint, source W for token, exact destination W for withdrawal, token program |
| 3 execute staged | intent length u16, exact intent | same accounts as 2, sealed witness account |
| 4 create witness | intent length u16, exact intent, witness length u32=2500 | payer WS, fresh witness account WS, state, system program |
| 5 write witness | offset u32, 1..900 signature bytes | creator S, witness account W |
| 6 trusted mode transition | new mode u8, leaf count u16 | admin WS, state W, system program |

Opcode 0 checks the standard Token Program, six decimals, initialized mint, and
no freeze authority. It creates and initializes the exact source with the
Token Program. Authority writing must begin at offset zero and continue
without gaps. Duplicate initialization is rejected.

Canonical action bytes are defined in `client/actions.py` and
`reports/interfaces.md`. The native parser independently checks lengths and
fields. Array witness is index u32LE + secret32. Merkle adds exactly one sibling
per tree level; index bits supply directions. XMSS is the exact raw RFC
2500-byte signature (its index remains big endian).

## Immutable signature transport

A witness account is a fresh signer account created for one exact intent.
Its 125-byte header holds `BUNKW001`, state32, SHA-256(intent)32, creator32,
epoch u64, signing index u32, witness length u32, written length u32, sealed u8.
Only its creator can append, only at the next sequential offset. A complete
signature seals it automatically; further writes fail. Execution requires
matching owner, state, exact intent hash, epoch, index, total length and seal.
The signature is still verified; uploading data does not authorize custody.

The fallback logical operation currently uses five transactions: witness
creation, three <=900-byte writes, and final execution. These account rent and
transaction costs must all appear in staged-operation evidence. The sprint
program intentionally leaves sealed witness accounts allocated: there is no
unreviewed close/refund path. Public deployments should use fresh private
signing state, never the public reference fixture keys.

## Authorization and trust

Only the selected mode can authorize. Every action must match program,
namespace, vault, state, treasury, mode, epoch, nonce and signing index.
Array/Merkle witnesses are intentionally bearer credentials: copied witnesses
can authorize altered amounts or destinations before consumption. XMSS
verifies the entire exact canonical action. Fresh leaf index and current
single action nonce are checked independently.

Burn targets are sorted, unique, nonempty (max32), in range, unused, and exclude
the signing leaf. A successful burn consumes both the signing leaf and targets.
Rotation requires current XMSS authorization over new root/public seed and
fixed parameter 1. It rejects the current authority, advances epoch and global
nonce, and clears only the fresh tree's bitmap. Treasury/source are untouched.
Historical keyset reuse is additionally rejected by the client journal; the
program does not maintain an unbounded authority history.

The ordinary deployment upgrade authority and opcode6 demo administrator are
trusted and outside the attacker simulation. Opcode6 visibly advances epoch
and nonce and requires completing new authority setup. It can replace custody
authorization and therefore undermines any whole-system claim if compromised.
There is no direct administrator withdrawal instruction or inactive verifier
fallback. Administrative selection of fresh key material is a fixture
responsibility; the independent XMSS rotation path rejects immediate reuse.

Token transfers validate mint, canonical source, source owner, standard token
program, six decimals, exact destination token account and positive amount.
Unexpected source delegates, close authority, or frozen state are rejected.
Native withdrawals reject destination aliases with state, treasury, and source.
All arithmetic uses checked operations. Authorization state is updated before
transfer; any later failure rolls back the complete transaction in the SVM,
while fee-payer fees remain outside that rollback.
