# Solana Bunker — technical walkthrough script, draft 1

Same nine beats as the pitch, same app, technical route (press T). Target 9 to 11 minutes. Spoken words only; the pitch lines are kept where they still work, and the expansions are marked with ▸. Screen notes at the end.

## Beat 1 — opener and the tweet (1:00)

Pitch beat 1 as written.

▸ After "there is nowhere to hide":

One more thing before we start. Here is everything we are going to touch tonight: public keys, elliptic curves, hash functions, preimages, Merkle trees, program derived addresses, one-time signatures, and signing state. Do not worry about any of them yet. Each one comes back when we need it.

## Beat 2 — the conspiracy (1:15)

Pitch beat 2 as written.

▸ After "the silence is real", before the hat comes off:

For the record, here is how we checked. The OpenAI catalogue was pinned at one commit, seven hundred nineteen manuscripts, every abstract read, two hundred thirty seven of them reviewed by hand. Under the strictest definition, zero have a cryptographic objective. Under a looser one, there is exactly one: a quantum factoring paper. For the war, we pulled nine thousand nine hundred twenty three Physical Review records from nineteen twenty to nineteen forty seven and counted fission in the title. Fifty four hits in the three years before Pearl Harbor. Zero in the three years after. The plutonium paper that was held from forty one to forty six is in the journal's own publication history.

## Beat 3 — we made a Solana Bunker (1:15)

Pitch beat 3 as written.

▸ After "immune to any future weakness in Ed25519":

Two accounts, not one. The treasury is the program derived address: it holds the SOL and owns the token account for USDC. The state account next to it holds the rules: which authorization mode is active, the current root, an epoch counter, a nonce, and a bitmap of used keys. Swapping the lock means rewriting the state account. The treasury never moves.

We did not invent any of these bricks. Lamport, Winternitz and Merkle did the signatures. XMSS is RFC 8391 and NIST SP 800-208. Dean Little's Winternitz vault and Blueshift's Winterwallet already put hash signatures on Solana. What we added is the progression, the permanent address with a replaceable lock, and the measurements.

## Beat 4 — version one (0:45)

Pitch beat 4 as written.

▸ After "crosses that one off":

Each slot is a SHA-256 digest, thirty two bytes. A thousand twenty four slots is thirty three thousand bytes of rent-paying state, and filling it took thirty eight transactions. The withdrawal itself is cheap: seven thousand compute units, one transaction. The secret in the transaction is thirty six bytes.

## Beat 5 — version two, robbed (1:00)

Pitch beat 5 as written.

▸ After "the vault does not know the difference":

Nothing about the Merkle tree fixed this, and nothing could. The proof shows the secret belongs to the tree. It says nothing about who is spending or where. Version two costs thirteen thousand compute units and a three hundred fifty six byte proof, so it is cheaper to store and slightly more expensive to spend. And we ran this robbery on purpose, under a scripted ordering, for both SOL and USDC, so it is a measured result, not a story.

## Beat 6 — a signature made of hashes (2:00)

Pitch beat 6 as written.

▸ Inside, after "a secret you never revealed":

Lamport for one bit: two secrets, publish both hashes, reveal the one matching the bit. For a two hundred fifty six bit message that is five hundred twelve secrets and a sixteen kilobyte signature. Winternitz chains fix the size: one secret per chunk of the message, hashed forward a number of times equal to the chunk's value, with a checksum so you cannot cheat by hashing further. That is a one-time key.

▸ After "what version three runs":

XMSS with SHA-256 and a height of ten gives a thousand twenty four one-time keys under one root. A signature is twenty five hundred bytes: the Winternitz chains plus the ten sibling hashes up the tree. Verifying it on chain is about half a million compute units, almost all of it SHA-256, around six thousand hashes.

The signed message is the full canonical intent: program, vault, treasury, mode, epoch, nonce, leaf index, action, amount, destination, token mint if it is a token transfer. Change any byte and the chains do not line up.

## Beat 7 — one transaction, and re-keying (1:45)

Pitch beat 7 as written.

▸ After "in a single shot":

The transaction is three thousand one hundred seventeen bytes out of four thousand ninety six. The compute cap, loaded account limit and heap are requested inline in the v1 header. On devnet we first simulated with a cap that was too small and watched it fail, then submitted with the real cap, so the limits are enforced for real, not just decoded.

▸ After "recovery is one instruction: rotate":

The signing state is the part people get wrong with stateful schemes. The client keeps a journal: before a leaf is released it is reserved on disk, and a retry reuses the exact same bytes. A failed transaction does not burn a leaf on chain, but a leaf whose signature was ever exposed is treated as spent by the client. If you are not sure, you burn the doubtful leaves with a different leaf, and the vault records it. If you are really not sure, you rotate.

## Beat 8 — live on devnet (0:45)

Pitch beat 8 as written.

▸ Add:

Ten confirmed operations on devnet: array and Merkle withdrawals, six XMSS operations in one transaction each, including a burn, a rotation, and a spend under the new root that the old root could not make. The same program, same vault, same addresses throughout. Everything reproduces from a clean checkout with one script and no private keys.

## Beat 9 — close (0:45)

▸ Before the pitch close:

What this does not protect. The program's upgrade authority is an ordinary key, by choice, and is disclosed. We assume Solana executes correctly and that SHA-256 holds. We do not claim an audit, and we do not claim to have broken anything. SLH-DSA is the stateless next step: no bitmap, no journal, but the smallest standard signature is seven thousand eight hundred bytes, which does not fit one transaction even at four kilobytes, so it is the right tool for rare administrative actions, like rotating a root or guarding the upgrade authority. That is the next experiment.

Pitch close as written.

---

## Screen notes, technical additions

- Beat 1: the cast roll call appears as pinned specimen cards, each one later reused in its scene.
- Beat 2: an evidence drawer with the source IDs and the two method notes, inspectable.
- Beat 3: the two-account diagram with field labels on the state account; the prior-work cards with status badges (standard, published code, research).
- Beat 4: the storage counter and the "38 setup transactions" figure; the 36-byte secret.
- Beat 5: the proof path lit up the tree; a small table 7,101 / 13,229 CU.
- Beat 6: the Lamport two-secrets-per-bit demo; the Winternitz chain with a checksum chunk; the tree; the redacted equations with unredact.
- Beat 7: the v1 header fields; the failed small-cap simulation beside the real one; the journal reserve-and-retry diagram; the burn instruction.
- Beat 8: the devnet operation list with ten signatures.
- Beat 9: the boundary diagram; the SLH-DSA size card (7,856 bytes vs 4,096).
