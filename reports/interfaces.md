# Shared interface v1

This is an executable research interface, not a production custody architecture.
Agreed by the program and client workers, 2026-10-12.

## Identities and mode identifiers

State seeds `[b"bunker_state", vault_id32]`; treasury seeds
`[b"bunker_treasury", state_address32]`. Canonical bumps. Roots and modes are
excluded from seeds. Address stability applies within one program and cluster.
Modes: 1 = SECRET_ARRAY_V1; 2 = MERKLE_SECRET_V1;
3 = XMSS_SHA2_10_256_V1. Actions: 1 = withdraw SOL; 2 = withdraw mock token;
3 = burn leaves; 4 = rotate XMSS root.

## Canonical intent

The Python APIs are `client.actions.encode_intent(mapping) -> bytes` and
`parse_intent(bytes) -> mapping`. Pubkeys are raw 32 bytes, or lowercase hex
in JSON. Monetary integers in public JSON use decimal strings.

| Offset | Bytes | Field |
|---:|---:|---|
| 0 | 8 | `BUNKER 00 01` (ASCII BUNKER then zero and version one) |
| 8 | 32 | Program ID |
| 40 | 32 | Namespace: decoded genesis hash for network deployments |
| 72 | 32 | Vault identifier |
| 104 | 32 | State PDA |
| 136 | 32 | Treasury PDA |
| 168 | 1 | Active mode |
| 169 | 8 | Authority epoch, little endian u64 |
| 177 | 8 | Expected action nonce, little endian u64 |
| 185 | 4 | Signing leaf, little endian u32 |
| 189 | 1 | Action ID |

Action payloads are concatenated without padding or optional fields:

- SOL: destination32, amount u64LE (40 bytes).
- Token: token_program32, mint32, source32, destination32, amount u64LE,
  decimals u8 (137 bytes); core token is six decimals.
- Burn: count u8, sorted unique target u32LE array (1..32 targets). Reject
  duplicates, already consumed, out-of-range, and authorizing-leaf target.
- Rotate: new mode u8=3, parameter ID u32LE=1, root32, public_seed32
  (69 bytes). Parameter ID 1 is RFC 8391 XMSS-SHA2_10_256; its own index
  and signature encoding remains big endian as standardized.

Reject unknown mode/action, truncation, trailing bytes, and integer overflow.
An action nonce serializes accepted actions even when skipped leaves are allowed.
Inner intent excludes outer recent blockhash and fee payer: a fresh outer
envelope can retry the exact intent/signature. It cannot alter signed effects.

## Baseline witness and commitments

Secrets are 32 bytes. Array stores SHA256(secret). Merkle leaf is
`SHA256(b"BUNKER-LEAF-V1\\0" || u32LE(index) || SHA256(secret))`;
internal node is `SHA256(b"BUNKER-NODE-V1\\0" || left32 || right32)`.
Proof directions derive only from index bits, least significant first.
Supported comparison counts are 16, 256, 1024; exact tree-height paths required.
Witness is index u32LE || secret32 || siblings in bottom-up order; array omits
siblings. This is intentionally bearer authorization, not an XMSS substitute.

## Crypto boundary and signing state

`crypto.xmss.keygen(seed96)->(public64, secret132)`;
`sign_at(secret132,index,message)->signature2500`;
`verify(public64,message,signature2500)->verified_index` or ValueError.
Public64 is root32 || public_seed32; parameter 1 is supplied by the mode/state.
Client reserves before signing, persists exact retry bytes before release,
and abandons every uncertain reservation. `SigningJournal` uses a nonblocking
OS writer lock and SQLite FULL synchronization; the journal is never a public
artifact. Back up state independently of mnemonic; onchain-unused does not mean
offchain-unexposed. Local `AuthorityHistory` rejects repeated roots/generations.

## Public vectors and execution adapter

Public fixture JSON uses schema_version=1, evidence_level=host_reference,
fixture_id, explicitly_disposable=true, intent_json, canonical_intent_hex,
intent_sha256, and public_commitments/root/proofs as applicable. Disposable
fixture seeds are never funded on shared clusters. No live seed or journal
belongs in exported events. Benchmark records use the handoff contract, with
null for unmeasured SVM CUs, real transaction serialization and fees.

The dependency-free CLI explicitly selects `host` adapter. An unavailable
`svm` adapter fails loudly; host model execution never produces network-confirmed
or local-SVM labels. The future network adapter must supply real serialization,
RPC submission/confirmation, token account plumbing, and runtime measurements.
