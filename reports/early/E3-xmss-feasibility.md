# Early update E3 — XMSS feasibility

**Status:** Partial — host interoperability passed; SVM compilation/measurement underway.
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

Infrastructure is building the SBF probe with Agave4.3.0/platform-tools1.57. Actual local SVM valid/invalid outcomes, CUs and binary digest remain unmeasured at this update. A2500-byte signature needs direct v1 or staged storage; the standalone fixture-account probe separates compute from public-cluster transport. Client has reference signing API; program has generic verifier interface. No funding wait blocks this path.
