# Milestone M1 — Foundation and experimental infrastructure

**Status:** Partial overall — local milestone complete; public devnet deployment blocked on funding.
**Checkpoint timestamp:** 2026-10-12T14:11:53.002Z.
**Validated custody binary SHA-256:** `8d7435ea6225ef4b09e972cef7ed3d2b99f7f4e1d1b9e9f8aa5124a0848f6e25`.
**Main measured source / run:** `e3938925e3b2153592328ca56163b47d8686c314` / `validation-20261012T135652`.
**Independent validation:** Infrastructure clean export and targeted replay; cryptography separately crosschecks XMSS reference and client rotation.

## Goal and delivered behavior

Separate state and treasury PDAs initialize with real runtime ownership and stable association. Native SOL and six-decimal mock-USDC SPL transfers both work; checked token CPI enforces the signed source/mint/destination. No temporary withdrawal bypass remains.

## Experimental findings

Actual initialization/deposit/withdrawal round trips and exact 100-base-unit transfers pass for both assets. Duplicate initialization, account substitutions, missing setup/admin privileges, readonly token source and disallowed aliases are independently runtime-tested in the final supplements. Canonical seeds exclude roots and modes; trusted same-vault transitions preserve receiving addresses and balances.

## Validation

Main functional harness: 195 cases / 573 measured attempts. Program supplement: 15 SVM cases, 19 measured attempts / 29 raw transactions including fixtures; independently replayed without Git/private credentials. These finite tests are not a security audit. Host suite has 37 passing cases.

Reproduction: `bash scripts/infrastructure-replay.sh`; individual actual demonstrations `python3 -m client.cli --adapter svm demo-array`, `demo-merkle`, `demo-xmss`. Raw records include runtime version, binary/source hashes, complete serialized envelopes and exact error stages. Local simulation/transaction identifiers are not public confirmations.

## Public deployment details

Developer `AxQBVSbA3tEc8RsMhn3D4gPLBLnEu3XD84Zd9yy3pmnQ`; **devnet**, last balance zero, recommendation two devnet SOL. [Public manifest](../../artifacts/public-deployment.json) labels program/mint IDs as prospective and undeployed/uncreated; no receiving account or application transaction is confirmed publicly. No mainnet or real USDC is involved.

## Decisions and limitations

[Decision log](../decisions.md) and [claim limits](../../research/limitations.md). Ordinary upgrade/demo administration is trusted and excluded from the simulated attacker. Local LiteSVM v1 does not enforce inline budgets; custody uses enforced legacy ComputeBudget and XMSS staging. Five-transaction XMSS operations retain temporary rent; refunds are not implemented. Measurements are finite local experiments, not worst-case bounds or an audit.

## Artifacts

[Main results](../../artifacts/validation-svm-results.json), [program supplement](../../artifacts/supplemental-program-results.json), [clean replay](../../artifacts/clean-reproduction-summary.json), [interfaces](../interfaces.md). [Runtime coverage](../../artifacts/acceptance-matrix.json) labels 29 bounded local IDs, one host signer-state ID and one source-inspected bypass ID.

## Next work and continuation

Public devnet deployment and mint creation are the only external gate. Source and local evidence are frozen. After funding, infrastructure runs the existing devnet-genesis-checked deployment and confirms actual application examples. Restart and key-continuity rules are in [status](../status.md) and [handover](../final-research-handover.md). No unattended background execution is claimed after the session ends.

