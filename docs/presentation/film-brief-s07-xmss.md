# Film brief: slide 7, a signature made of hashes (Liam 16175, composer vision 2026-10-15)

Liam: "In the same spirit, I'm gonna let you run with scene seven and just render it. Follow the same process for scene 7. Make sure Opus understands your vision by planning it out. And then let's just build it and see how it turns out." So: PLAN FIRST (composer reviews), then build; no Liam review before the build.

Script (spoken, Liam's draft 3 beat 6 slide 7, every line kept): "And lucky for us, it turns out you can build a signature out of nothing but hash functions." / "No curves at all." / "Shout out to Leslie Lamport who figured this out in 1979. Yes, that Lamport, the namesake for the smallest unit of Solana." / "Unfortunately Lamport signatures are massive" / "But Winternitz made these smaller, with hash chains." / "Merkle put thousands of those one time keys into a tree." / "That whole thing is called XMSS, it is a NIST standard, and it is what we built for version three." / "So now when the attacker copies our transaction and swaps the destination, the signature does not match anymore, and the program throws it out."

Audio: Liam's take, cut per line, standard chain (afftdn nr=18 profile from the take's silent 0.10–0.70 s once before cutting, 20 ms fades, brown-noise bed, single loudnorm −16 LUFS). Never let audio run while lips are still.

Characters and rules as slides 5 and 6: Liam's matted head on the generated bodies (`apps/web/film/assets/bodies/`), stop-frame poses, whole-figure moves, freeze when silent, narrator = lab coat, never rotated more than 35° from upright, side pokes only. Devil = red-tinted head, horns, domino mask across the eyes. Bouncer stays off screen.

## The style: a 1979 seminar
Cream paper, typewriter font, overhead-projector transparencies that slide in from the bottom with a slight keystone, a faint projector hot-spot. Slide 6's alley stays alive in a small window in a corner, frozen on the devil at the slot with the REJECTED stamp of scene 6's ending, because we return to it at the end. The transition from slide 6: the projector lamp clicks on and washes the alley out to cream.

## Beats
1. "nothing but hash functions": the tweet card slides in one more time; the three hash-based lines (drake-tweet.txt lines 21, 23, 25: SPHINCS; "go all-in on hash-based cryptography"; roadmap) light up one after another; it slides away.
2. "No curves at all": a transparency with the Ed25519 curve from slide 4 (same drawing, with its equation) gets crossed out with a grease pencil.
3. Lamport: a transparency, portrait placeholder (a simple drawn silhouette or a public-domain-safe sketch, no real photo unless one is clearly public domain) labelled "Leslie Lamport · 1979"; under it the word "lamport" with the Solana logo and "1 lamport = 0.000000001 SOL": tiny coin next to a huge name.
4. "massive": the big visual. A Lamport signature is 256 revealed 32-byte secrets = 8,192 bytes. The screen fills with a wall of 256 small key cards, row by row, accelerating, spilling past the edges, counter at the bottom climbing to "8,192 bytes" (public key 16,384 bytes in small print). The narrator gets pushed off screen by the wall.
5. Winternitz: the wall collapses, cards link into chains drawn as actual chain links (hash chains), the counter drops.
6. Merkle: the chains hang as leaves and a tree grows above them to one root, same drawing language as slide 5. The narrator pokes back in.
7. XMSS: the initials stack on the transparency, "X M S S" with the three names beside them (eXtended Merkle Signature Scheme); a NIST seal stamps down ("NIST SP 800-208" small). Then the see-the-code box (GitHub QR to program/src/lib.rs line 118 on main) and the proof box (Solscan QR to devnet withdrawal `CiZmcGsa…`, full signature in artifacts/public-deployment.json) slide in for VERSION 3, with the signature size "2,500 bytes" written beside the tree.
8. "swaps the destination… throws it out": cut back to the alley full frame. The devil hands his form through the slot with the swapped TO address. Inside the door a comparison card: the form's TO and AMOUNT beside the signature; the red-ink signature does not match, a big red X; the form is thrown back out of the slot and lands in the gutter in the rain. Freeze on the devil holding the soggy form. (REJECTED stamp belongs to scene 6's ending; do not repeat it here.)

Rules: 90% readable at 426x240; render on dev-mac only, never ffmpeg on do-box; delete frame folders with literal paths only; open your own stills at every beat; phone re-encode 960x540 crf 26. Branch: worktree `~/code/solana-bunker-s07`, branch `film/s07` from main with `film/floating-head` and `film/s06` merged in (reuse the alley scene and the head pipeline). Commit as the repo's configured identity (Liam), NO trailers. No push.

## Plan first
Write `docs/presentation/film-plan-s07.md`: per beat the on-screen elements, timings against the cut audio, production method per visual (the transparency look, the key wall and its performance at 256 cards, the chain morph, the tree, the NIST seal, the alley return), the risks and the fallback for each, and ONE draft still of the seminar look (transparency on cream with the Lamport card and the alley window in the corner). Report the plan and the still to the composer and STOP; build after approval.
