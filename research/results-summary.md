# Results summary

**Evidence checkpoint: implementation underway.**

| Claim | Current evidence | Status |
|---|---|---|
| Fresh developer wallet; selected development network | E1 and reports/environment.json; address AxQBVSbA3tEc8RsMhn3D4gPLBLnEu3XD84Zd9yy3pmnQ; devnet, balance 0 | Measured environment |
| XMSS reference selected | Pinned revision 171ccbd26f098542a67eb5d2b128281c80bd71a6 | Selection only |
| Stable state/treasury custody, SOL/mock USDC | Actual LiteSVM12smoke cases: all3modes/bothassets exact100unit transfers plus replay rejection; real account init/SPL checked CPI | Local SVM; broader coverage pending |
| Copied-witness attacks in primitive modes | Validation fixtures being prepared | Not yet validated |
| Standalone SVM XMSS verifier | 6 valid + 36 invalid local LiteSVM cases passed; success cases 464,546–496,643 CUs; directly installed fixture account | Verifier feasibility only |
| Integrated XMSS custody, burns, root rotation | Crypto/program/client work active | Not yet validated |
| v1 serialization/decode/execution | @solana/kit8.4.0, 2,029-byte SDK v1 transaction; local Memo execution2,056CUs; devnet unfunded payer AccountNotFound | Partial; no public submit/read confirmation |
| Canonical intent and Merkle/schema independent checks | 17/17 host tests at 009cc06a dirty-tree manifest; lengths SOL230/token327/burn3-target203/rotate259 | Host only |
| Account storage, transaction CUs, benchmark distributions | No final measured dataset yet | Null / pending |
| Public deployment | No funded developer balance / deployment evidence yet | Pending |

Missing values are never zero. Specification sizes in whitepaper.md are labeled arithmetic/reference facts, not benchmarks.

