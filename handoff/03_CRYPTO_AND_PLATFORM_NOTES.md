# Cryptographic target and platform notes

These are implementation starting points and externally checked reference facts, not experimental results. User-approved scope is in the research brief. Pin the actual versions you use and measure in the selected environment.

## 1. Core target: full XMSS, not an improvised signature

Use **`XMSS-SHA2_10_256`**, specified in RFC 8391: hash output 32 bytes, WOTS+ parameter 16, 67 chains, tree height 10, and 1,024 signing leaves. Its raw signature is **2,500 bytes**: 4-byte index, 32-byte randomization value, 2,144-byte WOTS+ component, and 320-byte authentication path. The public material is a 32-byte root plus a 32-byte public seed; some APIs add a parameter identifier. Document the exact wrapper/serialization rather than assuming every API reports the same length. [S01, S02]

Follow the complete reference-compatible construction: message processing, WOTS+ checksum/chains, address-dependent hashing, public-key compression, and authentication-path verification. Do not replace the XMSS tree with the simple Merkle-secret tree from Demo 2 or substitute plain `SHA256(intent)` for its specified message processing. [S01]

Implement against independently generated reference vectors. Self-written signer and verifier agreeing is insufficient. Test selected boundary indices, changed messages, changed public seeds, malformed encodings, and authentication-path corruption. Pin the reference commit and license. A library name or a NIST-related parameter set is not evidence of an audit, formal verification, or NIST implementation compliance. [S02, S03]

Host key generation/signing can use a reference process while the onchain verifier is Rust; there is no requirement to port a sophisticated signing implementation to the SVM. Preserve a simple client interface for later integration.

## 2. Minimal signer state — enough for the experiment

Stateful hash-based signatures require avoiding reuse of one-time signing material for different messages. Persist signing progress independently of transaction confirmation. [S03]

For this PoC, implement one writer per signing keyset:

1. Atomically reserve/retire the leaf in a durable local journal before releasing a signature.
2. Persist the exact canonical intent and signature so retries reuse the same bytes.
3. On uncertain signing failure, abandon that leaf and use a fresh one; onchain `burn_leaves` can subsequently retire uncertain indices.

No multidevice recovery service is required. The onchain bitmap describes accepted/burned uses, not every signature exposed offchain. A restored mnemonic alone is not permission to resume at the first onchain-unused index.

### Deterministic development seed

Support a dedicated BIP-39 mnemonic plus optional passphrase, or a documented deterministic test-seed entry point while the core benchmark is being built. Final demo tooling should document how the dedicated mnemonic reproduces key material. BIP-39 seed generation and XMSS key derivation are separate operations. [S12]

Use a versioned, domain-separated KDF with an established primitive, such as HKDF-SHA-256, to supply the scheme's seed inputs. Specify labels, lengths, byte order, vault identifier, mode, and fresh authority generation. Separate array/Merkle fixture material from XMSS secret/public-seed inputs and from Ed25519 fixture keys. This outer seed recipe is a **project convention**, not part of BIP-39 or an invented BIP-32 path standard. [S13]

Persist a fresh generation identifier for replacement trees. Do not regenerate and reuse the current tree merely because the local counter was lost. Keep mnemonic-recovery UX and alternate recovery authorities out of core scope.

## 3. Merkle-secret baseline is intentionally simpler

For the array, use 32-byte random secrets and SHA-256 commitments. For the Merkle baseline, authenticate those commitments under an ordered binary tree. Define a small domain-separated leaf/internal-node encoding, bind the leaf index, enforce the exact tree height, and validate path direction. This is the project's pedagogical commitment scheme, **not XMSS**.

For powers of two, the raw comparison is:

| Leaves | Array commitments | Merkle siblings per witness | Raw sibling bytes | Bitmap bytes |
|---:|---:|---:|---:|---:|
| 16 | 512 | 4 | 128 | 2 |
| 256 | 8,192 | 8 | 256 | 32 |
| 1,024 | 32,768 | 10 | 320 | 128 |

These are arithmetic design sizes, excluding metadata, alignment, the revealed secret, index, and transaction envelope. They are **not measured account sizes**. The root compresses public commitments but does not bind a bearer secret to a withdrawal destination.

## 4. v1 transport: verify the actual path

Current Solana documentation describes **4,096-byte v1 transactions**, with resource configuration in the message, inline addresses rather than ALTs, and legacy/v0 remaining separate formats. Explicitly configure compute and loaded-account-data limits. Larger submissions use base64; clients reading v1 transactions also need the appropriate supported-version setting. [S08, S09]

Run the E2 probe using the actual SDK, RPC, and selected cluster. Do not use an old hand-built byte estimate as proof. Record the complete serialized transaction including signatures, account keys, instruction framing, and configuration. The signature/public key do not need to be redundantly transmitted if the required public material is already in validated state.

If transport tooling blocks a direct withdrawal, staged witness storage is an allowed fallback. A program-owned account may receive bounded chunks, then become sealed against mutation. Bind the complete intent, witness, vault, mode, epoch, and nonce to verification. No funds move during upload. A final verified execution consumes authorization state and may close the temporary account to a predetermined refund destination. Count every upload and finalization transaction; do not imply cross-transaction atomicity.

## 5. Compute: benchmark the implementation, not a flat hash estimate

Solana documents a **1.4-million-CU transaction ceiling**. Exact hashing charges come from the selected runtime's syscall/cost implementation and input shape. [S10, S11]

The prior discussion's illustrative per-hash multiplication is not a measured XMSS budget. Nor should a reference algorithm's abstract hash-operation count be equated automatically with SHA-256 syscalls or compression blocks.

Run a short SHA-256 microbenchmark with representative input lengths and 1/512/1,024/2,048 repeated calls where they fit. Prevent compiler elimination by chaining outputs and checking a result. Record raw CUs, loop baseline, lengths, number of slices, syscall invocations if instrumented, runtime version, and failures. Profile the full verifier separately: WOTS+ reconstruction, public-key compression, authentication path, parsing, and transfer overhead where practical. Never mix instrumented and uninstrumented results without labeling them.

Prefer runtime hashing when it faithfully implements the required operation. Avoid copying a large signature and reconstructed public key onto a small SBF stack frame; borrow slices or use deliberately bounded workspace. Measure heap/stack limitations independently from transaction capacity. Allocating a larger account for signature bytes does not increase the transaction's execution budget.

## 6. Optional SLH-DSA investigation

The exact name is **SLH-DSA**, standardized in FIPS 205. Start an optional investigation with `SLH-DSA-SHA2-128s`, whose signature is **7,856 bytes**. It cannot fit in a single 4,096-byte transaction. It is a stateless signing scheme, not a claim that the vault no longer needs replay state. [S14]

Determine upload count from measured usable instruction payload, not `ceil(signature_size / 4096)`. For example, **if** usable chunks are 3,500 bytes, the signature needs three uploads, plus initialization/finalization unless safely combined. This is illustrative arithmetic only. Compute feasibility must be checked independently.

Preferred stretch narrative: compact stateful XMSS for spending, stateless authorization for rare root changes. Do not wire a second administrator path until the standalone verifier and its data protocol work. A documented host test, exact byte count, or measured SVM blocker is a legitimate stretch result; label it as such.

## 7. Terminology and claim boundaries

Use **hash syscall**, **signature verifier**, **leaf index**, **action nonce**, **authority epoch**, and **PDA signer privilege** distinctly. XMSS still uses WOTS+; moving to XMSS does not abandon Winternitz. Do not describe SHA-256 itself as a password or a signature scheme.

The final report should say what ran, under which assumptions. Ordinary development-key upgrade control is intentionally retained; no “every Ed25519 key can be compromised safely” claim applies to that administrator. Keep that limitation short and visible rather than building a recovery/governance product during this sprint.
