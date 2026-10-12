# Results summary

**Evidence checkpoint: implementation underway.**

| Claim | Current evidence | Status |
|---|---|---|
| Fresh developer wallet; selected development network | E1 and reports/environment.json; address AxQBVSbA3tEc8RsMhn3D4gPLBLnEu3XD84Zd9yy3pmnQ; devnet, balance 0 | Measured environment |
| XMSS reference selected | Pinned revision 171ccbd26f098542a67eb5d2b128281c80bd71a6 | Selection only |
| Stable custody for SOL/mock USDC | Program work active | Not yet validated |
| Copied-witness attacks in primitive modes | Validation fixtures being prepared | Not yet validated |
| Onchain XMSS, burns, root rotation | Crypto/program/client work active | Not yet validated |
| v1 serialization/decode | @solana/kit8.4.0, 2,029-byte v1 transaction; devnet preflight reaches AccountNotFound payer error | Partial; no submit/read confirmation |
| Canonical intent and Merkle/schema independent checks | 17/17 host tests at 009cc06a dirty-tree manifest; lengths SOL230/token327/burn3-target203/rotate259 | Host only |
| Account storage, transaction CUs, benchmark distributions | No final measured dataset yet | Null / pending |
| Public deployment | No funded developer balance / deployment evidence yet | Pending |

Missing values are never zero. Specification sizes in whitepaper.md are labeled arithmetic/reference facts, not benchmarks.

