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
| 3 | 6.64–10.20 | ["Leslie Lamport" 7.1] the Lamport transparency: Leslie Lamport's photograph in the blue oval, "Leslie Lamport · 1979", "one-time signatures from a hash function". | v5 (Liam 16681, photo two): `assets/lamport-oval.png`, 480x584 (2x of the oval's 240x292), B&W, graded, oval-masked with a soft edge, placed as an SVG `<image>` at the oval's box under the 5 px `#1d3fbf` ring; it comes in with the sheet as the drawn silhouette did (no new animation). The silhouette paths and collar chevron are deleted. Source: Lamport's own photo, Wikimedia Commons `File:Leslie_Lamport.jpg`, tag "Copyrighted free use". |
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
| R7 | Portrait rights for Leslie Lamport. | Resolved in v5: the photo used is Lamport's own (Commons `File:Leslie_Lamport.jpg`, "Copyrighted free use", attribution not required). Courtesy credit to add to the credits list in `film-brief-ending.md` on main (not edited from this branch): "Leslie Lamport portrait: photo by Leslie Lamport, via Wikimedia Commons". |
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

## 9. v5 (x11): Lamport photograph

Liam locked photo two (16681). `s07-xmss.html` beat 3: the drawn silhouette (head, jaw, shoulders, collar chevron) is replaced by `assets/lamport-oval.png` at the oval's box (x 50, y 44, 240x292 in the card's SVG), under the blue ring; nothing else in the scene changed. Built with the x11 chain: `V=v5 pipeline/s07/capture-x11.sh` (chunks in `out/x11/seg-v5`) and `V=v5 pipeline/s07/build-x11.sh` (same audio chain) -> dev-mac `~/video-work/solana-bunker/s07/out/s07-v5-x11.mp4`, `s07-v5-x11-phone.mp4`. Credits: add "Leslie Lamport portrait: photo by Leslie Lamport, via Wikimedia Commons" to the credits list in `film-brief-ending.md` on main (pending; see R7).

## 10. v6 (x11): clipboard pose until the Lamport card, 0.5 s out of the pause after "massive"

Liam 16718, three changes asked; two made, one not possible from the take:

1. Pose. The narrator starts on the existing lab-coat clipboard body (`assets/bodies/5-physicist-holding-clipboard.png`, film/floating-head 0b51c38, same art set as the point body: clipboard in the near hand, pipe in the other, no point) and switches to `5-physicist-professor-point.png` on the frame the Lamport sheet comes in (`SH.sLamport[0]` = M3 in + 0.35 s = page 6.99 s; x11 output frame 191, 6.367 s; the projector click is on that frame). Both bodies are made in the same `.fig` way (`NoirAlley.figs`, new body key `profC`) and placed by the same `poke()` call at the same neck point, so the head anchor (`chinKX` 308, `HK`, `chin` 306) is the same for both. Registration (source px, 1024x1536): collar/tie centre line x 397.1 (point) and 511.7 (clipboard), so `profC.ox` = 394.5 + 115 = 509.5; tie top y 400 in both, shoulder outline within 1 px for 140 px either side of the neck (y 317/316 at -120, 322/321 at -140), baseline 1463 vs 1462, so `chin` stays 306. The clipboard sprite is drawn 3.3 % wider than the point sprite (clipboard edge matches at +107, pocket at +118), so it is squeezed horizontally about its centre line, `sx` 0.967 (fit over clipboard, collar, lapels, buttons, pocket and the near shoulder: mean abs diff 24.0 -> 11.1); no vertical scale, so the shoulder line and baseline are untouched. On screen the collar block's best shift between the two frames is 0,0 px. What still differs is the art itself: the coat's front edge below the vest and the hem are drawn differently in the two sprites. Proof still: `s07-v6-pose-overlay.png` (x11 frames 190 and 191 from the lossless capture, their edges in red/cyan with white where they coincide, and the difference x3).
2. Speech cut A ("...one-time keys. ... and Merkle improved this by putting a bunch of one-time keys into a tree" -> "and Merkle improved this by putting it into a tree"): not made. Neither read-through of the take says it: both say "(And) then Merkle put thousands of those one-time keys into a tree" (first read 385.52-388.94 s, second 438.00-441.58 s, faster_whisper word times on `out/take-dn.wav`), and "improved" and "putting" are not in the take at all (checked against `bunker-transcript.json` and a fresh faster_whisper pass of 376-460 s). v5 already plays the clean second read (M7). M7 is unchanged.
3. Pause after "massive". M5 ends at scene 17.47 s and M6 starts at 18.70 s with only the bed between (the "massive" tail ends at 17.22 s). 0.55 s of scene time is cut at 17.49 s (`s07-timing.py` `TRIM_AT`/`TRIM_D`, written into the EDL as `trim`), which is exactly 15 frames = 0.500 s of the x11 output. Every line from M6 on starts 0.55 s earlier (M6 18.15, M7 21.51, M8 25.54, M9 29.40, M10 32.55, M11 37.90); the heads are unchanged (lines keep their source in/out). The pause after "massive" goes from 1.35 s to 0.85 s at 1.1x. In the scene every word-keyed event follows the EDL; the fixed v5 times after the cut go through `sh()` (hard cut 33.0 -> 32.45, freeze 40.45 -> 39.90, the 26.0/26.2/26.25 mini-tree and XMSS sheet times), and ambient motion (rain, dust, the root glow) runs on the uncut clock (`amb()`), so after the cut the picture is v5's 15 frames earlier and the frozen hand-off frame is v5's.

Scene 41.4667 s (1244 frames); x11 1131 frames = 37.70 s (v5 38.20 s); the alley cut is output frame 885 (29.5 s). Built with `V=v6 pipeline/s07/capture-x11.sh` and `V=v6 pipeline/s07/build-x11.sh` -> dev-mac `~/video-work/solana-bunker/s07/out/s07-v6-x11.mp4`, `s07-v6-x11-phone.mp4`.

Checks (v6): the lossless capture matches v5 frame for frame where nothing changed (frames 191-476 against v5 191-476 and 477-1130 against v5 492-1145: mean difference at most 0.001 except single frames where a seeded ripple/dust pattern or one falling card column lands on the neighbouring step, max 1.13), so the lip-sync after the cut is v5's, 0.5 s earlier, with the voice moved by the same 0.5 s (faster_whisper: "winter" 17.06 -> 16.56 s, "Merkel" 20.54 -> 20.02 s; the gap after "massive" measures 1.17 -> 0.67 s). Hand-off frame: capture v6 1130 vs v5 1145 differs by at most 2/255 on 1110 of 2.76 M values, the graded frame before x264 by PSNR 87.7 dB (same 246-frame alley run, so the same grain), the encoded masters by 42.8 dB (x264 of the grain). `glitch-scan.py`: only frame 3 (the lamp flicker), as v5. Loudness -15.9 LUFS, true peak -1.0 dBFS (phone -0.9). Stills: dev-mac `out/v6-stills/` (`s07-v6-pose-overlay.png`, `s07-v6-cutB-stills.png`, `s07-v6-lipsync-after-cut.png`).
