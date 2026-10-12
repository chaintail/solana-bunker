# Sprint status

Updated: 2026-10-12T13:45Z (early checkpoint; not final evidence).

Start: **2026-10-12T13:36:06.597515Z**. Target end: **2026-10-13T13:36:06.597515Z**.

## Current gate

E1 delivered: dedicated developer address `AxQBVSbA3tEc8RsMhn3D4gPLBLnEu3XD84Zd9yy3pmnQ`; selected cluster **devnet**; last measured balance **0 SOL**. Initial budget is an estimated 5 devnet SOL pending actual build/storage sizing. The permitted 2-SOL faucet request returned RPC -32603; public deployment is pending funding. This is not a blocker for local work.

Only the initial repository scaffold commit `009cc06a9f6df69dc3a9a6469eab057e8e182e6d` is presently referenced. No custody, SVM verification, public deployment or benchmark is declared complete by this checkpoint.

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

