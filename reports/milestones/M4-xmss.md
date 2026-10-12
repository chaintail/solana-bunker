# Milestone M4 — XMSS-authorized vault and findings

**Status:** Partial (preliminary checkpoint)
**Timestamp:** 2026-10-12T13:46:44.744114+00:00; sprint began2026-10-12T13:36:06.597515Z.
**Validated commit / program binary digest:** Host subset at009cc06a dirty-tree source manifest; no final validated SBF digest.
**Authoring / independent validation:** Program/crypto/client workers; validation worker; evidence consolidated by documentation worker.

## Goal and delivered behavior

Reference-compatible SVM withdrawals for both assets; authenticated burns/root rotation preserving treasury.

## Experimental findings

Reference pin and host vectors exist. Rust host agrees for six boundary indices; final index has a disclosed upstream signer control-flow fix, while the verifier reference is unchanged. Standalone LiteSVM verifier passed six valid and36invalid cases; success-case range464,546–496,643CUs. Fixture account installation bypasses witness upload and does not prove custody. No integrated XMSS custody result is yet declared. Measurements are not filled from theoretical estimates.

## Validation

X01–X06/B01–B03/R01–R03/S01–S03/D01–D02 pending integrated evidence. CUs/memory/rent/operation counts null. Initial host commands/evidence: `python3 tests/run_host.py`, `artifacts/test-results.json`, `artifacts/acceptance-matrix.json`.

## Public deployment

No XMSS-mode devnet deployment/confirmed transactions.

## Decisions and limitations

See [decision log](../decisions.md) and [interfaces](../interfaces.md). Ordinary development upgrade/demo administration remains trusted. Host tests do not establish Solana runtime account ownership/privileges or onchain execution.

## Artifacts

[Status](../status.md), [results summary](../../research/results-summary.md), [acceptance matrix](../../artifacts/acceptance-matrix.json), [test results](../../artifacts/test-results.json). Commands and benchmark identifiers will be finalized from real runs.

## Next work already underway

Crypto measures actual SVM compute/memory; program integrates only the active verifier; client provides durable one-writer journal and fresh root generation. Work continues without routine approval; devnet funding does not halt local verification.

