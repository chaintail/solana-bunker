# Solana Bunker

A research proof of concept comparing SHA-256 secret arrays, Merkle-committed bearer secrets and reference-compatible XMSS-SHA2_10_256 authorization over one stable Solana treasury. Native SOL and a six-decimal **Mock USDC — test token, no real value** mint are the two assets.

**The core demonstrations work in local SVM. Public devnet deployment is blocked on funding.** The final functional run passes 195 cases across 573 measured transaction attempts; 37 host tests pass. Each of the six principal mode/asset cases has 20 local measurements. Individual negative-test variants remain explicitly partial in [the acceptance matrix](artifacts/acceptance-matrix.json).

## Reproduce locally

Install Python 3.12 with `python3 -m pip install -r requirements.txt`, GCC/OpenSSL development headers, Rust, and Agave 4.3.0 `cargo-build-sbf` with platform-tools 1.57. Set `BUNKER_SOLANA_BIN` and `BUNKER_CARGO_BIN` to their binary directories if needed. Dependencies are locked.

```sh
bash scripts/infrastructure-replay.sh
```

This builds both SBF programs, builds the pinned C reference, generates disposable vectors, runs host tests and replays the full local-SVM harness with 20 principal samples. No private developer credential or public-cluster funding is needed for local replay. [Clean-build evidence](artifacts/clean-build-origin.json) records identical program digests from an exported source tree.

Individual actual local-SVM demonstrations:

```sh
python3 -m client.cli --adapter svm demo-array
python3 -m client.cli --adapter svm demo-merkle
python3 -m client.cli --adapter svm demo-xmss
python3 -m client.cli --adapter svm benchmark --samples 20
```

The 16-leaf benchmark uses five samples per asset to preserve leaf space; larger trees use the requested count. For the dependency-light host model, select `--adapter host` explicitly. Host output is labeled `host_reference` and is separate from SVM execution. See [client instructions](client/README.md) for private journal isolation, canonical amounts and exact retry rules.

## Results and evidence

- [Research handover](reports/final-research-handover.md), [status](reports/status.md), [four milestones](reports/milestones/).
- [Whitepaper](research/whitepaper.md), [measured comparison](research/results-summary.md), [claim limits](research/limitations.md).
- [Functional SVM results](artifacts/validation-svm-results.json), [raw attempts](artifacts/validation-benchmarks.jsonl), [summary CSV](artifacts/validation-benchmark-summary.csv).
- [Client/API contract](reports/interfaces.md), [structured runtime events](artifacts/client-svm-xmss-final.json), [presentation outline](research/presentation-outline.md).

Final custody binary SHA-256: `8d7435ea6225ef4b09e972cef7ed3d2b99f7f4e1d1b9e9f8aa5124a0848f6e25` (124,464 bytes). Main measured run: `validation-20261012T135652`, source `e3938925e3b2153592328ca56163b47d8686c314`; subsequent report/client/evidence commits do not change this custody binary.

## Devnet continuation

Developer public address: `AxQBVSbA3tEc8RsMhn3D4gPLBLnEu3XD84Zd9yy3pmnQ`. Selected cluster: **devnet**. Current recommendation: **2 devnet SOL**; last balance is zero. The faucet returned an RPC error. The [public manifest](artifacts/public-deployment.json) labels program and mint identifiers as prospective, undeployed/uncreated. They are not ready receiving addresses.

After funding, use the existing genesis-checked `python3 scripts/infrastructure-devnet-deploy.py` with the confidential development credentials. Then run confirmed devnet application demonstrations and record their actual accounts/transactions. No mainnet or real USDC is authorized.

Ordinary program upgrade authority and explicit demo administration remain trusted and outside the simulated relayer/funding-key compromise. Public deterministic vectors are disposable and must never back a funded shared-cluster vault. The public source package excludes credentials and live signer state. This is not an audited production wallet, whole-system independence from Ed25519, or a claim of real cryptanalysis.

