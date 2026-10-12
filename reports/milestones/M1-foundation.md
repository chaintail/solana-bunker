# Milestone M1 — Foundation and experimental infrastructure

**Status:** Partial (preliminary checkpoint)
**Timestamp:** 2026-10-12T13:50Z; sprint began2026-10-12T13:36:06.597515Z.
**Validated commit / program binary digest:** Host subset at009cc06a dirty-tree source manifest; no final validated SBF digest.
**Authoring / independent validation:** Program/crypto/client workers; validation worker; evidence consolidated by documentation worker.

## Goal and delivered behavior

Separate state/treasury, custody plumbing for SOL and six-decimal mock USDC.

## Experimental findings

Contract specifies stable PDA seeds, modes/actions and canonical intent. Independent host encoder/Merkle/schema checks pass 17/17. No SVM custody transfer or mock mint is yet validated. Measurements are not filled from theoretical estimates.

## Validation

F01–F06 pending actual program harness. Initial host commands/evidence: `python3 tests/run_host.py`, `artifacts/test-results.json`, `artifacts/acceptance-matrix.json`.

## Public deployment

Program ID, state/treasury, mock mint/token account and confirmation identifiers are pending. Devnet selected; funding pending.

## Decisions and limitations

See [decision log](../decisions.md) and [interfaces](../interfaces.md). Ordinary development upgrade/demo administration remains trusted. Host tests do not establish Solana runtime account ownership/privileges or onchain execution.

## Artifacts

[Status](../status.md), [results summary](../../research/results-summary.md), [acceptance matrix](../../artifacts/acceptance-matrix.json), [test results](../../artifacts/test-results.json). Commands and benchmark identifiers will be finalized from real runs.

## Next work already underway

Program worker completes raw-SDK account/transfer paths; infrastructure finishes SBF tooling; validation prepares LiteSVM. Work continues without routine approval; devnet funding does not halt local verification.

