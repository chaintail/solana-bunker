# XMSS cryptography

Target: RFC 8391 `XMSS-SHA2_10_256` (OID 1), n=32, w=16, 67 WOTS+ chains, height=10, 1024 leaves. Raw signature is `index_be32 || R32 || WOTS2144 || auth320` (2500 bytes). Public material is `root32 || public_seed32` (64 bytes), without an OID. Sign the complete canonical application message directly: XMSS H_msg incorporates R, public root and index; no application prehash replaces it.

`xmss-verifier` is an allocation-bounded generic Rust verifier. It borrows signature bytes and uses a 2144-byte heap buffer for reconstructed WOTS public nodes. Its only integration dependency is the `Sha256` trait; Solana implements this with hashv. Return value is the authenticated leaf index; callers must independently validate complete message/account bindings, mode, epoch, nonce and leaf usage. `xmss.py` provides an independent Python verifier and the low-level reference signer.

## Reproduce

```sh
crypto/build_reference.sh
python -m crypto.generate_vectors
cargo run --manifest-path crypto/xmss-verifier/Cargo.toml --example verify_file -- artifacts/public-vectors/xmss/public.bin artifacts/public-vectors/xmss/0.msg artifacts/public-vectors/xmss/0.sig
cargo-build-sbf --manifest-path crypto/svm-probe/Cargo.toml --sbf-out-dir target/deploy
python -m crypto.run_svm_probe
```

C build requires GCC and OpenSSL headers/library. Rust host example links OpenSSL. Probe uses solana-program4.0.0, SBF toolchain and solders0.29 LiteSVM. C reference sources are vendored, original bytes checked against `reference-lock.json`. Public fixture seed `00..5f` is explicitly disposable and must never back a funded public vault.

## Reference and maximum-index issue

Independent implementation: https://github.com/XMSS/xmss-reference commit `171ccbd26f098542a67eb5d2b128281c80bd71a6`, CC0-1.0. Original source remains unchanged under `reference/`. Thin C ABI wrapper selects fixed parameter OID1.

The original simple sign routine zeroes secret bytes when `idx >= 2^h-1`, before computing the signature. Its SK_SEED, SK_PRF and PUB_SEED variables are pointers into that same memory, so valid last index1023 signs with cleared material. This yields a signature rejected by the unchanged reference verifier. `reference-last-index.patch` postpones this clearing until `idx >= 2^h`; full cryptographic algorithms, hash domains, parameters and encodings remain unchanged. The generated patched file is only a build intermediate. Our journal limits indices to0..1023, and caller reservations—not this in-memory counter—enforce one-time use.

Fixture indices0,1,511,512,1022 are generated with the original reference signer and verified byte-identical to the patched signer. Index1023 is explicitly generated with the patch and accepted by the unchanged reference verifier. `manifest.json` separately records the invalid original final-index result. This patch is not an audit or production signer certification.

## Signing contract

`keygen(seed96) -> (public64, secret132)` with seed96 = SK_SEED || SK_PRF || PUB_SEED. `sign_at(secret132,index,message) -> signature2500` is intentionally low-level. The client must durably reserve the index before calling, must record exact intent/signature before release, and must retry only with identical bytes. Restoring seed or observing unused onchain indices does not authorize reuse.

## Evidence boundary

Host C/Python/Rust agreement proves interoperability for tested fixtures. Actual LiteSVM runs execute SBF cryptography but initialize fixture accounts directly with set_account. They do not prove witness upload, transaction v1 compatibility, custody/account validation, nonce or bitmap rules, public deployment or SPL transfers. Those are separate program/transport tests.
