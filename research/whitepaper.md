# Solana Bunker: stable custody addresses with replaceable hash authorization

**Research proof of concept — local-SVM results and confirmed devnet results.** The three core demonstrations run locally and on Solana devnet. All six XMSS operations, including burn, root rotation and spending from the new root, each ran as one inline v1 transaction and are confirmed on devnet. Complete raw measurements and acceptance coverage are recorded in results-summary.md and the milestone reports.

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

## Implementation and measured results

The custody program uses the raw Solana Rust SDK, separate stable PDAs and checked standard SPL transfers. A sealed program-owned signature stage provides a legacy transport path; no transfer occurs during upload. The client uses the pinned C reference for signing, a one-writer SQLite journal with synchronous reservation before signature release, exact retry records, fresh authority generation tracking, and a documented BIP-39/HKDF project seed recipe. These offchain conventions are separate from standardized XMSS.

The five-transaction staged baseline is the final functional run `validation-20261012T135652`, which passes 195 cases across 573 measured attempts on custody binary `8d7435ea6225ef4b09e972cef7ed3d2b99f7f4e1d1b9e9f8aa5124a0848f6e25`. Each principal mode/asset case has 20 measurements; 37 host tests also pass. An independent source export without Git history or private credentials reproduces all 37 host and 195 SVM cases (run `validation-20261012T140013`, source archive `10a96e861e087488753a43849415cbea0b1ad02b`). Targeted program/intent supplements add30actual runtime assertions and one separate host cryptographic mint-binding check; both supplements are independently reproduced. The bounded acceptance matrix is complete with explicit runtime/host/source distinctions. These are finite experimental tests, not complete security verification.

For 1,024 leaves, actual array state occupies 33,126 bytes versus 390 bytes for Merkle state; initialization/authority upload uses 38 versus two transactions. A fixed 128-byte usage bitmap is included in both allocations. Copied-witness destination substitution still succeeds in both primitive modes for both assets.

Complete XMSS executes both transfers, authenticated leaf retirement, current-root-signed rotation to a fresh tree, old-root rejection and exact retry after rolled-back insufficient-balance failure. Rotation preserves treasury/token addresses and balances. Separate independent client review passes 15 cases / 77 transactions. The trusted same-vault array→Merkle→XMSS mode transition also preserves receiving accounts.

With 20 measured withdrawal intents per asset, final XMSS execution has median 522,160 CUs for SOL and 531,758 for tokens; tested maxima are 603,323 and 578,142 respectively. In this staged baseline, a logical withdrawal uses five transactions, 30,000 lamports in observed fees and a retained 2,625-byte stage account funded with 19,160,880 rent lamports. The total-operation median includes staging: 534,351 CUs SOL / 539,497 tokens. Temporary accounts are not refunded. The numbers characterize this implementation/runtime and tested messages, not a worst-case cryptographic bound.

Reference vectors at indices 0, 1, 511, 512 and 1022 match the unmodified independent signer. The upstream signer prematurely clears secret seeds at index 1023; a small explicitly recorded control-flow patch supplies that boundary vector, which the unchanged reference verifier accepts. This patch and exact source provenance are preserved rather than silently reported as unmodified signer behavior.

Standalone XMSS has a separate 42-case valid/invalid SVM run, 120 repeated valid measurements and SHA-256 microbenchmarks. Its directly installed fixture account excludes custody/upload cost. Likewise, successful local execution of a v1 transaction establishes parsing and execution only: this LiteSVM binding does not enforce inline resource settings. The staged baseline uses verified legacy ComputeBudget enforcement; the inline v1 resource settings are enforced on devnet, as described below.

See [results-summary.md](results-summary.md), raw run links and the acceptance matrix for min/median/max, complete serialized envelopes, allocated storage/rent, setup costs, rejection stages and remaining test distinctions.

## Single-transaction XMSS over v1

The default client now places the exact canonical intent and the complete 2,500-byte signature in one v1 transaction. SOL withdrawal, Mock USDC withdrawal, leaf burning and authority rotation share this path. The program already accepted inline witnesses through opcode 2, so the verifier and custody rules are unchanged. The inline instruction is `02 || intent_length:u16LE || canonical intent || raw signature`. The transaction requests 1,400,000 compute units, 1,048,576 loaded-account bytes and a 32,768-byte heap through the v1 configuration. The staged path remains available as an explicit fallback.

Measured on devnet, each operation is one confirmed transaction:

| XMSS operation | Complete transaction bytes | Confirmed CUs |
|---|---:|---:|
| SOL withdrawal | 3,117 | 518,509 |
| Mock USDC withdrawal | 3,214 | 532,564 |
| Burn two target leaves | 3,086 | 529,687 |
| Rotate root and public seed | 3,146 | 483,319 |

The devnet program is `HssAePJfZrERFjEAhm89nY9Tc9BWAobxp2GqGhefNK6V`. The XMSS SOL withdrawal is [transaction CiZmcGsa...JdBM](https://explorer.solana.com/tx/CiZmcGsaX4G7upT1ECscLUr1vVrX1htShX4Q2y8K4wd1hJcsVpfZEQc9GZtod8MxVSmP4Hy6mbVqiM75QiAJdBM?cluster=devnet) and the root rotation is [transaction 5U4B7zhg...5iy](https://explorer.solana.com/tx/5U4B7zhgQ38cyUztvxUK5tYCJ2uHMweKjePJ14gYJGv2X42mDwWGqWreiQi9KYtYkkoWskS8pykD2Fab8RjML5iy?cluster=devnet). The rotation preserved the treasury and token receiving addresses and balances, and the new root then withdrew both assets. Devnet simulations rejected destination substitution before and after rotation, and rejected one-CU and one-byte loaded-account limits on the same authorization that then confirmed. The array and Merkle devnet fixtures use 16 leaves, so their figures are not comparable to the local 256-leaf comparison; XMSS keeps its 1,024-leaf parameter set in both environments.

The staged baseline above uses five transactions and 4,470 to 4,726 total bytes per operation, creates a 2,625-byte stage account and pays 30,000 lamports in fees. An inline operation creates no witness account and paid 5,000 lamports in the local runs. The staged and inline runs used different signatures and fixtures, so their compute differences are not a paired measurement of transport overhead. Details are in [the v1 report](../reports/v1-single-transaction.md).

## Limitations and future work

This is application-level authorization, not a Solana consensus migration. Live key theft, production recovery, multi-device signing, upgraded-code governance, timelocks and token issuer powers are outside the tested threat model. Larger transport capacity does not raise execution compute limits, and the inline operations use roughly 480,000 to 580,000 of the 1,400,000 requested CUs. Devnet figures are single confirmed transactions per operation, not repeated samples, and the local LiteSVM binding does not enforce inline limits. The devnet program's upgrade authority and the Mock USDC mint authority remain trusted. Optional SLH-DSA research is reported only at the level actually run. Its stateless signing does not remove vault replay state.

Sources: [sources.md](sources.md). Required experiment IDs and report schema: [handoff acceptance matrix](../handoff/04_TESTS_AND_EVIDENCE.md).

