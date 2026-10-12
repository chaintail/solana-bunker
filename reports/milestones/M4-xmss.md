# Milestone M4 — XMSS-authorized vault and findings

**Status:** Partial (preliminary checkpoint)
**Timestamp:** 2026-10-12T13:46:44.744114+00:00; sprint began2026-10-12T13:36:06.597515Z.
**Validated commit / program binary digest:** Host subset at009cc06a dirty-tree source manifest; no final validated SBF digest.
**Authoring / independent validation:** Program/crypto/client workers; validation worker; evidence consolidated by documentation worker.

## Goal and delivered behavior

Reference-compatible SVM withdrawals for both assets; authenticated burns/root rotation preserving treasury.

## Experimental findings

Reference pin and host vectors exist. Rust host agrees for six boundary indices; final index has a disclosed upstream signer control-flow fix, while the verifier reference is unchanged. Standalone LiteSVM verifier passed six valid and36invalid cases; success-case range464,546–496,643CUs. Fixture account installation bypasses witness upload and does not prove custody. Actual local-SVM client run `client-svm-20261012T135408-743edd` at source `27f76f646136a6099f0ba6d6de3598e632188ef0` passes 15 cases / 77 transactions on custody binary `8d7435ea6225ef4b09e972cef7ed3d2b99f7f4e1d1b9e9f8aa5124a0848f6e25`: both assets, exact-message rejection, authenticated leaf burn, old-root-signed fresh-root rotation, new-root withdrawal, old-root rejection, and exact retry after insufficient-balance rollback. Independent crosscheck/final main acceptance mapping remains in progress. Measurements are not filled from theoretical estimates.

## Validation

X01/burn/rotation/retry now have actual integrated client-SVM evidence; complete acceptance IDs and negative-field coverage remain pending independent replay. XMSS uses five transactions per staged logical operation; stage rent is retained and no refund is implemented. Initial host commands/evidence: `python3 tests/run_host.py`, `artifacts/test-results.json`, `artifacts/acceptance-matrix.json`.

## Public deployment

No XMSS-mode devnet deployment/confirmed transactions.

## Decisions and limitations

See [decision log](../decisions.md) and [interfaces](../interfaces.md). Ordinary development upgrade/demo administration remains trusted. Host tests do not establish Solana runtime account ownership/privileges or onchain execution.

## Artifacts

[Status](../status.md), [results summary](../../research/results-summary.md), [acceptance matrix](../../artifacts/acceptance-matrix.json), [test results](../../artifacts/test-results.json). Commands and benchmark identifiers will be finalized from real runs.

## Next work already underway

Crypto measures actual SVM compute/memory; program integrates only the active verifier; client provides durable one-writer journal and fresh root generation. Work continues without routine approval; devnet funding does not halt local verification.

