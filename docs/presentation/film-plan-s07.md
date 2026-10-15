# Film plan: slide 7, a signature made of hashes (plan for review, nothing built yet)

Brief: `docs/presentation/film-brief-s07-xmss.md` (main a99e0cd). Branch `film/s07` (worktree `~/code/solana-bunker-s07`) = main + `film/floating-head` + `film/s06` (slide 6 v3, 4f43fd8) merged.
This document is the plan only. The one thing rendered so far is the look draft (section 7).

## 1. Audio: the cut list

Source: Liam's take `audio/bunker-take.wav`, the second read-through of this passage (413–457 s), which matches the script's wording ("who figured this out", "with hash chains", "The program throws it out"); the first read (361–405 s) says "discovered" and "the problem throws it out". Same chain as slides 5 and 6: afftdn nr=18 with the profile from the take's silent 0.10–0.70 s, applied once to the whole take; cut; 20 ms fades; brown-noise bed under the whole scene; one two-pass loudnorm to -16 LUFS / TP -1.5. In/out points sit in the pauses found by `silencedetect=n=-38dB:d=0.12` on the denoised take (dev-mac); word times inside lines come from the transcript tokens and are rechecked on the waveform before capture (the tokens run up to 0.4 s early in this stretch).

| id | line (as spoken) | source in–out (s) | scene in–out (s) |
|---|---|---|---|
| (wash) | projector clicks on over slide 6's last frame, bed only | | 0.00–0.70 |
| M1 | And lucky for us, it turns out you can build a signature out of nothing but hash functions. | 413.95–418.23 | 0.70–4.98 |
| M2 | No curves at all. | 418.59–419.60 | 5.28–6.29 |
| M3 | Shout out to Leslie Lamport, who figured this out in 1979. | 420.30–423.86 | 6.64–10.20 |
| M4 | Yeah, that Lamport. The namesake for the smallest unit of Solana. | 424.15–427.87 | 10.45–14.17 |
| M5 | Unfortunately, Lamport signatures are massive. | 428.80–431.66 | 14.52–17.38 |
| (wall) | the key wall finishes, counter lands, bed only | | 17.38–18.70 |
| M6 | But Winternitz came along and made these smaller using hash chains. | 434.33–437.39 | 18.70–21.76 |
| M7 | Then Merkle put thousands of those one-time keys into a tree. | 438.05–441.73 | 22.06–25.74 |
| M8 | The whole thing is called XMSS, and it's a NIST standard. | 442.54–446.15 | 26.09–29.70 |
| M9 | It's what we built for version three. | 446.66–448.04 | 29.95–31.33 |
| (boxes) | see-the-code and proof boxes land, bed only | | 31.33–33.00 |
| M10 | So when the attacker copies our transaction and swaps the destination, the signature doesn't match anymore. | 448.77–453.92 | 33.10–38.25 |
| M11 | The program throws it out. | 454.42–455.43 | 38.45–39.46 |
| (end) | the form lands in the gutter; freeze; bed fades | | 39.46–42.00 |

Scene length 42.0 s (1260 frames). Not used: "Eight kilobytes each." (431.92–433.84), which is not in the brief's script; the 8,192-byte counter says it on screen. If the composer wants it, it slots in at 17.4 s with no other change.

Lip rule ("never let audio run while lips are still"): whenever the narrator is on screen during a line, his head is the lip-synced sprite of that line; when he is off screen the line is voice-over. Between lines he holds the last frame of the previous line (freeze when silent).

## 2. Beat table (scene times; key words with their approximate scene time)

| beat | time (s) | on screen | how it is made |
|---|---|---|---|
| 0 | 0.00–0.70 | Slide 6's last frame (the devil at the slot, REJECTED). A projector lamp clicks on: two frames of flicker, then a warm cream wash takes the alley out to white-cream in 0.4 s; as it clears, the seminar room is there and the alley sits small in its corner window, still frozen on the devil with REJECTED and live rain. | Slide 6 v3's graded end frame as a full-frame image, a cream overlay with a stepped flicker, then the same image scaled into the window (no tween, a cut at the brightest wash frame). |
| 1 | 0.70–4.98 | The narrator pokes in from the left edge (27° tilt, legs cut by the edge), lip-synced. ["signature" 2.9] the tweet card slides in on a transparency; ["nothing but hash functions" 4.2] three passages light up one after another (drake-tweet.txt lines 21, 23, 25: "SPHINCS", "go all-in on hash-based cryptography", the strawmap roadmap "fully embraces hash-based cryptography"); at 4.98 it slides away. | Tweet image `assets/tweet-body.jpg` cropped to those paragraphs; highlights from the OCR boxes in `data/tweet-body.tsv` (as `tweet-hl.js` does for the opening), yellow highlighter bars wiping on. |
| 2 | 5.28–6.29 | ["curves" 5.5] a transparency with slide 4's Ed25519 curve and its equation `−x² + y² = 1 − (121665/121666)·x²·y²`; a red grease-pencil cross strikes it out (two strokes, 0.3 s). | The curve function and equation ported from `s04-bunker.html` (film/s04 c5b141b, not on main), drawn in black transparency marker; strike-out = stroke-dashoffset reveal. |
| 3 | 6.64–10.20 | ["Leslie Lamport" 7.1] the Lamport transparency (as in the look draft): drawn silhouette portrait in an oval, "Leslie Lamport · 1979", "one-time signatures from a hash function". | Drawn silhouette, no photo (no clearly public-domain portrait to rely on). |
| 3b | 10.45–14.17 | ["that Lamport" 10.8] "lamport" types in huge beside the portrait with a tiny Solana coin; ["smallest unit of Solana" 12.9] "1 lamport = 0.000000001 SOL" and a red "(yes, that Lamport)". | Typewriter reveal per character; the coin is the three-bar mark from the presentation (`C4V1.tsx` SolCoin). |
| 4 | 14.52–18.70 | ["Unfortunately" 14.5] the transparency is pushed up and a wall of 256 key cards fills the screen row by row, accelerating (first row 0.4 s, last rows a blur), spilling past the projection window and the frame edges; the narrator is shoved off the left edge by the wall at ["massive" 17.0]; counter at the bottom climbs to "8,192 bytes" with "public key: 16,384 bytes" in small print under it; the last row lands at 17.6 and everything holds to 18.7. | 256 DOM cards (96x60, key glyph + 4 hex chars from a seeded RNG) on a 16 x 16 grid larger than the frame; each pops in over 2 frames. Counter = typewriter digits with an odometer roll. |
| 5 | 18.70–21.76 | ["Winternitz" 18.7] the wall collapses (cards drop in stepped falls); 48 of them re-form into 8 vertical hash chains drawn as actual chain links (6 links each, "hash" arrows up each chain, "67 chains × 16 steps" small); ["smaller" 20.2] the counter rolls down 8,192 → 2,144 bytes. | Card positions interpolate grid → link positions; links = interlocking SVG ovals (alternating face-on and edge-on). Cards not used fall off the bottom. |
| 6 | 22.06–25.74 | ["Merkle" 22.3] the chains hang as leaves under 8 leaf nodes; a tree grows upward two-into-one to one root that glows yellow (slide 5's marker language: wobbly black strokes, yellow root); ["thousands" 23.1] the leaf row multiplies into a dense "×1024" fringe; the narrator pokes back in from the right edge (mirrored body, unmirrored head), lip-synced. | Seeded wobble strokes revealed by stroke-dashoffset, level by level. |
| 7 | 26.09–33.00 | ["XMSS" 27.0] a transparency slides in: "X M S S" stacked big with "eXtended / Merkle / Signature / Scheme" beside the letters and "Lamport · Winternitz · Merkle" small under; ["NIST" 28.8] a round NIST seal stamps down (dossier slam curve, "SP 800-208" small); ["version three" 30.7] "VERSION 3" stamped, the see-the-code box (GitHub QR to `program/src/lib.rs#L118` on main) and the proof box (Solscan QR to devnet withdrawal `CiZmcGsa…`, full signature from `artifacts/public-deployment.json`) slide in top right, under the alley window; "2,500 bytes" written beside the tree. | QR codes pre-generated as SVG paths with `uqr` (ECC L, no logo, as `apps/web/src/scenes/cheap/proof.tsx`) into `data/s07-qr.js`. The seal is a drawn generic seal, not NIST's logo. |
| 8 | 33.00–42.00 | Hard cut to the alley, full frame, noir (no REJECTED). The narrator pokes in from the left as in slide 6 (lip-synced M10–M11). ["copies our transaction" 34.3] the devil holds up a copy of our signed form with our TO crossed out and "DEV1L…9x" scrawled in red; ["swaps the destination" 35.5] he posts it through the slot (the slot opens this time). ["signature doesn't match" 36.9] a comparison card pops out beside the door like a cutaway: "signed for: ADLw7W…xURt9Wod · 1.5 SOL" vs "form says: DEV1L…9x · 1.5 SOL", our red-ink signature between them; a big red X lands on it. ["throws it out" 38.9] the form shoots back out of the slot in an arc and lands in the gutter puddle (39.6), darkens and curls (soggy); the devil's head drops to it and his red hand holds it up dripping; freeze at 40.4, hold to 42.0. | The alley, door, rain, devil and narrator from `s06-signature.html`, moved into a shared `lib/noir-alley.js` used by slide 7 (slide 6 is left untouched). Comparison card in the sepia form language. Gutter splash = a few seeded droplet ellipses. |

Program boxes: one (VERSION 3) in beat 7, as the brief says.

## 3. Characters

- Narrator: lab coat professor-point body + lip-synced head sprites (pipeline from slide 6: `pipeline/s07/heads.py`, same key, sheets `film/heads/s07-narr-NN.png`). Side pokes only, 27° from upright: left edge for M1–M5 (shoved off on "massive"), right edge mirrored with an unmirrored head for M7–M9, left edge in the alley for M10–M11. Voice-over for M6 and while off screen.
- Devil: slide 6's red closed-mouth head, horns, domino mask; his red cartoon hand. Never speaks.
- Bouncer: off screen. Stick man: not in this slide.

## 4. The looks

Seminar (beats 0–7):
- Dim cream screen (#cfc3a3 edges to #ddd2b4 centre), the projector's bright window keystoned wider at the top (CSS `perspective(1400px) rotateX(-9deg)`), a warm hot-spot (radial #fffaf0 → #e9dec4), the cardboard mount's dark shadow round the aperture, seeded dust and the odd hair drifting in the beam.
- Transparencies: content in typewriter (Special Elite) and transparency-marker colours (black, blue #1d3fbf, red #c4161c); each slides up from the bottom of the aperture in 0.35 s with a projector click (2 frames brighter); the outgoing one slides up and out.
- The alley window: top right, 320x180, slide 6 v3's graded end frame with live rain drawn over it, captioned "meanwhile, in the alley…".
- Post (ffmpeg): warm curves (`curves=r='0/0.04 1/1':g='0/0.03 1/0.98':b='0/0.02 1/0.92'`), light luma grain `noise=c0s=14:c0f=t+u`, `vignette=angle=PI/4.6`.

Alley (beat 8): slide 6's noir grade exactly (lifted-black S-curve, c0s=30 grain, vignette). The two grades are applied to the two time ranges and joined in one ffmpeg pass (split at the 33.0 s cut).

## 5. Files and steps (after approval)

1. `pipeline/s07/s07-timing.py` -> `data/s07-edl.js`, `out/s07-audio.filter` (section 1).
2. `pipeline/s07/heads.py` -> narrator sprite sheets; `pipeline/s07/qr.mjs` -> `data/s07-qr.js`.
3. `lib/noir-alley.js` (copied out of `s06-signature.html`), `apps/web/film/s07-xmss.html` (the scene, grown from `s07-look.html`).
4. Stills opened before the full capture: the wash, tweet highlights, curve struck out, Lamport card, coin line, key wall mid-fill and full (and at 426x240), chains, tree with root, XMSS + seal, code/proof boxes, the devil posting, the red X, the soggy form freeze.
5. `pipeline/s07/capture.sh` (1260 frames in three chunks, frame folders deleted after each), `pipeline/s07/build.sh` (audio, two grades, mux, phone 960x540 crf 26) -> dev-mac `~/video-work/solana-bunker/s07/out/s07-v1.mp4`, `-phone.mp4`.

## 6. Risks and fallbacks

| # | risk | fallback |
|---|---|---|
| R1 | 256 DOM cards plus rain and two figures make frames slow or headless Chrome drops a paint. | Draw the wall on one canvas per frame (seeded, same look); `--fresh` capture for that range if paints drop. |
| R2 | The wall reads as noise at 426x240. | Cards stay 96x60 with a bold key glyph; the counter is the readable element (64 px digits); check a 240p still. |
| R3 | The wall-to-chain morph looks like a mush of moving cards. | Hard stepped falls (4 positions) and only 48 cards morph; the rest drop off; or a cut to the chains on a projector click. |
| R4 | Chain links drawn as ovals do not read as chains. | Thicker links with a highlight stroke, or a simpler "card → arrow → card" chain. |
| R5 | Too much for 3.1 s of M6 and 3.7 s of M7. | Add 0.4 s pauses after M6 and M7 (bed covers it). |
| R6 | Transcript token times in this stretch run early by up to 0.4 s. | Every beat trigger rechecked on the waveform; beats read their times from `data/s07-edl.js`. |
| R7 | Portrait rights for Leslie Lamport. | Drawn silhouette only (as in the draft); no photo. |
| R8 | NIST seal looks official. | Generic drawn seal with the text "NIST SP 800-208", no logo artwork. |
| R9 | QR codes do not scan after the keystone and grain. | QR boxes sit outside the keystoned window (flat, top right) and are checked with a decoder on a 720p still; fallback larger boxes. |
| R10 | Two grades in one pass go wrong at the join. | Grade the two ranges into two files and concat (cut is a hard cut anyway). |
| R11 | Slide 6's alley code duplicated in `lib/noir-alley.js` drifts from slide 6. | Copy once from the committed v3 file; slide 6 is not re-rendered from the shared file. |
| R12 | The narrator shoved off by the wall reads as a limb move. | Whole-figure stepped translate off the left edge (3 positions), no rotation change. |
| R13 | Slide 4's curve lives on film/s04, not main. | Ported by copy (function and equation text), noted in the scene header. |

Open questions for the composer: keep or drop "Eight kilobytes each"; the credit line under XMSS ("Lamport · Winternitz · Merkle"); whether the narrator should also be in the alley (planned: yes, left side poke, lip-synced).

## 7. Look draft (rendered)

`apps/web/film/s07-look.html` (draft, not the slide) and `pipeline/s07/look-still.sh` (pulls slide 6 v3's graded end frame into `assets/s07-alley-freeze.png`, captures t=0.5, applies the warm grade). Output: dev-mac `~/video-work/solana-bunker/s07/out/s07-look-draft.png`: cream room, keystoned projector window with hot-spot and mount shadow, the Lamport transparency (silhouette, "Leslie Lamport · 1979", huge "lamport" with a tiny Solana coin, "1 lamport = 0.000000001 SOL"), the alley window top right with REJECTED and live rain, dust, light grain, vignette.

## 8. As built, v1

Answers from the review: "Eight kilobytes each" dropped; credit line "Lamport · Winternitz · Merkle"; the narrator pokes into the alley from the left for M10–M11. Line out points were pushed 0.06–0.12 s later than the table in section 1 so word tails decay inside the fades (`pipeline/s07/s07-timing.py`). The Ed25519 curve (curve function, keyhole points, equation, "elliptic curve" note) is copied from `s04-bunker.html` at film/s04 c5b141b, with its font `fonts/ArchitectsDaughter-400.woff2`. The tweet card is the opening's dark tweet image with the three passages highlighted from the OCR boxes. The narrator leaves the right side just before "three" so the VERSION 3 boxes land clear of him (the rest of M9 is voice-over). Files: `apps/web/film/s07-xmss.html`, `lib/noir-alley.js`, `data/s07-edl.js`, `data/s07-qr.js`, `pipeline/s07/{s07-timing.py,heads.py,qr.mjs,capture.sh,stills.sh,build.sh}`. Output on dev-mac: `~/video-work/solana-bunker/s07/out/s07-v1.mp4`, `s07-v1-phone.mp4`.
