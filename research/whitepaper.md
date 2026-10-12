# Solana Bunker: stable custody addresses with replaceable hash authorization

**Working research draft — measurements pending.** This describes the experiment and its claim boundaries. Implementation status and measurements are recorded separately in results-summary.md and the milestone reports.

## Question and experimental scope

Can an application retain one Solana receiving address while changing how withdrawals are authorized? Bunker separates a state PDA, which records authority and usage, from a treasury PDA, which receives native SOL and controls a six-decimal SPL mock token account. The receiving addresses are stable within one program ID, cluster and vault identifier. Replacing a verifier or deploying another program is outside that narrower claim.

We compare three authorizations over shared custody machinery: SHA-256 commitments in an array, the same bearer secrets committed through an ordered Merkle tree, and complete XMSS-SHA2_10_256 signatures. The first two constructions intentionally show why compressing commitments does not authenticate a withdrawal destination. An attacker given an unexecuted secret witness can choose a replacement destination and be included first. The experiment scripts that ordering; it does not claim interception of real network traffic.

XMSS signs a canonical binary action including the deployment namespace, state and treasury identities, selected mode, epoch, action nonce, signing leaf, and every transfer/burn/rotation field. Outer fee payer and recent blockhash are excluded so an unchanged authorized intent can be retried. Copying identical authorization should cause at most the intended effect once; changing its requested effect must fail.

## Trust model

The experiment assumes correct runtime execution, selected hash constructions, and verifier code. It simulates disclosed ordinary relayer/funding credentials and hostile action ordering or modification. The ordinary program upgrade authority, explicitly retained demo administrator, test mint authority and XMSS seed material are excluded from that simulated compromise. Upgrade/demo administration can undermine custody; this proof of concept does not provide whole-system independence from Ed25519 or production recovery. No actual cryptanalytic key break, audit, formal verification or production-security guarantee is asserted.

## Related work and construction

RFC8391 specifies XMSS and its WOTS+ building block, including address-dependent hashes, message processing, public-key compression and authentication paths [S01]. NIST SP800-208 documents stateful hash-based signature requirements [S03]. We use existing constructions rather than inventing a signature scheme.

Existing Solana Winternitz Vault work authenticates lamport operations with WOTS, derives its vault address from public commitment material and closes/reopens vaults on spending [S15]. Its own documentation highlights ordinary update authority as a remaining trust boundary. Bunker's research emphasis is the progressive comparison, fixed treasury association, exact-action XMSS integration, two assets and reproducible SVM evidence. We do not claim the first Solana hash-signature vault. Winterwallet is listed for further implementation comparison [S16]; no construction/performance conclusions are drawn without inspecting its code.

The target XMSS tree has height ten, 1,024 one-time leaves and a 2,500-byte raw signature: four-byte index, 32-byte randomizer, 2,144-byte WOTS+ component and 320-byte authentication path. These are specification sizes, not observed transaction/account measurements. Public root and seed are 32 bytes each; any API parameter prefix is recorded separately. The pinned independent reference revision is `171ccbd26f098542a67eb5d2b128281c80bd71a6` [S02].

## Method

Each construction is tested for both native SOL and the fresh standard SPL token labeled **Mock USDC — test token, no real value**. Storage comparisons use equivalent 16/256/1,024-leaf fixtures where practical. Account allocation, rent deposit, proof/witness bytes, complete transaction bytes, setup transaction count, execution CUs and fees are measured independently. Staged witness operations count all upload/finalization transactions.

Reference-generated signatures and negative vectors are checked independently from the Rust verifier. Native success is a host result; the XMSS gate additionally requires a real SVM program execution. Local SVM, devnet simulation and confirmed devnet transaction evidence are never merged into one success claim. Invalid cases identify whether they reach signature verification or fail earlier account/nonce policy checks.

Burning is an authenticated action that consumes its own signing leaf and retires a bounded specified list. Root rotation must be authorized by the current XMSS root, install a genuinely fresh tree, preserve custody addresses/balances, and reject old-root authorizations. A trusted administrator reset is not equivalent evidence. The signer reserves leaves before releasing signatures and persists exact retry bytes; restoring seed material or seeing unused onchain leaves is insufficient permission to reuse uncertain signing state.

## Measured results

Pending. Read [results-summary.md](results-summary.md) for the current evidence gate; values are filled only from worker runs tied to commits/binary digests.

## Limitations and future work

This is application-level authorization, not a Solana consensus migration. Live key theft, production recovery, multi-device signing, upgraded-code governance, timelocks and token issuer powers are outside the tested threat model. Larger transport capacity does not raise execution compute limits; actual SDK/RPC support and SVM memory/compute are separate gates. Optional SLH-DSA research is reported only at the level actually run. Its stateless signing does not remove vault replay state.

Sources: [sources.md](sources.md). Required experiment IDs and report schema: [handoff acceptance matrix](../handoff/04_TESTS_AND_EVIDENCE.md).

