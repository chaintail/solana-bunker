# E1 — Developer wallet and environment

Status: pass (local development active; public deployment pending).

- Public developer address: `AxQBVSbA3tEc8RsMhn3D4gPLBLnEu3XD84Zd9yy3pmnQ`.
- Selected cluster: **devnet**; RPC `https://api.devnet.solana.com`.
- Observed balance: **0 lamports**, RPC apiVersion `4.4.0-beta.0`, slot `510281088`.
- Funding estimate: **5 devnet SOL**, provisional until binary/storage sizes are measured; development tokens have no real value.
- Faucet request for 2 SOL returned JSON-RPC `-32603 Internal error`; no confirmed airdrop.
- Sprint started `2026-10-12T13:36:06.597515Z`; target end `2026-10-13T13:36:06.597515Z`.
- Fresh recoverable developer keypair created with restrictive directory/file permissions and excluded from version control. No mnemonic or key bytes were printed.
- Isolated local repository initialized; no other project modified; project AGENTS adopted.
- Native worker delegation active with separate source-path ownership.
- Initial environment had Node/npm/Python/gcc, but no Rust/Solana CLI on PATH. Rust, npm SDK, and LiteSVM installations are in progress.
- Network probes succeeded for devnet RPC, Rust static, npm registry, PyPI, and XMSS GitHub reference.

Local work proceeds during funding and toolchain installation. Final exact versions and deployment outcomes will be recorded independently.

Toolchain update: Rust/cargo1.99.0, Agave/solana4.3.0, cargo-build-sbf4.3.0/platform-tools1.57, solders0.29.0 LiteSVM and official @solana/kit8.4.0 installed. A second bounded faucet attempt through solana CLI for1SOL failed with its generic rate-limit message; no confirmed airdrop. Exact versions: `artifacts/toolchain-manifest.json`.

Concrete funding update from the122,848-byte custody binary: devnet queried programdata rent624,946,680lamports and buffer rent624,906,040lamports at fixed max length. Estimated peak deployment funds about1.3devnetSOL plus test fixtures/fees; **2devnetSOL recommended**, replacing the early5SOL provisional estimate. Balance still0 at2026-10-12T13:46:18Z. `artifacts/devnet-funding-estimate.json` and prospective `artifacts/public-deployment.json` preserve exact results; program/mint identities are allocated but not yet created publicly.
