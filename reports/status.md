Updated: 2026-10-12T14:12:51.678721+00:00

# Sprint status

**Sprint start:** 2026-10-12T13:36:06.597515Z.
**Target end:** 2026-10-13T13:36:06.597515Z.
**Current state:** Core local-SVM demonstrations complete; public deployment blocked on funding. A 24-hour target does not imply unattended execution after this runtime ends.

## Completed local evidence

| Gate | Result | Evidence |
|---|---|---|
| E1 | Fresh developer wallet; devnet; last balance 0 SOL | early/E1-wallet-environment.md, environment.json |
| E2 | Exact 2,029-byte SDK v1 transaction executes locally; public submit/read unfinished | early/E2-v1-transport.md, v1 resource controls |
| E3 | Standalone XMSS 42/42 valid/invalid cases; 120 repeated valid measurements | early/E3-xmss-feasibility.md, crypto-svm-* |
| Host tests | 37 passed | artifacts/test-results.json |
| Functional custody harness | 195/195 cases, 573 measured attempts; 20 samples for each principal mode/asset | validation-20261012T135652 |
| Client XMSS / independent review | 15 cases, 77 transactions, both assets, burn, root rotation, exact retry | client-svm-xmss-final.json, crypto-reviewed-client-xmss.json |
| Storage comparison | Actual 16/256/1,024-leaf state allocation; all three modes on same treasury | validation-svm-results.json, client-comparison-summary.json |
| Clean source build/replay | Both SBF digests; 37 host + 195 main + 15 program + 15 intent SVM assertions independently reproduced, plus one intent host check | clean-build-origin.json, clean-reproduction-summary.json |

Final custody program: 124,464 bytes, SHA-256 `8d7435ea6225ef4b09e972cef7ed3d2b99f7f4e1d1b9e9f8aa5124a0848f6e25`.
Standalone XMSS probe: 33,864 bytes, SHA-256 `21088f9ef0f6add41231e5ef7b19eb8ab3272f17fc493fe104df44b612c8f700`.

## Remaining limitations and dependency

Developer address `AxQBVSbA3tEc8RsMhn3D4gPLBLnEu3XD84Zd9yy3pmnQ`, **devnet**, remains unfunded. Recommend 2 devnet SOL (about 1.3 SOL estimated peak deployment/fixture rent). No program/mint creation or application transaction is publicly confirmed. Funding affects public deployment only.

All 31 acceptance IDs have bounded evidence: 29 local-runtime IDs, S03 host-tested, D02 source-inspected. Program and intent supplements add 15 runtime assertions each, independently reproduced without Git/private credentials; intent also has one separately labeled host RFC mint-binding check. Sealed-stage write mutation and same-authority rotation rejection now have actual runtime cases. Cheap account/policy rejection and deep signature-verifier failures remain distinct. See the matrix and clean-reproduction-summary.json.

Local LiteSVM 0.29 does not enforce v1 inline resource limits. Custody measurements use enforced legacy ComputeBudget instructions and five-transaction XMSS staging. Temporary stage rent is retained; refunds are not implemented. Ordinary upgrade/demo administration remains trusted. SLH-DSA and final UI remain deferred.

## Execution and restart

The parent only coordinates. Workers own infrastructure/integration, program, cryptography, client, validation and documentation. The original validator worker stopped after runtime capability failures; infrastructure completed an independent replay and honest acceptance mapping, with a separate crypto crosscheck. All execution/source writers are frozen; final documentation and checkpoint packaging are complete.

Active local branch: `main`. Read README.md, decisions.md, interfaces.md, all early/milestone reports and final-research-handover.md. Reproduce with `bash scripts/infrastructure-replay.sh`; use fresh local disposable keysets. Do not treat a source review as a runtime test or a local transaction identifier as public confirmation.

The public checkpoint captures committed source/evidence, with a commit/file-digest manifest. Preserve the separate confidential continuation bundle privately to recover the development credentials. Never restore an old journal over a newer one or infer signer progress from unused chain leaves. If signing state is uncertain, retire/abandon affected leaves or install a fresh tree. If developer credentials are unavailable, generate a new dedicated wallet and report its address before funding.
