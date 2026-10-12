# XMSS in one v1 transaction

**Complete on devnet:** ten custody operations confirmed across all three modes and both assets. All six XMSS operations used one inline v1 transaction apiece, including burn, root rotation and spending from the new root. Fresh local validation and the explicit staged fallback also pass.

## What changed

The default SVM client now places the exact canonical intent and the complete
2,500-byte `XMSS-SHA2_10_256` signature in one v1 transaction. SOL withdrawal,
Mock USDC withdrawal, leaf burning and authority rotation use the same path.
`--xmss-transport staged` retains the legacy fallback: create one witness
account, upload three chunks, then execute the sealed authorization.

The custody program already accepted inline witnesses through opcode 2. The
program change names the existing opcodes and imports the verifier's signature
length constant; it does not introduce a second verifier or change custody
rules. Array and Merkle-secret operations keep their existing legacy transport.

The inline instruction is:

```text
02 || intent_length:u16LE || exact_canonical_intent || raw_XMSS_signature:2500
```

Its accounts are state, treasury, mint, source token account, exact destination,
and the Token Program, with the same privileges and checks as staged execution.
Root and public seed remain in validated state. XMSS verifies the full canonical
message, including domain, vault, epoch, nonce, leaf and every action field.
The RFC signature index remains big endian; application integers remain little
endian. There is no parameter reduction, custom signature substitute or extra
application prehash.

`MessageV1.try_compile` and `VersionedTransaction` serialize and sign the outer
envelope. The client checks its actual complete size against 4,096 bytes.
Inline `TransactionConfig` requests 1,400,000 CUs, 1,048,576 loaded-account bytes
and a 32,768-byte heap. No legacy ComputeBudget instruction is mixed into v1.
Outer blockhash, fee payer and resource settings remain outside the signed
application intent, so transport retries reuse the same durable authorization.

## Measured evidence

The fresh custody binary is 124,464 bytes, SHA-256
`48e2e324abcdcfd7e4c7cb601765da374595b922ed94e29d5ec168d37c06de79`,
built at `ba97a3067629dd6ffd9fb5693475c7ac5150f79c` with Agave
4.3.0/platform-tools 1.57 and SBF rustc 1.95.0; the
[build environment and source digests](../artifacts/v1-integration-environment.json)
record the exact provenance. The canonical local checkout is `e4d20bff4eb589f97fcdf84a9d668c2cbc46b67f`, running Python
3.13.5 and solders 0.29.0/LiteSVM. The custody and verifier source
digests match the build manifest. This binary differs from the earlier staged
baseline; its figures are kept separate.

The table records one fresh local client execution per row. Bytes include the
complete signed transaction, not just instruction data. The devnet columns
come from retrieved successful transactions. The requested cap is distinct
from measured consumption and local runtime enforcement.

| XMSS operation | Complete bytes, local / devnet | Local CUs, one sample | Confirmed devnet CUs | Requested inline cap |
|---|---:|---:|---:|---:|
| SOL withdrawal | 3,117 / 3,117 | 495,315 | 518,509 | 1,400,000 |
| Mock USDC withdrawal | 3,214 / 3,214 | 578,944 | 532,564 | 1,400,000 |
| Burn two target leaves | 3,086 / 3,086 | 529,688 | 529,687 | 1,400,000 |
| Rotate XMSS root and public seed | 3,146 / 3,146 | 494,909 | 483,319 | 1,400,000 |
| New-root SOL withdrawal | 3,117 / 3,117 | 518,509 | 506,910 | 1,400,000 |
| New-root Mock USDC withdrawal | 3,214 / 3,214 | 532,563 | 578,944 | 1,400,000 |

Devnet source: [completed validation summary](../artifacts/v1-devnet-validation-summary.json)
and its ten linked custody receipts. The six XMSS envelopes decode as v1,
contain exactly one opcode-2 custody instruction with inline resource fields,
and match the submitted bytes. The register contains 140 confirmed signatures,
including deployment/setup, and one separately recorded unconfirmed loader
preflight rejection. The [SOL withdrawal](https://explorer.solana.com/tx/CiZmcGsaX4G7upT1ECscLUr1vVrX1htShX4Q2y8K4wd1hJcsVpfZEQc9GZtod8MxVSmP4Hy6mbVqiM75QiAJdBM?cluster=devnet)
and [root rotation](https://explorer.solana.com/tx/5U4B7zhgQ38cyUztvxUK5tYCJ2uHMweKjePJ14gYJGv2X42mDwWGqWreiQi9KYtYkkoWskS8pykD2Fab8RjML5iy?cluster=devnet) are directly inspectable on Explorer.

Local source: [canonical inline client results](../artifacts/canonical-v1-inline-results.json),
including exact transaction evidence and before/after state. All 22 scenarios
passed across 24 measured transactions, including initialization and authority
upload. Inline operations create no witness staging account.

The separate full local run passed 195 cases across 317 measured attempts.
Its 20 principal samples per XMSS asset measured SOL at
483,722 / 518,507.5 / 564,891 CUs (minimum / median / maximum), and Mock USDC at
499,275 / 522,467.5 / 580,447 CUs, with the same 3,117 / 3,214-byte envelopes.
The [canonical validation summary](../artifacts/canonical-v1-validation-summary.json)
links the [full results](../artifacts/canonical-v1-full-results.json),
[raw attempts](../artifacts/canonical-v1-full-benchmarks.jsonl), 37 passing host
tests and 16 passing client tests. The separate staged run passed all 22
scenarios across 112 measured transactions. All 453 local measurement rows
passed the evidence-schema checks.

The explicit fallback still performs five transactions per operation. Its
fresh measured totals, including stage creation and every upload, are:

| Staged XMSS operation | Total serialized bytes | Total local CUs | Final execution bytes |
|---|---:|---:|---:|
| SOL withdrawal | 4,532 | 492,059 | 674 |
| Mock USDC withdrawal | 4,726 | 517,806 | 771 |
| Burn two target leaves | 4,470 | 468,423 | 643 |
| Rotate root and public seed | 4,590 | 491,684 | 703 |

Each staged sample created 2,625 temporary account bytes and paid 30,000
lamports in total transaction fees; each inline sample created zero temporary
witness bytes and paid 5,000 lamports. The staged accounts remain allocated;
no refund is claimed. These runs used different isolated signatures and
fixtures, so their CU differences are **not** a paired measurement of transport
overhead. Source: the summary above and
[staged client results](../artifacts/canonical-v1-staged-results.json).

A separate funded transport control already confirmed and finalized a
2,036-byte v1 Memo transaction using 649,988 CUs, with byte-identical network
retrieval and version-1 decoding. The same Memo with a one-CU inline limit
failed simulation after consuming exactly one CU, with runtime logs identifying
meter exhaustion. This establishes oversized v1 transport and that CU control
on devnet; it is not an XMSS custody measurement. Sources:
[probe summary](../artifacts/v1-devnet-transport-result.json),
[confirmed receipt](../artifacts/devnet-transactions/v1-funded-transport-probe.json),
[low-CU control](../artifacts/v1-devnet-low-compute-probe.json),
[Explorer transaction](https://explorer.solana.com/tx/4iG3KScZ3yC1UhjNKtc57pfz7XtFs5bJAwYdfUcNWoDEhS8GoEgqvb3s5xiCVoWuerwGVR9H2safCFdqyp3MPMC7?cluster=devnet).

## Confirmed devnet deployment and vaults

Program [`HssAePJfZrERFjEAhm89nY9Tc9BWAobxp2GqGhefNK6V`](https://explorer.solana.com/address/HssAePJfZrERFjEAhm89nY9Tc9BWAobxp2GqGhefNK6V?cluster=devnet)
is executable. The dumped onchain binary matches the fresh 124,464-byte SBF
and SHA-256 above. Mock mint
[`41BK2eVZsGdua58DFz3U7ydMd7bBqZbumTNbv61RpZgS`](https://explorer.solana.com/address/41BK2eVZsGdua58DFz3U7ydMd7bBqZbumTNbv61RpZgS?cluster=devnet)
has six decimals, the SPL Token Program owner and no freeze authority. Its mint
authority remains trusted. [Deployment receipt](https://explorer.solana.com/tx/4RstPT79ifVUkbV1EzRf5xCuyumfipdw16gTmga4VNrG7qC1iYHNj3KsgV6Y2vBmpvSTfC3G7tzGE4yssN9upyrw?cluster=devnet)
and [public manifest](../artifacts/public-deployment.json).

The three initialized vaults have distinct state and receiving accounts.
Send SOL to the treasury and Mock USDC to the token account; the state PDA
stores authority and policy.

| Mode | Vault state PDA | SOL treasury | Mock USDC token account |
|---|---|---|---|
| Array | `42FviRigMXDQrpe6VjDd6htSU2uiomYrLCUgjBQb88pu` | `CZws1WQuBbDGKNmfyQBQr2dh96J29kMaySP4CW9MrAru` | `EhYdR2pcWssWtuEWos62NWKNuj6u9jPhZH2TTDXq8avz` |
| Merkle | `AnWeB6VGu8JEtYQhUiYqsTkV67yzgUcc3dmsB43RNtHK` | `EfKbhDHzpKRHCUU57NvJMdiNcesHkzAbr7xYfMgViwK8` | `H61ZX58hFXsnmGCYPLHx5TrHmQFXVyuzrpPYQ75tGDdt` |
| XMSS | `2XKaDsFdizBjutyRD2BLxNd2wF2J11Do5CbcxSbCG7dj` | `ExUjnwyEprLp2oMppaTca8zN6Ae7qqF5eeMJm5MTRFco` | `EZ6aP4ekd8uCW1VP8YrnJZf9W7gwBZcgH7zwPv45D4oJ` |

The public RPC reports `solana-core 4.4.0-beta.0`, feature set `1855282951`,
on genesis `EtWTRABZaYq6iMfeYKouRu166VU2xqa1wcaWoxPkrZBG`. The deployment
runner used commit `d4e854806e74933e3279d7574d578fd39358a102`;
the custody demonstration used `8b2fc08b077990afc4fcb81a18d3ee5642e1a9bb`.

The CLI upload exhausted bounded retries under RPC throttling. Deployment
resumed with paced official upgradeable-loader writes, compared the complete
buffer against the binary, then atomically created and deployed the program.
Accepted 1,200-byte payload writes were 1,436-byte v1 envelopes. Larger loader
writes were separately rejected; that is loader recovery evidence, not an XMSS
custody size result.

## Execution and resource limits

Solders 0.29.0/LiteSVM decodes and executes v1, but this binding does **not**
enforce serialized v1 CU or loaded-account limits. The inline local harness
explicitly applies a 1.4-million-CU runtime override and labels every relevant
record. Local consumption values describe that execution environment; they do
not establish enforcement of the transaction's inline configuration.

Devnet **simulation** rejected the exact same journaled authorization with a
one-CU limit (`ProgramFailedToComplete`, one CU consumed, explicit meter
exhaustion in the logs) and a one-byte loaded-account limit
(`MaxLoadedAccountsDataSizeExceeded`). With the ordinary limits, that
unchanged intent and signature then confirmed at 518,509 CUs. The witness digest
and message commitment match across both controls and the accepted receipt.
These are simulated rejection controls followed by confirmed execution;
no rejected control is described as a confirmed transaction.

The devnet array/Merkle fixtures use 16 leaves (Merkle height 4); the canonical
local comparison uses 256. XMSS retains its standardized 1,024-leaf parameter
set in both environments. Array/Merkle devnet byte and CU values therefore
belong to their own fixture, rather than the local 256-leaf comparison.

The 16-leaf devnet bearer-secret withdrawals also confirmed:

| Mode | Asset | Complete signed bytes | Confirmed CUs |
|---|---|---:|---:|
| Array | SOL | 677 | 7,101 |
| Array | Mock USDC | 774 | 9,512 |
| Merkle | SOL | 805 | 8,003 |
| Merkle | Mock USDC | 902 | 10,413 |

## Signing, attacks and custody

The confirmed rotation preserved the XMSS treasury and token receiving
addresses and both custody balances while installing a fresh root/public seed.
The new root then withdrew both assets; the final XMSS state is epoch 1, nonce
6. Devnet simulations rejected destination substitution with `Custom(12)` for
both assets before and after rotation. An unused old-epoch authorization was
rejected after rotation with `Custom(8)`, a stale-intent policy rejection.
The deeper old-root/current-epoch signature check remains a local runtime test.

The signer reserves a leaf durably before invoking the pinned C reference and
stores the exact intent/signature before release. Preparing another outer
transaction does not sign a different XMSS message. The devnet runner persists
prepared authorizations and outer transactions, reconciles pending signatures,
and checks both treasury debits and recipient credits.

Local SVM coverage includes destination and amount substitution, altered burn
targets and replacement authority, replay, consumed/burned leaves, unchanged
authorization retry, and post-rotation spending. Rotation must preserve treasury
and token receiving addresses and balances while advancing epoch/nonce and
installing a fresh root. Stale old-epoch rejection is distinct from verification
failure for an old-root signature carrying current epoch fields.

Ten [native Rust tests](../artifacts/v1-native-program-test-results.json)
passed at program commit `912537badf94776849a5068aa44b5e30c6c2114c`
with host rustc/cargo 1.96.1; their custody and test sources match the canonical
checkout. They independently exercise inline/staged parity, malformed
witness lengths/framing, signature rejection without pre-transfer mutation,
burning and fresh/old-root behavior. Their public disposable vectors come from
the pinned C reference at `171ccbd26f098542a67eb5d2b128281c80bd71a6`;
[fixture provenance](../program/tests/fixtures/README.md) and generator are
committed. Host tests do not establish SVM rollback or token CPI behavior.

## Reproduce

Use Agave 4.3.0/platform-tools 1.57 and the locked dependencies:

```sh
bash scripts/infrastructure-replay.sh
cargo test --locked --manifest-path program/Cargo.toml
python -m client.cli --adapter svm demo-xmss
python -m client.cli --adapter svm --xmss-transport staged demo-xmss
```

Shared-network demonstrations require the dedicated devnet credentials and
their current private journals. Never fund deterministic public vectors, reuse
an old signing journal, or infer safe leaf availability from the chain bitmap.
The stable-address claim is within one program ID and cluster. The ordinary
Ed25519 upgrade authority and explicit demo administrator remain trusted; the
mock mint authority is retained. This is an unaudited research prototype, not
whole-system Ed25519 independence or production recovery. No mainnet or real
USDC is involved.
