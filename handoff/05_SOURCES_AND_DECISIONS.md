# Provenance, decisions, and primary sources

**Reference check date:** 2026-10-12. These sources establish background facts and implementation starting points. They do not establish that this PoC has been implemented, audited, deployed, or benchmarked.

## User-derived basis

**U1 — User's `Solana Bunker.pdf`, six pages.** Page 1 proposes progressively stronger demonstrations and conventional hashes. Page 2 identifies the Merkle one-time-signature favorite and stateless stretch direction. The screenshots on pages 3–4 describe a stable receiving address, hash-authorized transfers, root rotation, and a scoped adversarial demonstration. Pages 5–6 describe replaceable authorization and future cryptographic agility. The PDF is not required to execute this handoff; its relevant scope is summarized here.

**U2 — Final approved conversation decisions.** The later instructions narrow the project to a 24-hour PoC; separate state/treasury; three core demos; both SOL and six-decimal mock USDC; fresh development wallet/local and devnet work; leaf burning; XMSS root rotation; ordinary demo upgrade authority; no advanced recovery or UI implementation; optional SLH-DSA; coordinator-only parent with parallel execution subagents; automatic continuation after reports. These later decisions take precedence over earlier exploratory lessons.

The proposed seed labels, source-tree paths, intent format requirements, benchmark schema, test IDs, and timeboxes are **handoff engineering defaults**, not claims that they were already implemented or standardized. Codex may adjust defaults with a short decision-log entry while preserving locked scope.

## Important calibrations carried into this handoff

- The four phases produce **four milestone briefs**; wallet, transport, and XMSS feasibility produce **three early updates**. They are not seven serial implementation gates.
- v1 has a documented 4,096-byte limit, but success on the selected SDK/RPC/cluster must be demonstrated. No exact historical activation date is needed for execution.
- Earlier rough transaction-size and per-hash compute estimates are not accepted benchmark evidence. Measure complete serialization and the actual SVM verifier.
- The smallest listed FIPS 205 signature is 7,856 bytes; do not assume it fits in one v1 transaction or in two usable upload payloads.
- An action nonce and a leaf index are different. A bitmap does not remove the serial effect of a single global action nonce.
- A trusted ordinary upgrade/admin key invalidates any unqualified claim that compromising *all* ordinary keys is harmless. The attack experiment excludes those authorities; it tests the normal withdrawal path.
- A Merkle root/public seed rotation changes an implemented authority, not arbitrary immutable program code. Advanced verifier governance remains future work.

## Primary-source register

Use the identifiers below in implementation notes and the final research paper. Pin actual software commits/tags in the experiment manifest instead of citing a moving branch as the tested version.

| ID | Source | Use |
|---|---|---|
| S01 | [RFC 8391 — XMSS](https://www.rfc-editor.org/rfc/rfc8391.html) | Exact construction, parameter identifiers, signature encoding |
| S02 | [XMSS reference implementation](https://github.com/XMSS/xmss-reference) | Independent interoperability/reference tests; inspect license and pin revision |
| S03 | [NIST SP 800-208](https://csrc.nist.gov/pubs/sp/800/208/final) | Stateful-signature usage requirements; not an implementation certification |
| S04 | [Solana PDAs](https://solana.com/docs/core/pda) | Derivation and PDA authority model |
| S05 | [Solana accounts](https://solana.com/docs/core/accounts) | Runtime ownership and account structure |
| S06 | [Solana token transfers](https://solana.com/docs/tokens/basics/transfer-tokens) | Checked transfers and token-account authority |
| S07 | [Solana transactions](https://solana.com/docs/core/transactions) and [fees](https://solana.com/docs/core/fees/fee-structure) | Atomic execution and fee accounting |
| S08 | [Versioned transactions](https://solana.com/docs/core/transactions/versioned-transactions) | v1 SDK/message configuration and transaction reading |
| S09 | [Larger transaction sizes](https://solana.com/upgrades/larger-transaction-sizes) | v1 capacity, base64 transport, compatibility considerations |
| S10 | [Compute budget](https://solana.com/docs/core/fees/compute-budget) | Execution limits, memory budget, v1 distinction |
| S11 | [Agave compute budget source](https://github.com/anza-xyz/agave/blob/master/compute-budget/src/compute_budget.rs) | Entry point for tracing runtime cost structures; follow imports in the pinned version |
| S12 | [BIP 39](https://bips.dev/39/) | Mnemonic/passphrase-to-seed specification |
| S13 | [RFC 5869 — HKDF](https://www.rfc-editor.org/rfc/rfc5869.html) | Established KDF primitive for the project's domain-separated seed recipe |
| S14 | [NIST FIPS 205](https://csrc.nist.gov/pubs/fips/205/final), [standard PDF](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf) | SLH-DSA; signature sizes in Table 2, printed page 43 |
| S15 | [Solana Winternitz Vault](https://github.com/blueshift-gg/solana-winternitz-vault) | Prior art; not proof of this project's security or performance |
| S16 | [Winterwallet](https://github.com/blueshift-gg/winterwallet) | Related implementation; inspect actual construction before reuse |
| S17 | [OpenAI Codex subagents](https://developers.openai.com/codex/multi-agent) | Native delegation and inherited execution permissions; page may redirect to current documentation |
| S18 | [OpenAI Codex worktrees](https://developers.openai.com/codex/app/worktrees) | Parallel repository isolation; verify installed client behavior |
| S19 | [Solana clusters](https://solana.com/docs/references/clusters) | Development-cluster selection and public RPC conventions |

## Decisions to make during execution, not ask the user by default

Choose the fastest compatible Rust framework; Anchor is optional. Select a working client SDK, reference implementation, serialization, account-allocation strategy, and bounded burn-list policy. Choose supported local SVM tooling and decide whether a transport fallback is needed. Record the choice and evidence, then continue.

Reopen user approval only for an actual boundary change: mainnet/real funds, publication, unrelated project changes, unavailable mandatory permissions, or an unresolved requirement conflict that blocks the core work. Ordinary tradeoffs, partial results, or failure of the optional stretch goal do not require pausing the sprint.
