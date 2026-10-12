# E2 — Actual v1 transport probe

Status: partial; signed v1 serialization and devnet RPC transport accepted, execution/confirmation blocked by unfunded fee payer.

- SDK: official `@solana/kit 8.4.0`; runtime RPC `4.4.0-beta.0`, feature-set `1855282951`.
- Cluster: devnet, `https://api.devnet.solana.com`.
- Full serialized signed transaction: **2,029 bytes**; memo instruction data **1,843 bytes**. SDK decoded its own actual serialized bytes successfully.
- Resource settings: 1,000,000 CUs, 1,048,576 loaded-account-data bytes, 32,768-byte heap.
- `simulateTransaction` accepted base64 v1 decoding but returned `AccountNotFound`, 0 consumed CUs, no program logs.
- `sendTransaction` returned RPC `-32002`, preflight `AccountNotFound`: fee payer has no prior credit. No transaction was confirmed. Memo acceptance is not established.
- Generated transaction identifier: `3aC3ezVM1rkCZfnkzeG1NZUs4wwDD16FFFWCAukvW3BmRERinKuhbLujvJ4ZRaXS6TEkzdCzWHcUs5cUxsSva6At` (local signed identifier only, not a confirmed network transaction).
- Network retrieve/decode cannot be claimed because submission failed before inclusion. The reusable probe uses `maxSupportedTransactionVersion:1` for retrieval after a successful submission.

Raw evidence: `artifacts/v1-probe-result.json`, `artifacts/v1-probe-transaction.bin`. Reproduction: `npm run probe:v1` from project root with private developer key available. Retrying produces a new outer blockhash/signature while retaining harmless payload.

Next: funded local validator transport execution; retry devnet when developer funds are available. Staged-data application fallback and SVM verifier work proceed independently.

## Local execution follow-up

The exact 2,029-byte official SDK serialization also executed successfully in solders0.29.0 LiteSVM after a local-only credit to the fee-payer address, with expired outer-blockhash checking disabled. Actual Memo program logs report success, consuming 2,062 CUs. This establishes local v1 decode and execution for those bytes; it is not devnet confirmation. Raw evidence: `artifacts/v1-sdk-local-result.json`.

A separately constructed solders MessageV1 probe serialized to2,035bytes and also executed successfully with2,062CUs (`artifacts/v1-local-result.json`; `python scripts/infrastructure-local-v1.py`). Inline settings are serialized, but LiteSVM logs its default200,000CU execution budget; enforcement of those v1 configuration limits is not established by this local run.

Agave4.3.0 local-validator startup is blocked by the environment's unsupported `io_uring`: `Operation not permitted` followed by `assertion failed: io_uring_supported()`. No security settings were changed. LiteSVM is the working local execution harness.
