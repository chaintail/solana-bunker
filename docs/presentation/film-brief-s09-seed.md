# Film brief: scene 9, the seed phrase (Liam 16250/16251: "your plan for scene 9 is cool, let's cook that up… same process, plan first… then get it built")

Script (spoken, Liam's draft 3 slide 8). The take's wording wins over draft 3, as in scenes 6–8. Take `audio/bunker-take.wav`, the only read of this passage, 497.28–518.48 s (the trailing "Yeah." at 495.68 belongs to scene 8 and is not used):

| take (ASR; check by ear before cutting) | time (s) |
|---|---|
| Okay, there's still one really annoying part. | 497.28–500.16 |
| How are we supposed to keep track of our thousand one-time secrets? | 500.16–503.44 |
| If only there was some kind of convenient way to derive a secret from keys or like something memorable. | 503.44–510.16 |
| You know, rather than memorizing thousands of strings of gibberish, what if… | 510.16–~514 |
| yeah, we did that too. | ~514–516.56 |
| Go check it out. | 516.56–518.48 |

"BIP-39" is never spoken: it is the on-screen reveal in the pause after "what if". Cut anything that reads as a stumble ("from keys or like") only if the cut is clean; otherwise keep the take as recorded. Scene length: the speech plus a 6–8 s on-screen tag (proof boxes, FREE, CALL NOW). Target about 28–30 s.

Facts and links: BIP-39 seed derivation is `bip39_seed` in client/kdf.py line 10 (https://github.com/chaintail/solana-bunker/blob/main/client/kdf.py#L10). The whitepaper's BIP-39/HKDF project-seed recipe is research/whitepaper.md line 35 (https://github.com/chaintail/solana-bunker/blob/main/research/whitepaper.md#L35). CALL NOW resolves to the repo, https://github.com/chaintail/solana-bunker. The mnemonic shown is 24 words from the BIP-39 English wordlist (any valid mnemonic; never a funded one; no "example" or "demo" caption). The thousand secrets are the one-time keys of scenes 5–8; the key cards are the Lamport wall's cards from scene 7.

Audio: standard chain (afftdn nr=18, profile from the take's silent 0.10–0.70 s, applied once before cutting; 20 ms fades; brown-noise bed lowpass 220 volume 0.05 under the whole scene; one two-pass loudnorm −16 LUFS / TP −1.5). Never let audio run while lips are still. SFX markers in the EDL only (`SFX_TV_STATIC`, `SFX_RECORD_SCRATCH`, `SFX_WHOOSH`, `SFX_STAMP`, `SFX_CASH_REGISTER`), nothing in the mix.

Characters as before (generated bodies in `apps/web/film/assets/bodies/`, stop-frame, freeze when silent, narrator never beyond 35° from upright, side pokes, whole-figure moves). Joe = the sufferer (`2-street-hands-in-pockets`, then `2-street-celebrate` as hands-in-the-air). Suit = the pitchman (`1-suit-point-right`, `1-suit-standing`). Lab coat = the satisfied customer at the end (`5-physicist-holding-clipboard`, the clipboard reads WHITEPAPER). Who lip-syncs: Joe speaks the first two lines (the complaint, at the kitchen table), the suit speaks from "If only" to "Go check it out" (the announcer who steps into frame). Heads re-keyed per line from the matte footage as in scenes 6–8.

## Style: a late-night infomercial, 1990s
Transition in: scene 8 ends frozen on the arcade credits. The arcade's CRT changes channel: a half-second burst of TV static, then the infomercial is playing inside the cabinet's screen; the camera pushes in until the CRT fills the frame (about 1 s), and the CRT's 4:3 pillarbox stays as the scene's TV frame.

## Beats
1. The problem half, black and white, grainy, 4:3 with pillarbox bars, soft vignette, a lower-third "DRAMATIZATION" caption, cheesy push-in zooms. Joe at a kitchen table buried in sticky notes, each reading `secret_1`, `secret_2`… `secret_1000`, raining down through the shot, one stuck to his forehead. On "keep track of our thousand one-time secrets" the pile grows faster. On "If only there was…" Joe throws his hands up (hard cut to the celebrate pose read as despair) and the caption "THERE HAS TO BE A BETTER WAY!" wipes in. The suit steps into the edge of the shot as the announcer (still black and white).
2. "what if…": record-scratch beat (`SFX_RECORD_SCRATCH` marker). Colour snaps on, the pillarbox bars drop away, the grain goes. A glossy card spins in: **BIP-39** in big letters. Twenty-four words appear one at a time on a parchment card (a seed-phrase backup card) in two columns, numbered 1–24, fast enough to finish inside the pause. Then the phrase shrinks into a single golden key, and the key forks into a thousand tiny keys (the Lamport wall's key cards from scene 7) fanning out in a grid, a thousand being represented by a dense grid that keeps forking off the edge.
3. "yeah, we did that too": the caption "YEAH, WE DID THAT TOO!" stamps in (`SFX_STAMP`). The suit points at the card (pitchman pose).
4. "Go check it out": "BUT WAIT, THERE'S MORE" slides up from the bottom (`SFX_WHOOSH`), and the two proof boxes drop in on the right: **see the code** (GitHub QR to client/kdf.py line 10, file and line printed under the QR) and **whitepaper** (GitHub QR to research/whitepaper.md line 35, file and line printed under the QR). QR codes flat, no grain or curvature on them, decoder-checked on a 720p still and a phone-encode still.
5. Tag (no speech): a "FREE" price tag swings in with an old price crossed out (`SFX_CASH_REGISTER`); a flashing "CALL NOW" that turns into the GitHub link text `github.com/chaintail/solana-bunker` with a QR. The lab coat pokes in from the side holding up the WHITEPAPER clipboard as the satisfied customer. Hold the final frame 2 s for scene 10's handoff.

Rules: 90% of the spoken beats readable at 426x240 (the 24 words need not be readable at 240p, "BIP-39", the captions and "FREE" must be); render on dev-mac only (`ssh dev-mac`, PATH `/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/bin`, tree `~/video-work/solana-bunker/s09/`), never ffmpeg on do-box; delete frame folders with literal paths; open your own stills at every beat and look at them; phone re-encode 960x540 crf 26. Branch: worktree `~/code/solana-bunker-s09`, branch `film/s09` from main with `film/floating-head` and `film/s08` merged in (reuse the head pipeline, bodies, QR generator, and scene 8's last frame from dev-mac `~/video-work/solana-bunker/s08/out/s08-v1.mp4` for the transition). Commit as the repo's configured identity, NO trailers. No push.

## Plan first
Write `docs/presentation/film-plan-s09.md` (cut list with in/out points vs the take, beat table with word-anchored timings, production method per visual including the black-and-white film look, the colour snap, the 24-word card, the key fork and the proof boxes, risks and fallbacks) and ONE draft still as two panels: left the black-and-white kitchen with Joe under the sticky notes and the DRAMATIZATION caption; right the colour product shot with the suit pointing at the BIP-39 card, the 24 words, YEAH WE DID THAT TOO and the two proof boxes. Report and STOP; build after the composer approves.
