# Brief: single-transaction XMSS withdrawal over Solana v1 transactions

Repo: `/home/claude/code/solana-bunker` (branch `main`). Read `README.md`, `handoff/01_RESEARCH_AND_PROGRAM_BRIEF.md`, `handoff/03_CRYPTO_AND_PLATFORM_NOTES.md`, `reports/early/E2-v1-transport.md`, `research/results-summary.md`, `client/README.md`, then `program/src/lib.rs` and `client/svm.py`, `client/actions.py`, `client/cli.py`.

Toolchain on this host (add to PATH): `$HOME/.local/share/solana/install/active_release/bin` (solana-cli 4.0.2, cargo-build-sbf 4.0.0, platform-tools v1.53) and `$HOME/.cargo/bin` (cargo 1.96.1). Python 3.13. The README pins Agave 4.3.0 / platform-tools 1.57 and says `BUNKER_SOLANA_BIN` / `BUNKER_CARGO_BIN` select binary directories; install a matching toolchain under `$HOME/.local/share/solana/install` if the pinned build requires it rather than loosening the pin. Network access is on.

## Goal

The XMSS withdrawal currently needs five legacy transactions (stage create, three uploads, execute) because a legacy transaction is capped at 1,232 bytes and the XMSS-SHA2_10_256 signature is 2,500 bytes. Solana v1 transactions allow 4,096 bytes. Make the XMSS withdraw, burn and rotate instructions executable in **one v1 transaction** that carries the signature inline in the instruction data, with explicit inline compute settings. Keep the staged path only as a documented fallback; the single-transaction path becomes the default for `--adapter svm` and for devnet.

Measured compute today is about 490k to 600k CU per XMSS execute, so one transaction fits inside the 1.4M CU ceiling.

## Steps

1. Program: add (or generalise) an instruction variant that reads the full canonical intent plus the XMSS signature from instruction data instead of a stage account. Reuse the existing verifier and custody path; the acceptance semantics (leaf consumption, nonce advance, atomic transfer, rejection cases) must be identical. Smallest diff wins. Do not change the array or Merkle modes.
2. Client: build and sign a v1 (MessageV1) transaction with the inline instruction and inline compute-unit limit for XMSS withdraw SOL, withdraw mock USDC, burn leaves and rotate root. `client/svm.py` already has local v1 decode/execute evidence via solders 0.29 LiteSVM; `scripts/infrastructure-local-v1.py` shows a working MessageV1 probe.
3. Tests: run the existing host tests and the SVM harness with the new path. Add the single-transaction XMSS cases to the harness so the 15 client XMSS cases and the attack/rotation cases pass over v1. Record serialized transaction bytes and CU per operation in the same benchmark JSONL format as `artifacts/validation-benchmarks.jsonl`. Note in the report that local LiteSVM does not enforce v1 inline resource limits (E2 finding), so real enforcement is proven on devnet in step 4.
4. Devnet: the developer wallet is `/srv/world/secrets/agents/composer-dobot/solana/bunker-devnet.json` (public key `N4FZnqmfXWoGhofuJAYnDdnYF8ows635ZAw2omFCtW1`). It is being funded now; poll `solana balance -u devnet` until it has at least 2 SOL. Then deploy the program with `scripts/infrastructure-devnet-deploy.py` (or the equivalent `solana program deploy`), create the mock USDC mint, initialise a vault, and run on devnet: one array withdraw, one Merkle withdraw, the single-transaction XMSS withdraw for SOL and for mock USDC, one burn, one root rotation, and one post-rotation withdraw. Record every signature and account address in `artifacts/devnet-deployment.json` and update `artifacts/public-deployment.json` from "prospective" to confirmed values with explorer links of the form `https://explorer.solana.com/tx/<sig>?cluster=devnet`.
5. Docs: update `README.md`, `research/results-summary.md` and `reports/status.md` with the single-transaction measurements and the devnet confirmations. Write `reports/v1-single-transaction.md`: what changed, bytes per transaction, CU per operation, devnet confirmations, and what remains staged (if anything).
6. Commit on `main` in small commits with the repo-local git identity. Never print or commit private keys. Do not push.

## Fallback

If the single-transaction path cannot be made to work within about four hours, stop, keep the staged path as default, deploy the current program to devnet anyway, run the devnet demonstrations with the staged path, and write up exactly where the v1 path failed (which limit, which error, with raw output).

## Report

When done, write `reports/v1-single-transaction.md` and print a ten-line summary: outcome, single-transaction bytes and CU per XMSS operation, the devnet program id, mint, vault addresses, and the explorer link for the XMSS withdraw and for the root rotation. Flag anything that is a local-only result rather than a devnet confirmation.
