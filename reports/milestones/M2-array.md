# Milestone M2 — Naive SHA-256 secret-array vault

**Status:** Partial overall — local milestone complete; public devnet deployment blocked on funding.
**Checkpoint timestamp:** 2026-10-12T14:11:53.002Z.
**Validated custody binary SHA-256:** `8d7435ea6225ef4b09e972cef7ed3d2b99f7f4e1d1b9e9f8aa5124a0848f6e25`.
**Main measured source / run:** `e3938925e3b2153592328ca56163b47d8686c314` / `validation-20261012T135652`.
**Independent validation:** Infrastructure clean export and targeted replay; cryptography separately crosschecks XMSS reference and client rotation.

## Goal and delivered behavior

The commitment array accepts an unused one-time secret for both assets, consumes its leaf and advances nonce atomically. The experiment intentionally leaves the revealed secret unbound to the requested destination.

## Experimental findings

A copied pending witness with substituted destination succeeds for both assets under scripted first-included ordering; no administrator or seed privilege is used. Incorrect, out-of-range, consumed and replayed slots reject. Actual state allocation for 16/256/1,024 leaves is 870/8,550/33,126 bytes; program initialization/authority upload takes 2/11/38 transactions.

## Validation

Principal 256-leaf withdrawals have 20 local measurements per asset: 7,101 CUs / 677 transaction bytes SOL, 8,012 CUs / 774 bytes tokens. Each is one transaction with 5,000 observed fee lamports. Array range/privilege variants are covered by the independently repeated program supplement. Expected attacker success is a passing experiment.

Reproduction: `bash scripts/infrastructure-replay.sh`; individual actual demonstrations `python3 -m client.cli --adapter svm demo-array`, `demo-merkle`, `demo-xmss`. Raw records include runtime version, binary/source hashes, complete serialized envelopes and exact error stages. Local simulation/transaction identifiers are not public confirmations.

## Public deployment details

Developer `AxQBVSbA3tEc8RsMhn3D4gPLBLnEu3XD84Zd9yy3pmnQ`; **devnet**, last balance zero, recommendation two devnet SOL. [Public manifest](../../artifacts/public-deployment.json) labels program/mint IDs as prospective and undeployed/uncreated; no receiving account or application transaction is confirmed publicly. No mainnet or real USDC is involved.

## Decisions and limitations

[Decision log](../decisions.md) and [claim limits](../../research/limitations.md). Ordinary upgrade/demo administration is trusted and excluded from the simulated attacker. Local LiteSVM v1 does not enforce inline budgets; custody uses enforced legacy ComputeBudget and XMSS staging. Five-transaction XMSS operations retain temporary rent; refunds are not implemented. Measurements are finite local experiments, not worst-case bounds or an audit.

## Artifacts

[Raw benchmarks](../../artifacts/validation-benchmarks.jsonl), [comparison summary](../../artifacts/client-comparison-summary.json), [array runtime demo](../../artifacts/client-svm-array-smoke.json), [acceptance matrix](../../artifacts/acceptance-matrix.json). [Runtime coverage](../../artifacts/acceptance-matrix.json) labels 29 bounded local IDs, one host signer-state ID and one source-inspected bypass ID.

## Next work and continuation

Array behavior and local cost baseline are stable. Confirm devnet examples after public funding; do not spend further sprint time fixing the intentionally exposed bearer-secret construction. Restart and key-continuity rules are in [status](../status.md) and [handover](../final-research-handover.md). No unattended background execution is claimed after the session ends.

