# Film plan: scene 8, one transaction (plan for review, nothing built yet)

Brief: `docs/presentation/film-brief-s08-txsize.md` (main 0bbe8f5). Branch `film/s08` (worktree `~/code/solana-bunker-s08`) = main + `film/floating-head` (fc5a163) + `film/s07` (98cc04c, the slide 7 plan; slide 7's build is still in progress and not on the branch).
This document is the plan only. The one thing rendered so far is the look draft (section 7).

## 1. Audio: the cut list

Source: Liam's take `audio/bunker-take.wav`, the only read of this passage (456.2–495.7 s). Same chain as slides 5–7: afftdn nr=18 with the profile from the take's silent 0.10–0.70 s, applied once to the whole take; cut; 20 ms fades on every cut; brown-noise bed (lowpass 220, volume 0.05) under the whole scene; one two-pass loudnorm to -16 LUFS / TP -1.5. In/out points sit in the pauses found by `silencedetect=n=-38dB:d=0.12` on the denoised take (run on dev-mac). Word times come from the transcript tokens, rechecked against a 50 ms energy/spectral scan; the tokens run up to 0.4 s early here (for example "I guess" is at 468.14 s, not 467.84 s).

The take follows `pitch-script-final.md`, not the brief's draft 3 wording. Every brief line is in the take, plus three short lines; I use the take as recorded (as slides 6 and 7 did):

| brief (draft 3) | take |
|---|---|
| They are way smaller… | They're way smaller. **Only 2500 bytes.** |
| But… damn that 1,232 byte transaction size limit! | Ah, damn it, that 1232 byte transaction limit. |
| Sigh… i guess we could use temporary data accounts… | (a real sigh, 466.96–467.96 s) I guess we could use temporary data accounts to upload signatures in pieces. |
| That's not cool… | Not really cool. |
| (on-screen in draft 3: "Solana Transactions V1 to the rescue!", 1,232 ticks to 4096) | **Oh, but Solana Transactions V1 to the rescue. 4,096 bytes.** |
| So we rebuilt it. | So we built that, and it worked. (transcript reading; checked by ear before the cut, see R1) |

| id | speaker | line (as spoken) | source in–out (s) | scene in–out (s) |
|---|---|---|---|---|
| (load) | | scene 7's last frame sucked into the cabinet, bed only | | 0.00–1.20 |
| E1 | engineer | XMSS signatures seem awesome. | 456.40–458.66 | 1.20–3.46 |
| E2 | engineer | They're way smaller. | 458.76–459.76 | 3.56–4.56 |
| E3 | engineer | Only 2500 bytes. Ah, damn it, that 1232 byte transaction limit. | 460.06–465.86 | 4.86–10.66 |
| S1 | lab coat | (sigh) | 466.90–467.99 | 11.70–12.79 |
| E4 | engineer | I guess we could use temporary data accounts to upload signatures in pieces. | 468.10–471.95 | 12.90–16.75 |
| E5 | engineer | But from our research, that took five transactions just to do a simple withdrawal. | 472.86–477.11 | 17.66–21.91 |
| (trucks) | | trucks 4 and 5 arrive, bed only (inserted 1.80 s) | | 21.91–23.71 |
| C1 | lab coat | Not really cool. | 477.12–478.30 | 23.71–24.89 |
| E6 | engineer | Oh, but Solana Transactions V1 to the rescue. | 479.12–481.95 | 25.71–28.54 |
| E7 | engineer | 4,096 bytes. | 482.30–484.05 | 28.89–30.64 |
| E8 | engineer | So we built that, and it worked. | 484.40–486.62 | 30.99–33.21 |
| (drop) | | the block falls through the slot, bed only (inserted 0.60 s) | | 33.21–33.81 |
| E9 | engineer | One transaction, 3100 bytes, about half a million compute units, and the full signature verifies on-chain in a single shot. | 486.68–495.10 | 33.81–42.23 |
| (tag) | | LEVEL COMPLETE, rotation text box, bitmap, new tree, credits table; bed only | | 42.23–48.50 |

Scene length 48.50 s (1455 frames at 30 fps). There are only two real cuts. E1 to E5 play as one continuous stretch of the take (456.40–477.11) with its own pauses, and C1 to E8 are another (477.12–486.62). The rows exist only to assign the lip-synced heads. The cut after E5 has almost no silence ("withdrawal" runs into "Not", see R2). The cut after E8 sits in a 0.2 s pause (486.54–486.74). Not used: the trailing "Yeah." (495.68).

Lip rule: the speaking character is always on screen with that line's lip-synced sprite. Between his lines he holds the last frame of his previous line. A character who is silent holds a closed-mouth frame.

## 2. Beat table (scene times; key words in brackets with their scene time)

| beat | time (s) | on screen | how it is made |
|---|---|---|---|
| 0 | 0.00–1.20 | Scene 7's last frame, full screen (0.00–0.25). It gets sucked into the cabinet: the camera pulls back from the screen (the cabinet starts at 2.2x, centred on the screen, and eases to 1x) while the old frame shrinks with it (0.25–0.60). CRT power-off: the picture squashes to a bright white horizontal line (0.60–0.75). Load: the line expands back up as pixels, in chunky mosaic steps of 32, 16, 8 and 4 virtual px (4 frames each), into the empty playfield (0.75–1.20). The engineer stands at the cabinet's left side throughout. | Scene 7's final graded last frame as a PNG (`assets/s08-s07-last.png`, pulled from slide 7's output; stand-in R9) inside `#screenBox`. Squash = scaleY on the screen box plus a white overlay. Mosaic = the playfield canvas drawn at 1/8, 1/4 and 1/2 resolution and scaled up pixelated. |
| 1 | 1.20–4.86 | Engineer speaks E1–E2. ["XMSS" 1.28] a huge magenta LAMPORT block "8,192" drops from the top. At 240 virtual px it is 1.5x the screen width, so it jams between the screen walls, crushed and bulging (lands 1.70, 2-frame shake). ["awesome" 2.88] a small cyan XMSS block "2,500" drops onto it. ["smaller" 4.08] the LAMPORT block explodes into pixels (about 300 seeded particles, gravity, 0.6 s), the XMSS block falls to the floor, and SCORE ticks up by 5,692, the bytes saved (4.1–4.8). | Everything drawn on the 160x120 playfield canvas per frame from t, seeded, so any frame is reproducible. Block widths 0.0293 virtual px per byte: 8,192 = 240, 2,500 = 73, 1,232 = 36, 4,096 = 120. |
| 2 | 4.86–12.90 | Engineer speaks E3. ["Only 2500 bytes" 4.92–6.64] the block's "2,500" label blinks twice, with "BYTES" under it. ["Ah" 7.50] three floor bricks drop out of the floor's middle: a slot opens. ["1232" 8.56] the yellow dimension line and "1,232" pop into the slot, plus "TX LIMIT" beside it. The block hops up (game jump, 3 stepped positions) over the slot. ["transaction" 9.84] it drops, does not fit and wedges on the rims (10.00), with a 6-frame screen shake of the whole playfield and grinding sparks. ["limit" 10.48] a red flash, then GAME OVER flashing red (4 Hz) with "2,500 > 1,232" under it (the ">" at double size, set up for beat 4). The engineer freezes at the end of E3 with his head tilted down (no facepalm pose exists, so the brief's fallback). [sigh 11.76] the lab coat pokes in from the right edge (shrug pose, 27° tilt, legs cut by the edge), lip-synced to the sigh, and slides back out at 12.80. | This is the look draft (section 7). Shake = whole-canvas offset of ±2 virtual px for 6 frames. The engineer is one body PNG with the head rotated 11° about the chin, frozen. |
| 3 | 12.90–25.71 | Engineer speaks E4–E5. ["I guess" 12.94] GAME OVER clears and "WORKAROUND LEVEL" slides in as a stage title (2x type, 12.9–14.0). ["temporary data accounts" 14.08] a pixel "TEMP ACCT" box appears at the playfield's right. Outside the screen, at the top right of the frame, the program card "BUNKER PROGRAM 003-A" slides in with its see-the-code card (GitHub QR to `program/src/lib.rs#L118` on main) and proof card (see R8 / Q2). ["upload" 15.36] a pixel saw sweeps through the wedged block. ["pieces" 16.48] it falls apart into 4 chunks. ["research" 18.48] five little pixel mail trucks (12x8 sprites, 2-frame wheel cycle) leave from the left one at a time, each carrying a chunk to the TEMP ACCT box. The fifth carries a red EXECUTE flag. The HUD counter reads "TX 1/5" and steps to "TX 5/5" as each truck arrives (about 0.9 s apart: 19.1, 20.0, 20.9, 21.8, 22.8). Each arrival drops a small ticket box into a row of five under the program card. ["Not" 23.74] the lab coat pokes in from the right edge (professor-point, mirrored body, unmirrored head, as in slide 6), low, under the QR cards, lip-synced. ["cool" 24.59] a red pixel THUMBS-DOWN stamp slams onto the playfield (scale 3 to 1 in 4 frames). | Trucks, saw and stamp are pixel sprites drawn from tiny arrays in the scene file (own pixel art, palette below). The program card, QR cards and ticket boxes are flat HTML cards outside the CRT, in the see-the-code/proof box style of slides 5 and 7. They get no scanlines or curvature, so the QR codes scan. The QRs are pre-generated with `pipeline/s08/qr.py` (port of `s05-qr.py`) into `data/s08-qr.js`. |
| 4 | 24.89–33.81 | (pause) The lab coat slides out. "INSERT COIN" flashes on the playfield and the coin door's red slot light blinks with it (24.9–25.8). Engineer speaks E6–E8. ["Oh, but" 25.79] a Solana coin (three-bar mark, `SolCoin` from `apps/web/src/scenes/cheap/C4V1.tsx`) pops from the engineer's pointing glove and drops into the coin slot in 4 stepped positions (25.8–26.3); "CREDIT 1" appears on the HUD. ["Solana Transactions V1" 26.27] the banner "SOLANA TRANSACTIONS V1" scrolls in from the right across the playfield top, with a flashing yellow "NEW!" label above it. It settles centred at "rescue" (28.19). ["4,096" 28.97] the slot widens: bricks slide apart in 4 steps while its label ticks 1,232 → 4,096 like an odometer (28.97–30.20). The ">" between 2,500 and the limit grows (2x to 4x), spins through 4 drawn pixel frames (> ∨ < ∧ … twice) and settles as "<": "2,500 < 4,096" (29.6–30.4). ["So we built that" 31.05] the "-A" flies off the program card with a tumble (31.05–31.40) and "-B" flies in, overshoots and settles (31.40–31.80). The five ticket boxes shrink away one after another (31.3–32.3, 0.2 s apart) and a single new "TX 1/1" box pops in (32.35). The proof card switches to the Solscan QR for the confirmed v1 withdrawal `CiZmcGsa…` (32.40). ["and it worked" 32.19–32.67] the 2,500 block drops straight through the wide slot and out of the bottom of the playfield (32.4–32.8). | The banner is a pixel text scroller (1 virtual px per frame step, so the scroll stays on the pixel grid). The odometer works on the pixel digits. The card swaps are DOM transforms on the flat cards. |
| 5 | 33.81–42.23 | WIN SCREEN. Engineer speaks E9. The playfield clears to a high-score table look (gold border). ["One transaction" 33.87] "1 TRANSACTION" pops in. ["3100 bytes" 35.46] "3,117 BYTES". ["compute units" 37.69] "518,509 CU". ["verifies on-chain" 40.01–40.65] "SIGNATURE VERIFIED ON CHAIN" types in letter by letter, high-score-entry style. At 40.01 the engineer hard-cuts to the thumbs-up pose (still lip-synced). ["single shot" 41.53–42.10] a green pixel checkmark grows in 4 steps until it fills the screen. Optional: Joe (street-celebrate pose, frozen closed-mouth head) pops up from the bottom right at 41.53, as in slide 5. | Lines in 2x pixel type. Numbers come from `artifacts/public-deployment.json` (`v1-live-20261012-xmss-withdraw-sol`: v1, 3,117 bytes, 518,509 CU). |
| 6 | 42.23–48.50 | Tag, no speech. "LEVEL COMPLETE" (2x, yellow) flashes (42.5–43.3). The text crawl in small pixel type (5x7 font at 2 real px per pixel, 12x14 px glyphs, uppercase) holds Liam's rotation text box on the left two thirds. On the right sits the spent-leaf bitmap as slide 5's LED column: 46 LEDs, green, one turning red (spent). A pixel tree grows from leaves to root under a "NEXT LEVEL" label, the root lights and "ROTATE" stamps under it (43.3–46.0). Then the transaction table scrolls up like end credits (46.0–48.5) and the frame freezes on the last line. | The text box and table are drawn on a second, finer pixel canvas (320x240 virtual) in the same CRT. Credits rows come from `artifacts/public-deployment.json`. XMSS (v1 tx): withdraw SOL 3,117 B / 518,509 CU; withdraw mock USDC 3,214 / 532,564; burn leaves 3,086 / 529,687; rotate root 3,146 / 483,319; new-root withdraw SOL 3,117 / 506,910; new-root withdraw mock USDC 3,214 / 578,944. Earlier vaults (legacy tx): array withdraw SOL 677 / 7,101 and USDC 774 / 9,512; Merkle withdraw SOL 805 / 8,003 and USDC 902 / 10,413. Program deploy; mock USDC mint. 6 s is too short to read all of this (R10, Q3). |

Program boxes: one card that changes from BUNKER PROGRAM 003-A to 003-B, with its see-the-code and proof cards (beats 3–4).

## 3. Characters

- Engineer (the player): `4-engineer-point-clipboard` body (clipboard in his far hand, pointing at the screen), at the cabinet's left side, scale 0.36, feet on the floor line (y 700); his glove tip overlaps the bezel. He lip-syncs E1–E8 and E9 and holds his last frame between lines. Beat 2: frozen with his head tilted 11° down. Beat 5: hard cut to `4-engineer-thumbs-up`. Whole-figure moves only.
- Lab coat (commentary): side pokes from the right edge, never more than 27° from upright. For the sigh: `5-physicist-shrug`. For "not cool": `5-physicist-professor-point`, mirrored with an unmirrored head, pointing left at the stamp. He comes in and goes out horizontally in 3 stop-frame steps.
- Joe (optional, beat 5): `2-street-celebrate`, frozen closed-mouth head, pops up from the bottom edge and freezes.
- Heads: `pipeline/s08/heads.py` (port of `pipeline/s06/heads.py`, same key as `pipeline/head-test/key.sh`). Sprite sheets cut with the audio's in/out points: `film/heads/s08-eng-NN.png`, `s08-lab-NN.png`.
- Bodies: `pipeline/s08/bodies.py`, a port of film/s05's `s05-bodies.py`. It erases the grey oval and keeps the engineer's own hard hat; the head is drawn behind the body, so the collar and hat sit over it. Output `assets/s08/*.png` plus `anchors.js`. Head fit: key chin (338,905), 0.326 key px to body px, chin on the oval bottom (engineer: cx 411.5, chin 303). The look draft shows this fit.

## 4. The arcade look recipe

Room and cabinet (ordinary vector art, not pixel):
- The room is dark purple-black with a magenta glow at the top left and a cyan glow at the right. A dim second cabinet sits in the dark at the far right. The floor is dark carpet with seeded neon specks, and a cool screen-light spill lies in front of the cabinet.
- The cabinet is seen from the front (x 318–1022) with a sliver of side panel and side-art stripes. Marquee "SOLANA BUNKER" in the pixel font with a two-tone chrome fill (yellow, orange band, pink) on a backlit purple panel. Black bezel with magenta and cyan neon pinstripes around the screen. Control panel in perspective with a red ball-top joystick and two buttons. Coin door with two slots, the left one lit red; that is where the coin goes.

Playfield (the CRT), all inside `#screenBox` (640x480 at 350,96):
- Pixel art: one 160x120 canvas drawn per frame from t with no smoothing, shown at 4x with `image-rendering: pixelated`. Everything in the playfield sits on that grid. The tag's small type uses a second 320x240 canvas (2 px per pixel).
- Font: my own 5x7 bitmap glyphs (A–Z, 0–9, , . > < ! - : ? /), 6 px advance, 1x (28 px on screen) for body text and 2x for titles. No font files or licences involved.
- Palette (arcade): black field, blue bricks #1f2fd0/#4c66ff/#10187a, cyan #19e3ff/#0088c0, yellow #ffe000, red #ff2030, magenta #ff2bd6, white, sparse blue stars.
- Phosphor glow: a copy of the playfield canvas, blurred 5 px and brightened, laid over it with screen blend at 0.75.
- Scanlines: a dark line on every virtual pixel row (4 px period). Aperture grille: faint RGB stripes, screen blend.
- Curvature: SVG `feDisplacementMap` on the screen layers with a generated barrel map (offset = (u,v)·r²·6 px, corners about 12 px; `color-interpolation-filters=sRGB`). On top, undistorted: the glass, with rounded corners, inner edge shading and a soft highlight at the top left.
- Post (ffmpeg on dev-mac, with the audio mux): light luma grain `noise=c0s=7:c0f=t+u` and `vignette=angle=PI/4.6`. Master x264 crf 14; phone 960x540 crf 26.

## 5. Files and steps (after approval)

1. `pipeline/s08/s08-timing.py` → `data/s08-edl.js` and `out/s08-audio.filter` (section 1; two real cuts; SFX markers in `markers` for coin, explosion, wedge and GAME OVER, nothing in the mix).
2. `pipeline/s08/heads.py` → head sprite sheets (dev-mac). `pipeline/s08/bodies.py` (done for the draft). `pipeline/s08/qr.py` → `data/s08-qr.js`.
3. `apps/web/film/s08-txsize.html`, grown from `s08-look.html`: the cabinet, the playfield renderer, sprites, cards and characters.
4. Stills opened before the full capture, each also checked at 426x240: mid-suck, the line, the mosaic load, LAMPORT jammed, explosion and score, the slot with 1,232, wedge plus GAME OVER, the sigh poke, WORKAROUND LEVEL with the 003-A cards, the saw, trucks 2 and 5, the thumbs-down plus lab coat, INSERT COIN, the coin mid-drop, the banner with NEW, the slot at 4,096 with "<", -B settled with the TX 1/1 box, the block through the slot, each win line, the checkmark, LEVEL COMPLETE, the text box with bitmap and tree, the credits. The QR cards are run through a decoder on a 720p still and a phone-encode still.
5. `pipeline/s08/capture.sh` (1455 frames in three chunks, frame folders deleted with literal paths after each chunk is encoded), then `pipeline/s08/build.sh` (audio chain, grade, mux, phone encode) → dev-mac `~/video-work/solana-bunker/s08/out/s08-v1.mp4` and `s08-v1-phone.mp4`.

## 6. Risks and fallbacks

| # | risk | fallback |
|---|---|---|
| R1 | The take's wording differs from the brief (table in section 1). "So we built that, and it worked" is the ASR's reading and has not been checked by ear (no whisper model on dev-mac). | Use the take as recorded. Before cutting I check E8 by ear and on the waveform. If Liam wants the draft 3 wording, he records a pickup and only the EDL rows change. |
| R2 | The E5/C1 cut ("withdrawal" → "Not") has only a 50 ms dip (477.05–477.10). | Band-energy scan plus nearest zero crossing, as slide 6's L1a/L1b cut; if it clicks, a 30 ms crossfade into the bed. |
| R3 | The SVG displacement (curvature) is slow or drops paints in headless Chrome over 1455 frames. It worked for the draft still. | `--fresh` capture for affected ranges. Or drop the in-scene displacement and keep only the glass cues (rounded corners, edge shading, highlight), which still read as curved. Or apply ffmpeg `lenscorrection` to the cropped screen region in post (the glove tip and coin are the only things that cross the screen edge). |
| R4 | Scanlines (4 px period) may moiré or smear in the 960x540 crf 26 phone encode. | Check a phone-encode still. If needed, lighter scanlines (0.25) for the phone file, or scale with lanczos before encoding. |
| R5 | Pixel text readability at 426x240. | 1x type is 28 px at 720p, about 9 px at 240p, and the draft's 240p downscale is readable. Spoken-beat text never goes below 1x. Only the tag's small type is below that, which Liam allowed. |
| R6 | No hand-to-face pose for the facepalm. | The brief's fallback: frozen with the head tilted 11° down (in the draft). Option: a cartoon glove prop slapped over the face for 0.5 s (a prop, not a limb move). |
| R7 | The coin "drop" with no handing pose may read oddly. | The coin appears just above the slot and drops in (no throw), with the slot light flashing. |
| R8 | Proof box on the 003-A card: the staged five-transaction path has no devnet proof (local SVM only, per the brief's facts). `CiZmcGsa…` is the inline v1 single-transaction withdrawal, so it belongs to 003-B. | Planned: the 003-A proof card reads "STAGED · 5 TX · LOCAL SVM ONLY" with no QR, and the `CiZmcGsa…` QR pops in with 003-B. This is what Liam's note "old proof boxes disappear, new proof boxes pop into their places" describes. The brief's literal version (`CiZmcGsa…` already on 003-A) is one switch, if the composer prefers it. |
| R9 | Scene 7's last frame does not exist yet (slide 7 is being built). | A stand-in: slide 6 v3's graded end frame (`../s06/out/s06-v3.mp4` at 29.95 s), swapped for slide 7's real last frame when it lands. One PNG, one script line. |
| R10 | The tag is about 6 s for a 75-word text box, the bitmap, the tree and a 12-row table. Nobody can read that. | Recommended: lengthen the tag to 12 s (text box held 6 s, credits 4.5 s). Or keep 6 s and page the text box in two halves with the credits as a fast joke scroll. Or move the text box to scene 9's opening. |
| R11 | The LAMPORT block is 1.5x the screen width. That is the gag, but it may read as a glitch. | Draw it as a two-row block of the same area that fits the screen. |
| R12 | Beat 4 packs a lot into 7.4 s (coin, banner, NEW, tick, slot widening, ">" flip, -A/-B, five boxes, new box, block drop). | Each piece is tied to its own word (table). If it is still crowded, lengthen the E8 → E9 gap from 0.6 s to 1.0 s and shrink the five boxes all at once. |
| R13 | QR scannability. | The cards are flat, outside the CRT (no scanlines, no curvature), with 150 px QR codes at ECC M; decoder check on 720p and phone stills; bigger cards if they fail. |
| R14 | The engineer's head tilts under a fixed hard hat (the hat is part of the body PNG). | Keep the tilt at 12° or less (11° in the draft looks right). Larger tilts would need the hat as a separate layer that rotates with the head. |
| R15 | The engineer lip-syncs the main lines, but slides 6 and 7 used the lab coat as narrator. | The brief makes the engineer the player and the lab coat the commentator, so the plan follows it. Alternative: the lab coat speaks all lines from side pokes and the engineer stays frozen (would need the QR cards moved off the right side). |
| R16 | The 6 s tag and the uppercase-only font: Liam's text box will be in capitals. | Fine for an arcade (authentic). If lowercase is wanted, add lowercase glyphs (no other change). |
| R17 | dev-mac disk (`~/video-work` on the shared overflow volume, about 105 GB free now). | Three capture chunks, each encoded and its frames deleted before the next. |

Open questions for the composer:
- Q1: the take's wording (R1). Fine to use as recorded?
- Q2: the 003-A proof card (R8). Should it be "local SVM only" with no QR, or the brief's `CiZmcGsa…`?
- Q3: tag length (R10): 6 s as briefed, or 12 s?
- Q4: Joe on the win screen: yes or no?
- Q5: the engineer as the speaker (R15).
- Q6: any chiptune SFX (coin, explosion, GAME OVER jingle)? Default is none, with markers only.

## 7. Look draft (rendered)

Files: `apps/web/film/s08-look.html` (a draft scene, not the slide), `pipeline/s08/bodies.py` and `pipeline/s08/look-still.sh`. The still script reuses `pipeline/s06/look-head.sh` for one keyed head frame at 463.15 s (the pause after "damn it"), captures t=0.1 and applies the post grade. Output: dev-mac `~/video-work/solana-bunker/s08/out/s08-look-draft.png`. It shows the beat 2 moment:
- the cabinet with its marquee, neon bezel, control panel and lit coin slot
- the playfield: SCORE 05692, GAME OVER, "2,500 > 1,232", the blue brick floor with the 36 px slot, the yellow "1,232" dimension and "TX LIMIT", and the cyan 2,500 block wedged on the rims with sparks
- the CRT treatment: phosphor glow, scanlines, aperture grille, barrel curvature and glass
- the engineer at the left side with Liam's keyed head under his hard hat, tilted down

The 426x240 downscale was checked: GAME OVER, both numbers, the slot label and SCORE are readable.

## 8. As built, v1

Answers from the review: the take's wording as recorded; the 003-A card says "staged: 5 transactions / local SVM only / no devnet proof" with no QR, and the see-the-code (line 118) and proof (`CiZmcGsa…`) QR cards pop in on 003-B after it settles; tag 12 s; Joe on the win screen; the engineer speaks the main lines and the lab coat the sigh and "not cool"; no SFX, timing markers only (`SFX_<what>` in `data/s08-edl.js` `markers`). Beat 0 uses scene 7 v1's real last frame (`s07-v1.mp4`, film/s07 08bcea9, re-merged).

- Wording check: I could not listen. E8 was re-transcribed on its own (484.30–486.75 s) and in context (482.2–495.4 s) with parakeet-tdt 0.6b v2 and v3 on dev-mac: both read "So we built that, and it worked." Used as recorded.
- Audio: two real cuts. E5/C1 ("withdrawal" | "Not") is cut at 477.100 s, the quietest 10 ms frame in 477.00–477.15 s snapped to a zero crossing (R2 fallback was not needed beyond that). Scene 54.57 s (1637 frames): speech ends 42.30 s, tag 42.57–54.57 s.
- Beat times come from `data/s08-edl.js` `T` (take word times mapped through the edit list); the five trucks arrive at 19.08, 19.98, 20.88, 21.78, 22.68 s.
- Changes against the plan's beat table: the sawn chunks fly off to the left and each truck enters already loaded (no queue on screen); the TEMP ACCT box sits on a ledge at the right wall (clear of the slot when it widens); the five tx boxes, then the TEMP ACCT box, shrink away and a green "1 TX" box pops in at the same spot; a fresh 2,500 block spawns on "rescue" and drops through the 4,096 slot on "and it worked"; the win lines use 2x type at an 11 px advance so "1 TRANSACTION" fits inside the border; the engineer's head-down tilt runs from the end of E3 to the start of E4.
- Tag (12 s): LEVEL COMPLETE flash (1 s), then 6 s of the rotation text box (2 px pixel type, lines crawl in), the 64-LED spent bitmap (7 turn red) and the NEXT LEVEL tree growing to a lit root with a ROTATE stamp; then the credits table (16 rows from `artifacts/public-deployment.json`) scrolls up over 3.9 s and holds 1.1 s.
- Capture: headless Chrome painted one seek late with this scene (the SVG barrel filter), so every still showed the previous time. `scripts/capture.mjs` got an optional `--settle=N` (animation frames to wait after a seek, default 2 as before); scene 8 captures with `--settle=6`, which removed the lag.
- QR: both cards decode with zxing-cpp on a graded 720p still and on its 960x540 downscale.
- Files: `apps/web/film/s08-txsize.html`, `data/s08-edl.js`, `pipeline/s08/{s08-timing.py,heads.py,bodies.py,capture.sh,stills.sh,sheets.sh,build.sh}`. Output on dev-mac: `~/video-work/solana-bunker/s08/out/s08-v1.mp4`, `s08-v1-phone.mp4`.

## 9. As built, v4 (fix round, Liam 16455 and 16470)

Scene 52.32 s (1570 frames; v3 was 54.57 s). Speech ends 40.05 s, tag 40.32-52.32 s.
- E5/C1: the inserted 1.80 s is gone. The take has its own pause there (speech ends 477.04 s, "Not" starts 477.14 s, silent 477.06-477.12), about 0.10 s, so E5 and C1 are one audio segment with no cut and no fade (the old 50 ms dip is gone). Only the head rows split at 477.10 s. The lab coat's poke starts 0.3 s before C1 (during "withdrawal") and is in place before "Not". Trucks 1-3 unchanged; 4 and 5 arrive at "Not" +0.04 s and +0.64 s (under C1), the TX counter keeps its order.
- E6 starts at "Solana": "Oh, but" (479.20-479.58 s) is cut; the in-point is 479.60 s (silent, -62 dB, onset at 479.65 s) with the 20 ms fade. E6 is placed so "Solana" starts 0.93 s after C1 ends. Beat anchors come from the take words through the edit list as before; the coin drop is now anchored to the banner (T.oh = solana - 0.48 s, drop at oh + 0.45 s).
- E8 is split at the comma: E8a engineer "So we built that," (484.40-485.58 s), E8b lab coat "and it worked." (485.58-486.62 s). The take has a clean pause 485.30-485.60 s, so no audio cut (rows that touch play as one segment). The lab coat pokes from the right edge with the professor-point pose (the C1 poke, 0.3 s lead, 3 steps in and out), the engineer holds his last frame. Block drop and card swaps are unchanged (on their words).
- Joe (16470): from 39.65 s (after the three-step pop-up) he cheers with a whole-figure bounce (12 px, 3 Hz, sin squared ease) and a rock (+-4 deg, 1 Hz) about his neck; head rides behind the body, no limb animation.
- Tag audio: `pipeline/s08/chiptune.py` (numpy, square/triangle/noise, 44.1 kHz mono) writes `apps/web/film/audio/s08/{jingle,bed,coin,tick}.wav`. Jingle 2.1 s (C major arpeggio, two squares + triangle bass, peak -12 dBFS) at the LEVEL COMPLETE flash; bed 8 bars at 124 BPM (C Am F G x2, 12.5 % square lead, triangle bass, noise hat; RMS -30 dBFS, 15.48 s, plays from the text box (tag + 1 s) to the end with a 0.6 s fade-out); coin blip (B5 to E6, peak -18 dBFS) on the ROTATE stamp; 18 ticks (30 ms, peak -18 dBFS, 5 ms edge fades because 20 ms would eat the blip) as the credits rows scroll in. The cues are mixed in build.sh after the speech loudnorm (absolute levels), with the brown-noise bed, before the limiter; `s08-timing.py` writes the cue times (`out/s08-sfx.args/.filter`). Measured in the final mix over the tag: jingle peak -11.1 dBFS, text box -15.1, credits -11.5 (includes the quiet brown bed and ticks).
- Checks: waveforms at the E5/C1 join, the E6 head and the tag; stills at 22.1, 24.0, 24.25, 30.1, 30.4, 40.4, 45.2, 49.0 s and a 3-frame Joe bounce strip. Outputs `out/s08-v4.mp4`, `s08-v4-phone.mp4`, `s08-v4-tag-audio.wav`. Heads re-keyed (1024 frames).
