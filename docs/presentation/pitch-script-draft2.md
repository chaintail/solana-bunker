# Solana Bunker — pitch script, draft 2 (co-written with Liam, in progress)

Spoken words only. Screen notes live in a separate section at the end.

## Beat 1 — opening (opening line: Liam to pick A, B or C)

A. Who's excited for some mathematics? ... Nobody? Okay. Stay with me, I swear this gets good.
B. I know you have watched a hundred pitches today. Mine has math in it. No, wait, don't close the tab. It also has a conspiracy.
C. Before you skip this one: yes, there is math. There is also a tin foil hat. Stay.

A couple of years ago I watched this debate. It is the moment I started to believe in Solana.

Last week, one of the top Ethereum Foundation researchers put out a massive tweet that sent crypto Twitter into a spiral. Get ready for bunker mode, he said. So that is exactly what I did.

His advice was simple. Move your funds to an address that has never sent a transaction, in case AI breaks the math behind elliptic curves before quantum computers do.

That works on Ethereum, because your address is a hash of your key. The key stays hidden until you spend. On Solana, your wallet address *is* your key. There is nowhere to hide.

So. Am I screwed? Should I panic sell?

## Beat 2 — the conspiracy

This next part is for the conspiracy theorists.

Last month OpenAI dropped over seven hundred math papers and turned the field on its head overnight. Seven hundred nineteen papers, seventeen disciplines. And one area was suspiciously missing. Cryptography.

The conspiracy minded were quick to point out that the US government may be leaning on OpenAI to hold back the dangerous ones. And that this would not be the first time. During the Second World War, right as the Manhattan Project got going, physicists mysteriously stopped publishing on atomic physics.

Now, I could have just trusted a tweet. Instead, I checked.

The silence is real.

[hat on; hold]

Draw your own conclusions.

## Beat 3 — we made a Solana Bunker

Whether or not anyone is hiding anything, there is a real research question under all of this. It is a fascinating side quest for math nerds like us, and an engineering question worth answering.

Solana has program derived addresses. They sit off the curve, so there is no private key behind them at all. We used one to build a vault: a permanent address where you can park your valuable coins, immune to any future weakness in Ed25519.

And we didn't build it once. We built it three times, each version better than the last.

## Beat 4 — version one

Version one is simple. We generate a bunch of one time secrets, hash each of them, and store the hashes in the vault. To spend, you reveal one of the secrets. If it matches, the vault lets you in and crosses that one off.

Pretty clever, eh? But keeping track of a thousand one time passwords is annoying, storing them all on chain is expensive, and that is why we built version two.

## Beat 5 — version two, robbed

Version two. Same thousand secrets, but now we commit them as a single Merkle root. Thirty three thousand bytes of storage becomes three hundred ninety.

So we send a withdrawal, and... oh crap. What happened there? We got robbed.

Here is the problem. It is unlikely, but if an attacker can see our transaction before it lands, and has already broken Ed25519, they copy our secret, swap the destination, and pay a bigger fee. The vault does not know the difference.

## Beat 6 — a signature made of hashes

Okay, this is where it gets really interesting.

The problem with versions one and two is that a secret is just a password. Whoever shows it first gets in, and it says nothing about where the money should go. What we actually want is a signature. Something that says: this exact withdrawal, to this exact address, and nothing else.

Turns out you can build a signature out of nothing but hash functions. No curves at all. Leslie Lamport figured this out in nineteen seventy nine. Yes, that Lamport, the one Solana named its smallest unit after. You make a pile of secrets, publish their hashes, and then to sign a message you reveal the secrets that match the bits of that message. Change one bit and you would need a secret you never revealed.

Winternitz made it smaller with hash chains. Merkle put thousands of those one time keys into a tree. That whole thing is called XMSS, it is a NIST standard, and it is what version three runs.

So now when the attacker copies our transaction and swaps the destination, the signature does not match anymore, and the program throws it out.

## Beat 7 — one transaction, and re-keying

Here is the part I am proudest of. An XMSS signature is twenty five hundred bytes. A Solana transaction used to cap out at twelve hundred, so the first build needed five transactions to get one signature on chain. Gross.

But last month Solana shipped version one transactions, four kilobytes each. So we rebuilt it. One transaction, thirty one hundred bytes, about half a million compute units, and the full signature verifies on chain in a single shot.

And because every one time key gets used exactly once, the vault keeps a bitmap of which leaves are spent. When you run low, or you just get paranoid, you sign one more message that installs a brand new tree. New root, new keys, same address, same balance. The new tree comes from the same twelve word seed phrase, just the next generation. So recovery is one instruction: rotate.

## Beat 8 — live on devnet

This is not a diagram. All of it is live on devnet right now. Three vaults, SOL and USDC, the robbery, the rejection, the rotation. Every number on this screen is a transaction you can open in the explorer.

## Beat 9 — close

There is a lot more in the whitepaper. The stateless version of this, SLH-DSA, which is bigger but never has to track which keys are spent. And my favourite idea we did not get to: using the vault to guard its own upgrade authority, so the bunker protects the bunker.

Thanks for sticking around. I told you the math would be worth it.

## Stamps (final set; no mirrored-fragment slogans anywhere)

1. THIS IS A DRILL
2. CLASSIFIED; RECEIVED 1941 · PUBLISHED 1946
3. NOT YOUR KEY, STILL YOUR COINS (or BUNKER MODE: ENGAGED; Liam to pick)
4. SECRET ACCEPTED (small) or none
5. ROBBED
6. REJECTED
7. ONE TRANSACTION (small), RE-KEYED (large)
8. CONFIRMED
9. none; whitepaper QR and repo link

Fact notes: "last month" for v1 transactions is Liam's framing; the research ledger (C007) verifies v1 is active on mainnet with a 4,096-byte cap but does not date it. Lamport one-time signatures: 1979 (SRI technical report). Numbers: 719 / 17 / 0; 3.4% → 0 (1942–44); 33,126 / 390 / 422 bytes; 3,117 bytes / 518,509 CU; 2,500-byte signature.

---

## Screen notes

### Beat 1
- Bankless debate thumbnail (docs/presentation/assets/bankless-debate-thumb.jpg), caption "This debate is when I first started to believe in Solana." Arrow to Justin Drake with his name; never spoken.
- Tweet appears on "massive tweet", bunker-mode sentence highlighted.
- Correction cards, bottom third, typewriter: "ECDSA on secp256k1 · Ed25519 on Solana", "quantum is the known threat; AI is the speculative one".
- Address contrast: Ethereum key → hash → address; Solana key = address.
- Stamp THIS IS A DRILL lands on "panic sell".

### Beat 2
- Stamp CLASSIFIED on "for the conspiracy theorists".
- 719 dots clustered by discipline, labelled; then an empty dashed circle "cryptography · 0" at the edge.
- Physical Review fission chart slides in beside it; 1942–1944 zero band; stamp RECEIVED 1941 · PUBLISHED 1946.
- On "I checked": flash "I had my agents check. It's true." then "719 papers reviewed · 9,923 journal records, 1920–1947".
- On "the silence is real": nothing new. Charts hold. Hat moves.
- "Draw your own conclusions": small, last text; cut in rehearsal if the hat carries it.

### Beat 3
- Hat off on "whether or not". Coin icons stream into the blueprint vault on "park your valuable coins". Disclaimer scrolls at pharmaceutical-ad speed on "immune": "with a properly secured upgrade authority, assuming no bugs in the program, not covering consensus failures, relayer compromise, lost seed phrases, or anything else ChatGPT warned us about."

### Beat 4
- Wrong-secret withdrawal bounces with a red REFUSED tag; right-secret withdrawal goes through and slot 7 is crossed off in the array. No attacker here.

### Beat 5
- Array folds into one root with the storage counter dropping 33,126 → 390. Then the withdrawal, the attacker's copy with the swapped destination landing first, ROBBED.

### Beat 6
- One-bit Lamport demo (two secrets per bit, reveal one). Winternitz chain ticking forward. Tree with one leaf lit. Attacker's swapped copy arrives and bounces: REJECTED.

### Beat 7
- Five transaction cards stack, then one wide card replaces them: "3,117 bytes", "518,509 CU". Bitmap with spent cells. Rotation: root changes, epoch 0 → 1, bitmap wipes, pinned address never moves. Twelve redacted words, "generation 0" crossed out, "generation 1" active. RE-KEYED.

### Beat 8
- Real explorer transaction page with the signature visible. Beside it the storage chart 33,126 / 390 / 422 bytes. CONFIRMED.

### Beat 9
- Whitepaper QR, repo link, Liam's name.
