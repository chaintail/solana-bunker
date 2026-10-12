# Solana Bunker — technical video script, three-minute cut

Rule: the technical video is capped at three minutes. Same app, technical route. The conspiracy is one line here; the time goes to the signature and the single transaction. Spoken words only.

## 0:00 — the question (0:20)

One of the top Ethereum Foundation researchers told everyone to move funds to addresses that have never revealed a public key, in case AI breaks elliptic curves. On Solana your address is your key, so that advice does not apply. We built the thing that does: a permanent receiving address with a lock we can swap. And yes, we checked the conspiracy. The charts are in the app.

## 0:20 — the architecture (0:30)

Two accounts. The treasury is a program derived address: off the curve, no private key, holds the SOL and owns the USDC token account. The state account next to it holds the rules: the active authorization mode, the current root, an epoch, a nonce, and a bitmap of used keys. Changing the lock rewrites the state account. The treasury address never moves.

## 0:50 — versions one and two, and the robbery (0:30)

Version one stores a thousand hashed one-time secrets, thirty three thousand bytes of rent. Version two commits the same secrets as one Merkle root, three hundred ninety bytes. Both fail the same way, and we ran the failure on purpose: an attacker who sees the pending transaction copies the secret, swaps the destination, pays a bigger fee, and lands first. A revealed secret is a password. It is not bound to the withdrawal.

## 1:20 — a signature made of hashes (0:50)

Version three signs the withdrawal with XMSS: SHA-256 only, no curves, RFC 8391, NIST SP 800-208. Lamport's one-time trick, Winternitz chains to shrink it, Merkle's tree to hold a thousand twenty four one-time keys under one root. The signed message is the full canonical intent: program, vault, treasury, mode, epoch, nonce, leaf, action, amount, destination, mint. Change one byte and the chains do not line up. The attacker's swapped copy is rejected on chain. Verification is about half a million compute units, almost all of it SHA-256.

## 2:10 — one transaction, re-keying (0:35)

The signature is twenty five hundred bytes. Legacy transactions cap at twelve hundred, so the first build needed five transactions. Version one transactions cap at four thousand ninety six, so we rebuilt it: one transaction, three thousand one hundred seventeen bytes, five hundred eighteen thousand compute units, limits requested inline and enforced on devnet. Every leaf is used once; the bitmap tracks it. One more signed message installs a fresh tree: new root, next epoch, clean bitmap, same address, same balance. The new tree is the next generation of the same seed phrase.

## 2:45 — proof and boundaries (0:15)

Ten operations confirmed on devnet, every one linked in the app. The upgrade authority is an ordinary key by choice and is disclosed. No audit claimed, nothing broken. Stateless SLH-DSA is the next experiment. Repo and whitepaper at the link.
