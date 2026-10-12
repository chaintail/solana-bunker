These public, disposable XMSS-SHA2_10_256 vectors exercise the native custody
entry point. Never fund their vault or use their publicly derived keys outside
isolated tests. No secret key or live signing journal is stored here.

Regenerate from the repository root with:

```sh
bash crypto/build_reference.sh
python program/tests/generate_inline_vectors.py
```

The generator uses the pinned RFC reference at commit
`171ccbd26f098542a67eb5d2b128281c80bd71a6` (CC0-1.0), checks every generated
signature with that C verifier, and durably reserves distinct signing leaves.
Its deterministic seed labels identify public test material. The reference
last-index patch does not affect the low-index leaves used here.

`public.bin` signs SOL at leaf 0, token at leaf 1, burn at leaf 2, rotation at
leaf 3 and an unused old-authority burn at leaf 4 with the post-rotation epoch
and nonce. `new-public.bin` signs a post-rotation burn at its leaf 0. Every
`.intent` is the exact canonical application message and every `.sig` is the
raw 2,500-byte RFC signature. The rotation intent installs `new-public.bin`.
The unused old-authority vector tests a cryptographic rejection after rotation,
independently of stale-epoch rejection. Native host tests do not establish
network transport, transaction rollback, actual token CPI or measured CUs.
