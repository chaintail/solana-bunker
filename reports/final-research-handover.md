# Solana Bunker — Research handover checkpoint

**Sprint start:** 2026-10-12T13:36:06.597515Z.
**Target end:** 2026-10-13T13:36:06.597515Z.
**Overall status:** Partial; local implementation and validation continue. This is a resumable checkpoint, not a declaration that the 24-hour sprint ran unattended.
**Custody smoke binary SHA-256:** `a84a81cd97e78dd1090acaaaae22d5f103e3c258eab248ad1ef2e47f84301020`.
**Standalone XMSS probe binary SHA-256:** `21088f9ef0f6add41231e5ef7b19eb8ab3272f17fc493fe104df44b612c8f700`.

## What a reviewer can run

Current command contract (clean-export verification underway):

```sh
bash scripts/infrastructure-build.sh
bash crypto/build_reference.sh
python3 crypto/generate_vectors.py
python3 tests/run_host.py
python3 tests/svm_harness.py --full --samples 20
```

Individual actual local-SVM demonstrations use `python3 tests/svm_harness.py --demo array`, `--demo merkle`, and `--demo xmss`. Host-only client demos use `python3 -m client.cli --adapter host demo-array`, `demo-merkle`, and `demo-xmss`; do not treat host narration as chain execution.

Prerequisites: Python 3.12 and requirements.txt; GCC/OpenSSL development headers; Rust host toolchain; Agave 4.3.0 cargo-build-sbf and platform-tools 1.57. Set `BUNKER_SOLANA_BIN`/`BUNKER_CARGO_BIN` to the installed binary directories when different from this sprint environment. Optional v1 probes require `npm ci`. Public devnet deployment needs the confidential development credentials and approximately 2 devnet SOL; local fixtures use disposable credits and require no public funding.

## Deliverable status

| Deliverable | Current status | Evidence |
|---|---|---|
| Separate state/treasury; both SOL and mock USDC | Local SVM smoke passed | 12 principal/replay cases, validation-20261012T134723 |
| Array-secret copied-witness attack | Under extended validation | M2 / acceptance matrix |
| Merkle attack and actual storage comparison | Under extended validation | M3 / acceptance matrix |
| Reference-compatible XMSS verifier | Standalone local SVM gate passed | 42 valid/invalid cases; E3 |
| XMSS SOL/mock-USDC withdrawals | Local SVM smoke passed | Staged witness, exact 100-base-unit transfers |
| Leaf burning and current-root rotation | Under extended validation | M4 / acceptance matrix |
| Independent raw benchmark/evidence package | Active; smoke results exist | artifacts/validation-* and crypto-* |
| Public deployment | Blocked on funding | public-deployment.json; developer balance 0 |
| Research and UI-ready narrative | Draft and contract available | research/; reports/interfaces.md |
| Optional SLH-DSA | Deferred | No implementation/performance claim |

## Results presently supported

The complete XMSS verifier executes in local LiteSVM within the requested 1.4-million-CU legacy transaction budget for the tested boundary vectors: 464,546–496,643 CUs. This standalone fixture-account test excludes upload/custody policy. Independent integrated custody smoke separately moves exactly 100 base units for both assets under all three modes and rejects replay.

The 2,029-byte official SDK v1 bytes execute locally, but LiteSVM 0.29 does not enforce inline CU/loaded-account limits in the resource-control experiment. Actual custody uses legacy explicit ComputeBudget controls and staged signature upload. No public v1 submission/retrieval or devnet application transaction is confirmed.

Ordinary program upgrade authority and explicit demo administration remain trusted and excluded from simulated relayer/funding-key disclosure. These results do not claim complete Ed25519 independence, an audit, production safety or real cryptanalytic attack.

## Public deployment manifest

[artifacts/public-deployment.json](../artifacts/public-deployment.json) distinguishes prospective program/mint public keys from deployed accounts. Developer address: `AxQBVSbA3tEc8RsMhn3D4gPLBLnEu3XD84Zd9yy3pmnQ`, cluster **devnet**. Prospective IDs are not ready receiving addresses. Mock USDC has six decimals, standard Token Program, retained test mint authority, and no freeze authority. No real USDC is used.

## Core gaps and next actions

Extended SVM cases, sample distributions, burn/rotation evidence, finalized clean replay and complete acceptance mapping are in progress. Devnet is gated by the unfunded developer wallet; a permitted faucet request returned RPC -32603. The next funded action is the existing devnet-genesis-checked deployment script. Optional SLH-DSA remains deferred while core work proceeds.

## UI and presentation handoff

[Interfaces](interfaces.md), [presentation outline](../research/presentation-outline.md), [results summary](../research/results-summary.md), and [whitepaper](../research/whitepaper.md) are the UI handoff. Show receiving-address stability, intentionally successful bearer-secret attacks, measured commitment allocation, exact-message authorization, leaf retirement and fresh-root replacement. Use actual run/event evidence; leave unmeasured quantities unknown. No UI or final slide deck is built.

## Resume instructions

The active local branch is `main`; all agents use the same repository with explicit owned paths. Read [status](status.md), [decisions](decisions.md), all early reports, milestones and acceptance matrix before continuing. The public ZIP captures committed source/evidence; a manifest explicitly labels any in-progress changes excluded from a preliminary snapshot. Reinitialize local Git if replay needs a commit identity, or preserve original checkpoint commit metadata with the resulting file hashes.

Keep the confidential continuation bundle separate from every public export. It restores development credentials, not proof of signing-state freshness. Never overwrite a newer journal with an older snapshot or reuse an uncertain signing leaf. Use fresh disposable keysets for replay; preserve the actual live journal only for any funded keyset. If continuity is unavailable, create a fresh development wallet and report its new address rather than guessing/reconstructing private keys.

