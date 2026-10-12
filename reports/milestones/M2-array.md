# Milestone M2 — Naive SHA-256 secret-array vault

**Status:** Partial (preliminary checkpoint)
**Timestamp:** 2026-10-12T13:46:44.744114+00:00; sprint began2026-10-12T13:36:06.597515Z.
**Validated commit / program binary digest:** Host subset at009cc06a dirty-tree source manifest; no final validated SBF digest.
**Authoring / independent validation:** Program/crypto/client workers; validation worker; evidence consolidated by documentation worker.

## Goal and delivered behavior

Both assets authorized by consumed slots, with deliberately reproducible copied-secret substitution.

## Experimental findings

Actual local-SVM copied-witness destination substitution succeeds for SOL and mock USDC, as intended. Legitimate withdrawals and consumed-witness replay rejection also pass. Source binary SHA-256 `8d7435ea6225ef4b09e972cef7ed3d2b99f7f4e1d1b9e9f8aa5124a0848f6e25`; partial extended run `validation-20261012T135046`, and independent runnable array client run `client-svm-20261012T135221-e45bf8` (7 cases, 9 transactions). Measurements are not filled from theoretical estimates.

## Validation

A01/A03/A04 have actual local-SVM evidence for both assets. The main full-coverage run was interrupted and is being independently replayed; complete acceptance mapping and storage comparison remain pending. Principal 256-leaf array cases currently have 20 measured attempts per asset in the partial dataset; quote only their exact run/binary group. Initial host commands/evidence: `python3 tests/run_host.py`, `artifacts/test-results.json`, `artifacts/acceptance-matrix.json`.

## Public deployment

No array-mode devnet deployment/confirmed transactions.

## Decisions and limitations

See [decision log](../decisions.md) and [interfaces](../interfaces.md). Ordinary development upgrade/demo administration remains trusted. Host tests do not establish Solana runtime account ownership/privileges or onchain execution.

## Artifacts

[Status](../status.md), [results summary](../../research/results-summary.md), [acceptance matrix](../../artifacts/acceptance-matrix.json), [test results](../../artifacts/test-results.json). Commands and benchmark identifiers will be finalized from real runs.

## Next work already underway

Program and client implement matching commitments; validator prepares isolated owner/attacker ordering. Work continues without routine approval; devnet funding does not halt local verification.

