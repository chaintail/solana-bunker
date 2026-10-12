# Decision log

| ID | Decision | Reason / evidence | Status |
|---|---|---|---|
| D01 | Dedicated repository and explicit path ownership | No existing project was supplied. Root acts only as coordinator; workers execute. | Adopted |
| D02 | Public cluster devnet, local SVM first | Locked handoff scope; E1 confirms devnet RPC connection, initial balance 0 SOL. | Adopted |
| D03 | State `[bunker_state,vault_id32]`; treasury `[bunker_treasury,state_address32]` | Treasury seeds exclude authority root and mode; same program/cluster/vault scope. See reports/interfaces.md. | Adopted and local SVM validated |
| D04 | Full XMSS-SHA2_10_256, reference commit 171ccbd26f098542a67eb5d2b128281c80bd71a6 | RFC8391-compatible target with independent reference vectors. | Reference pinned; SVM gate passed |
| D05 | Array and Merkle witnesses deliberately remain bearer secrets | Exposing destination substitution is an experiment, not a hidden defect. | Required |
| D06 | Development upgrade/demo administration remains trusted | Those ordinary authorities can alter custody; adversary receives separate relayer/funding keys only. | Required disclosure |
| D07 | Null for missing measurements | Host timings, SVM CUs, theoretical bytes, simulation and confirmed transactions are different evidence. | Required |
| D08 | Public checkpoint and confidential continuation packages are separate | Public exports exclude developer keys and live signer state. Preserve private continuity without public publication. | Separate final public/confidential checkpoint outputs |
| D09 | UI and final slides deferred | Produce structured event/API contract and narrative only. | Adopted |
| D10 | SLH-DSA remains optional | Core three modes, both assets, burn and authenticated rotation have priority. | Deferred |
| D11 | Raw Solana SDK; actual custody uses legacy envelopes with explicit ComputeBudget plus staged witnesses | LiteSVM0.29 executes v1 but does not enforce inline compute/loaded-account limits; legacy explicit controls verified. Staging separates transport and verifier gates. | Adopted; public v1 submit/read remains partial |
| D12 | Burn targets sorted, unique, 1..32; reject consumed, out-of-range and authorizing leaf targets | Exact canonical intent contract in reports/interfaces.md. | Adopted |
| D13 | Strict versioned binary intent with little-endian application integers | Independent host encoder checks lengths 230/327/203/259; XMSS encoding remains standardized big endian. | Host and local-SVM validated |

Routine development choices are authorized. No mainnet, real USDC, unrelated project changes, repository publication, or submission is authorized.


## E2 runtime caveat

Infrastructure resource-control run at45aba47 shows local LiteSVM v1 requests of1CU and1loaded-account byte still succeed, whereas equivalent legacy explicit1CU rejects. Local v1 results establish decode/execution only, not enforcement of message resource settings. Custody measurements use legacy explicit ComputeBudget and are unaffected by that v1 control limitation. Devnet remains unconfirmed.

## Final coverage and reproduction

Main195SVM cases plus targeted15program/15intent runtime assertions are independently reproduced from source exports without private credentials. Intent also contains one separately labeled host RFC mint-binding check; host unit suite37 and source inspection remain distinct. All31matrix IDs have bounded evidence; no audit claim applies. Public devnet funding remains the only external continuation gate.
