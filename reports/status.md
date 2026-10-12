# Sprint status

Updated: 2026-10-12T13:46:44.744114+00:00 (early checkpoint; not final evidence).

Start: **2026-10-12T13:36:06.597515Z**. Target end: **2026-10-13T13:36:06.597515Z**.

## Current gate

E1 delivered: dedicated developer address `AxQBVSbA3tEc8RsMhn3D4gPLBLnEu3XD84Zd9yy3pmnQ`; selected cluster **devnet**; last measured balance **0 SOL**. Current recommendation is **2 devnet SOL**, based on122,848-byte program and about1.3SOL estimated peak deployment/fixture rent; initial5SOL was provisional. The permitted 2-SOL faucet request returned RPC -32603; public deployment is pending funding. This is not a blocker for local work.

Initial validation reports 17/17 host contract/schema tests passed at scaffold commit `009cc06a9f6df69dc3a9a6469eab057e8e182e6d` with a dirty-tree SHA-256 file manifest. Canonical encoded lengths are 230 bytes SOL, 327 bytes token, 203 bytes three-target burn and 259 bytes rotation. These results validate host encodings/oracles, not custody execution. All 31 core acceptance IDs still require integration evidence. No integrated custody or public deployment is declared complete by this checkpoint.

E2 is partial: @solana/kit 8.4.0 produced a 2,029-byte v1 transaction and decoded it locally. The exact SDK bytes executed the Memo program in local LiteSVM at 2,056 CUs, with local fee-payer credit and blockhash checks disabled. Devnet RPC 4.4.0-beta.0 reached simulation, which failed `AccountNotFound` for the unfunded payer; submission returned -32002. The locally derived signature is not a confirmed transaction, and public submit/read is unfinished. Raw records: `artifacts/v1-probe-result.json`, `artifacts/v1-sdk-local-result.json`.

E3 standalone verifier gate: six valid and 36 invalid cases passed in actual local LiteSVM. Reported success-case range is 464,546–496,643 CUs; raw binary SHA-256 is `21088f9ef0f6add41231e5ef7b19eb8ab3272f17fc493fe104df44b612c8f700`. The fixture account is installed directly by the harness: this proves verifier execution, not witness upload, custody, epoch/nonce enforcement or public deployment. Raw record: `artifacts/crypto-svm-probe.json`. Final-index reference signer patch is disclosed; verifier reference is unchanged.

## Workers and ownership

| Worker | Active responsibility | Owned paths |
|---|---|---|
| Infrastructure/integration | Toolchain, E1/E2, shared deployments, integration | setup/deployment scripts, early E1/E2, environment metadata |
| Program/custody | Account model, both assets, selected authorization modes | programs/ |
| Cryptography | Pinned XMSS reference, host vectors, actual SVM verification and E3 | crypto/, early E3 |
| Client | Canonical intent, Merkle proofs, signer journal, CLI and event contract | client/, interfaces |
| Validation | Independent adversarial cases, raw results and benchmark checking | tests/, validation artifacts |
| Documentation | Checkpoints, research, final public package and confidential continuation | reports/status, decisions, milestones, research/, README |

## Dependencies and continuation

Rust/toolchain installation and SDK selection proceed alongside host XMSS research and speculative client/program work. XMSS reference is pinned to `171ccbd26f098542a67eb5d2b128281c80bd71a6`. E2 requires actual submit/read evidence; E3 requires actual SVM execution. Funding affects devnet deployment only. Mode/canonical-intent contracts must agree before final integration. Local tests and eventual public transactions are separate evidence groups.

## Restart rules

Read this file, reports/decisions.md, reports/interfaces.md when available, and the latest early/milestone reports. Resume only from actual evidence; don't treat planned commands as passing runs. Preserve one writer per XMSS keyset, never reuse an uncertain leaf, and never infer signer progress from the onchain bitmap alone. The public source package excludes private credentials and signing journals; the separate confidential continuity artifact is required to resume a previously funded developer wallet. If it is unavailable, generate a fresh dedicated development wallet and report the new address before funding. No unattended work is implied after this runtime ends.


Actual integrated custody smoke: local LiteSVM12cases pass all3modes/bothassets exact100base-unit transfers plus replay rejection, custody binary a84a81cd97e78dd1090acaaaae22d5f103e3c258eab248ad1ef2e47f84301020. Extended copied-witness/account/burn/rotation scenarios are already running.
