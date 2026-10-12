# Execution plan — Four milestones, three early updates

## 1. Coordinator mandate

Run the project as overlapping workstreams, not a serial checklist. The milestone order tells the research story; it is not a barrier preventing later work from starting.

The parent dispatches and coordinates. Subagents do all implementation, research, tests, merges, deployments, and report writing. The parent can relay their brief findings to the user. Use native delegation and isolated worktrees where supported; verify actual environment capabilities instead of assuming them. [S17, S18]

Assign these responsibilities immediately, subject to actual concurrency limits:

| Workstream | Initial responsibility | Subsequent responsibility |
|---|---|---|
| Infrastructure/integration | Repo inspection, developer wallet, toolchain, cluster, v1 probe | Shared deployments, mock mint, merges, reproducible commands |
| Program/custody | State and treasury interfaces, SOL/token plumbing | Array mode, shared actions, XMSS integration |
| Cryptography | Reference selection, known-answer checks, SVM verifier | Profiling, exact XMSS signing, optional stateless spike |
| Client/Merkle | Intent encoding, secrets, proof builders, CLI interfaces | Merkle mode, signer journal, root rotation client |
| Independent validation | Test matrix and fixtures before implementation | Attack tests, differential checks, benchmark verification |

Delegate report drafting and evidence consolidation to an available worker; create a separate documentation worker if capacity permits. Do not let one overloaded integration worker delay crypto or testing. Workers may change assignments after a handoff.

### Shared-interface checkpoint: first 30–45 minutes

Have workers agree on PDA seeds, account/mode identifiers, intent encoding, verifier input/output contract, public fixture format, and benchmark record shape. Write a short interface document and decision log. Do not design production recovery. Start independent crypto research immediately while this interface is being agreed.

Give every delegated task a goal, worktree/branch, owned files, interface assumptions, acceptance tests, expected artifacts, and next handoff. When a worker is waiting for a build, give it another independent task or use another worker. Speculative downstream code is allowed, but cannot be declared validated before its dependencies are checked.

## 2. Clock and priority

Record `T0` and `T0 + 24h`. These are provisional scheduling targets, not guarantees:

- **T+0–2h:** environment/public-key update; interface agreement; transport probe; host XMSS vectors; parallel scaffolding.
- **T+2–6h:** foundation and array demonstration; Merkle tooling; SVM XMSS feasibility findings.
- **T+6–16h:** complete Merkle comparison and integrate XMSS for both assets; validation runs continuously.
- **T+16–20h:** leaf burning, root rotation, adversarial verification, reproducible deployed demos.
- **Final ~4h:** stop adding features; stabilize, rerun final evidence, write findings, and package UI/presentation handover.

Reallocate based on measured blockers. XMSS has highest technical priority. Do not spend most of the sprint polishing naive demos. SLH-DSA requires stable core results and real remaining time; disable it at the integration cutoff.

If all deliverables finish early, conclude with the final package. If the execution environment interrupts the sprint, persist restart instructions rather than pretending work continues.

## 3. Three early updates — notify, then continue

### E1 — Developer wallet and environment

**Immediate goal:** Give the user the address they need to fund while the rest of the work proceeds.

Infrastructure worker:

- Inspect the intended repository/tooling without changing unrelated projects. Preserve existing files and instructions. If no project exists, scaffold a dedicated local `solana-bunker` project.
- Generate a **fresh dedicated developer keypair** outside version control with restrictive file permissions. Report only its public address. Never print a mnemonic/private key, including through command stdout.
- Default to **devnet** for public application testing, with local validators/SVM harnesses for speed. Make the RPC configurable and verify the selected cluster; devnet and testnet are different networks. [S19]
- Report public address, cluster, balance, and estimated test-SOL need based on build/deployment/storage costs. A permitted faucet may be used; otherwise request funding and keep working locally.
- Verify native subagents, compilers, dependency access, local test facilities, and deployment permissions. Record versions and missing capabilities.

**Deliver:** `reports/early/E1-wallet-environment.md` and public environment metadata. No private paths in public exports that expose secret contents; local secret-file paths may be documented in a private runbook.

**Pass:** A recoverable local developer key exists, its public address and cluster have been reported, and useful local work is running. Deployment funding is not a global approval gate.

### E2 — v1 transport verification

**Goal:** Separate client/RPC compatibility from cryptographic feasibility.

Build a harmless transaction with serialized size greater than 1,232 and no more than 4,096 bytes. Use actual v1 tooling, configure resources, submit on the selected development cluster when available, and retrieve/decode the transaction. A lightweight probe program is preferable to assuming an arbitrary builtin accepts large data. [S08, S09]

**Deliver:** SDK/runtime versions, serialized byte length, resource settings, cluster, submission/retrieval outcome, transaction identifier, and exact failure stage if blocked. Record local-only success separately from network confirmation.

**Continue:** If the path fails, investigate a bounded tooling fix and prepare the staged-data fallback. Do not wait for this result before building a host verifier or ordinary small transactions.

### E3 — XMSS feasibility gate

**Goal:** Obtain a real SVM result before committing to the full custody integration.

Pin a reference implementation. Produce reference-compatible signatures and negative vectors, verify offchain, then compile/run the verifier in the SVM. Measure actual compute and memory constraints, not only native CPU time. Target the parameter set in the crypto notes.

**Deliver:** implementation and reference commits/licenses, signature/public-key encodings, host comparison results, SVM valid/invalid results, serialized size, compute consumed, and transport/compute/memory blockers. Include a recommended integration or fallback path.

**Continue:** Send partial findings if a blocker persists. The absence of public-cluster funding does not prevent local SVM measurements. Do not replace an unmeasured result with a prediction.

## 4. Milestone 1 — Foundation and experimental infrastructure

**Goal:** Separate state/treasury PDAs and demonstrably working custody plumbing for native SOL and mock USDC.

**Build:**

- Reproducible workspace, pinned dependencies, test commands, shared verifier/action interface, isolated agent fixtures.
- Fresh six-decimal mock mint; explicit token-program and authority configuration; distribute test units.
- Initialization, stable PDA derivation, native deposits, PDA-controlled token account, and both transfer paths.
- Initially use a narrowly marked development authorization mechanism to test plumbing. It must be removed from the later withdrawal path or remain only as an explicitly scoped administrator operation.
- Deploy to devnet when funded. Avoid global CLI configuration changes that could redirect another project.

**Success criteria:** Both assets complete local deposit/withdrawal round trips; wrong state/treasury/token accounts are rejected; deployment evidence is present or its absence is precisely explained. Updating authority data leaves receiving addresses unchanged.

**Deliver/report:** M1 brief, program and mint IDs, public account map, transaction evidence, initial account sizes/rent/CUs, reproducible commands, and list of temporary development paths still to remove. Other work continues immediately.

## 5. Milestone 2 — Naive SHA-256 secret-array vault

**Goal:** Establish the functional and storage baseline, including its intentional weakness.

**Build:** Deterministically generated test secrets, onchain commitment array, consumed slots, both withdrawal assets, and bounded slot-burning support. Start with a small fixture; add 16/256/1,024 commitment cases when practical. Account-allocation and upload costs count as setup work.

**Experiment:** In isolated local fixtures, give an attacker the witness from an unexecuted withdrawal. Submit the substituted destination/action first. Demonstrate that the naive bearer-secret authorization accepts it. Then show rejection of reuse after consumption. The scripted ordering is the declared adversarial model, not a claim of live network interception.

**Success criteria:** Valid secrets work, invalid/consumed secrets fail, and the intended copied-secret weakness is reproducible for both assets. No unrelated admin privilege is used in the attack.

**Deliver/report:** M2 brief; account bytes and setup costs by fixture size; witness/transaction sizes and CUs; successful/failed cases; structured attacker/owner balance changes. An expected attacker success is a passing experimental test, not a reason to hide the result.

## 6. Milestone 3 — Merkle-committed secrets

**Goal:** Reduce commitment storage while isolating the unchanged bearer-secret risk.

**Build:** SHA-256 tree/proof tooling; root plus usage-state storage; strict index/proof checks; both assets; leaf burning. Use the same disposable secret sets as the array comparison where possible, but never share mutable signing state between workers.

**Experiment:** Compare equivalent array and Merkle withdrawals for 16, 256, and 1,024 leaves. Record actual allocated storage, rent deposits, proof bytes, full transaction bytes, CUs, and setup transactions. Reproduce the copied-secret destination substitution.

**Success criteria:** Valid paths pass, altered paths/indices fail, and the known bearer attack still works. Show a mode transition on the same treasury address. If the main program keeps spare allocation for convenience, also measure right-sized accounts and label the difference; do not claim rent savings from logical byte counts alone.

**Deliver/report:** M3 brief, comparison dataset, evidence of stable address/mode transition, attack traces, and setup/steady-state cost separation. Do not postpone the already-running XMSS worker until this milestone finishes.

## 7. Milestone 4 — XMSS-authorized vault and final findings

**Goal:** Execute exact-message hash-based authorization for SOL and mock USDC, then demonstrate leaf retirement and authority replacement.

**Build:** Reference-compatible verifier, canonical intent, signer journal, usage bitmap, action nonce, XMSS withdrawals, authenticated `burn_leaves`, and current-root-authorized rotation to a fresh root/public seed.

**Experiment:** With ordinary relayer/funding fixture keys exposed to a local attacker, show rejection of unauthorized withdrawals, substituted destinations/amounts/assets, replay, used or burned leaves, invalid authentication paths, and old authorities after rotation. Copying an unchanged authorized intent may execute the intended transfer once; it must not redirect it.

**Success criteria:**

- Correct XMSS authorization moves both assets on the SVM and, when infrastructure permits, in confirmed devnet transactions.
- Valid current-root rotation preserves treasury/token addresses and balances; new-root withdrawal works and an old-root authorization fails.
- Burning retires the exact specified leaves and consumes its own authorizing leaf; retries obey signer-state rules.
- Independent reference comparisons and negative tests pass for the final integrated commit.
- Three clean demo commands and a benchmark command are reproducible; raw data and a concise research write-up exist.

**Deliver/report:** M4 brief, final comparison, evidence package, limitations/deviations, program/mint/account manifest, client/CLI contract, and final research handover. Distinguish `complete`, `partial`, and `blocked`; a host-only verifier is not a completed onchain XMSS demo.

## 8. Fallback policy

A worker should timebox unproductive investigation, report the actual blocker, and select a defensible next action. Do not stop all work because one branch is blocked.

- **Funding/RPC:** continue local fixtures and SVM validation; retry deployment when available.
- **Client v1 support:** use a compatible official path or stage witness bytes in a program-owned account. Record extra transactions and storage.
- **Compute/memory:** profile real hotspots, use runtime hashing where correct, avoid large stack copies, and retest full-reference compatibility.
- **Persistent verifier limit:** consider authenticated staged verification only if time permits. Partial progress must be tied to immutable witness/intent/current authority; an offchain “verified” flag is never a substitute. Otherwise publish the measured limitation and leave milestone status partial.
- **Nonstandard alternative:** isolate and label it as an extra experiment; it does not complete the specified XMSS milestone.

Do not respond to a blocker by weakening security parameters, substituting an Ed25519 approval, or inventing successful measurements.

## 9. Reports and automatic continuation

Save each update/brief to the repository, relay a short summary, and state what is already proceeding next. No routine checkpoint requires user approval. Use the supplied templates. Keep a small `reports/status.md` with active agents, commits, completed gates, blockers, next actions, and restart instructions so a resumed session does not repeat finished work or reuse signing leaves.
