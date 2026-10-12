# Milestone M3 — Merkle-committed bearer secrets

**Status:** Partial overall — local milestone complete; public devnet deployment blocked on funding.
**Checkpoint timestamp:** 2026-10-12T14:11:53.002Z.
**Validated custody binary SHA-256:** `8d7435ea6225ef4b09e972cef7ed3d2b99f7f4e1d1b9e9f8aa5124a0848f6e25`.
**Main measured source / run:** `e3938925e3b2153592328ca56163b47d8686c314` / `validation-20261012T135652`.
**Independent validation:** Infrastructure clean export and targeted replay; cryptography separately crosschecks XMSS reference and client rotation.

## Goal and delivered behavior

Ordered, domain-separated Merkle proofs compress commitments while keeping the same deliberate bearer-secret weakness. Both assets, strict indices/proof lengths, burning and same-treasury transition are implemented.

## Experimental findings

Actual state is 390 bytes at each of 16/256/1,024 leaves, compared with array 870/8,550/33,126. The header includes a fixed 128-byte bitmap; no hidden 32-KiB array is allocated in Merkle mode. Program initialization/authority upload uses two transactions. Witness sizes are 164/292/356 bytes, including 128/256/320 sibling bytes. Copied-witness destination substitution still succeeds for both assets.

## Validation

For 256 leaves, 20 principal measurements per asset: SOL CUs 13,227/13,229/13,231 min/median/max and 933 full transaction bytes; tokens 9,638/9,640/9,642 and 1,030 bytes. Corrupt sibling, incorrect index/direction and malformed proof length are runtime-tested, with rejection stages in supplemental raw records. Independent clean replay reproduces the suite.

Reproduction: `bash scripts/infrastructure-replay.sh`; individual actual demonstrations `python3 -m client.cli --adapter svm demo-array`, `demo-merkle`, `demo-xmss`. Raw records include runtime version, binary/source hashes, complete serialized envelopes and exact error stages. Local simulation/transaction identifiers are not public confirmations.

## Public deployment details

Developer `AxQBVSbA3tEc8RsMhn3D4gPLBLnEu3XD84Zd9yy3pmnQ`; **devnet**, last balance zero, recommendation two devnet SOL. [Public manifest](../../artifacts/public-deployment.json) labels program/mint IDs as prospective and undeployed/uncreated; no receiving account or application transaction is confirmed publicly. No mainnet or real USDC is involved.

## Decisions and limitations

[Decision log](../decisions.md) and [claim limits](../../research/limitations.md). Ordinary upgrade/demo administration is trusted and excluded from the simulated attacker. Local LiteSVM v1 does not enforce inline budgets; custody uses enforced legacy ComputeBudget and XMSS staging. Five-transaction XMSS operations retain temporary rent; refunds are not implemented. Measurements are finite local experiments, not worst-case bounds or an audit.

## Artifacts

[Measured comparison](../../research/results-summary.md), [comparison source runs](../../artifacts/client-comparison-summary.json), [program supplement](../../artifacts/supplemental-program-results.json), [benchmark CSV](../../artifacts/validation-benchmark-summary.csv). [Runtime coverage](../../artifacts/acceptance-matrix.json) labels 29 bounded local IDs, one host signer-state ID and one source-inspected bypass ID.

## Next work and continuation

Local construction, storage comparison and shared-treasury transition are stable. Public confirmations await the dedicated devnet wallet's funding. No rent refund is claimed for shrinking an existing state. Restart and key-continuity rules are in [status](../status.md) and [handover](../final-research-handover.md). No unattended background execution is claimed after the session ends.

