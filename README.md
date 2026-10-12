# Solana Bunker

A development-cluster research proof of concept comparing SHA-256 secret arrays, Merkle-committed bearer secrets and complete XMSS-SHA2_10_256 authorization over a stable Solana treasury. Native SOL and a six-decimal mock-USDC SPL mint are the two test assets.

**Implementation underway.** No final deployment/onchain verification result is claimed here yet. Start with [reports/status.md](reports/status.md), [research/results-summary.md](research/results-summary.md) and the [handoff](handoff/00_START_HERE.md). Reproducible commands will be finalized against independently validated worker runs.

Dedicated developer public address: `AxQBVSbA3tEc8RsMhn3D4gPLBLnEu3XD84Zd9yy3pmnQ`. Selected public cluster: **devnet**. Initial deployment budget: estimated 5 devnet SOL; funding and final sizing pending. Never send real assets.

The source and evidence package excludes live credentials and signer state. Explicit deterministic public vectors are disposable only and must never back funded shared-cluster vaults.

Ordinary upgrade/demo administration remains trusted and excluded from simulated relayer-key compromise. This is not an audited production wallet or a claim that every ordinary key can be disclosed safely. No mainnet, real USDC, UI, repository publication or submission is included.

