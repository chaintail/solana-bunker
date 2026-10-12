# Second custody correctness review

Reviewed source HEAD: `c7d6f60ee7ef0427154bfea451a1a594528b43ec`. Cryptography worker reviewed program/client integration; this is a bounded implementation review, not an audit or formal verification.

## Reviewed invariants

- Canonical binary offsets match client codec: magic8 + five publicidentities32 each + modeu8 + epochu64LE + nonceu64LE + leafu32LE + actionu8; header190bytes. SOL/token/burn/rotation payload lengths40/137/bounded/69 match.
- Only active mode dispatches authorization. Failed XMSS has no array/Merkle fallback and no administrator withdrawal instruction.
- Program/state/namespace/vault/treasury identities, mode, epoch, nonce and signed leaf are checked against current validated state.
- Sealed stage binds state, exact whole-intent hash, epoch and leaf. Sequential chunk writes require creator signature and stop after sealing. Whole-intent hash includes nonce and mode.
- Burns reject signer-as-target, out-of-range, unsorted/duplicate and previouslyused targets. The authorizing leaf and exact target list are atomically consumed.
- Rotation requires current XMSS over complete replacementmode/parameter/root/seed; rejects identical current64-byte authority, increments epoch+nonce, resets bitmap, preserves treasury/source. Historical reuse protection is localclient history, not onchain historical tracking.
- Native transfers exclude state/treasury/token-source aliases and preserve treasury rent. Token transfers bind canonicalprogram,mint,source,destination,amount,decimals and validate sourceowner/delegate/closeauthority; runtime CPI checks balances atomically.
- Prefunded empty system PDA handling uses systemownership/nonexecutable/emptydata checks, renttopup, canonical PDA allocation+assignment; existing deposits preserved.

## Finding and disposition

Client persistent rotation initially selected activegeneration+1 after retiring a replacement in history before signing/submission. A crash/failure then prevented fresh rotation because that generation was already recorded. Client owner changed freshselection to AuthorityHistory.next_generation and exactretry recovery to generation_for(public). Unit test test_uncertain_rotation_uses_fresh_generation covers abandonedgeneration selection. Historicalroot refusal remains.

## Reproduction boundary

Independent probe rebuild into target/review-crypto exactly reproduced binary SHA25621088f9ef0f6add41231e5ef7b19eb8ab3272f17fc493fe104df44b612c8f700. Standalone42cases reran with identical CUcounts; artifact artifacts/crypto-independent-reproduction.json. Original reference final-index defect/controlflowpatch remains explicitly separated from original reference0..1022 signatures.

Full original validator harness at its interrupted artifact had148passingcases/363attempts; it was incomplete after mid-Merkle extra checks. Infrastructure owns continuing that unchanged suite and final acceptance-matrix reconciliation.

## Source fingerprints

- `program/src/lib.rs` SHA256 `4e8db919e96074592bfeb1b5021c957f14338393f8cc93b3b826c849e5006816`
- `client/actions.py` SHA256 `9c369347ad340bc24181f32923a30eb6ca008d5ce4475aea2e1f4b014df2f06a`
- `client/journal.py` SHA256 `ed56ad777fd1c49f2f5b686029072ecdd2aedf914678cd6c46e2127652dbe972`
- `client/cli.py` SHA256 `4ca777ae2958b6838a65bc20de6436d7f1ae3617b8ee50d68373310beb2bd6a2`
- `client/svm.py` SHA256 `d72cd373fff2065de589962d59d588218e24441be06410ba1f6a3a124d3df8d1`

## Independent actual client reproduction

Ran `python -m client.cli --adapter svm demo-xmss` on source27f76f6, exact custody binary8d7435ea6225ef4b09e972cef7ed3d2b99f7f4e1d1b9e9f8aa5124a0848f6e25. Own artifact artifacts/crypto-reviewed-client-xmss.json contains15passingcases and77recordedtransactions with fresh local random XMSS keysets. Verified burn signer+targets consumed; rotation treasury/tokenaddress and balances identical, epoch+nonce eachadvance1, freshbitmapempty; postrotation SOL and mocktoken withdrawals eachmove100baseunits undernewtree. Insufficient-balance signedoperation rejects atomically, then exactsignature retry succeeds afterdeposit. All recorded outcomes pass.

The clientrun does not attempt sealedstage mutation or same-current-authority rotation. Those guards were reviewed in source; do not label this run as their runtime validation. Original finalindexpatch provenance is separate standalone evidence.
