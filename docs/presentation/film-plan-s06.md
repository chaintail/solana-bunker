# Film plan: slide 6, a password is not a signature (plan for review, nothing built yet)

Brief: `docs/presentation/film-brief-s06-signature.md`. Branch `film/s06` (worktree `~/code/solana-bunker-s06`) = main 29ffa59 + `film/floating-head` merged.
This document is the plan only. The one thing rendered so far is the look draft (section 7).

## 1. Audio: the cut list

Source: Liam's take `audio/bunker-take.wav` (same timeline as `bunker-transcript.json` and the matte footage `~/video-work/bunker/matte-full-{comp,alpha}.mp4`).
Chain as in `pipeline/build-conspiracy-v4.sh`: afftdn nr=18 with the noise profile from the take's silent 0.10–0.70 s, applied once to the whole take (`take-dn.wav`); then cut; 20 ms fades on every cut; brown-noise bed (lowpass 220, volume 0.05) under the whole scene; one two-pass loudnorm to -16 LUFS / TP -1.5. Source in/out points below come from the transcript tokens plus a `silencedetect=n=-38dB:d=0.12` pass on `take-dn.wav` (run on dev-mac); I will check every cut by ear and on the waveform before the capture.

The take differs slightly from the brief's wording ("Alright, so this is where things", "a password says nothing about where the money should go", "gets in the vault"). Every brief line is in the take; I use the take as recorded.

| id | line (as spoken) | source in–out (s) | scene in–out (s) |
|---|---|---|---|
| L1a | Alright, so this is where things | 337.70–339.12 | 0.30–1.72 |
| (gap) | freeze + "*the math*" flash, bed only | | 1.72–2.22 |
| L1b | start to get cool. | 339.12–339.95 | 2.22–3.05 |
| L2 | The problem with version one and version two is that a secret is just a password. | 340.22–343.75 | 3.30–6.83 |
| L3 | Whoever shows the password first gets in the vault. | 343.95–346.20 | 7.50–9.75 |
| L4 | But a password says nothing about where the money should go. | 346.58–349.58 | 10.00–13.00 |
| L5 | So if someone steals it on the way to the vault, they can get in first. | 349.80–353.02 | 13.20–16.42 |
| L6 | What we actually want is a signature. | 353.42–355.08 | 16.90–18.56 |
| L7 | Something that says this exact withdrawal, to this exact address, and nothing else. | 355.28–361.06 | 19.20–24.98 |
| (tag) | no line, bed only | | 26.30–27.80 |

Scene length 28.10 s (843 frames at 30 fps). The pauses after L2 (0.67 s), L5 (0.48 s) and L6 (0.64 s) are added for the door, the shove and the form; the bed runs through them so the audio never drops out. The L1a/L1b cut sits between "things" and "start" with no silence in the take (see risk R1).

Speaking heads (lip-sync only while that character's line plays; frozen on a closed-mouth frame otherwise):
- L1a: the slide 5 lab coat on the whiteboard (continuity from slide 5).
- L1b: nobody (the sweep); the bouncer's head is frozen when the alley is revealed.
- L2–L5: the bouncer. He explains his own door policy, which is the joke. Alternative if the composer prefers: L2–L5 as voice-over with the bouncer frozen throughout.
- L6–L7: the lab coat narrator, after he pokes in.
- The devil never speaks (his whisper is mimed: he leans in, a small "psst" glyph).

## 2. Beat table (scene times; key words in brackets with their scene time)

| beat | time (s) | on screen | how it is made |
|---|---|---|---|
| 1a | 0.00–1.72 | Slide 5's last whiteboard frame: lab coat Liam on the left in professor-point, lip-synced to L1a. | Plate = last frame of the slide 5 render (fallback: my own whiteboard plate, R9). Lab coat body PNG + head sprite in-scene. |
| 1b | 1.72–2.22 | ["things" 1.48–1.72] Whole frame freezes. "*the math*" cuts in centre, cheap bright yellow (#ffe600) Anton, black 6 px outline, rotated -4°, about 150 px tall; hard cut in and out, 500 ms. | In-scene: everything holds its 1.72 s state; an overlay div is visible 1.72–2.22 only. |
| 1c | 2.22–3.05 | ["start to get cool"] A car's headlight sweep passes left to right (two soft white beams plus a flare) and wipes the whiteboard away; behind the beam is the wet alley: rain, streetlight cone, red door on the right, the suit bouncer left of it, arms crossed, head frozen. Grain ramps in over 0.4 s from 2.3 s. | The alley is built underneath; the whiteboard plate sits on top with a CSS mask whose hard-soft edge trails the beam (mask position driven by t). Beam = two blurred white ellipses + horizontal flare, `mix-blend-mode: screen`. |
| 2 | 3.30–7.50 | Bouncer speaks L2. ["problem" 3.48] The stick man (white marker lines, whiteboard style, deliberately out of place in the noir) hops in from the left in three whole-figure hops (3.5–4.4). ["secret" 5.56] a speech bubble "secret_42" pops over him (Special Elite, 44 px). ["password" 6.36] the slot's shutter slides open (0.2 s), a pair of eyes in the slot; ["password" end 6.83] the door swings inward (6.83–7.25) and the stick man hops into the doorway (7.25–7.50) and stops there. | Stick man = SVG paths with a seeded wobble, unfiltered (already white). Hops = whole-figure translate on a parabola, 6 frames each, no limb animation. Door swing = CSS 3D rotateY about the hinge edge, perspective 900 px (fallback R5). |
| 3 | 7.50–9.75 | Bouncer speaks L3. ["Whoever" 7.50] the devil head slides up from the bottom edge behind the stick man; ["password" 8.11] he holds up the same "secret_42" bubble and leans to the bouncer's ear ("psst"); ["gets in" 8.99] the bouncer cuts to his point-right pose, pointing at the door: he is waved in too. | Devil = one closed-mouth head frame tinted red (R3), SVG horns and black bandit mask over the eyes, no body. Pose change = hard cut between body PNGs (arms-crossed -> point-right), head stays. |
| 4a | 10.00–13.00 | Bouncer speaks L4. ["says nothing" 10.70] the two identical "secret_42" bubbles side by side; ["where the money should go" 11.74] a small blank tag "TO: ?" dangles off each bubble. Slow 4% push-in on the doorway. | Tags are SVG; push-in = transform on the noir group (door and characters move together). |
| 4b | 13.20–16.42 | Bouncer speaks L5. ["they can get in first" 15.16] the devil shoulders past the stick man in the doorway (devil slides right-in with a 10° shove tilt; the stick man is knocked back out in two hops); ["first" 16.12] the door slams behind the devil; a big white "?" pops over the stick man, who freezes outside. | Whole-figure translate/rotate only. Slam = rotateY back to 0 in 4 frames with a 3 px frame shake. |
| 5 | 16.90–19.20 | Narrator speaks L6. ["What" 16.90] a cheap grey vaudeville hook slides in from the left edge, catches the bouncer at the waist and yanks him off screen left (16.95–17.30, stepped, 3 positions, no motion blur). ["actually want" 17.30] the lab coat narrator pokes in diagonally from the top right corner, rotated so the pointing arm points down-left at the left half. ["signature" 18.12] a paper withdrawal form floats up from the bottom and fills the left half in warm sepia: "WITHDRAWAL", "TO: ____", "AMOUNT: ____", "X ________ signature". The stick man stands at its lower right corner. | Hook = flat SVG crook, unfiltered grey. Narrator = professor-point body PNG, flipped and rotated about 140°, entering along the diagonal over 6 frames, head sprite lip-synced, the whole figure in the noir filter. Form = HTML/SVG card outside the noir filter: sepia paper (#dcc69c base, feTurbulence fibre, darker edges), Special Elite labels 40 px, 2° tilt. |
| 6 | 19.20–26.30 | Narrator speaks L7. ["this exact withdrawal" 20.48] AMOUNT types in "1.5 SOL" (40 ms per character). ["to this exact address" 22.00] TO types in the real devnet recipient `ADLw7WkPsqngneGqoCKmGR17w16kmgA9q1WnxURt9Wod` (vaults[].recipient_sol in `artifacts/public-deployment.json`), shown big as "ADLw7W…xURt9Wod" with the full address in small type under it. ["and nothing else" 23.52] a quill signs the line with a flourish in red ink (24.40 "else" lands on the final flourish). 25.00 the form shrinks and slides through the slot (the shutter opens 24.95, closes 25.55); 25.70–26.20 the door swings open; the stick man hops in (26.0–26.3). | Typing = per-character reveal driven by t. Signature = seeded SVG path (same idea as `signaturePath()` in `vaultscene.tsx`), stroke-dashoffset reveal, ink #c1121f, quill SVG riding the path tip. The form is clipped by the slot rectangle as it slides in. |
| 7 | 26.30–28.10 | Tag, no line. The devil pops up from the bottom edge by the door, a cartoon red hand pushes his own sepia form (TO: "DEV1L…9x" in red, already signed) at the slot; 27.30 the shutter slams down on his fingers (fingers squash 2 frames, a little "!"); 27.40 everything freezes to the end. | Same form component with other values; red cartoon hand SVG (Rayman style, not attached to a body). The freeze holds the last state; the bed fades out over the last 0.6 s. |

Program boxes: none. No see-the-code or proof QR on this slide.

## 3. Characters and the head pipeline

- Bodies: `apps/web/film/assets/bodies/` (1024x1536 PNGs, each with a grey placeholder oval for the head). Bouncer = `1-suit-arms-crossed.png` + `1-suit-point-right.png`; narrator = `5-physicist-professor-point.png`; the slide 5 lab coat on the whiteboard uses the same.
- Head sprites: the key from `pipeline/head-test/key.sh` (RVM alpha minus the luma key of the black shirt below the chin, `zone.png`/`kill.png`, 760x1100 crop), cut per line with the same in/out as the audio, scaled and tiled into sprite sheets that the scene draws frame by frame, exactly like `s05-heads.py` on dev-mac. New script `pipeline/s06/heads.py`; sheets `film/heads/s06-{bouncer,narr,lab}-NN.png`. Sprite size 152x220 (2x the bouncer's on-screen head), so the narrator can be larger without upscaling.
- Fitting a head to a body (verified in the look draft for the suit): the body PNG gets a CSS mask that cuts out the oval (ellipse 103x119 at 511,196 in body pixels); the head (chin at 338,905 in key pixels) is scaled by 0.326 and placed with its chin on the collar line (511,306); a second copy of the body PNG, clipped to the region below the collar line minus the drawn neck V, sits in front of the head so the real neck goes behind the collar. Per-body numbers for the professor-point body will be measured the same way and checked on stills.
- Devil: one closed-mouth frame of Liam (from a pause, around 353.2 s), made red at sprite time (`hue`/`colorchannelmixer` to a red monochrome), horns and bandit mask in SVG. If slide 5's build commits its devil head, I reuse it so the two slides match.
- Stick man: SVG, white 7 px marker strokes with a seeded wobble, no grade (he is the out-of-place whiteboard character).
- Stop-frame rule: characters move only as whole figures (translate, rotate, flip) and pose changes are hard cuts between body PNGs; limbs never animate. Each head freezes on a closed-mouth frame the moment its line ends.

## 4. The noir look recipe

In the scene (Chrome):
- Noir layers (alley, characters, rain, hook) are in containers with `filter: grayscale(1) contrast(1.28) brightness(.92)`.
- Colour layers sit outside that filter: the door (and its red reflection in the wet ground), the sepia form, the red ink, the devil (see R3).
- Alley: dead-end view: brick back wall (seeded per-brick shades), dark side walls in perspective, fire escape silhouette, drainpipe, wet asphalt with puddles. One wall-bracket streetlight above, left of the door, and its cone (blurred trapezoid, `screen`) plus a light pool on the ground and a smeared reflection streak. A faint rim light from the alley mouth on the left.
- Rain: canvas redrawn per frame from a seeded list (420 streaks, 1600–2300 px/s, 10° wind slant, 16–46 px long), brighter and thicker inside the light cone, plus seeded ground splashes. Deterministic for any t, so stills and frames match.
- The door: the vault elevation from `apps/web/src/components/Door.tsx` recast as a deep red speakeasy door (#8e0c13 -> #1e0103 gradient, lamp-side highlight, right-side falloff): its two hinges on the left edge, its 36-bolt ring and three-spoke wheel in brass on the lower panel, and its address plate turned into the brass-framed sliding slot at the bouncer's eye height (shutter slides left to open).

After capture (ffmpeg on dev-mac, one pass with the audio mux):
- `format=yuv444p, curves=all='0/0.035 0.25/0.21 0.75/0.82 1/1'` (lifted blacks so grain shows in the shadows, slight S-curve),
- `noise=c0s=30:c0f=t+u` (luma-only temporal grain, so the red stays clean), mixed in from 2.3 s over 0.4 s with a `blend` time expression (the whiteboard in beat 1a has no grain),
- `vignette=angle=PI/4.2`,
- then `format=yuv420p`, x264 crf 14 master, phone 960x540 crf 26.
- Optional, off unless approved: 1 px seeded gate weave and one or two dust specks per second (in-scene).

## 5. Files and steps (after approval)

1. `pipeline/s06/s06-timing.py` -> `data/s06-edl.json`, `data/s06-audio.filter` (the table in section 1).
2. `pipeline/s06/heads.py` -> head sprite sheets (dev-mac).
3. `apps/web/film/s06-signature.html` (the scene; grows out of `s06-look.html`).
4. Stills at every beat opened with Read before any full capture: math flash, mid-sweep, stick man with bubble at the slot, devil whisper, the wave-in, the shove with "?", the hook yank, narrator + form, typed address, red signature, form in the slot, door open, slot slam. Each also checked at 426x240.
5. `pipeline/s06/capture.sh` (843 frames in two chunks), `pipeline/s06/build.sh` (audio chain, grade, mux, phone encode) -> dev-mac `~/video-work/solana-bunker/s06/out/s06-signature.mp4` and `-phone.mp4`; frame folders deleted after the encode.

## 6. Risks and fallbacks

| # | risk | fallback |
|---|---|---|
| R1 | "things" runs straight into "start" with no silence, so the freeze cut can clip a consonant. | Cut at the nearest zero crossing within ±40 ms, 10–20 ms fades, check by ear; if it still clicks, a 30 ms crossfade into the bed. |
| R2 | The bouncer lip-syncing the narration may read oddly. | Voice-over with the bouncer frozen for L2–L5 (switch in the scene, no other change). |
| R3 | The brief says the door is the only colour, but the devil is "tinted red". | Plan: the devil keeps his red (he is the slide 5 villain and must read as him). Fallback: a dark red-tinted monochrome devil inside the noir filter, so only door, form and ink carry colour. Composer to choose. |
| R4 | The headlight wipe looks glitchy or cheap in a bad way. | Hard cut through a 2-frame white flash from whiteboard to alley, with the beam crossing the alley afterwards. |
| R5 | CSS 3D door swing misrenders in headless Chrome. | 2D fake: scaleX about the hinge edge from 1 to 0.25 with a darkening gradient. Works everywhere. |
| R6 | Rain turns to mush or moiré at 426x240 and in the crf 26 phone encode. | Fewer, thicker streaks (2 px, 250 drops); checked on downscaled stills and on a phone-encode still. |
| R7 | Grain starves the phone encode (blocking in the darks). | Lower grain for the phone file (c0s=18) or apply grain before the scale with a light denoise; check a phone still. |
| R8 | Head-to-body fit for the rotated narrator (collar clip, grey-oval remnants at other scales). | Everything is in one scene transform group, so rotation is exact; mask and collar polygon measured per body PNG and checked on 2x crops. |
| R9 | Slide 5 is not built yet, so its last frame does not exist for beat 1a. | My own whiteboard plate in the slide 5 style (lab coat on the left, board on the right), swapped for the real slide 5 last frame when it exists. |
| R10 | Beat 5 is crowded (hook, poke-in and form in about 2.3 s). | Lengthen the pause after L6 from 0.64 s to 1.0 s (the bed covers it). |
| R11 | dev-mac disk (about 5.8 GB free; `~/video-work` is on the shared overflow volume). | Capture in two chunks, encode each, delete the frames before the next; no layer captures needed. |
| R12 | Transcript token times are approximate. | All in/out points rechecked on the waveform before capture; beat times move with them (the scene reads times from `data/s06-edl.json`, so nothing is hard-coded twice). |

Open questions for the composer: R2 (bouncer lip-sync vs voice-over), R3 (devil red or not), the "TO: ?" tags in beat 4a (my addition for L4, droppable), and the optional rain/car/slot sound effects (not in the brief; default off).

## 7. Look draft (rendered)

`apps/web/film/s06-look.html` (draft scene, not the slide), `pipeline/s06/look-head.sh` (one head frame from the take at 341.0 s), `pipeline/s06/look-still.sh` (capture t=0.5 + grade). Output: dev-mac `~/video-work/solana-bunker/s06/out/s06-look-draft.png`. It shows the alley, the red door with the slot, the bouncer with Liam's real keyed head (grayscaled), the light cone, rain, grain and vignette.

## 8. As built, v1 (after the plan review)

Decisions from the review: R2, the bouncer never speaks (one closed-mouth frame, 360.90 s); the lab coat narrator lip-syncs every line: on the whiteboard for L1a/L1b, poked in diagonally from the top left (mirrored) for L2–L5, from the top right for L6–L7, holding his last frame through every pause. R3, the devil stays red (closed-mouth frame 353.00 s, red monochrome); the palette is "red only: door, devil, ink", plus the sepia form. "TO: ?" tags kept. No sound effects. Walls lifted (brick shades 66–106, softer wall falloff). R1, R9 and R11 fallbacks used.

- Audio: L1a/L1b is cut at 339.165 s, the middle of the sibilant that "things" and "start" share (band-energy scan in `pipeline/s06/s06-timing.py`; the quietest point, 339.21, would have left "tart"), snapped to a zero crossing. L7 ends at 360.70 ("else" ends 360.56; a lip click at 361.04 is left out), so L7 is 19.20–24.62 in the scene.
- Narrator pose (v2, fix round): side pokes, never more than 35° from upright. L2–L5 from the left edge, tilted 27° in, neck at (118,282), legs cut off by the edge, pointing right at the bouncer and the door; L6–L7 from the right edge, neck at (1162,262), tilted -27°, body mirrored but head not (the head is flipped back about the neck line), pointing left at the form. He slides in and out horizontally in 3 stop-frame steps. (v1 hung him nearly upside down from the top corners.)
- Whiteboard stand-in for slide 5's last frame: `S5_HANDOFF` in `s06-signature.html` holds the lab coat's neck point and scale.
- Files: `apps/web/film/s06-signature.html`, `data/s06-edl.js`, `pipeline/s06/{s06-timing.py,heads.py,capture.sh,stills.sh,build.sh}`. Outputs on dev-mac: `~/video-work/solana-bunker/s06/out/s06-v1.mp4`, `s06-v1-phone.mp4`; v2 (side pokes) `s06-v2.mp4`, `s06-v2-phone.mp4` (`build.sh video v2`).

## 9. v3 (Liam's notes on the tag)

L7 is split at the pause after "address": L7a (355.28–359.49, scene 19.20–23.41) and L7b "and nothing else" (359.49–360.70, scene 26.65–27.86). In the gap our form is signed (22.86–23.86), goes through the slot (24.0–24.8), the door opens for the stick man and shuts (24.95–25.60), then a speech pause of 0.8 s on the shut door (25.60–26.40). The devil rises at 26.40 and tries to post his form under "and nothing else"; the slot slams on "else" at 27.72 (`SFX_SLOT_SLAM` in `data/s06-edl.js` `markers`, for Liam's slam sound; nothing in the mix). A big red REJECTED stamp slams in at 28.07 (conspiracy stamp language: Anton caps, red border, rough-ink filter, scale 3 -> 1 in 0.14 s, -8°, camera thump), the frame freezes at 28.27 and holds to 30.00 (2.3 s after the slam, was 0.8 s). Output `s06-v3.mp4`, `s06-v3-phone.mp4`.

## 10. v9, x12 build ("1.2 on all"; continues from whiteboard v7 x12)

v8 edit unchanged (no "*the math*" flash, no opening zoom, devil whisper, red-face devil, notched suit and lab coat bodies). Build: `pipeline/s06/capture-x12.sh` (capture.mjs --speed=1.2, 885 scene frames -> ceil(885/1.2) = 738 output frames, 24.6 s, three 300-frame chunks with the capture warm-up) and `pipeline/s06/build-x12.sh` (the whole mix through atempo=1.2, pitch kept, since the scene's audio is Liam's take only: the devil's whisper is the on-screen "psst" and the slot slam is a marker, not a sound; two-pass loudnorm -16 LUFS, brown-noise bed at the new length; grade times scaled by 1/1.2) -> dev-mac `s06/out/s06-v9-x12.mp4`, `-phone.mp4`.

Hand-off from slide 5 v7 x12 (film/s05 adace2f, notched lab coat bodies, professor-point legs re-seated under the collar):
- `assets/s06/s05-end-full.png` re-pulled with `pipeline/s06/s05-end.sh`: s05-hash.html at its last frame time 96.7333 s (total 96.78 s, frame 2902). It is s06 frame 0. Headless Chrome sometimes rasterises with 4-level edge anti-aliasing and sometimes with smooth anti-aliasing; the committed frame is in the s05 master's mode (board PSNR 41.5 dB against the master's last frame after the master's own x264 round trip, 37.6 dB for a render in the other mode).
- `assets/s06/s05-end-plate.png` (behind the live lab coat from 0.30 s) = the full frame with only the coat silhouette (plus 4 px) taken from a render with `#figL` hidden, so the board pixels are byte-identical to frame 0 and do not change at the takeover.
- The live whiteboard lab coat now matches slide 5 at the takeover: body placed with slide 5's geometry (professor-point collar at x 174.8, as s05 pose-align dx 115.5), the s06 head offset by (-6.49, +2.68) px to stay on slide 5's head, and layered the slide 5 way (oval-erased `assets/s06/s05-physicist-professor-point.png` from film/s05, head behind the body), so the notched skin strip under the chin and the collar look the same. Measured across the takeover (x12 frames 7/8): collar and tie 0 px, legs and shoes +1 px, face (0, -2) px at the same size; only the arms change (shrug -> professor-point). v8 moved the body 6 px left and 3 px down here.
- `assets/bodies/5-physicist-professor-point.png` is the 20ae821 version (legs re-drawn under the collar), the same art as slide 5 v7.
- Results: 738 frames, 24.600 s (master 1280x720 crf 14, 114.7 MB; phone 960x540 crf 26, 2.6 MB); muxed master -16.0 LUFS, true peak -1.0 dBFS, LRA 9.2 LU. glitch-scan v2 `--chunk-starts 300,600 --ref 0`: 0 flagged on master and phone (chunk-start jumps 1.3-1.7 against a median of 1.2; nearest frame to frame 0 is frame 4, inside the 8-frame hold of the baked frame). Hand-off: the lossless capture's frame 0 equals `s05-end-full.png` (0 pixels differ); decoded s06 frame 0 vs decoded s05 v7 x12 last frame: PSNR 44.9 dB, mean |diff| 0.63. Stills checked: takeover 7/8, devil rise 174-190, "psst" 200/204, bouncer arms-crossed -> point-right 212/213 (head, legs and shoes 0 px, only the arms change), chunk joins 299/300 and 599/600, devil tag 648/652, REJECTED hold 700/737. Proof sheet: composer outbox `s06-v9-handoff-proof.png`.

## 11. v10, x12 build (re-joined to slide 5 v8; the pause after "address" cut)

Liam: "scene 5 starts with the final frame of scene 4" (re-join to the whiteboard v8 x12, film/s05 a38d379) and, 2026-10-16, "cut out that pause" after "to this exact address". Everything else is v9 (devil whisper, red-face devil, no "*the math*" flash, no zoom, REJECTED ending); same method (`capture-x12.sh`, `build-x12.sh`, which now take the frame count from `out/s06-edl.json`, default V=v10).
- Opening: `assets/s06/s05-end-full.png` / `-plate.png` re-pulled with `MASTER=out/s05-v8-x12.mp4 pipeline/s06/s05-end.sh` (s05-hash.html at 91.4333 s, frame 2286; board PSNR 40.98 dB after the round trip = the master's raster mode, first try).
- Whiteboard head: slide 5 v8 shows c22's full-chin cut (s05-heads.py NORM), 8% smaller and placed differently from s06's own sheets. `pipeline/s06/wb-heads.py` cuts L1a + L1b the s05 v8 way (head-test zone/kill masks, 136x197) with one NORM (1000, 1334, 90, 86) for both lines (one continuous take), anchored so L1a's first frame registers on c22's last sprite (residual scale 1.000, 0/0 px, NCC 0.83) -> `heads/s06-wb-00.png` (built on dev-mac, not committed, like the other lip-sync sheets). The scene draws it with slide 5's head geometry (anchor 511.5/308, KF 217/665, scale KF/0.1793; slide 5 fig x = this body x + 116), behind the oval-erased body; the v9 head offset is gone. `html data-duration` is 26.5 (was 30; v9 relied on `--to`).
- Pause: L7b out_in 26.15 -> 23.15 (`s06-timing.py`). The take is silent 359.43-359.54 s, so both cut edges and their 20 ms fades are in silence; 0.24 s inserted = 0.35 scene s between the words = 0.27 s below -40 dB in the master (19.06-19.33 s). Slot slam marker 27.22 -> 24.22, REJECTED and the freeze follow; scene 29.50 -> 26.50 s.
- Gap animation: v9's sign -> form through the slot -> door open, stick man in, narrator out, door shut (sign0 22.36 .. 25.10) plus the devil's rise (25.90 .. 26.10) with the 0.80 s hold on the shut door dropped, played GK = 2.94 / 0.74 = 3.97x faster from sign0 (0.80 s after "address", unchanged) so the rise ends 0.05 s before "and" (as in v9); `g()` and every gap duration / GK in `s06-signature.html`. Output frames 559-578 (signature 559-565, slot 566-571, door 572-576, devil 576-578).
- Results: 663 frames, 22.100 s (v9 738, 24.600 s: 2.50 s shorter); master 1280x720 crf 14 102.5 MB, phone 2.3 MB; -16.1 LUFS, true peak -1.0 dBFS, LRA 3.6 LU. glitch-scan v2 `--chunk-starts 300,600 --ref 0`: 0 flagged on master and phone (chunk-start jumps 1.11-1.47 against a median of 1.19; nearest frame to frame 0 is frame 4, inside the baked hold). Lossless frame 0 and frame 7 = `s05-end-full.png` (0 px differ); decoded frame 0 vs decoded s05 v8 last frame PSNR 44.8 dB, mean |diff| 0.68. Takeover frames 7/8 (`pipeline/s06/takeover-check.py`): head 0 px, collar/tie 0 px, legs/shoes +1 px, only the arms change. Transcript 15.2-23.2 s (faster-whisper small): "...to this exact address and nothing else." with no doubled or clipped word. Proof sheet: composer outbox `s06-v10-handoff-proof.png`.
