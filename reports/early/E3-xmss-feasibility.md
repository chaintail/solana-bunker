# Early update E3 — XMSS feasibility

**Status:** Ready — reference interoperability and actual SBF verifier feasibility passed.
**Worker:** cryptography

## Exact target and host result

RFC8391 XMSS-SHA2_10_256, raw signature2500 bytes, public64 root||public_seed, height10 and1024 leaves. Generic Rust no_std+alloc verifier implemented with exact H_msg, WOTS+ checksum/chains, address PRFs/masks, L-tree and authentication path. Independent pinned C reference: XMSS/xmss-reference `171ccbd26f098542a67eb5d2b128281c80bd71a6`, licenseCC0-1.0, vendored original source verified by per-file manifest.

Six indices0,1,511,512,1022,1023 passed C reference verification, Python verification and native Rust verification. First five signatures are byte-identical original/patched reference signer results. Last index1023 has a separately documented minimal upstream index-control patch: the original signer prematurely zeroes seeds and yields an invalid signature. See crypto/reference-last-index.patch and crypto/README.md. The verifier reference itself is unchanged.

Native SHA256 backend calls for the six tested messages were respectively1790,1880,1790,1745,1880,1745. These are actual native instrumentation counts; they are not Solana CU measurements. Host duration is not an SVM budget estimate.

## Evidence

- artifacts/public-vectors/xmss/manifest.json and raw binary public/message/signature fixtures.
- artifacts/crypto-host-verifier.json: native outputs, per-fixture wall time, executable SHA256 and runtime version.
- crypto/reference-lock.json: exact source provenance and SHA256 digests.
- crypto/svm-probe: fixed verifier program using fixture-account transport.

## SVM and integration continuation

SBF build Agave4.3.0/platform-tools1.57 and execution solders0.29.0 LiteSVM: all42cases pass (6valid,36invalid). Valid CU counts by indices0,1,511,512,1022,1023:475220,496608,475248,464546,496643,464559. Changed message, authentication path, public seed and WOTS bytes reject after verification; out-of-range index rejects495CU and short fixture rejects466CU. The short fixture is rejected by the probe framing; other cryptographic mutations reach the verifier.

Binary SHA256: `21088f9ef0f6add41231e5ef7b19eb8ab3272f17fc493fe104df44b612c8f700`. Source commit: `ad9ccd6d33a2732fb4f8c97b5a7fb8ab2c0690a2`. Raw metadata, serialized transaction sizes, logs, fees and failures: artifacts/crypto-svm-probe.json. Fixture accounts are deliberately preinstalled; this is standalone cryptographic execution, not upload/custody/devnet evidence. The42case preliminary binary before microbench dispatch used16CU less for valid cases; quote this final recorded binary only.

Twenty repetitions per valid fixture (120SVMexecutions) all pass with identical per-fixture CUs: artifacts/crypto-svm-repeat-profile.json. SHA256microbenchmark48rows covers64/96/128byte inputs,1/512/1024/2048calls,1/3slices and deliberately separate loop-only baselines: artifacts/crypto-hash-microbench.json. The baseline workload differs and cannot be subtracted as an exact syscall-only cost model.

Recommendation: integrate full RFC8391 verifier now. Observed standalone valid budget remains below1.4millionCU, with heap workspace2144bytes and standard entrypoint32KiBheap. Do not extrapolate these fixtures to every possible intent or treat standalone success as complete custody validation. A2500-byte signature still needs verified v1 or staged storage. Client reference signing and program hashv adapter are ready; integrated SOL/token/burn/rotation tests continue independently.
