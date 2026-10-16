# Film plan: the ending (scene 9 testimonial, scene 10 news desk sign-off, scene 11 Chaintail News Network credits). Plan for review; nothing built yet

Brief: `docs/presentation/film-brief-ending.md` (main d944b61, with Liam's final credits list in 4aef292, after 2d50b9b). Branches:
- `film/s09` (worktree `~/code/solana-bunker-s09`): part A, the testimonial, appended to scene 9 v2 (c51a941).
- `film/s10` (worktree `~/code/solana-bunker-s10`) = main d944b61 + `film/floating-head` (fc5a163) + `film/s09` (c51a941) + main 2d50b9b and 4aef292: part B.
- `film/s11` (worktree `~/code/solana-bunker-s11`), the same merges: part C.
All merges had no conflicts. This document is on all three branches.
The only things rendered so far are the three look drafts (section 8).

## 1. Sources and audio chain

- Take: dev-mac `~/video-work/solana-bunker/audio/bunker-take.wav` (587.07 s). The ending is its last 68 s (518.48–586.08 s).
- Matte: `~/video-work/bunker/matte-full-comp.mp4` and `matte-full-alpha.mp4` are 1080x1440 at 29.998 fps and 587.07 s long. They run on the take's clock (scenes 5–9 key heads at take times), so they cover 518–586 s. No new matting is needed. I checked frames at 20, 300 and 539.3 s: the framing is the same as the opening, and in the tail the head sits about 15 px (of 1440) lower. The opening composites the comp despilled and scaled to 525x700 at (377, −20) under the alpha (`pipeline/desk-v7.filter`). Part B does the same. The lab coat's head in part A uses the head key (`pipeline/head-test/key.sh`, via `pipeline/s09/heads.py`).
- Audio chain as every scene: afftdn nr=18 once on the whole take (the existing dev-mac `s09/out/take-dn.wav`, reused); cut; 20 ms fades on every cut; brown-noise bed (lowpass 220, volume 0.05) under the whole scene; two-pass loudnorm −16 LUFS / TP −1.5; limiter as scene 9 (`alimiter=limit=0.80:level=0`). No SFX, generated or otherwise. Part B takes its voice from the take (`take-dn.wav`), not from `bunker-raw.mov` as the opening did. The take is the same recording.
- How the points were found (dev-mac): `silencedetect=n=-38dB:d=0.12` on `take-dn.wav` from 516 s, plus a 10 ms RMS scan of speech islands above −38 dB. Pauses: 517.31–518.86 (click 517.77, breath 518.1–518.5), 520.41–520.75, 522.67–523.10, 523.80–524.02, 525.47–525.73, 527.58–527.84, 528.82–529.64, 532.81–533.98, 535.97–536.10, 537.19–537.47, 539.52–540.52, 541.81–542.45, 544.73–545.59, 548.36–548.91, 550.05–550.54, 551.47–554.09, 556.83–557.71, 558.55–558.92, 560.27–563.77, 565.17–565.53, 566.82–567.13, 568.34–568.64, 569.94–570.40, 573.52–574.01, 575.36–575.74, 579.76–579.97, 581.44–581.98, 583.24–583.82, 585.50–587.03.
- The transcript's tokens lead the energy onsets by 0.11–0.41 s at every sentence start in this stretch (And 518.48 → 518.85, Thanks 533.60 → 533.98, The 563.36 → 563.77, Feel 583.52 → 583.84). The cut points below come from the energy scan, not the transcript. The word times in the beat tables are each token plus its sentence's onset offset. The timing scripts recheck every anchor with the 50 ms energy scan, as scenes 8 and 9 did (risk R1). I could not listen. The A/B listening files are listed in section 7.
- The take matches the brief's wording, with three small differences: "SOL" is transcribed "Seoul"; the kept read says "For this, we want to explore SLH DSA."; and the brief's "Thanks for sticking around" sentence starts 0.38 s later than its transcript time.

## 2. Cut lists

| part | segment | take in–out (s) | scene in–out (s) | what is kept | why the points |
|---|---|---|---|---|---|
| A | TA | 518.62–533.30 | 30.10–44.78 (scene 9) | "And this is not just a bunch of diagrams." … "you can open in the explorer." | in after the breath (518.1–518.5), before "And" (518.85); out in the pause after "explorer." (532.80 → 533.98) |
| B | B1 | 533.75–545.10 | 2.00–13.35 (scene 10) | "Thanks for sticking around." … "Go check it out." | in before "Thanks" (533.98); out in the pause after "out." (544.72 → 545.59) |
| B | (cut) | 545.10–563.55 | removed, 18.45 s | the two false starts: "The next cool piece … stateless version of this. And for that, we want to ex exp." (545.59–551.24) and "The next cool piece … of this. For this, we want to explore uh." (554.09–560.23) | the brief's cut (545.28–563.36), moved into the pauses on either side |
| B | B2 | 563.55–583.50 | 13.35–33.30 (scene 10) | "The next cool piece of research …" … "Lots more to cook up in the lab." | in before "The" (563.77); out in the pause after "lab." (583.22 → 583.82) |
| C | C1 | 583.62–586.00 | 3.90–6.28 (scene 11) | "Feel free to reach out with any questions." | in before "Feel" (583.84); out after "questions" (585.49), before the take ends |

Part A's join leaves 0.60 s of silence between "Go check it out." and "The next cool piece" (544.72→545.10 plus 563.55→563.77), close to the take's own pauses. Mappings: scene 9 = take − 488.52 (TA); scene 10 = take − 531.75 (B1), take − 550.20 (B2); scene 11 = take − 579.72 (C1).

**Lengths:**
- Part A: scene 9 grows from 29.83 s to **46.78 s** (+16.95 s, 1403 frames). Frames 0–894 keep v2's timing and content (only the heads change, see the head fixes in section 3). The testimonial starts at 29.83, the voice at 30.10, the last word ends at 44.28, the audio ends at 44.78, and 44.78–46.78 is the frozen 2 s handoff hold.
- Part B: scene 10 is **33.40 s** (1002 frames). It is 2.00 s of wipe, 31.30 s of voice and footage, and a 0.10 s tail that ends in the pause before "Feel".
- Part C: scene 11 is **39.40 s** (1182 frames). It is 3.0 s of ident, a 0.6 s split, a 26.9 s roll (Liam's final list, 3503 px at 5 px a frame), then two full-screen cards (4.0 s and 3.0 s, each with a 0.5/0.4 s crossfade in) and a 1.0 s fade to black.
- The whole ending, from scene 9's old end to black, is 16.95 + 33.40 + 39.40 = **89.8 s**.

Lip rule: the voice runs only while the speaker's lips are on screen (the lab coat's lip-synced head in A; Liam's own footage in B). Part C has no face: it is voice only over the parchment (Q11).

## 3. Part A: the testimonial (scene 9, film/s09)

Framing: an infomercial testimonial. At 29.83 there is a hard cut, as infomercials hard-cut to the customer. The lab coat stands upright in the studio (starburst re-centred behind him) and points right at the results. The product moves to a packshot top left: the BIP-39 card at 0.42, with the FREE tag still hanging from its corner. CALL NOW becomes a full-width strip at the bottom: the flashing CALL NOW! block and the repo URL. So the FREE tag and CALL NOW stay on screen throughout. The name card sits above the strip.

Word times (scene s): And 30.33, diagrams 31.69, All 32.23, live 32.87, DevNet 33.27, right now 33.91 (ends 34.15), Three 34.59, vaults 34.99, SOL 35.71, USDC 36.12 (ends 36.93), We 37.21, demonstrate 37.37, robbery 38.01, rejection 38.73, and 39.32, rotation 39.85 (ends 40.28), Every 41.12, number 41.52, screen 42.08, transaction 42.64, open 43.44, explorer ≈43.9 (ends 44.28).

| beat | time (s) | on screen | how it is made |
|---|---|---|---|
| A0 | 29.83 | Hard cut to the testimonial framing. The lab coat is now `5-physicist-professor-point` (hard pose cut from the poke), upright, chin at (330, 318), scale 0.52. Packshot plus FREE tag top left; CALL NOW strip at the bottom. The checklist and the card area are empty. | `s09-seed.html` grows a `#testi` layer that shows from `T.testi`. Bodies from `bodies.py` (professor-point added; anchors as v2, `KEY_CHIN_X` 289). |
| A1 | 29.90–30.25 | Name card wipes in left to right: yellow tab SATISFIED CUSTOMER, blue bar "Dr. L. C." / "cryptography nerd". It stays to the end. | DOM, Anton / Inter, clip-path wipe. |
| A2 | 30.10–44.78 | The lab coat speaks TA (lip-synced head), standing still. He never moves his body: the pose is fixed and nothing rotates. | `heads.py` gets a row LAB2 (518.62–533.30, 441 frames, about 2.3 sheets) re-keyed from the matte. |
| A3 | 32.87 ("live") | Checklist line ✓ LIVE ON DEVNET pops in (scale 1.3 → 1, 4 frames). Featured results card #1 drops in on the right: "LIVE ON DEVNET!", Solscan QR of program `HssAePJf…NK6V`, caption "program HssAePJf…NK6V". A REAL RESULTS starburst sticker stays at the top right. | Card: white, navy border, yellow header (Anton 38), QR at 4 px per module (account QR 37+8 modules = 180 px). |
| A4 | 34.99 ("vaults") | ✓ 3 VAULTS. Three account cards fan in over card #1 like a dealt hand: array `CZws1WQu…MrAru`, Merkle `EfKbhDHz…wiK8`, XMSS `ExUjnwye…RFco` (treasury accounts), each at 3 px per module (135 px). | Only 0.72 s before "SOL", so these three are scannable in the final grid (A10), not here (R-A2). |
| A5 | 35.71 ("SOL") | ✓ SOL. Card "SOL WITHDRAWN!": QR of XMSS withdraw SOL `CiZmcGsa…dBM` (the tx scenes 7–8 already show). | 4 px per module (41+8 modules = 196 px). |
| A6 | 36.12 ("USDC") | ✓ USDC, with the small label "mock". Card "USDC WITHDRAWN!": XMSS withdraw mock USDC `VveVy2HN…7yHd`, caption "mock USDC (test token, no real value)". | The label text comes from the json's `mock_token_label`. |
| A7 | 38.01 ("robbery") | ✓ ROBBERY, labelled "dramatized". Card "ROBBED!": the corrected devil head (`heads/s06-devil-v2.png`, film/s06 90924b2) as a mugshot, "version two, front-run", and a DRAMATIZATION strip (scene 9's own caption style). **No QR: no devnet signature exists** (R-A1). | Flat image in the card; the devil head is a still prop here, not a moving character. |
| A8 | 38.73 ("rejection") | ✓ REJECTED, labelled "simulated". Card "REJECTED!": a red stamp over the program log line from the json, "Program failed: custom program error: 0xc", and "devnet simulation". **No QR: simulations have no signature** (R-A1). | The text comes from `simulations[…-xmss-withdraw-sol-destination-substitution]` in public-deployment.json. |
| A9 | 39.85 ("rotation") | ✓ ROTATION (yellow, the current line). Card "ROOT ROTATED!": QR of XMSS rotate root `5U4B7zhg…L5iy`, caption "XMSS vault: new root, epoch 1". **This is look draft A.** | The epoch comes from the json's XMSS `final_snapshot.epoch`. |
| A10 | 41.12 ("Every number") | The checklist slides off right. Every card with a QR deals into one grid on the right two thirds: program, three vaults, SOL, USDC, rotation (7 codes, 4 + 3), each at 3 px per module (135–147 px). The robbery and rejection cards shrink into a small "not on devnet" tray under the grid (R-A1). Header: Solscan mark + "every code: devnet, on Solscan". | Grid cells 170x200 from x 580 to 1260. Every code is decoded on a 720p still and a phone-encode frame. |
| A11 | 42.64 ("transaction"), 43.44 ("open") | A white highlight frame steps across the seven codes, one per 0.12 s, then rests on the rotation code. | Prop move only. |
| A12 | 44.78–46.78 | Everything frozen (handoff hold). | `T.hold`. |

The robbery and rejection cards are only on screen briefly, and A10 keeps them visibly apart from "every number … a transaction". The ruling is the composer's (Q1).

### Scene 9 head fixes, folded into this re-render (composer, 16 Oct)

Scene 9 is re-rendered with the testimonial anyway, so two head fixes go into the same build. **All head sheets are regenerated** (J1–J2, S1–S4, LAB, and the new LAB2).

1. **Jaw notch (chin patch).** `zone.png` and `kill.png` are centred on x 625 and hard-kill x < 453 below y 950, which cut a rectangular notch out of the lower-left jaw (sprite x < 39, y > 161). Apply the composer's patch `chin-s09-heads.diff` to `pipeline/s09/heads.py`: it builds recentred masks (`out/heads/zone-jaw.png`, `kill-jaw.png`) around the jaw centre JX. The patch has JX = 539 for scene 9's own lines (jaw span x 331–747). The testimonial is a different stretch: its jaw-span centre on rows 930–1080 of `matte-full-alpha` is 541–549 at eight times between 518.9 and 532.5 s (median 545). So the build makes JX a per-row value: 539 for J1–S4 and LAB, 545 for LAB2. It rechecks each row's median before keying, and if every row lands within ±6 px, one shared value is used. Look draft A already uses these recentred masks at JX = 545, and the notch is gone (before/after checked on 2x crops of the head).
2. **Joe's chin.** Joe's crop box cuts off the bottom of his chin and leaves white under it. Fix:
   - Extend the sprite crop lower: 760x1100 at (250, 150) → 760x1200 at (250, 150). The cell goes from 152x220 to 152x240, so sheets are 16 x 12 cells of 152x240 (2432x2880), and more neck shows.
   - The crop top is unchanged, so `KEY_CHIN_X` 289 and the key chin row 905 stay valid. The forehead track (glasses rows 66–112) is unaffected.
   - `s09-seed.html`: `.hd` height 220 → 240, and the sheet offset uses a cell-height constant (`CH = 240`) instead of the literal 220.
   - The head is already drawn BEHIND the body (`makeFig` puts `.hd` before the pose images), so the longer neck runs down under Joe's t-shirt collar. Checked on 2x crops at 2.6 s and 9.0 s with the collar line drawn: no skin or white may show above or outside the neckline. If the street pose's neckline sits lower than the extended neck reaches, the crop goes to 760x1250 (cell 152x250).
   - The suit and the lab coat get the same taller cells (one sheet format for the scene). Their collars already cover the neck.

## 4. Part B: back at the news desk (scene 10, film/s10)

The desk is the opening's desk. Layers as in `build-opening-v7.sh`:
- the back layer is `s02-news.html?layer=back` (unchanged, one still);
- the anchor is the matte, cut to B1 + B2;
- the front layer is a new `s10-news.html?layer=front`: a copy of s02-news's front (desk, LIVE • lemur • CNN bug, lower third, OTS box, chyron, SPECIAL REPORT wipe) with the scene 10 timeline.

They are composited with a `desk-s10.filter` that differs from desk-v7.filter only in the trims, plus the punch-in on B2.

Word times (scene s): Thanks 2.23 (ends 3.18), If 3.27, asleep 5.03, crypto 6.55, nerd 7.03, like us 7.51 (ends 7.69), I told you 8.77, math 9.57, And there's 10.75, white paper 11.95, Go check it out 12.17 (ends 12.97), [cut 13.35], The next 13.57, stateless 15.89, For this 16.93, SLH 18.45, DSA 19.12 (ends 19.66), The signatures 20.20, bigger 21.16, never 21.80, track 22.28, spent 23.24, And my 23.84, favorite 24.64, vault 27.84, guard 28.24, upgrade authority 28.88 (ends 29.53), It's 29.77, bunker 30.09, protecting 30.49, bunker 31.05 (ends 31.17), Lots 31.79, cook 32.43, lab ≈32.8 (ends 33.02).

| beat | time (s) | on screen | how it is made |
|---|---|---|---|
| B0 | 0.00–2.00 | **We now return to the studio.** The opening's exit, reversed. 0.00–0.55: the red SPECIAL REPORT panel sweeps in left to right over scene 9's last frame (the opening's keyframes and easing). 0.55–1.10: full cover, SPECIAL REPORT, with a white strip under it typing "WE NOW RETURN TO THE STUDIO" (Inter 800, 34 px; Q5). 1.10–2.00: the panel runs back out to the left (the opening's wipe played backwards), revealing the desk. A 0.3 s white flash at the reveal (the opening's entry flash). | Front-layer `.wipe`, same element and CSS. Scene 9's last frame is a PNG pulled by `build.sh assets`, as scene 9 pulled scene 8's. |
| B1 | 1.60–2.05 | The lower third slides in as in the opening: tag **UPDATE** (Q6) / bar LIAM / sub "Liam C., Chaintail Labs, Senior Bunker Correspondent". Chyron (CT LIVE) running at 150 px/s with new Crypto Twitter jokes (`data/s10-chyron.js`, draft wording, Q7). Bug: LIVE • lemur • CNN. | Opening CSS. |
| B2 | 2.23–7.69 | "Thanks for sticking around. If you made it this far …" ["crypto" 6.55] the bar hard-cuts to **CRYPTO NERD**. [7.10–7.45] **GRAPHY** squeezes in: CRYPTO and NERD slide apart and GRAPHY grows from scaleX 0 to 1.06 to 1 in yellow, so the bar reads **CRYPTOGRAPHY NERD**, done before "us" ends (7.69). **This is look draft B.** | Three spans; GRAPHY's wrapper width animates, so NERD is pushed right. |
| B3 | 8.77–10.13 | "I told you the math would be worth it." Nothing new on screen (the brief has no beat here). | |
| B4 | 11.95 ("white paper") | OTS box in top right (the opening's 410x230 box, white outline, red tag WHITEPAPER): the title "Solana Bunker: stable custody addresses with replaceable hash authorization" (the whitepaper's first heading), "research/whitepaper.md", and a QR to https://github.com/chaintail/solana-bunker/blob/main/research/whitepaper.md (version 4, 41 modules with quiet zone, 5 px per module = 205 px, decoder-checked). | Opening's `.ots` box, no zoom. QR from `pipeline/s10/qr.mjs` (uqr, ECC L). |
| B5 | 13.35 | **Jump cut** (B1 → B2, 18.45 s of take removed). It is hidden by a hard punch-in from 100 % to 108 % of the anchor framing (a "second camera"), while the OTS box stays up across the cut. | Matte scaled 567x756 instead of 525x700, offset so the face centre stays put. Fallback R-B3. |
| B6 | 15.89 ("stateless") | The OTS box exits up. The lower third flips to **COMING UP NEXT** / A STATELESS BUNKER. ["SLH" 18.45] the bar flips to **SLH-DSA (FIPS 205)**. ["bigger" 21.16] the sub types "7,856-byte signatures". ["never" 21.80] it continues ", no state to track". | Same lower third; the tag widens to fit (Inter 800, 30 px). 7,856 bytes is the brief's number: the FIPS 205 SLH-DSA-SHA2-128s signature size. |
| B7 | 23.84 ("my personal favorite idea") | The lower third returns to UPDATE / LIAM. | |
| B8 | 30.09 ("bunker") | OTS box in with scene 4's vault door (its `vault(parent, cx, cy, R, level)` SVG drafting function, ported, fully drawn). ["protecting" 30.49] the door's centre opens into a second, smaller vault door (level 1) that draws itself inside it. ["bunker" 31.05] a slow push into the inner door (box content only, 1 → 1.35 over 1.2 s). | Port of `s04-bunker.html`'s `vault()` into a shared `lib/vault.js`; nesting = a second call at R × 0.42 inside the hub. |
| B9 | 32.43 ("cook") | A beaker bug pops in top left (0.25 s, scale 0 → 1.15 → 1): a flask icon with bubbles rising on a loop and the label LAB, in the bug style of LIVE / CNN. The OTS box exits at 32.20. | SVG; the bubbles are props. |
| B10 | 33.02–33.40 | Liam's last frame of B2 runs on to 583.60 (the pause before "Feel"). Scene 11's ident cuts in at 33.40. | |

## 5. Part C: Chaintail News Network credits (scene 11, film/s11)

| beat | time (s) | on screen | how it is made |
|---|---|---|---|
| C0 | 0.00–0.35 | Broadcast hit: four diagonal bars (red #e30613, navy #0d1830, #7fa6ff, white) sweep across over scene 10's last frame and leave the ident background. | DOM bars, eased. |
| C1 | 0.35–3.00 | **Ident.** Swirling abstract colours in the desk palette: two conic gradients rotating in opposite directions at 9°/s and −14°/s, three blurred colour blobs on slow Lissajous paths, light rays from the opening's studio. [0.35–1.15] the lemur logo (`assets/chaintail-logo-white.svg`) spins in: rotateY 720° → 0, scale 0.2 → 1.08 → 1. [1.15–1.75] CHAINTAIL NEWS NETWORK, letters dropping in 0.03 s apart (Inter 800, letter-spaced). [1.80–2.05] **CNN** slams in (Oswald 700, 180 px, scale 2.4 → 1, a 2-frame frame shake) with a red rule shooting out under it. [2.20–2.60] a light streak sweeps across the logo. Hold to 3.00. | All seeded and t-driven (`film.rng`). The logo is a prop, so the 35° rule (for characters) does not apply to its spin. |
| C2 | 3.00–3.60 | **The split.** The ident panel squeezes to the left third (1280 → 427 px wide, ease-in-out). Logo, CNN and the network name shrink into the panel's header. The parchment card slides in from the right edge (427–1280), and a red divider bar drops down between them. | |
| C3 | 3.60–30.50 | **The roll.** Credits scroll up under the header at 5 px a frame (150 px/s, whole pixels, so no shimmer), in a window from y 190 to 720 with soft top and bottom edges. Each line is on screen for 3.5 s. Text: `data/s11-credits.js`, one block (below). The right two thirds hold still: the parchment (Chaintail Labs R&D / Solana Vault, the colour lemur, the GitHub QR with the GitHub mark and github.com/chaintail/solana-bunker beneath, the Telegram QR with the Telegram mark and t.me/chaintail beneath). [Feel 4.12] "Feel free to reach out with any questions!" fades in on the parchment as Liam says it (C1, 3.90–6.28, voice only). **Look draft C is t = 8.1, with the CAST block in the window.** | Heading Oswald 700 34 px white. CAST / VOICE ACTORS sub-roles Oswald 700 30 px yellow (#ffd400). Names Inter 700 25 px #c9d6f2, one per line, long ones wrap. Joke lines Inter 700 italic 24 px yellow. 30 px between blocks. Measured roll height 3503 px; distance 530 + 3503 = 4033 px = 807 frames = 26.9 s. Codes: 7 px per module (repo, 259 px) and 8 px per module (Telegram, 264 px), ink on paper colour, quiet zone 4 modules. |
| C4 | 30.50–35.00 | Crossfade (0.5 s), then full-screen card 1, held 4.0 s: "Based on a true story." / "Events were dramatized." / "Characters and names may have been changed to protect the identity of victims." / "Any resemblance to actual elliptic curves, living or broken, is purely coincidental." | Liberation Serif italic, white on black, centred: 54 px for the first two lines, 30 px for the last two. |
| C5 | 35.00–38.40 | Crossfade (0.4 s), then card 2, held 3.0 s: PRODUCT OF / the lemur logo (white) / **Chaintail Labs** / © 2026 Chaintail Labs. | |
| C6 | 38.40–39.40 | Fade to black. The bed fades with it. | |

**Credits text** (`data/s11-credits.js`): Liam's final list from the brief on main 4aef292, section C.3, verbatim. It is one block, so a text change is one edit. The order is:
1. The 21 headed blocks: EXECUTIVE PRODUCERS … SPECIAL THANKS. CAST and VOICE ACTORS give each sub-role with its name.
2. The two joke lines ("No curves were harmed in the making of this film." / "No meme coins were harmed either. Yet."), at the end of the roll.
3. The brief's closing lines on the two cards C4 and C5 (Q12).
The composer is "Claude-Do" throughout, Mikail has no H, and surnames are initials.

**Readability at 426x240 (look draft C):**
- Headings (Oswald 34 px, caps 24 px tall, so 8 px at 240p) and the CAST sub-roles (30 px, so 7 px) read.
- Names (Inter 25 px) are softer but legible, which the brief allows.
- On the parchment, the brand, the ask line and the Telegram link read; the GitHub link (19 px Special Elite) is small but legible.

## 6. Production method per visual (summary)

| visual | method |
|---|---|
| lab coat (A) | s09 bodies (+ professor-point), lip-synced head sprites from the matte (`heads.py`, head key), stop-frame only, upright |
| results cards, QR (A) | DOM/SVG; codes from `data/s09-results.js`. `pipeline/s09/qr-results.mjs` reads `artifacts/public-deployment.json` by operation name or vault mode and fails if a tx is missing or unconfirmed, so no number is typed in |
| anchor (B) | matte comp + alpha, two trims, despill, composited between the backdrop still and the front layer frames (ffmpeg on dev-mac, as the opening) |
| desk graphics (B) | `s10-news.html` (front layer, transparent PNG frames) |
| nested vault (B) | port of scene 4's `vault()` drafting SVG |
| ident, credits, parchment (C) | `s11-cnn.html`, one full-frame HTML scene; parchment after the deck's closing slide (`C9Close.tsx`) with the film's vendored fonts (Playfair Display / Liberation Serif / Special Elite instead of Libre Caslon / Courier Prime, which are not vendored) |
| audio | `take-dn.wav` cut per section 2, bed, loudnorm, limiter (one `build.sh audio` per part) |
| post | A: vignette only (colour half of scene 9); B: none (the opening had none); C: none. Masters crf 14; phone 960x540 crf 26 |

Files after approval:
- A, in order:
  1. `heads.py`: apply `chin-s09-heads.diff`, then JX per row (539 for J1–S4 and LAB, 545 for LAB2) and the 760x1200 crop (cells 152x240).
  2. Add row LAB2 (518.62–533.30) through `s09-timing.py`, then **regenerate every sheet** and `s09-headbox.js`.
  3. `bodies.py` (done; professor-point).
  4. `s09-seed.html`: `#testi`, `.hd` 240 px, `CH` constant.
  5. `s09-timing.py`: TA row, `T.testi`…`T.hold`, total 46.78.
  6. `qr-results.mjs` (done).
  7. Stills: the jaw at J1, S2, S3 and LAB2 on 2x crops (no notch); Joe's neck under the collar at 2.6 s and 9.0 s; every v2 beat re-opened, because every head changed.
  8. `capture.sh` (all 1403 frames in three chunks, since frames 0–894 change with the heads), then `build.sh` → `s09-v3.mp4` and `s09-v3-phone.mp4`.
- B: `s10-news.html`, `data/s10-chyron.js` (done, draft), `pipeline/s10/{s10-timing.py,qr.mjs,capture.sh,build.sh,desk-s10.filter,stills.sh}`.
- C: `s11-cnn.html`, `data/s11-credits.js`, `data/s11-qr.js` (done), `pipeline/s11/{s11-timing.py,capture.sh,build.sh,stills.sh}`.
- Every capture is chunked, each chunk packed to FFV1 and its frame folder emptied with a literal path (`find render/a -name 'f*.png' -delete`).
- Stills of every beat are opened, each also at 426x240. Every QR is decoded on a 720p still and a phone-encode frame.

## 7. Risks and fallbacks

| # | risk | fallback |
|---|---|---|
| R-A1 | **No explorer-openable signature exists in public-deployment.json for the robbery or the rejection.** The robbery (version two's front-run) is only local SVM test M03 in `artifacts/acceptance-matrix.json`. The rejection is a devnet *simulation* (`…-xmss-withdraw-sol-destination-substitution`, Custom 12 / 0xc, `network_confirmation: false`), which has no signature. Liam's line says "Every number on the screen is a transaction you can open in the explorer". | Default (drafted): both claims are ticked and get cards with no QR, labelled honestly ("dramatized", "devnet simulation"). They are kept out of the A10 grid of openable codes. Options: (b) QR to GitHub evidence instead (the M03 test, the json's simulation entry); (c) drop the two cards and leave only the ticks; (d) run the front-run on devnet first (out of scope for the film). |
| R-A2 | The three vault QRs arrive 0.72 s before "SOL", too fast to scan. | They are scannable in the A10 grid, held about 3.7 s plus the 2 s hold. |
| R-A3 | The grid's codes are 3 px per module at 720p, so 2.25 px at 540p. | Decode check on the phone encode. Fallback: grid of the 4 tx codes only at 4 px per module, with the program and vaults as a second page on "screen". |
| R-A4 | Scene 9 v2's 2.00 s frozen hold (27.83–29.83) now sits before the testimonial: 2.3 s with nothing moving before he speaks. | Default: v2's 29.83 s timing untouched, per "keeps its existing 29.83 s". Option: trim the hold to 0.8 s (scene 9 46.78 → 45.58 s) (Q2). |
| R-A5 | The repo QR on the CALL NOW bar is dropped in the testimonial strip, which is 72 px tall. The URL stays. | Keep a 116 px repo QR at the strip's right end over the grid area (crowds A10) (Q3). |
| R-A6 | The lab coat's head scale and collar join for professor-point are not yet verified on 2x crops (v2 checked the other five poses). | Same check as v2 on the first stills; `hx` per pose from `bodies.py`. |
| R-B1 | **dev-mac Chrome stalls.** From about 23:39 to 23:56 (16 Oct, Eastern), every Chrome launch on dev-mac hung at startup in SkyLight's WindowServer session lookup (`get_session_port`, sampled). That included Google's chrome-headless-shell and another worker's s08 capture, which sat at 0 frames. WindowServer (pid 203, up 9 days) was in state U. It recovered by itself at 23:56. The system volume has 4.5 GB free, and there are 14 leftover `film-chrome-*` profiles from 14 Oct in `$TMPDIR` (not mine). | The look scripts retry a capture 3 times. For the builds: test that Chrome starts (10 s) before each chunk and wait if it does not. A long stall needs someone at dev-mac (logout or reboot), which I did not attempt. |
| R-B2 | Matte edges in the tail: the AirPod shows in the left ear (it does in the opening too), and there is a faint halo at the hair. | As the opening; no change. |
| R-B3 | The punch-in may still read as a jump cut. | Move the OTS swap (whitepaper out, SLH-DSA in) onto the cut, or a 6-frame whip zoom. |
| R-B4 | Transcript tokens lead the audio by up to 0.4 s. | Every anchor is rechecked with the energy scan in the timing scripts. |
| R-B5 | The chyron jokes are new wording, not Liam's. | `data/s10-chyron.js` is one list; or reuse the opening's jokes verbatim (Q7). |
| R-B6 | The OTS whitepaper box has the code and a long title in 410x230. | Title in two lines at 18 px; the code is the priority (5 px per module). |
| R-C1 | Liam's final list makes a 26.9 s roll at 5 px a frame, with only 2.4 s of voice: a long stretch with only the bed. | 6 px a frame (22.4 s, 2.9 s per line; the CAST sub-roles still read at 240p), or start with EXECUTIVE PRODUCERS already in the window (−3.5 s) (Q9). |
| R-C4 | STUNTS reads "Every transaction in this film is real and open in the explorer.", but the robbery and the rejection have no devnet transaction (R-A1). | It is Liam's text, kept verbatim; the ruling on Q1 should cover it (e.g. the A10 "not on devnet" tray makes the distinction on screen). |
| R-C2 | The deck's parchment fonts (Libre Caslon, Courier Prime) are not vendored in the film. | Playfair Display / Liberation Serif / Special Elite (drafted); or vendor Libre Caslon (OFL) into `film/fonts`. |
| R-C3 | Names at 240p are soft (allowed); the CNN header subtitle is borderline. | Headings and sub-roles are what is checked; the header can go to 22 px. |
| R-G1 | I could not listen. Every point comes from silencedetect plus the energy scan. | Listening files, made on approval: `ending/out/cut-B1B2-join.wav` (544.4–545.10 + 563.55–564.6) and the in and out of each segment. |

## 8. Look drafts (rendered on dev-mac)

Output: dev-mac `~/video-work/solana-bunker/ending/out/ending-look-{A,B,C}.png` (1280x720) and `ending-look-{A,B,C}-240.png` (426x240). The 720p stills are also in the composer's outbox as `ending-look-A.png`, `-B.png` and `-C.png`. Every QR on them decodes (zxing-cpp) on the 720p still, on a 960x540 downscale and on a frame of a 960x540 crf 26 encode of the still.

- **A** (`film/s09`: `s09-testimonial-look.html`, `pipeline/s09/testimonial-look.sh`, `qr-results.mjs`, `data/s09-results.js`, `bodies.py` with professor-point): beat A9, "rotation".
  - The lab coat's head is keyed from the take at 528.45 s with the recentred jaw masks (JX 545). The checklist runs LIVE ON DEVNET … ROTATION, and the card ROOT ROTATED! carries the rotate-root code. Name card, packshot with the FREE tag, CALL NOW strip, vignette.
  - The code reads exactly `https://solscan.io/tx/5U4B7zhg…8RjML5iy?cluster=devnet`, the json's `v1-live-20261012-xmss-rotate-root`.
  - At 240p the checklist with its "mock / dramatized / simulated" labels, the card header, the name card, FREE and CALL NOW all read.
  - Fixes after looking: the name card was clipped by the strip (moved up 40 px); REAL RESULTS covered the card title (moved to the top-right corner); the finger landed on a checkbox (list moved right); the labels were unreadable at 240p (15 → 20 px); the old masks cut a notch out of the jaw (re-keyed with the chin patch's masks).
- **B** (`film/s10`: `s10-desk-look.html`, `data/s10-chyron.js`, `pipeline/s10/desk-look.sh`): beat B2. The matted anchor at 539.30 s ("like us"), composited as desk-v7.filter, under CRYPTOGRAPHY NERD with GRAPHY in yellow. At 240p the lower third, the sub line, the bug and the chyron read.
  - Fixes after looking: the first composite had no anchor (the single-frame PNG inputs and the seeked matte had different start PTS; now looped and reset to 0); a proofreader's caret under GRAPHY collided with the sub line, so it was dropped.
- **C** (`film/s11`: `s11-credits-look.html`, `data/s11-credits.js`, `data/s11-qr.js`, `pipeline/s11/{qr.mjs,credits-look.sh}`): beat C3 at t = 8.1, with Liam's final list (STORY INSPIRATION leaving at the top, then the CAST block). Both outro codes decode: `https://github.com/chaintail/solana-bunker` and `https://t.me/chaintail`.
  - Fix after looking: the GitHub link ran into the Telegram mark (columns widened, links 22 → 19 px).

## 9. Open questions for the composer

- Q1 (R-A1): the robbery and rejection have no devnet signature. Use the default (honest labelled cards, no QR, kept out of the grid), GitHub-evidence QRs, or ticks only?
- Q2 (R-A4): keep scene 9's 2 s hold before the testimonial, or trim it to 0.8 s?
- Q3 (R-A5): drop the repo QR from the CALL NOW strip during the testimonial (the URL stays)?
- Q4: the name card text "Dr. L. C." / "cryptography nerd" and the tab "SATISFIED CUSTOMER", as briefed. OK?
- Q5: the wipe's second line "WE NOW RETURN TO THE STUDIO" on the red panel, or SPECIAL REPORT alone?
- Q6: the lower-third tag for the sign-off: UPDATE (drafted), BREAKING (as the opening), or LIVE?
- Q7: the new chyron jokes (draft in `data/s10-chyron.js`), or the opening's list?
- Q8: the punch-in to 108 % on the jump cut, or a whip zoom?
- Q9 (R-C1): roll speed 5 px a frame (26.9 s, drafted) or 6 px (22.4 s)?
- Q10: the closing cards on black (drafted), or on the parchment?
- Q12: the brief's closing lines split over two cards: card 1 the four "Based on a true story …" lines (4 s), card 2 PRODUCT OF + logo + Chaintail Labs + © (3 s). Or all on one card?
- Q11: Liam's last line voice only (drafted), or the anchor in a small box on the CNN panel?

## 10. As built: scene 10 v1

Rulings applied: Q5 the wipe's "WE NOW RETURN TO THE STUDIO", Q6 UPDATE, Q7 the drafted jokes, Q8 the punch-in.
- **Cut list and lengths:** as section 2, B1 533.75–545.10 at 2.00 and B2 563.55–583.50 at 13.35. Scene 33.40 s, 1002 frames. The picture switches at frame 401 (13.367 s). Each footage stream is seeked so its source time = scene time + 531.75 (B1) or + 550.20 (B2), so lips match the audio frame by frame.
- **Audio:** −16.4 LUFS, −1.9 dBTP on the master. `take-dn.wav` is regenerated in `s10/out` with the same chain.
- **Word anchors:** moved from the beat table after a 20 ms energy recheck. "white" 11.55 (was 11.95), "nerd" 6.89, "stateless" 15.48 (15.89), "bigger" 20.92, "never" 21.74, "bunker" 30.02 / 30.82, "cook" 32.24. GRAPHY squeezes in 7.19–7.54, ending before "us" ends (7.69). `data/s10-edl.js` owns the numbers.
- **Nested vault:** the inner door is drawn in scene 4's accent yellow (#ffd23f), and the outer door's hub, spokes and two inner rings fade as it opens. The first stills showed the inner door blending into the outer one. Port: `lib/vault.js` (scene 4's `vault()`, strokes scaled with R).
- **Fixes after looking:** the chyron's CT LIVE label showed through the SPECIAL REPORT wipe (`.wipe` z-index 10).
- **Scene 9's last frame (deviation):** under the wipe this is still from `s09-v2.mp4`. Scene 9 v3 (with the testimonial) is being built by another builder. When it exists: `S09V=v3 build.sh assets` and `build.sh video v2`; no recapture.
- **Checks:**
  - Stills opened at 0.3, 0.8, 1.5, 2.1, 6.7, 7.3, 7.6, 11.9, 13.33, 13.4, 16.0, 18.6, 22.4, 24.0, 30.2, 30.7, 31.6, 32.5 and 33.35, plus the same times on master frames.
  - The whitepaper QR decodes (zxing-cpp) on a master frame and on a phone frame, at 720p and at 540p.
- **Files:**
  - `s10-news.html`, `lib/vault.js`, `data/s10-{edl,qr,chyron}.js`, `pipeline/s10/{s10-timing.py,qr.mjs,build.sh,capture.sh,stills.sh}`.
  - Outputs: dev-mac `~/video-work/solana-bunker/s10/out/s10-v1.mp4` and `s10-v1-phone.mp4`.

### Scene 10 v2 (Liam's notes)
- The lower third first reads CRYPTO NERD. Then NERD slides right (7.19–7.44) and GRAPHY fades in yellow between them (7.31–7.54), ending before "us" ends.
- The sub line under the name reads "Liam C. · Bunker Correspondent, Chaintail Labs".
- Positions: the bar, sub line, ticker and LIVE / lemur / CNN bug are on the same pixels as opening v7 (side-by-side checked against `opening-v7.mp4` at 30 s). Nothing moved.
- Fully recaptured. Output: dev-mac `s10/out/s10-v2.mp4` and `s10-v2-phone.mp4`, 33.40 s, −16.4 LUFS / −1.9 dBTP. The whitepaper QR decodes on master and phone frames.

### Scene 10 v3 (scene 9 v3 underneath the wipe)
- The frame under the SPECIAL REPORT wipe (0–0.55 s) is now the last frame of `s09-v3.mp4` (bd2c428, the testimonial's results grid). It was built with `S09V=v3 build.sh assets` and `build.sh video v3`, with no recapture. Nothing else changed.
- Output: dev-mac `s10/out/s10-v3.mp4` and `s10-v3-phone.mp4`, 33.40 s, 1002 frames, −16.4 LUFS / −1.9 dBTP. The whitepaper QR decodes on master and phone frames (12.5 and 14.5 s) at 720p and 540p.

### Scene 10 v4 (Liam's notes)
- **No name bar anywhere.** The lower third slides in at 6.17 s (0.40 s before "crypto") already reading CRYPTO NERD. NERD slides and GRAPHY fades in as in v2. After COMING UP NEXT (B7, from 23.84) it reads CRYPTOGRAPHY NERD again. The sub line "Liam C. · Bunker Correspondent, Chaintail Labs" stays under it. The CNN bug still fades in at 1.60.
- **No punch-in.** B2 is composited at B1's size and place (525x700 at 377,-20), so the head keeps one size for the whole scene. The jump cut is hidden by a 2-frame white flash in the front layer: frame 401 is solid white, frame 402 is half white, and both sit above the chyron. The wipe's own flash (1.10–1.40) is unchanged.
- **Head match across the cut:** master frames 400 and 403, glasses outer temples at row 285 are 510–775 (265 px) and 508–771 (263 px). The rims are rows 240–319 on both. B2's head is turned very slightly (the bridge sits about 11 px left).
- **Composite fix:** the front layer's FFV1 Matroska chunks carry millisecond timestamps, so the overlay took the previous front frame on about a third of frames (in v1–v3 too). It is now retimed (`settb=1/30,setpts=N`), so master frame n carries front frame n (checked on frames 398–404).
- Output: dev-mac `s10/out/s10-v4.mp4` and `s10-v4-phone.mp4`, 33.40 s, 1002 frames, −16.4 LUFS / −1.9 dBTP. Cut strip (frames 400/401/402): `s10-v4-cut.png`. The whitepaper QR decodes on master and phone at 720p and 540p.

### Scene 10 v5 (Liam's note)
- After A STATELESS BUNKER and SLH-DSA (FIPS 205), the lower third does not return to CRYPTOGRAPHY NERD. It becomes a third COMING UP NEXT reading BUNKER IN A BUNKER, with the sub line "Next on Chaintail News", from the onset of "And my personal favorite idea" to the end of the scene.
- The onset (`T.and_fav`) is take 573.53 s, scene 23.33 s, frame 700, taken from the 20 ms RMS of the denoised take, which leaves silence at 573.38–573.50 after "spent". Frame 699 reads SLH-DSA and frame 700 reads BUNKER IN A BUNKER.
- The bunker-in-a-bunker shoulder box is unchanged. Only front chunk B (17 s to the end) was recaptured.
- Output: dev-mac `s10/out/s10-v5.mp4` and `s10-v5-phone.mp4`, 33.40 s, 1002 frames, −16.4 LUFS / −1.9 dBTP. The whitepaper QR decodes on master and phone at 720p and 540p.

### Scene 10 v6 (Liam's notes)
- **The bar is on screen for the whole scene.** It sits under the wipe from 0.55 s and is revealed as the wipe moves out: the white tag reads UPDATE and the red box is empty. At 6.32 s (0.25 s before "crypto") CRYPTO NERD pops in (0.2 s, scale 0.70 → 1.06 → 1). The NERD slide and GRAPHY fade are unchanged. The sub line "Liam C. · Bunker Correspondent, Chaintail Labs" stays under it.
- **Switches are no longer hard cuts.** Each switch is centred on its old time: the changed texts fade out (150 ms), the white tag and red box resize to the next state's widths (250 ms, eased in and out), and the new texts fade in (150 ms).
  - UPDATE → COMING UP NEXT at 15.48 s resizes, so it runs 15.205–15.755.
  - SLH-DSA (18.44) and BUNKER IN A BUNKER (23.33) keep the COMING UP NEXT width, so only the changed texts cross: 150 ms out, 150 ms in. The sub line fades only when it changes.
  - The tag width is measured from the text (as v5: UPDATE 180 px).
- Strip across the first switch (15.3, 15.4, 15.5, 15.6, 15.7 s): `s10-v6-transition.png`.
- Output: dev-mac `s10/out/s10-v6.mp4` and `s10-v6-phone.mp4`, 33.40 s, 1002 frames, −16.4 LUFS / −1.9 dBTP. The cut flash is unchanged (frame 401 white, 402 half). The whitepaper QR decodes on master and phone at 720p and 540p.
