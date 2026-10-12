# Milestone M1 — Foundation and experimental infrastructure

**Status:** Partial (preliminary checkpoint)
**Timestamp:** 2026-10-12T13:46:44.744114+00:00; sprint began2026-10-12T13:36:06.597515Z.
**Validated commit / program binary digest:** Host subset at009cc06a dirty-tree source manifest; no final validated SBF digest.
**Authoring / independent validation:** Program/crypto/client workers; validation worker; evidence consolidated by documentation worker.

## Goal and delivered behavior

Separate state/treasury, custody plumbing for SOL and six-decimal mock USDC.

## Experimental findings

Actual local LiteSVM custody smoke passes12cases: six principal transfers (all three modes, SOL and mock USDC) plus six replays. Each transfer moves exactly100base units. Harness initializes real state/treasury/token accounts, a six-decimal SPL mint and checked token CPI; developer/demo, mint and relayer roles are separate. Validated custody binary SHA-256 `a84a81cd97e78dd1090acaaaae22d5f103e3c258eab248ad1ef2e47f84301020`, run `validation-20261012T134723`. Extended account/privilege coverage remains underway. Measurements are not filled from theoretical estimates.

## Validation

F01/F03/F04 now have actual local-SVM initialization/asset-transfer evidence. F02/F05/F06 and complete acceptance mapping await extended harness. Raw records: `artifacts/validation-svm-results.json`, `artifacts/validation-benchmarks.jsonl`, `artifacts/validation-benchmark-summary.csv`. Initial host commands/evidence: `python3 tests/run_host.py`, `artifacts/test-results.json`, `artifacts/acceptance-matrix.json`.

## Public deployment

Program ID, state/treasury, mock mint/token account and confirmation identifiers are pending. Devnet selected; funding pending.

## Decisions and limitations

See [decision log](../decisions.md) and [interfaces](../interfaces.md). Ordinary development upgrade/demo administration remains trusted. Host tests do not establish Solana runtime account ownership/privileges or onchain execution.

## Artifacts

[Status](../status.md), [results summary](../../research/results-summary.md), [acceptance matrix](../../artifacts/acceptance-matrix.json), [test results](../../artifacts/test-results.json). Commands and benchmark identifiers will be finalized from real runs.

## Next work already underway

Program worker completes raw-SDK account/transfer paths; infrastructure finishes SBF tooling; validation prepares LiteSVM. Work continues without routine approval; devnet funding does not halt local verification.

