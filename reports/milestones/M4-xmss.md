# Milestone M4 — XMSS-authorized vault and final findings

**Status:** Partial overall — local milestone complete; public devnet deployment blocked on funding.
**Checkpoint timestamp:** 2026-10-12T14:11:53.002Z.
**Validated custody binary SHA-256:** `8d7435ea6225ef4b09e972cef7ed3d2b99f7f4e1d1b9e9f8aa5124a0848f6e25`.
**Main measured source / run:** `e3938925e3b2153592328ca56163b47d8686c314` / `validation-20261012T135652`.
**Independent validation:** Infrastructure clean export and targeted replay; cryptography separately crosschecks XMSS reference and client rotation.

## Goal and delivered behavior

Complete reference-compatible XMSS-SHA2_10_256 signs exact canonical actions for both assets, bounded burns and current-root-authorized fresh-root rotation. Durable one-writer journal reservation and exact retry prevent normal client leaf reuse.

## Experimental findings

Both asset transfers, burn targets plus authorizing leaf consumption, fresh-root rotation, unchanged receiving accounts/balances, new-root withdrawals and unused old-root rejection pass in actual SVM. Destination/amount/action/root/burn mutations, nonce/epoch/vault/program/namespace mismatches, missing hash authorization and inactive verifier reject. Sealed-stage overwrite/reseal/different-intent attempts reject; original sealed authorization executes. Same-current-authority rotation rejects. Cheap policy rejections and reached-verifier failures remain explicitly distinct.

## Validation

Main195 cases plus program15 and intent15 runtime cases give 225 SVM assertions across separate groups; all are independently reproduced. Intent supplement also has one separately labeled host-only full-RFC mint-binding check, while runtime mint mutation rejects at exact account policy. Host suite37 and source inspection are not counted as SVM cases. Standalone verifier42 valid/invalid cases plus120 repeated valid measurements are a separate group. Independent client XMSS review passes15 cases /77 transactions. Final-index reference signer patch is disclosed; unchanged reference verifier accepts it.

Reproduction: `bash scripts/infrastructure-replay.sh`; individual actual demonstrations `python3 -m client.cli --adapter svm demo-array`, `demo-merkle`, `demo-xmss`. Raw records include runtime version, binary/source hashes, complete serialized envelopes and exact error stages. Local simulation/transaction identifiers are not public confirmations.

## Public deployment details

Developer `AxQBVSbA3tEc8RsMhn3D4gPLBLnEu3XD84Zd9yy3pmnQ`; **devnet**, last balance zero, recommendation two devnet SOL. [Public manifest](../../artifacts/public-deployment.json) labels program/mint IDs as prospective and undeployed/uncreated; no receiving account or application transaction is confirmed publicly. No mainnet or real USDC is involved.

## Decisions and limitations

[Decision log](../decisions.md) and [claim limits](../../research/limitations.md). Ordinary upgrade/demo administration is trusted and excluded from the simulated attacker. Local LiteSVM v1 does not enforce inline budgets; custody uses enforced legacy ComputeBudget and XMSS staging. Five-transaction XMSS operations retain temporary rent; refunds are not implemented. Measurements are finite local experiments, not worst-case bounds or an audit.

## Artifacts

[Final handover](../final-research-handover.md), [XMSS early gate](../early/E3-xmss-feasibility.md), [intent supplement](../../artifacts/supplemental-intent-results.json), [independent client review](../../artifacts/crypto-reviewed-client-xmss.json), [clean replay](../../artifacts/clean-reproduction-summary.json). [Runtime coverage](../../artifacts/acceptance-matrix.json) labels 29 bounded local IDs, one host signer-state ID and one source-inspected bypass ID.

## Next work and continuation

Core local behavior is complete and frozen. Public deployment/confirmed examples require devnet funding. SLH-DSA, production recovery/governance and the final UI remain deferred; no further feature work is pending. Restart and key-continuity rules are in [status](../status.md) and [handover](../final-research-handover.md). No unattended background execution is claimed after the session ends.

