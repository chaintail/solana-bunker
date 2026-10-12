# Solana Bunker — Final research handover

**Sprint start:** 2026-10-12T13:36:06.597515Z.
**Target end:** 2026-10-13T13:36:06.597515Z.
**Final checkpoint:** 2026-10-12T14:12:51.678827+00:00.
**Overall status:** Partial — core local demonstrations work; devnet deployment is blocked on funding. This is the current session checkpoint, not a claim of unattended work through the 24-hour target.
**Custody binary:** 124,464 bytes, SHA-256 `8d7435ea6225ef4b09e972cef7ed3d2b99f7f4e1d1b9e9f8aa5124a0848f6e25`.
**Standalone XMSS binary:** 33,864 bytes, SHA-256 `21088f9ef0f6add41231e5ef7b19eb8ab3272f17fc493fe104df44b612c8f700`.

## What a reviewer can run

Install Python 3.12 and requirements.txt, GCC/OpenSSL development headers, Rust, and Agave 4.3.0 cargo-build-sbf/platform-tools 1.57. Configure `BUNKER_SOLANA_BIN`/`BUNKER_CARGO_BIN` if needed. Dependency locks and source licenses are included.

```sh
bash scripts/infrastructure-replay.sh
```

This builds, regenerates explicitly disposable reference vectors, runs host tests and replays the full actual local-SVM harness with 20 principal samples. No public funding or live developer credentials are required.

Individual actual local-SVM commands:

```sh
python3 -m client.cli --adapter svm demo-array
python3 -m client.cli --adapter svm demo-merkle
python3 -m client.cli --adapter svm demo-xmss
python3 -m client.cli --adapter svm benchmark --samples 20
```

Small 16-leaf benchmark fixtures use five samples per asset to leave leaves for attack/burn cases. Host-only commands explicitly select `--adapter host` and produce `host_reference` events. Do not conflate those with the SVM adapter.

[Clean reproduction](../artifacts/clean-reproduction-summary.json) independently runs the exported source without Git history or private credentials: 37 host tests, 195 SVM cases, 573 measured attempts, same custody digest. Its source archive is `10a96e861e087488753a43849415cbea0b1ad02b`; runtime identity `source_snapshot:65a218da0390302dc650912918306fe081f55d58b85ecefc323b9022b1e612c4` is a file snapshot hash, not a Git commit.

## Deliverable status

| Deliverable | Status | Evidence |
|---|---|---|
| Separate state/treasury; SOL and six-decimal mock USDC | Complete locally | Main SVM initialization/transfer cases |
| Array-secret demo and copied-witness attack | Complete locally | Both assets, consumed/replay rejection |
| Merkle-secret demo and allocated-storage comparison | Complete locally | 16/256/1,024 leaves; same bearer attack |
| Reference-compatible SVM XMSS verification | Complete locally | Pinned reference vectors, 42 valid/invalid probe cases |
| XMSS SOL/mock-USDC withdrawals | Complete locally | 20 principal samples per asset; sealed staging |
| Leaf burning | Complete locally | Exact targets plus authorizing leaf consumed; bounds/mutations rejected |
| Current-root-authorized fresh-root rotation | Complete locally | Same receiving accounts/balances; new root passes, old root fails |
| Independent tests and raw benchmarks | Complete for bounded local scope; independently replayed | Main195 + program15 + intent15 SVM cases; intent also has one host-only cryptographic case |
| Public deployment and mint | Blocked on devnet funding | public-deployment.json: zero balance, no confirmed transactions |
| Research and UI-ready evidence | Complete | Whitepaper, results, sources, contract and runtime event feeds |
| Optional SLH-DSA | Deferred | No implementation/performance claim |

## Results that can be quoted

- The main functional run `validation-20261012T135652` passes 195/195 cases across 573 measured attempts. Each principal mode/asset case has 20 samples. It is independently reproduced from a clean export (`validation-20261012T140013`).
- For 1,024 leaves, actual array state is 33,126 bytes versus 390 bytes for Merkle state. Program initialization/authority upload requires 38 versus two transactions. Both primitive modes still accept the scripted copied-witness destination substitution for both assets.
- XMSS authorizes exact withdrawals, leaf retirement and a fresh-root replacement while preserving receiving accounts/balances. Its tested final-execution medians are 522,160 CUs SOL / 531,758 tokens; total staged-operation medians are 534,351 / 539,497. A logical withdrawal uses five transactions, 30,000 observed fee lamports and 19,160,880 retained stage-rent lamports. These are measured local values, not worst-case guarantees.
- Ordinary program upgrade authority and explicit demo administration remain trusted and outside simulated relayer/funding-key disclosure. No whole-system Ed25519 independence, production audit, real cryptanalytic break or first-ever-vault claim applies.

Full raw evidence and calculation grouping: [results summary](../research/results-summary.md), [benchmark JSONL](../artifacts/validation-benchmarks.jsonl), [CSV](../artifacts/validation-benchmark-summary.csv), and per-attempt runtime logs.

## Public account and deployment manifest

Developer public address: `AxQBVSbA3tEc8RsMhn3D4gPLBLnEu3XD84Zd9yy3pmnQ`.
Cluster: **devnet**. Recommended funding: **2 devnet SOL**, against approximately 1.3 SOL peak deployment/fixture rent. Initial five-SOL estimate was provisional.

[Public manifest](../artifacts/public-deployment.json) records prospective program `6pPoFS9m3ghJzz7pcebmyDY7mnPc1zmnNvGXsBD5Na2k` and mint `5NPuFsUuus2V67HwAB3z3S7AbpqgypaYAPpqmprckM9F` as **not deployed / not created**. They are not ready receiving addresses. Mock USDC uses standard Token Program, six decimals, retained test mint authority and no freeze authority.

After funding, run `python3 scripts/infrastructure-devnet-deploy.py` with confidential development credentials; it checks devnet genesis and funding. Then execute confirmed application examples and record actual accounts/transaction identifiers. Local fixtures must never be funded on a shared network.

## Deviations, blockers and remaining work

Public deployment, confirmed devnet demonstrations and v1 submit/read await funding. The faucet returned an RPC error; local work continued. Local-validator startup is unavailable because io_uring is unsupported; LiteSVM supplies actual SBF runtime execution.

The local LiteSVM v1 parser executes oversized bytes but does not enforce inline compute/loaded limits. Application measurements therefore use verified legacy ComputeBudget and sealed staging. Temporary stage accounts and excess state rent after shrinking are retained; no refund is claimed.

The acceptance matrix distinguishes actual runtime policy rejection, signature-verifier rejection, host-only cryptographic checks and source inspection. Targeted supplemental records close previously missing variants. Both are independently replayed without Git/private credentials: program15 runtime cases, intent15 runtime plus one separate host cryptographic case, yielding225 actual runtime assertions across main/supplement groups. [Clean replay metadata](../artifacts/clean-reproduction-summary.json) pins the exact committed scripts, snapshot identities and unchanged binary. No source guard is promoted to a runtime result. The final-index reference signer patch is disclosed and accepted by the unchanged verifier.

Production recovery, protected upgrade governance, multidevice signing, final UI/slides and SLH-DSA remain outside this completed local scope.

## UI and presentation handoff

[Interfaces](interfaces.md), [presentation outline](../research/presentation-outline.md), [whitepaper](../research/whitepaper.md), [client comparison](../artifacts/client-comparison-summary.json) and [final XMSS runtime events](../artifacts/client-svm-xmss-final.json) provide the handoff. Events contain public identities, epochs/nonces, message commitments, bytes/CUs, balances and raw evidence links, with an explicit local/network evidence label.

Show the same receiving address across modes/roots, expected bearer-secret attacker success, actual storage/setup costs, rejected XMSS effect substitutions, burned leaves and fresh-root rotation. Do not publish unused secrets, seed material or signer journals.

## Resume instructions

Active branch: `main`. The parent coordinates and workers execute. All source/execution writers are frozen; the final source/evidence archive is ready for continued funded devnet work. Read status.md, decisions.md, interfaces.md, all early/milestone reports and the acceptance matrix. The public checkpoint manifest pins its final source commit and file digests.

Public source/evidence and confidential continuation are separate. Restore development credentials only privately with restrictive permissions. Never restore an older signer journal over a newer one, infer signing progress from the chain bitmap, or reuse an uncertain leaf. Use fresh disposable local keysets for reproduction; use a fresh root if live signing continuity is uncertain.

If credentials cannot be recovered, generate a new dedicated developer wallet and report its public address before funding. Do not reuse the attached input handoff as an output identity. No publication, entry submission, mainnet or real-USDC action is included.

