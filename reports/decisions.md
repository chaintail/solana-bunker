# Decision log

| ID | Decision | Reason / evidence | Status |
|---|---|---|---|
| D01 | Dedicated repository and explicit path ownership | No existing project was supplied. Root acts only as coordinator; workers execute. | Adopted |
| D02 | Public cluster devnet, local SVM first | Locked handoff scope; E1 confirms devnet RPC connection, initial balance 0 SOL. | Adopted |
| D03 | State `[bunker_state,vault_id32]`; treasury `[bunker_treasury,state_address32]` | Treasury seeds exclude authority root and mode; same program/cluster/vault scope. See reports/interfaces.md. | Interface adopted; SVM validation pending |
| D04 | Full XMSS-SHA2_10_256, reference commit 171ccbd26f098542a67eb5d2b128281c80bd71a6 | RFC8391-compatible target with independent reference vectors. | Reference pinned; SVM gate pending |
| D05 | Array and Merkle witnesses deliberately remain bearer secrets | Exposing destination substitution is an experiment, not a hidden defect. | Required |
| D06 | Development upgrade/demo administration remains trusted | Those ordinary authorities can alter custody; adversary receives separate relayer/funding keys only. | Required disclosure |
| D07 | Null for missing measurements | Host timings, SVM CUs, theoretical bytes, simulation and confirmed transactions are different evidence. | Required |
| D08 | Public checkpoint and confidential continuation packages are separate | Public exports exclude developer keys and live signer state. Preserve private continuity without public publication. | Packaging pending validated checkpoint |
| D09 | UI and final slides deferred | Produce structured event/API contract and narrative only. | Adopted |
| D10 | SLH-DSA remains optional | Core three modes, both assets, burn and authenticated rotation have priority. | Deferred |
| D11 | Raw Solana SDK for program; staged witness path prepared | Framework avoids Anchor dependency; staging separates transport and verifier gates. | Adopted; direct v1 probe partial |
| D12 | Burn targets sorted, unique, 1..32; reject consumed, out-of-range and authorizing leaf targets | Exact canonical intent contract in reports/interfaces.md. | Adopted |
| D13 | Strict versioned binary intent with little-endian application integers | Independent host encoder checks lengths 230/327/203/259; XMSS encoding remains standardized big endian. | Host validated; integration pending |

Routine development choices are authorized. No mainnet, real USDC, unrelated project changes, repository publication, or submission is authorized.

