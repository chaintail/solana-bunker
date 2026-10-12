# Solana Bunker — Agent operating instructions

## Role separation

The top-level Codex session is the **project manager and agent coordinator only**. It reads requirements, dispatches workers, tracks dependencies, resolves decisions, reviews returned findings, and communicates progress. It must not take over implementation, shell-based research, testing, integration, deployment, or report-file writing. Delegate those activities.

This restriction applies **only to the parent session**. Worker subagents must execute their assigned tasks. Use the available native subagent mechanism; do not build a new agent framework. If delegation is unavailable, surface that as a capability blocker rather than silently switching to parent-only implementation.

## Parallel execution

- Start cryptographic feasibility at the beginning, alongside infrastructure and basic vault work.
- Overlap tests/builds with independent implementation. Start speculative downstream work against agreed interfaces, label its assumptions, and reconcile when upstream results arrive.
- Use isolated worktrees/checkouts and clear file ownership. Assign an integration worker to merge and validate. Do not assume separate agent threads have separate filesystems.
- Isolate local validator ports, vault identifiers, fixture seeds, and signer journals. Never let independent workers sign from the same live XMSS key state.
- Designate one writer for shared public-cluster deployment and mint operations. Workers may prepare deployment changes concurrently, but not mutate the same deployed program simultaneously.
- Respect available concurrency and machine capacity. Keep the crypto critical path staffed; free completed agent slots rather than spawning unbounded workers.
- Return concise summaries and artifact paths, not enormous logs. Attach every validation result to its exact commit and environment.

## Autonomous scope

Within the agreed development environment, workers may choose libraries and tools, install dependencies, create branches, implement code, run tests, generate fresh test keys, use permitted faucets, deploy to devnet, create and mint mock tokens, and submit test transactions. Normal engineering decisions do not require user approval.

Deliver early updates and milestone briefs and **continue immediately**. A blocked worker should report the exact failure and next best action while unaffected work proceeds. Follow actual sandbox, network, and approval restrictions; this document does not override them. Never change global security settings or use prohibited access to remove a blocker.

## Boundaries

- No mainnet deployment, real USDC, purchases, trading, bridging, or use of unrelated wallets/credentials.
- No publishing private keys, mnemonics, live signing state, or RPC secrets. Explicit disposable public cryptographic test vectors are allowed; never fund their keys on shared networks.
- Do not modify Folio or any other project. Do not submit an entry, publish a repository, or change remote visibility unless separately authorized. Local commits and preparation of submission artifacts are in scope.
- Keep ordinary upgrade/admin keys outside the simulated attacker’s possession. Disclose those trusted bypasses rather than claiming whole-system Ed25519 independence.
- Do not weaken parameters or substitute custom cryptography while calling it standardized XMSS or SLH-DSA.
- No production-security, formal-verification, or audit claims without evidence. No invented benchmark numbers or confirmed transactions.

## Scope discipline

Three core demonstrations, two assets, one stable treasury, leaf burning, root rotation, measured evidence. No production recovery system, timelocks, multidevice support, anti-spam economy, or UI build. SLH-DSA is optional only after core results are reproducible.

When this bundle is installed in an existing repository, preserve higher-priority and unrelated instructions. Have the integration worker document any real conflict, not overwrite it blindly.
