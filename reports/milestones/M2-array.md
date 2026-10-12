# Milestone M2 — Naive SHA-256 secret-array vault

**Status:** Partial (preliminary checkpoint)
**Timestamp:** 2026-10-12T13:50Z; sprint began2026-10-12T13:36:06.597515Z.
**Validated commit / program binary digest:** Host subset at009cc06a dirty-tree source manifest; no final validated SBF digest.
**Authoring / independent validation:** Program/crypto/client workers; validation worker; evidence consolidated by documentation worker.

## Goal and delivered behavior

Both assets authorized by consumed slots, with deliberately reproducible copied-secret substitution.

## Experimental findings

Host model/client and attack fixtures are under construction. No copied-secret transfer result is declared at this checkpoint. Measurements are not filled from theoretical estimates.

## Validation

A01–A04 pending independent model/SVM evidence; account allocation/setup/CUs null. Initial host commands/evidence: `python3 tests/run_host.py`, `artifacts/test-results.json`, `artifacts/acceptance-matrix.json`.

## Public deployment

No array-mode devnet deployment/confirmed transactions.

## Decisions and limitations

See [decision log](../decisions.md) and [interfaces](../interfaces.md). Ordinary development upgrade/demo administration remains trusted. Host tests do not establish Solana runtime account ownership/privileges or onchain execution.

## Artifacts

[Status](../status.md), [results summary](../../research/results-summary.md), [acceptance matrix](../../artifacts/acceptance-matrix.json), [test results](../../artifacts/test-results.json). Commands and benchmark identifiers will be finalized from real runs.

## Next work already underway

Program and client implement matching commitments; validator prepares isolated owner/attacker ordering. Work continues without routine approval; devnet funding does not halt local verification.

