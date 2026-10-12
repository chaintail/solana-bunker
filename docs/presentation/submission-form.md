# Colosseum submission form — paste-ready text (draft 1)

## Product name

Solana Bunker

## One-line

A permanent Solana receiving address whose spending rule can be replaced: from hashed one-time secrets, to Merkle-committed secrets, to XMSS hash-based signatures, with every step measured and confirmed on devnet.

## Description

Solana Bunker is a research proof of concept that answers one question: can a Solana account keep receiving funds at the same address while the cryptography that unlocks it is swapped out?

The treasury is a program-derived address with no private key. The authorization rule lives in a separate state account and is replaced in three versions, each tested for native SOL and a six-decimal SPL token. Version one stores a thousand SHA-256 commitments to one-time secrets. Version two commits the same secrets as a single Merkle root, cutting state from 33,126 bytes to 390. Both are deliberately robbed in a scripted test: a revealed secret is a bearer credential, so an attacker who sees the pending transaction copies it, swaps the destination and lands first. Version three signs the full canonical withdrawal with XMSS (RFC 8391, NIST SP 800-208), built from SHA-256 alone, so the copied-and-edited transaction is rejected on chain.

With Solana v1 transactions (4,096 bytes) the 2,500-byte XMSS signature fits in one transaction: 3,117 bytes and 518,509 compute units for a SOL withdrawal, limits requested inline and enforced on devnet. The vault tracks spent one-time keys in a bitmap, supports burning doubtful keys, and installs a fresh tree with a signed rotation: new root, next epoch, same address, same balance. The next tree is derived from the same BIP39 seed phrase, so recovery is one instruction.

Ten operations are confirmed on devnet (program HssAePJfZrERFjEAhm89nY9Tc9BWAobxp2GqGhefNK6V), 225 runtime assertions reproduce from a clean checkout with one script, and the whitepaper records every measurement. The presentation app also investigates the "missing cryptography papers" claim with real data: 719 OpenAI manuscripts classified, and 9,923 Physical Review records from 1920 to 1947.

## Chains and tools

Solana (devnet), native Rust SBF program (no framework), Agave 4.3.0 / platform-tools 1.57, Python client with solders and LiteSVM, XMSS reference C implementation (pinned), SPL Token, v1 transactions. Presentation: Vite + React.

## Go-to-market

This is a research submission, not a company. The target users are the people Justin Drake's post was aimed at: treasuries, exchanges and protocols holding large balances on Solana who want a "bunker mode" option before any network-wide signature migration exists. The path is: publish the whitepaper and measurements, get the program reviewed, then offer the vault as an open-source primitive that wallets and custodians can adopt, with SLH-DSA for administrative actions as the next milestone. The near-term goal is adoption of the pattern, not revenue.

## Past development work disclosure

All program, client, test and presentation code in this repository was written during the hackathon window, starting 2026-10-12 UTC. Prior work used, not written by us: the XMSS reference C implementation (github.com/XMSS/xmss-reference), RFC 8391, NIST SP 800-208 and FIPS 205. Related prior projects acknowledged in the whitepaper: Dean Little's Solana Winternitz Vault and Blueshift's Winterwallet. The founder's other hackathon-period project (Folio) is submitted by a separate team of which he is not a member.

## Team

Liam (solo). Location: [Liam to fill].

## Links

- Repo: https://github.com/chaintail/solana-bunker
- Program (devnet): https://explorer.solana.com/address/HssAePJfZrERFjEAhm89nY9Tc9BWAobxp2GqGhefNK6V?cluster=devnet
- Presentation app: [publish-shared URL when the build lands]
- Pitch video: [upload]
- Technical video: [upload]
- Logo/graphic: [image to generate with the README header]
