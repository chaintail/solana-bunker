# Research and program brief

## 1. Purpose and scope

**Research question:** Can an application use Solana PDAs to keep a stable receiving address while replacing ordinary curve-key withdrawal authorization with hash-based authentication, before a network-wide signature migration?

Build a research proof of concept, not a production wallet. The contribution is the progressive experiment, integration of established cryptography with the SVM, stable-address authority replacement, and reproducible measurements. Do not claim invention of hash-based signatures or the first Solana hash-signature vault. Related work is listed in [the source register](05_SOURCES_AND_DECISIONS.md).

The project should tell a clear story:

1. An array of hashed one-time secrets is easy to implement but uses storage and exposes a bearer credential at withdrawal.
2. A Merkle tree compresses the commitments but preserves the same authorization weakness.
3. XMSS authenticates the exact action, so copying a valid authorization does not permit substituting a destination or amount.
4. SLH-DSA offers a possible stateless future authority; implementation is optional.

The original notes also explored hidden Ed25519 keys and commit–reveal. Preserve those as brief background/future comparisons, not additional required implementations.

### Required outputs

A working program, offchain signer/client, local adversarial harness, devnet deployment when infrastructure permits, mock-USDC mint, four milestone reports, raw benchmark data, reproducible demo commands, and a concise Markdown research write-up. Leave the visual UI and final video production for the next discussion; prepare the data and narrative they will need.

## 2. Threat model in one paragraph

Test application-level authorization while assuming correct Solana execution, the selected hash constructions, and the deployed verifier code. Simulate disclosure of ordinary funding/relayer Ed25519 keys and hostile modification or ordering of submitted actions. The ordinary development-key upgrade authority and any explicitly retained demo-mode administrator remain trusted and outside that attack simulation. They can undermine custody and must be disclosed. Consensus compromise, stolen Bunker seed material, production recovery, token-issuer powers, and network-wide migration are outside this experiment. This is not a real cryptanalytic break or a production-security guarantee.

## 3. Architecture

### Fixed design

Use one program with shared asset-transfer machinery and distinct, explicitly selected authorization modes:

- `SECRET_ARRAY_V1`
- `MERKLE_SECRET_V1`
- `XMSS_SHA2_10_256_V1`
- Optional later: a precisely identified SLH-DSA mode or administrator path.

Only the **active mode** can authorize a vault operation. An inactive naive verifier must never serve as a fallback when XMSS verification fails.

Keep two distinct PDAs:

**State PDA:** stores version, stable vault identifier, treasury association, mode, authority material, epoch, action nonce, and leaf-use state.

**Treasury PDA:** is the permanent native-SOL receiving account and the transfer authority for the mock-USDC token account. Default to a small program-owned treasury for direct lamport debits. Use PDA signer privileges when calling the Token Program. Account ownership and PDA signing authority are separate concepts; follow the runtime rules rather than assuming an off-curve address grants arbitrary control. [S04, S05, S06]

Suggested seeds, to be finalized quickly by the interface worker:

```text
state    = PDA(program_id, ["bunker_state", vault_id])
treasury = PDA(program_id, ["bunker_treasury", state_address])
```

Use canonical bumps. `vault_id` is a fixed public identifier; neither current root nor current mode is a seed. The stable-address claim is within the same program ID and cluster, not across deploying unrelated replacement programs.

A separate variable-size authority-data PDA is acceptable if it simplifies allocation. It must not replace the separate treasury model. Do not preallocate a 32 KiB array in every mode and then claim Merkle mode reduced actual account storage.

### Assets

Support native SOL and a fresh, ordinary SPL mint named in reports as **Mock USDC — test token, no real value**. Use six decimals and the standard Token Program; Token-2022 features and real Circle USDC are unnecessary. Record mint and freeze-authority choices. Retain a documented test mint authority for fixture distribution; no need for elaborate token metadata.

The treasury controls the mock token account. Validate the exact mint, token-program ID, source authority, source account, and signed destination token account. Use checked token transfers. Reject unexpected delegates/authorities in the demo source account. Never conflate a recipient wallet address with the token account actually receiving units. [S06]

Native SOL deposits can be ordinary transfers after initialization. A custom deposit instruction is optional. Preserve treasury/state rent requirements; measure storage deposits separately from transferred SOL and transaction fees.

## 4. Minimal state and identity

Let the implementation worker choose serialization and framework. Agree early on these conceptual fields:

```text
version, initialized status, vault_id, PDA bumps
active_mode, authority_epoch, action_nonce
authority payload and parameter identifier
leaf_count, consumed_leaf_bitmap
mock_mint and expected token-program ID
explicit demo administrator, if retained
```

XMSS authority needs both its root and public seed. Array mode stores commitments; Merkle-secret mode stores its root. Keep logically used bytes and physically allocated bytes measurable.

A 1,024-leaf bitmap is 128 bytes. For this prototype, use a single sequential `action_nonce` plus the bitmap. **The bitmap allows skipped or abandoned signing leaves; it does not make two operations with the same expected action nonce concurrently executable.** One succeeds and the other becomes stale. No concurrent-withdrawal scheduler is required.

Large array initialization may need account growth and chunked writes. Bound writes, track initialization completeness, and disable spending before finalization. Count setup transactions and storage in the results rather than hiding them.

## 5. Program operations

### Initialize

Create state, treasury, authority storage as needed, and token accounts. Bind all of them to the same vault. Reject duplicate/reinitialization attempts. The deployment/admin key can authorize bootstrap setup; this is not part of the alternative-signature claim. Do not present a receiving address as ready until initialization is confirmed.

### Withdraw SOL / withdraw mock USDC

Use a shared path: validate accounts and current state, verify the selected witness, check usage and intent, consume the authorizing leaf, advance `action_nonce`, then execute the exact asset transfer atomically. A failed transaction must not leave a partial debit or persisted leaf-use update. Fee-payer fees are outside that rollback accounting. [S07]

For the two primitive modes, intentionally demonstrate that the revealed secret is not bound cryptographically to the caller's requested action. Do not “fix” this by precommitting the destination and then present it as the same naive experiment.

For XMSS, require a valid signature over the complete canonical action. The offchain client and onchain parser must share the encoding specification and independent vectors.

### Burn leaves

Accept a small bounded list or range of indices under the current mode/epoch. In XMSS mode, a **different unused signing leaf** signs the exact burn request; execution consumes that authorizing leaf as well as retiring the requested leaves. Bind the target list, current epoch, and action nonce. Reject out-of-range input; choose and test an explicit duplicate/already-burned policy. Do not expose permissionless burning.

The primitive modes may authorize burning with one of their still-unused bearer secrets; their known authorization weakness remains. Burning prevents later accepted uses only after it lands. It neither erases leaked signatures nor repairs cryptographic key reuse.

### Rotate XMSS authority

A valid current XMSS authorization installs a **fresh** root, public seed, and parameter/mode identifier, advances the epoch and action nonce, and starts a fresh leaf bitmap. Bind the complete replacement authority to the signed message. Preserve treasury and token receiving accounts and their balances.

Use fresh key material. Never reset an old tree's bitmap and call its keys unused. Incrementing an epoch does not make reused one-time secrets cryptographically safe. At minimum reject replacement with the current authority and have the client refuse historical keyset reuse. Full onchain history management is not required for this PoC.

Prove rotation using the old XMSS authority; an admin-only reset is not a substitute for this core feature. Demonstrate a post-rotation withdrawal under the new authority and rejection of an unused old-root authorization.

### Demo-mode transition and cleanup

An explicit development administrator may switch the demonstration between already-implemented modes. Log this transition, advance the epoch, and label it as trusted setup. Do not add a general bypass-withdraw instruction. Remove any temporary Phase 1 bypass from the final withdrawal path.

Bounded cleanup of empty temporary fixtures is useful but secondary. Any closure/refund behavior must have an explicit authorization and destination; it is not part of the headline benchmark. Do not make immutability or closing program bytecode a sprint requirement.

## 6. Canonical authorization

Write an unambiguous versioned binary format, not JSON serialization whose field order might vary. Codex chooses the layout and documents it. Authenticate at least:

- Domain/version, program ID, deployment/network namespace, vault/state identity, treasury identity, mode, authority epoch, expected action nonce, and signing leaf index.
- Action type and all action-specific fields: SOL amount/destination; token program, mint, source/destination token accounts, amount/decimals; replacement authority; or the exact burn list.

Use integer base units, bounded lengths, checked arithmetic, and explicit byte order. XMSS's own encoding remains exactly as specified even if the application chooses another byte order for its intent fields.

The inner message excludes outer recent blockhash, incidental fee payer, and transaction transport details so the same authorized intent can be retried unchanged. Avoid adding expirations unless useful; adding one creates another signed field and must be tested. No caller-selected relayer reimbursement in the core demo.

Prefer carrying explicit expected nonce/epoch values and checking them against state. Signing and verification must never disagree about whether a field comes from submitted intent or current state. Test account substitution and aliasing, including destination equal to state or treasury; rejecting unusual aliases is fine for this narrowly scoped PoC.

## 7. Client and demonstration surface

Expose simple commands or equivalent API functions for `init`, `inspect`, `deposit-sol`, `deposit-mock-usdc`, `withdraw`, `burn-leaves`, `rotate-root`, `demo-array`, `demo-merkle`, `demo-xmss`, and `benchmark`.

Commands should support JSON output. Keep signing separate from transaction assembly/submission. Record a durable leaf reservation and exact signed authorization before releasing it; retries reuse those bytes. Keep the signer single-process/single-device for this sprint. See [crypto notes](03_CRYPTO_AND_PLATFORM_NOTES.md).

## 8. Explicitly not required

Do not build dual recovery trees, timelocked administration, multi-device coordination, seed-knowledge proofs, production mnemonic recovery, arbitrary DeFi execution, a generic verifier registry, an account-cleanup economy, a mainnet bounty, or the frontend. A short future-work section is enough. SLH-DSA may later authorize XMSS root rotation, but must not delay the three experiments.
