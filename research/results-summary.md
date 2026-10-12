# Measured results

All application measurements below are **local SVM**, solders 0.29.0/LiteSVM, enforced legacy ComputeBudget, custody binary `8d7435ea6225ef4b09e972cef7ed3d2b99f7f4e1d1b9e9f8aa5124a0848f6e25`. No devnet transaction is confirmed.

Final functional run `validation-20261012T135652` at source `e3938925e3b2153592328ca56163b47d8686c314`: **195/195 cases passed, 573 measured transaction attempts**. Host run: **37 passed**. Individual acceptance variants remain partial as recorded in the [matrix](../artifacts/acceptance-matrix.json).

## Principal withdrawals

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

## Actual allocation and setup

State-only values include the program's fixed 358-byte header, including the 128-byte leaf-use bitmap. Persistent totals add the 8-byte treasury and 165-byte source token account. Setup counts include program initialization and authority uploads, excluding separate mint/recipient/funding fixture setup.

| Leaves | Array state / persistent total bytes | Merkle state / persistent total bytes | Array setup transactions | Merkle setup transactions | Array setup rent lamports | Merkle setup rent lamports |
|---:|---:|---:|---:|---:|---:|---:|
| 16 | 870 / 1,043 | 390 / 563 | 2 | 2 | 9,931,920 | 6,591,120 |
| 256 | 8,550 / 8,723 | 390 / 563 | 11 | 2 | 63,384,720 | 6,591,120 |
| 1,024 | 33,126 / 33,299 | 390 / 563 | 38 | 2 | 234,433,680 | 6,591,120 |

XMSS state is 422 bytes; persistent custody total 595 bytes; initialization/authority upload uses two transactions and 6,813,840 rent lamports. These persistent values exclude temporary signature staging.

Array witness is 36 bytes. Merkle witnesses are 164/292/356 bytes for 16/256/1,024 leaves, including 128/256/320 sibling bytes. Complete Merkle legacy withdrawal envelopes are 805/933/997 bytes for SOL and 902/1,030/1,094 for tokens. XMSS raw signature is measured at 2,500 bytes.

These values come from seven client comparison run groups (all assertions passed), linked in [client-comparison-summary.json](../artifacts/client-comparison-summary.json), and are corroborated by the final functional size-comparison cases.

## Attack and authority outcomes

Both bearer-secret modes accept the copied pending witness with attacker-selected destination for both assets, under scripted first-included ordering. That is the expected experiment. XMSS rejects modified destination/amount/burn list/replacement root, missing hash authorization, consumed/burned leaves and replay; exact unchanged authorization can execute its intended effect once.

Current-root-authenticated rotation preserves treasury/token addresses and balances, increments epoch/nonce, installs a fresh root, accepts new-root withdrawals and rejects an unused old-root signature even when presented with current epoch fields. Explicit trusted mode transitions also preserve the same vault's receiving addresses. Independent client-XMSS review: 15 cases / 77 transactions; [reviewed record](../artifacts/crypto-reviewed-client-xmss.json).

Standalone crypto measurements are a separate group: 42 valid/invalid cases and 120 repeated valid runs, final probe digest `21088f9e...`, 464,546–496,643 CUs for tested valid messages. Its fixture account is preinstalled, so it does not measure custody transport. The final-index C signer control-flow patch is disclosed; verification uses the unchanged pinned reference.

## Limits

Local v1 decoding/execution of the official 2,029-byte SDK transaction succeeds, but inline CU/loaded limits are not enforced by this LiteSVM binding. Devnet submit/read remains blocked by an unfunded payer. Public deployment and mint identifiers are prospective only.

Ordinary upgrade/demo administration is trusted. Partial matrix variants, source-only guards and host-only tests are not promoted to full runtime coverage. Missing measurements stay null. No production, audit, formal-verification, cryptanalytic break or first-ever-vault claim is made.

