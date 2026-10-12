# Solana Bunker

A research proof of concept comparing SHA-256 secret arrays, Merkle-committed bearer secrets and reference-compatible XMSS-SHA2_10_256 authorization over one stable Solana treasury. Native SOL and a six-decimal **Mock USDC — test token, no real value** mint are the two assets.

**XMSS operations now default to one inline v1 transaction, confirmed on devnet.** SOL and Mock USDC withdrawals, leaf burning and root rotation carry the unchanged canonical intent and full 2,500-byte signature through the existing custody verifier. The explicit staged fallback remains available. See the [v1 execution report](reports/v1-single-transaction.md) for measured results, transport limits and evidence status.

## Reproduce locally

Use Python 3.13.5 (the current measured environment) with `python3 -m pip install -r requirements.txt`, GCC/OpenSSL development headers, Rust, and Agave 4.3.0 `cargo-build-sbf` with platform-tools 1.57. Set `BUNKER_SOLANA_BIN` and `BUNKER_CARGO_BIN` to their binary directories if needed. Dependencies are locked.

```sh
bash scripts/infrastructure-replay.sh
```

This builds both SBF programs, builds the pinned C reference, generates disposable vectors, runs host tests and replays the full local-SVM harness with 20 principal samples. No private developer credential or public-cluster funding is needed for local replay. The [current build manifest](artifacts/v1-integration-environment.json) records the fresh binary and source digests. [Earlier clean-build evidence](artifacts/clean-build-origin.json) reproduces the separately labeled staged baseline from an exported source tree.

Individual actual local-SVM demonstrations:

```sh
python3 -m client.cli --adapter svm demo-array
python3 -m client.cli --adapter svm demo-merkle
python3 -m client.cli --adapter svm demo-xmss
python3 -m client.cli --adapter svm --xmss-transport staged demo-xmss
python3 -m client.cli --adapter svm benchmark --samples 20
```

The 16-leaf benchmark uses five samples per asset to preserve leaf space; larger trees use the requested count. Array/Merkle retain legacy transport. Inline XMSS local execution uses a disclosed 1.4-million-CU runtime override because LiteSVM does not enforce serialized v1 limits. For the dependency-light host model, select `--adapter host` explicitly. Host output is labeled `host_reference` and is separate from SVM execution. See [client instructions](client/README.md) for private journal isolation, canonical amounts and exact retry rules.

## Results and evidence

- [Current v1 report](reports/v1-single-transaction.md), [status](reports/status.md), [earlier research handover](reports/final-research-handover.md), [four milestones](reports/milestones/).
- [Whitepaper](research/whitepaper.md), [measured comparison](research/results-summary.md), [claim limits](research/limitations.md).
- [Fresh local validation](artifacts/canonical-v1-validation-summary.json), [confirmed devnet results](artifacts/v1-devnet-validation-summary.json), [earlier staged results](artifacts/validation-svm-results.json).
- [Client/API contract](reports/interfaces.md), [earlier staged runtime events](artifacts/client-svm-xmss-final.json), [presentation outline](research/presentation-outline.md).

The earlier staged baseline used custody binary `8d7435ea6225ef4b09e972cef7ed3d2b99f7f4e1d1b9e9f8aa5124a0848f6e25` and run `validation-20261012T135652`. It remains a separately labeled comparison; current inline measurements and their exact binary/source identity belong to the v1 report.

## Devnet

The [public manifest](artifacts/public-deployment.json) records the executable program, six-decimal mock mint and three initialized vaults. All ten custody operations confirmed, including six single-transaction XMSS operations. SOL withdrawal is 3,117 bytes / 518,509 CUs; token withdrawal is 3,214 bytes / 532,564 CUs. Burn, rotation, post-rotation withdrawals and Explorer links are in the [v1 report](reports/v1-single-transaction.md). Rejection controls are separately labeled devnet simulations.

The genesis-checked deployment and demonstration scripts use dedicated confidential credentials and persistent signing journals. Local demos require neither. No mainnet or real USDC is authorized.

Ordinary program upgrade authority and explicit demo administration remain trusted and outside the simulated relayer/funding-key compromise. Public deterministic vectors are disposable and must never back a funded shared-cluster vault. The public source package excludes credentials and live signer state. This is not an audited production wallet, whole-system independence from Ed25519, or a claim of real cryptanalysis.
