# Client and signing state

Actual compiled-SBF demonstrations in isolated LiteSVM fixtures are:

```sh
python -m client.cli --adapter svm demo-array
python -m client.cli --adapter svm demo-merkle
python -m client.cli --adapter svm demo-xmss
python -m client.cli --adapter svm benchmark --samples 20
```

These commands use `tests/svm_harness.py`, the built program binary at
`program/target/deploy/bunker_program.so`, and solders 0.29.0. They execute real
SBF custody and SPL-token CPIs, check balances, demonstrate both asset attacks,
burning, signed root rotation and exact durable retry. Each run has fresh
disposable local signing keysets and emits separate `artifacts/client-svm-*`
event/benchmark files. XMSS defaults to one `MessageV1` transaction per
logical operation, containing the canonical intent and complete 2,500-byte
signature inline. SOL/token withdrawals, leaf burns, root rotation, attacks,
replay and exact retry all use this same transport. Array/Merkle retain their
legacy transport.
Runtime CUs and full serialized transaction bytes come from real metadata.
There is no devnet confirmation in these commands. Small 16-leaf benchmarks
use five successful samples per asset to leave room for attacks and burning;
256/1024-leaf and XMSS cases can use twenty.

The v1 message explicitly requests 1,400,000 CUs, 1,048,576 loaded account-data
bytes and a 32,768-byte heap. It contains no legacy ComputeBudget instruction.
The builder measures the fully signed serialization and rejects envelopes over
4,096 bytes. **LiteSVM 0.29.0 does not enforce those serialized inline limits.**
The local XMSS fixture explicitly sets LiteSVM's execution budget to 1,400,000
CUs; each raw log and benchmark row records that runtime override separately
from the serialized configuration and measured consumed CUs. Local execution
does not establish devnet resource enforcement or confirmation.

To select the sealed-account legacy fallback explicitly:

```sh
python -m client.cli --adapter svm --xmss-transport staged demo-xmss
python tests/svm_harness.py --demo xmss --full --xmss-transport staged
```

Staged XMSS consumes five transactions per logical operation: initialization,
three bounded uploads and execution. Temporary accounts remain allocated;
no refunds are claimed. The transport choice does not change canonical intent
bytes or authorize signing the same leaf again. An exact retry reuses the
durably recorded signature and can refresh only the outer transaction.

The shared devnet transaction assembly API is:

```python
from client.transport import execute_instruction, build_xmss_transaction

# intent and signature were already reserved/signed by SigningJournal.
# accounts: state W, treasury W, mint, source W for tokens,
# destination W for withdrawals, Token Program.
instruction = execute_instruction(intent, signature, accounts)
transaction = build_xmss_transaction(payer.pubkey(), [payer], [instruction], blockhash)
serialized = bytes(transaction)
```

Submission uses base64 encoding; retrieving a v1 transaction requires
`maxSupportedTransactionVersion: 1`. The public-cluster runner owns submission
and confirmation; local signatures must not be labeled confirmed network
transactions. Shared-cluster signers require fresh private keys and durable
journals, never the disposable harness vectors.

From the repository root, the standalone disposable host demonstrations are:

```sh
python -m client.cli --adapter host demo-array
python -m client.cli --adapter host demo-merkle
python -m client.cli --adapter host demo-xmss
python -m client.cli --adapter host benchmark
python -m unittest discover -s client/tests -v
```

XMSS commands require `bash crypto/build_reference.sh` first. The signer is the
pinned C reference wrapper; custody is explicitly the Python host model here.
Host commands do not provide evidence of SVM execution or network transactions.
Output JSON labels every event `host_reference`; missing CUs/transaction IDs are
null. Public benchmark comparison contains measured raw commitment/proof bytes,
not allocated Solana account bytes or rent savings.

A persistent disposable fixture can be exercised with these commands:

```sh
python -m client.cli init --mode xmss --fixture private-host-demo
python -m client.cli inspect
python -m client.cli deposit-sol --amount 1000000
python -m client.cli deposit-mock-usdc --amount 1000000
python -m client.cli withdraw --asset sol --amount 100 --operation-id sol-1
python -m client.cli withdraw --asset mock-usdc --amount 100 --operation-id token-1
python -m client.cli burn-leaves --targets 8 9 --operation-id burn-1
python -m client.cli rotate-root --operation-id rotate-1
python -m client.cli inspect
```

Use separate `--state-file` and `--journal-dir` for isolated workers/fixtures.
Flags precede the subcommand. Amounts are integer base units. Token destination
is an actual token-account address, not a recipient wallet. The host default
addresses are deterministic, explicitly disposable fixtures and must never be
funded on any shared cluster. Journals and host state are restricted to local
private files; exported events contain only public identities, hashes and sizes.

## Retry and uncertain failure

```sh
python -m client.cli withdraw --asset sol --amount 2000000 --operation-id too-large
# After the above reports insufficient balance, add funds without signing again:
python -m client.cli deposit-sol --amount 2000000
python -m client.cli retry --operation-id too-large
```

`retry` loads the exact durable canonical message and signature. Outer transport
details are intentionally absent from the signed intent. An already executed
operation is rejected by the current nonce/bitmap. A crash or uncertain signing
failure abandons that leaf; use a fresh operation/leaf, and burn the uncertain
leaf onchain when useful. A reserved leaf is durably committed before invoking
the signer, and a signature is durably stored before it is returned. One OS lock
permits one writer to a keyset journal. A copied journal or seed restoration on
a second computer is outside this single-writer experiment and is not safe.

## Reproducing dedicated mnemonic key material

`client.kdf.bip39_seed(mnemonic, passphrase)` implements NFKD-normalized
PBKDF2-HMAC-SHA512, 2,048 iterations, 64 bytes, with salt `mnemonic` concatenated
with the NFKD-normalized passphrase. It converts a mnemonic to a seed; callers
must separately validate mnemonic entropy/checksum using their BIP39 wallet.
The unit tests independently include the published `abandon ... about` /
`TREZOR` vector. This public test mnemonic must never back a funded vault.

For a dedicated validated mnemonic, derive `(SK_SEED, SK_PRF, PUB_SEED)` with:

```python
from client.kdf import bip39_seed, xmss_seeds
from crypto.xmss import keygen
master_seed = bip39_seed(dedicated_mnemonic, optional_passphrase)
seed96 = b"".join(xmss_seeds(master_seed, vault_id32, fresh_generation_u64))
public64, secret132 = keygen(seed96)
```

The versioned project recipe uses HKDF-SHA256 with salt
`Solana-Bunker-KDF-v1`. Expand info is `BUNKER-SEED 00 01` || vault_id32 ||
mode u8 || generation u64LE || ASCII-label-length u8 || ASCII label.
Labels `xmss-sk-seed`, `xmss-sk-prf`, `xmss-pub-seed` each derive 32 bytes.
Mode 3 is XMSS; mode 0 deliberately shares disposable secret sets between array
and Merkle comparisons under labels `baseline-secret-<decimal index>`.
The outer recipe is a project convention, separate from standardized XMSS and
BIP39; it is not a BIP32 path.

Persist fresh generation IDs and `AuthorityHistory`; old tree reuse is refused.
Fresh rotation attempts choose a generation greater than every previously
reserved generation, including failed/uncertain attempts. Exact retries use the
generation recorded for their original replacement authority.
Mnemonic reproduction recovers key material, **not** safe signing progress.
Restore a backed-up durable journal or conservatively abandon exposed/uncertain
leaves; never start at the first onchain-unused index using a mnemonic alone.

Canonical layout, Merkle domains, shared APIs and public vector contract are in
`reports/interfaces.md`. Actual program instruction transport is in
`program/src/lib.rs` and is separate from the signed inner intent.
