# Measured results

XMSS now defaults to one inline v1 transaction for SOL, Mock USDC, burn and
rotation. The full 2,500-byte signature and canonical intent use the existing
verifier; `--xmss-transport staged` retains the five-transaction fallback.
The [v1 execution report](../reports/v1-single-transaction.md) records the fresh
integrated local measurements and confirmed devnet results. Preliminary smoke
measurements are not used below.

## Current inline comparison: local SVM

Fresh custody binary SHA-256
`48e2e324abcdcfd7e4c7cb601765da374595b922ed94e29d5ec168d37c06de79`
(124,464 bytes), source `e4d20bff4eb589f97fcdf84a9d668c2cbc46b67f`,
Agave 4.3.0/platform-tools 1.57; Python 3.13.5/solders 0.29.0 LiteSVM.
The full run passed 195 cases across 317 measured attempts. Separate inline
and staged client runs each passed 22 scenarios; 37 host and 16 client tests
passed. [Canonical summary and raw evidence](../artifacts/canonical-v1-validation-summary.json).

Each row below has **20 successful samples**, one transaction per withdrawal.
Array/Merkle use 256 leaves; standardized XMSS uses 1,024. XMSS local execution
uses an explicit 1.4-million-CU runtime override because LiteSVM ignores v1
inline resource fields; this table does not claim their network enforcement.

| Mode / transport | Asset | Measured CUs min / median / max | Full signed bytes | Requested CU cap |
|---|---|---:|---:|---:|
| Array / legacy | SOL | 7,101 / 7,101 / 7,101 | 677 | 1,400,000 |
| Array / legacy | Mock USDC | 8,012 / 8,012 / 8,012 | 774 | 1,400,000 |
| Merkle / legacy | SOL | 7,227 / 7,229 / 7,231 | 933 | 1,400,000 |
| Merkle / legacy | Mock USDC | 21,638 / 21,640 / 21,642 | 1,030 | 1,400,000 |
| XMSS / inline v1 | SOL | 483,722 / 518,507.5 / 564,891 | 3,117 | 1,400,000 |
| XMSS / inline v1 | Mock USDC | 499,275 / 522,467.5 / 580,447 | 3,214 | 1,400,000 |

The single-operation client measurements add a two-target burn at 3,086 bytes /
529,688 CUs and rotation at 3,146 bytes / 494,909 CUs. Inline operations create
no temporary witness account. Explicit staged fallback still needs five
transactions and 2,625 new temporary bytes per operation; complete staged
operation sizes are 4,532 SOL / 4,726 token / 4,470 burn / 4,590 rotation bytes.
Different isolated signatures prevent interpreting CU differences between
these client runs as a paired transport benchmark. The v1 report keeps local
and confirmed devnet consumption separate, including post-rotation withdrawals.

## Confirmed devnet XMSS

All six operations below used one v1 transaction with a 1,400,000-CU inline cap.
These are single confirmed samples, separate from the local 20-sample groups.

| Operation | Complete signed bytes | Confirmed CUs |
|---|---:|---:|
| SOL withdrawal | 3,117 | 518,509 |
| Mock USDC withdrawal | 3,214 | 532,564 |
| Burn two target leaves | 3,086 | 529,687 |
| Rotate XMSS root and public seed | 3,146 | 483,319 |
| New-root SOL withdrawal | 3,117 | 506,910 |
| New-root Mock USDC withdrawal | 3,214 | 578,944 |

The [devnet summary](../artifacts/v1-devnet-validation-summary.json) links each
retrieved receipt and verifies the same binary hash as the fresh local run.
Array/Merkle withdrawals also confirmed for both assets, using 16-leaf fixtures
rather than the local 256-leaf comparison. Rotation preserved receiving
addresses and balances. Same-authorization low-resource and tampering
rejections are separately labeled simulations; the full-limit successes are
confirmed transactions. Ordinary Ed25519 upgrade/demo authorities remain trusted.

## Earlier staged baseline

The tables below describe the earlier **local SVM** staged baseline, solders
0.29.0/LiteSVM with legacy ComputeBudget, custody binary
`8d7435ea6225ef4b09e972cef7ed3d2b99f7f4e1d1b9e9f8aa5124a0848f6e25`.
These rows are not inline v1 or devnet measurements.

Baseline run `validation-20261012T135652` at source `e3938925e3b2153592328ca56163b47d8686c314`: **195/195 cases passed, 573 measured transaction attempts**. Host run: **37 passed**. Targeted supplements add 15 program and 15 intent runtime assertions, independently reproduced, plus one separately labeled host RFC mint-binding check. The 31-ID [matrix](../artifacts/acceptance-matrix.json) records 29 bounded local IDs, S03 host and D02 source inspection.

### Principal staged-baseline withdrawals

Each row has 20 measured successful operations. Array/Merkle use 256-leaf fixtures; XMSS uses its specified 1,024-leaf tree. Final execution transaction size is separate from all staged transport bytes.

| Mode | Asset | Execute CUs min / median / max | Full execute tx bytes | Transactions per operation | Median total operation CUs |
|---|---|---:|---:|---:|---:|
| Array | SOL | 7,101 / 7,101 / 7,101 | 677 | 1 | 7,101 |
| Array | Mock USDC | 8,012 / 8,012 / 8,012 | 774 | 1 | 8,012 |
| Merkle | SOL | 13,227 / 13,229 / 13,231 | 933 | 1 | 13,229 |
| Merkle | Mock USDC | 9,638 / 9,640 / 9,642 | 1,030 | 1 | 9,640 |
| XMSS | SOL | 487,372 / 522,160 / 603,323 | 674 | 5 | 534,351 |
| XMSS | Mock USDC | 415,808 / 531,758 / 578,142 | 771 | 5 | 539,497 |

Total-operation CUs sum records with the same operation ID, including stage create, three uploads and final execution, then take the median over 20 operations. Principal array/Merkle operations pay 5,000 lamports in observed fees. Staged XMSS operations pay 30,000 lamports and retain 19,160,880 lamports of stage-account rent per operation (2,625 temporary bytes); no refund is claimed.

Raw records and min/median/max groups: [validation-benchmarks.jsonl](../artifacts/validation-benchmarks.jsonl), [summary CSV](../artifacts/validation-benchmark-summary.csv), with raw runtime logs linked per attempt. [Client comparison](../artifacts/client-comparison-summary.json) separately records staged total serialized bytes of 4,532 SOL / 4,726 token; do not mistake the final 674/771-byte envelope for the entire operation.

### Actual allocation and setup

State-only values include the program's fixed 358-byte header, including the 128-byte leaf-use bitmap. Persistent totals add the 8-byte treasury and 165-byte source token account. Setup counts include program initialization and authority uploads, excluding separate mint/recipient/funding fixture setup.

| Leaves | Array state / persistent total bytes | Merkle state / persistent total bytes | Array setup transactions | Merkle setup transactions | Array setup rent lamports | Merkle setup rent lamports |
|---:|---:|---:|---:|---:|---:|---:|
| 16 | 870 / 1,043 | 390 / 563 | 2 | 2 | 9,931,920 | 6,591,120 |
| 256 | 8,550 / 8,723 | 390 / 563 | 11 | 2 | 63,384,720 | 6,591,120 |
| 1,024 | 33,126 / 33,299 | 390 / 563 | 38 | 2 | 234,433,680 | 6,591,120 |

XMSS state is 422 bytes; persistent custody total 595 bytes; initialization/authority upload uses two transactions and 6,813,840 rent lamports. These persistent values exclude temporary signature staging.

Array witness is 36 bytes. Merkle witnesses are 164/292/356 bytes for 16/256/1,024 leaves, including 128/256/320 sibling bytes. Complete Merkle legacy withdrawal envelopes are 805/933/997 bytes for SOL and 902/1,030/1,094 for tokens. XMSS raw signature is measured at 2,500 bytes.

These values come from seven client comparison run groups (all assertions passed), linked in [client-comparison-summary.json](../artifacts/client-comparison-summary.json), and are corroborated by the final functional size-comparison cases.

### Attack and authority outcomes

Both bearer-secret modes accept the copied pending witness with attacker-selected destination for both assets, under scripted first-included ordering. That is the expected experiment. XMSS rejects modified destination/amount/burn list/replacement root, missing hash authorization, consumed/burned leaves and replay; exact unchanged authorization can execute its intended effect once.

Current-root-authenticated rotation preserves treasury/token addresses and balances, increments epoch/nonce, installs a fresh root, accepts new-root withdrawals and rejects an unused old-root signature even when presented with current epoch fields. Explicit trusted mode transitions also preserve the same vault's receiving addresses. Independent client-XMSS review: 15 cases / 77 transactions; [reviewed record](../artifacts/crypto-reviewed-client-xmss.json).

Standalone crypto measurements are a separate group: 42 valid/invalid cases and 120 repeated valid runs, final probe digest `21088f9e...`, 464,546–496,643 CUs for tested valid messages. Its fixture account is preinstalled, so it does not measure custody transport. The final-index C signer control-flow patch is disclosed; verification uses the unchanged pinned reference.

## Limits

Local v1 decoding and execution do not establish inline CU/loaded-limit
enforcement in LiteSVM. The new inline harness explicitly applies a 1.4-million
CU runtime override and labels it. The earlier tables above use legacy
ComputeBudget instructions; they cannot demonstrate enforcement of v1 resource
fields. See the current report and public manifest for devnet status and
separately labeled resource controls.

Ordinary upgrade/demo administration is trusted. Runtime policy rejection, signature-verifier failure, host-only signing/cryptographic checks and source inspection are explicitly labeled. Missing measurements stay null. No production, audit, formal-verification, cryptanalytic break or first-ever-vault claim is made.
