# Solana Bunker — pitch script, draft 1

Target: 2 minutes 15 seconds spoken. Nine beats. Each beat names the stamp that lands on screen.

## Beat 1 — Contains mathematics (0:00–0:15)

> You have watched a hundred pitches today. I am sorry. This one contains mathematics.

> Last week one of the sharpest cryptographers in Ethereum told the whole industry to go into bunker mode: move your coins to addresses that have never revealed a public key, because AI might break elliptic curves before quantum computers do.

> Great advice. On Ethereum your address is a hash of your key. On Solana your address *is* your key. There is no bunker to go into.

Stamp: **THIS IS A DRILL**

## Beat 2 — The missing papers (0:15–0:40)

> He said one more thing. That OpenAI's big math drop had suspiciously little cryptography in it. So we checked.

> Seven hundred nineteen manuscripts. Seventeen disciplines. One hundred thirty one in number theory and theoretical computer science. Zero with a cryptographic objective.

> And in nineteen forty two, Physical Review stopped publishing papers with fission in the title. Three point four percent of the journal, then nothing for three years. One plutonium paper was received in forty one and published in forty six.

> We checked. The silence is real. Draw your own conclusions.

[Tin foil hat. Hold the silence. Nothing on screen moves.]

Stamp: **RECEIVED 1941 · PUBLISHED 1946**

## Beat 3 — Meet Solana Bunker (0:40–0:55)

> Whether or not anyone is hiding anything, the engineering question is worth answering. Can a Solana address keep receiving funds forever while we change the math that unlocks it?

> Solana Bunker is one permanent treasury address, a program-derived account, with a lock we can swap. We built the lock three times, each one better than the last.

Stamp: **THE ADDRESS STAYS. THE LOCK CHANGES.**

## Beat 4 — A drawer full of passwords, robbed (0:55–1:15)

> Version one. Hash a thousand secrets, store the fingerprints on chain. Reveal a secret, the vault pays once.

> It works. Until someone reads your pending transaction, copies the secret, and sends their own withdrawal to their own address first.

> We did not break the hash. We copied the password.

Stamp: **ROBBED**

## Beat 5 — One root, robbed again (1:15–1:25)

> Version two. Same thousand secrets, committed as one Merkle root. Thirty three thousand bytes of storage become three hundred ninety.

> Same attacker. Same trick.

Stamp: **SMALLER. STILL ROBBED.**

## Beat 6 — A signature made of hashes (1:25–1:45)

> Version three stops revealing passwords and starts signing instructions. XMSS: a tree of one-time signing keys built from nothing but SHA-256, standardised by NIST.

> The signature covers the amount, the destination, the vault, the nonce. Copy it and change one byte, and the program refuses.

Stamp: **REJECTED**

## Beat 7 — Same address, new lock, same twelve words (1:45–2:00)

> This is live on devnet. One transaction, three thousand bytes, half a million compute units. We rotate the entire signing tree to a fresh root, the old root is rejected, and the receiving address never moved.

> The next tree comes from the same twelve word seed phrase. Recovery is just: rotate.

Stamp: **SAME ADDRESS. NEW LOCK.**

## Beat 8 — The receipts (2:00–2:10)

> Every number on this screen is a confirmed devnet transaction you can open. Five staged transactions became one.

Stamp: **FIVE BECAME ONE**

## Beat 9 — Close (2:10–2:20)

> Solana Bunker. The address stays. The lock changes. The whitepaper and the code are at the link.

> You survived the mathematics. The passwords didn't.

Stamp: **CONTAINS MATHEMATICS** (callback, small)

---

## Notes

- Beat 2 runs long on purpose; it is the hook. If the cut is over 2:30, trim Beat 1's Ethereum line, never Beat 2.
- The technical route uses the same nine beats and adds: cast roll call after Beat 1, prior work after Beat 3, Lamport and Winternitz chains inside Beat 6, account architecture and the bitmap inside Beat 7, boundaries and SLH-DSA before Beat 9.
- Numbers: 719 / 17 / 131 / 0 and 3.4% → 0 come from docs/research-story/visualizations.json. 33,126 → 390 bytes and 3,117 bytes / 518,509 CU come from research/results-summary.md and reports/v1-single-transaction.md.
