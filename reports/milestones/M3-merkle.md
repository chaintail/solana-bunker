# Milestone M3 — Merkle-committed bearer secrets

**Status:** Partial (preliminary checkpoint)
**Timestamp:** 2026-10-12T13:46:44.744114+00:00; sprint began2026-10-12T13:36:06.597515Z.
**Validated commit / program binary digest:** Host subset at009cc06a dirty-tree source manifest; no final validated SBF digest.
**Authoring / independent validation:** Program/crypto/client workers; validation worker; evidence consolidated by documentation worker.

## Goal and delivered behavior

Compress equivalent commitment sets, measure actual account allocation, preserve bearer-secret attack.

## Experimental findings

Independent ordered-tree oracle passed 16/256/1,024-leaf boundary proof checks at host level. Program/client domain/index mismatch was identified for reconciliation before integration. Measurements are not filled from theoretical estimates.

## Validation

M01–M04 pending custody attack/storage/SVM data. Canonical proof direction derives from leaf index; sibling bytes are not account-size benchmarks. Initial host commands/evidence: `python3 tests/run_host.py`, `artifacts/test-results.json`, `artifacts/acceptance-matrix.json`.

## Public deployment

No Merkle-mode devnet deployment/confirmed transactions.

## Decisions and limitations

See [decision log](../decisions.md) and [interfaces](../interfaces.md). Ordinary development upgrade/demo administration remains trusted. Host tests do not establish Solana runtime account ownership/privileges or onchain execution.

## Artifacts

[Status](../status.md), [results summary](../../research/results-summary.md), [acceptance matrix](../../artifacts/acceptance-matrix.json), [test results](../../artifacts/test-results.json). Commands and benchmark identifiers will be finalized from real runs.

## Next work already underway

Client supplies strict Merkle proof tooling; program reconciles exact domain encoding; XMSS work proceeds independently. Work continues without routine approval; devnet funding does not halt local verification.

