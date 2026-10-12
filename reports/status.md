# Sprint status

Updated October 12, 2026 (Eastern Time).

**Complete: fresh local validation and all ten devnet custody operations pass.** The default XMSS client carries one exact
canonical intent and a full 2,500-byte signature in one transaction. SOL, Mock
USDC, leaf burning and root rotation share the existing custody verifier.
Array/Merkle remain unchanged; explicit staged XMSS remains supported.

The [v1 execution report](v1-single-transaction.md) is the current evidence
index. Earlier milestone reports describe the staged baseline and retain their
historical scope. Public identifiers and confirmation state come from the
[deployment manifest](../artifacts/public-deployment.json).

## Confirmed devnet evidence

The [completed summary](../artifacts/v1-devnet-validation-summary.json) records
three initialized vaults, the verified six-decimal mock mint and exact onchain
SBF hash. Six XMSS operations each used one v1 transaction: SOL 3,117 bytes /
518,509 CUs; Mock USDC 3,214 / 532,564; burn 3,086 / 529,687; rotation 3,146 /
483,319; post-rotation SOL 3,117 / 506,910 and token 3,214 / 578,944. The
rotation preserved receiving addresses and balances; both new-root withdrawals
passed custody and recipient checks.

Low-CU, loaded-data, destination-substitution and stale-old-authorization
rejections are devnet **simulations**, distinct from those confirmed successes.
The register contains 140 confirmed signatures including deployment/setup and
one unconfirmed loader preflight rejection. Full addresses, receipts and the
separate local/deployment/demo source commits are in the v1 report.

## Fresh local validation

Source `e4d20bff4eb589f97fcdf84a9d668c2cbc46b67f`, custody binary
`48e2e324abcdcfd7e4c7cb601765da374595b922ed94e29d5ec168d37c06de79`
(124,464 bytes), Agave 4.3.0/platform-tools 1.57, Python 3.13.5 and solders 0.29.0.

| Check | Result | Evidence |
|---|---|---|
| Full custody harness | 195 cases; 317 measured attempts; 20 principal samples per mode/asset | [Full results](../artifacts/canonical-v1-full-results.json) |
| Inline XMSS client | 22 scenarios; 24 measured transactions including setup | [Inline results](../artifacts/canonical-v1-inline-results.json) |
| Explicit staged fallback | 22 scenarios; 112 measured transactions including setup | [Staged results](../artifacts/canonical-v1-staged-results.json) |
| Host / client tests | 37 / 16 passed | [Validation summary](../artifacts/canonical-v1-validation-summary.json) |
| Native program tests | 10 passed on program-worker commit `912537b` | [Native result and log](../artifacts/v1-native-program-test-results.json) |

## Implemented behavior

- Existing opcode 2 supports inline XMSS; opcode 3 retains sealed-stage execution.
- The client serializes signed MessageV1 envelopes and checks the full 4,096-byte
  limit, with explicit CU, loaded-account and heap configuration.
- Ten new native Rust tests pass for inline/staged parity, malformed witnesses,
  signature/replay rejection, burns and fresh/old authority behavior.
- The devnet runner persists exact authorizations and prepared envelopes,
  reconciles pending signatures, checks expected simulation errors, and verifies
  both custody debits and recipient credits.

## Evidence boundaries

Solders 0.29.0/LiteSVM ignores serialized v1 inline resource limits. Local inline
execution uses a disclosed 1.4-million-CU runtime override; it measures execution
and full transaction bytes, not network acceptance of those limits. Devnet
resource controls and retrieved confirmed transactions are separate evidence.

The earlier staged baseline passed 195 main runtime cases and 30 supplemental
runtime assertions, plus separately labeled host checks. Its results remain in
[the comparison](../research/results-summary.md); they are not new inline
measurements. Stable receiving addresses are scoped to the same program and
cluster. Ordinary upgrade/demo administration and mock mint authority remain
trusted. SLH-DSA, UI, mainnet and real USDC remain outside this delivery.

## Reproduce and continue

Use `bash scripts/infrastructure-replay.sh` with Agave 4.3.0/platform-tools 1.57.
Run `python -m client.cli --adapter svm demo-xmss` for inline v1, or add
`--xmss-transport staged` before the subcommand for the fallback. Native Rust
checks use `cargo test --locked --manifest-path program/Cargo.toml`.

Shared-cluster continuation requires the dedicated private credentials and
current journals. Keep one writer per XMSS keyset; retain exact authorized bytes
for retries. Never overwrite a newer journal, fund public deterministic vectors,
or infer safe signing progress from the onchain bitmap. No private material
belongs in the public evidence package.
