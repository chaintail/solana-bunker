# Tests, measurements, and research evidence

## 1. Experimental design

Use equivalent fixture sizes and transfer intents across authorization modes. Compare both SOL and mock USDC. Distinguish initialization/setup, verifier-only execution, and full withdrawal cost.

The tests must distinguish **expected vulnerability**, **expected rejection**, and **unexpected defect**. An attacker redirecting a naive bearer-secret withdrawal is a successful demonstration. The equivalent outcome in XMSS mode is a failed security test.

Run adversarial scheduling in isolated local fixtures. Submit the attacker transaction first after deliberately disclosing an unexecuted witness. Do not spend time building a public-network interception pipeline or claim that the harness performs real cryptanalysis.

Use a different ordinary funding/relayer fixture from the development administrator. Give the attacker the fixture keys, not the upgrade key, demo-mode administrator, mock mint authority, mnemonic, or XMSS secret seeds. Record this scope in every attack summary. No public key disclosure campaign or mainnet bounty is part of this sprint.

## 2. Acceptance matrix

The validator worker may expand this matrix, but should not replace the core demonstration with a large unrelated security audit.

| ID | Test | Required outcome |
|---|---|---|
| F01 | Initialize state and treasury | Deterministic addresses; correct ownership and association |
| F02 | Duplicate initialization | Rejected; authority/balances unchanged |
| F03 | Deposit and withdraw SOL | Exact base-unit movement; rent reserve preserved |
| F04 | Deposit and withdraw mock USDC | Exact token movement; six-decimal mint and source authority checked |
| F05 | Substitute state, treasury, mint, token program, or source account | Rejected before unauthorized movement |
| F06 | Wrong writable/signing privileges or disallowed account alias | Rejected without partial vault state changes |
| A01 | Valid unused array secret | Withdrawal succeeds for each asset |
| A02 | Incorrect/out-of-range/consumed array slot | Rejected |
| A03 | Copy pending secret; substitute destination | Attacker succeeds under declared first-included ordering |
| A04 | Replay after consumption | Rejected |
| M01 | Valid Merkle secret/path | Withdrawal succeeds for each asset |
| M02 | Corrupt sibling, index, direction, or proof length | Rejected |
| M03 | Copy pending secret/path; substitute destination | Same bearer weakness remains |
| M04 | Compare array/Merkle at 16/256/1,024 leaves | Actual storage/proof/transaction/CU data saved |
| X01 | Reference-valid XMSS signature | Host and SVM agree; full withdrawals succeed for each asset |
| X02 | Change signature chain byte, authentication node, index, or public seed | Rejected for the intended verification/format reason |
| X03 | Change amount, destination, mint, action, or burn list | Rejected; signed effect cannot be substituted |
| X04 | Copy identical valid authorization | At most one intended effect; never attacker-chosen redirection |
| X05 | Replay, stale nonce, stale epoch, wrong vault/program namespace | Rejected |
| X06 | Relayer/funding Ed25519 key only; no hash authorization | Rejected in XMSS mode |
| B01 | Valid burn request from a fresh leaf | Target leaves and authorizing leaf consumed; unrelated leaves unaffected |
| B02 | Try a burned leaf; tamper with burn list | Rejected |
| B03 | Duplicate/already-burned/out-of-range burn inputs | Chosen bounded policy enforced and documented |
| R01 | XMSS-authorized rotation to fresh root/public seed | Epoch advances; treasury/token addresses and balances unchanged |
| R02 | Unused old-root authorization after rotation | Rejected; new-root withdrawal succeeds |
| R03 | Malicious replacement root or mode substitution | Rejected unless explicitly authorized |
| S01 | Transaction fails after an authorization was signed | Chain state rolls back; client does not reuse leaf for a different message |
| S02 | Retry exact inner authorization in fresh outer envelope | Succeeds when still current and underlying execution condition is fixed |
| S03 | Two different messages requested for one local leaf | Signer refuses; isolated adversarial tests may bypass client deliberately |
| D01 | Change active mode using explicit demo administration | Receiving addresses stay fixed; inactive-mode withdrawal is rejected |
| D02 | Final branch contains temporary bypass | Remove it or scope/document it as trusted administration; no hidden fallback |

For X02/X03, confirm the fixture reaches the relevant verifier rather than failing solely on an unrelated insufficient balance, account mismatch, or stale nonce. Early policy rejections are valuable too, but label them accurately. Do not weaken normal cheap checks just to measure deep invalid paths; prepare a valid surrounding fixture.

For S02, an insufficient-balance failure is a simple scenario: retain the exact authorization, deposit the missing test amount, then submit a fresh outer transaction. Restoring a test snapshot is not evidence of real-world mnemonic recovery.

## 3. Benchmark collection

Start with a small smoke sample, then aim for roughly 20 local measurements per principal success case and several invalid cases. A few confirmed devnet examples per mode/asset are sufficient for deployment evidence; do not exhaust the sprint or faucet quota gathering cosmetic statistics. Record actual sample counts. Include min/median/max and late-invalid cases; do not report a mean as a worst-case bound.

Keep build flags and transaction configuration comparable. If a mode uses staging, compare **total logical-operation cost** as well as the final transaction. If measurements use a different runtime or transaction version, keep separate groups.

Record:

- Signature/witness bytes, proof bytes, instruction-data bytes, and **full serialized transaction bytes**.
- Requested and consumed compute units; success/error stage; instrumented hash-call counts where available.
- Logical authority bytes versus total allocated account bytes, usage bitmap, rent-exempt funding, and any temporary-account storage.
- Setup transaction count, per-withdrawal transaction count, observed fees, and storage deposits/refunds separately.
- Reference key-generation/signing/host-verification time as optional host metrics, clearly separated from onchain CUs.
- Environment, commit, program binary digest, parameter set, fixture, command, and raw-evidence location.

Null means “not measured/not applicable,” never zero. An RPC timeout is not a confirmed program rejection. Label simulation separately from confirmed network execution. The data should be auditable without reading the entire conversation.

## 4. Suggested evidence layout

Workers may adapt names to the repository, but preserve these artifact categories:

```text
reports/
  status.md
  decisions.md
  interfaces.md
  early/E1-wallet-environment.md
  early/E2-v1-transport.md
  early/E3-xmss-feasibility.md
  milestones/M1-foundation.md
  milestones/M2-array.md
  milestones/M3-merkle.md
  milestones/M4-xmss.md
  final-research-handover.md
research/
  whitepaper.md
  results-summary.md
  sources.md
  limitations.md
artifacts/
  public-deployment.json
  benchmarks.jsonl
  benchmark-summary.csv
  demo-events.jsonl
  test-results.json
  evidence-index.json
  logs/
  public-vectors/
```

Do not pre-fill these with invented measurements. Keep actual secrets in an ignored, private location outside public artifacts. A public reference fixture may contain explicitly disposable test secret inputs if necessary for reproducibility, but those inputs must never back a funded shared-cluster vault.

## 5. Benchmark record contract

Use one record per measured attempt, plus a logical-operation ID to group staged transactions. The integration worker should implement a lightweight validator for required fields. This illustrative shape is a schema example, not a result:

```json
{
  "schema_version": 1,
  "run_id": "TO_BE_GENERATED",
  "operation_id": "TO_BE_GENERATED",
  "observed_at_utc": null,
  "commit": null,
  "program_binary_sha256": null,
  "environment": {
    "evidence_level": null,
    "cluster": null,
    "genesis_hash": null,
    "runtime_version": null,
    "toolchain_manifest": null
  },
  "experiment": {
    "mode": null,
    "parameter_set": null,
    "asset": null,
    "mint": null,
    "leaf_count": null,
    "scenario": null,
    "fixture_id": null,
    "command": null
  },
  "outcome": {
    "expected": null,
    "observed": null,
    "test_passed": null,
    "error_code": null,
    "failure_stage": null,
    "verifier_reached": null
  },
  "transport": {
    "version": null,
    "transaction_index": null,
    "transaction_count_for_operation": null,
    "transaction_bytes": null,
    "instruction_data_bytes": null,
    "signature_or_witness_bytes": null,
    "merkle_proof_bytes": null,
    "transaction_signature": null,
    "confirmation_status": null
  },
  "resources": {
    "compute_limit": null,
    "compute_consumed": null,
    "sha256_syscall_count": null,
    "allocated_account_bytes": null,
    "logical_authority_bytes": null,
    "storage_deposit_lamports": null,
    "storage_refund_lamports": null,
    "actual_transaction_fee_lamports": null
  },
  "evidence_paths": []
}
```

Suggested measured `evidence_level` values: `host_reference`, `local_svm`, `local_validator`, `devnet_simulation`, `devnet_confirmed`. Keep theoretical size calculations in a clearly separate specification/estimate dataset. Serialize large monetary integers without losing precision, for example as decimal strings in JavaScript-facing JSON.

## 6. UI-ready demo events

No visual UI is required now. Emit JSON records for events such as `vault_initialized`, `deposit_observed`, `authorization_prepared`, `withdrawal_confirmed`, `withdrawal_rejected`, `leaves_burned`, `authority_rotated`, and `attack_result`.

Include event version, run/operation IDs, mode, asset, public addresses, epoch/index, message commitment, witness bytes, CUs, before/after balances, network/local evidence label, and transaction/evidence link where available. Distinguish client narration from actual onchain events. Never emit mnemonic, secret seeds, unused one-time passwords, or secret signing state. The naive attack harness can share its witness internally without publishing unrelated secrets in the event feed.

The later frontend should be able to show: **same treasury → changed authorization → changed storage cost → attack result → verified transfer**, without reimplementing cryptography.

## 7. Research write-up and final package

Write a concise Markdown research paper incrementally: question and threat model; related work; three constructions; implementation; methods; measured results; limitations; future work. Keep upgrade/recovery limitations short and clear. Discuss SLH-DSA only at the level actually researched or implemented.

A technical reviewer should be able to map each results claim to an experiment ID and artifact. No claim that ECDSA/Ed25519 has actually been broken, no security deadline speculation, and no novelty claim that ignores existing Winternitz vaults.

Prepare one clean command per demonstration plus a full local replay command. Package public artifacts, reports, source/build instructions, and a brief presentation outline. The tone can be playful: “You've watched a hundred startup pitches. Unfortunately, this one contains math.” Then make the experiment concrete rather than overselling it.

Do not build slides or the final UI in this sprint unless the user separately requests them. A short narrative and structured evidence are the handoff.
