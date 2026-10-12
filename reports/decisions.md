# Decision log

| ID | Decision | Reason / evidence | Status |
|---|---|---|---|
| D01 | Dedicated repository and explicit path ownership | No existing project was supplied. Root acts only as coordinator; workers execute. | Adopted |
| D02 | Public cluster devnet, local SVM first | Locked handoff scope; E1 confirms devnet RPC connection, initial balance 0 SOL. | Adopted |
| D03 | Separate stable state and treasury PDAs | Treasury seeds exclude authority root and mode; same program/cluster/vault scope. | Required; final seeds pending interface agreement |
| D04 | Full XMSS-SHA2_10_256, reference commit 171ccbd26f098542a67eb5d2b128281c80bd71a6 | RFC8391-compatible target with independent reference vectors. | Reference pinned; SVM gate pending |
| D05 | Array and Merkle witnesses deliberately remain bearer secrets | Exposing destination substitution is an experiment, not a hidden defect. | Required |
| D06 | Development upgrade/demo administration remains trusted | Those ordinary authorities can alter custody; adversary receives separate relayer/funding keys only. | Required disclosure |
| D07 | Null for missing measurements | Host timings, SVM CUs, theoretical bytes, simulation and confirmed transactions are different evidence. | Required |
| D08 | Public checkpoint and confidential continuation packages are separate | Public exports exclude developer keys and live signer state. Preserve private continuity without public publication. | Packaging pending validated checkpoint |
| D09 | UI and final slides deferred | Produce structured event/API contract and narrative only. | Adopted |
| D10 | SLH-DSA remains optional | Core three modes, both assets, burn and authenticated rotation have priority. | Deferred |

Routine development choices are authorized. No mainnet, real USDC, unrelated project changes, repository publication, or submission is authorized.

