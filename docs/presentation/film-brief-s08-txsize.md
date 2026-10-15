# Film brief: scene 8, one transaction (Liam 16204: "first pass at creating scene 8 based on your vision, then I'll provide my feedback")

Script (spoken, Liam's draft 3 beat 7, every line kept): "XMSS signatures seem awesome. They are way smaller…" / "But… damn that 1,232 byte transaction size limit!" / "Sigh… i guess we could use temporary data accounts to upload signatures in pieces, but from our research that took 5 transactions just to do a simple withdrawal!" / "That's not cool…" / "So we rebuilt it." / "One transaction, thirty one hundred bytes, about half a million compute units, and the full signature verifies on chain in a single shot."
On-screen only (not spoken), Liam's directions: a table of all the transactions we built (rotation, mock USDC etc., from artifacts/public-deployment.json and research/results-summary.md), and this text box: "And because every one time key gets used exactly once, the vault keeps a bitmap of which leaves are spent. When you run low, or you just get paranoid, you sign one more message that installs a brand new tree. New root, new keys, same address, same balance. The new tree comes from the same twelve word seed phrase, just the next generation. So recovery is one instruction: rotate."

Facts: Lamport 8,192 bytes; XMSS-SHA2_10_256 signature 2,500 bytes; legacy tx cap 1,232; v1 cap 4,096; staged transport = 5 transactions (local SVM only, no devnet proof); inline v1 SOL withdraw 3,117 bytes, 518,509 CU; program 003 line 118, devnet program HssAePJfZrERFjEAhm89nY9Tc9BWAobxp2GqGhefNK6V, proof withdrawal `CiZmcGsa…` (artifacts/public-deployment.json).

Audio: Liam's take, cut per line, standard chain (afftdn nr=18 once before cutting, 20 ms fades, brown-noise bed, loudnorm −16 LUFS). Never let audio run while lips are still.

Characters as before (generated bodies, stop-frame, freeze when silent, narrator never beyond 35° from upright, side pokes). Engineer = the player, with clipboard, standing at the cabinet's side. Lab coat = commentary pokes (the sigh, "not cool"). Joe optional on the win screen (celebrate pose).

## Style: an eighties arcade cabinet
Black playfield, chunky pixel font, scanlines, a bezel with a coin slot, phosphor glow, slight CRT curvature. Transition in: scene 7's last frame gets sucked into the cabinet screen like a game loading (shrink to a line, then expand as pixels). Everything in the playfield is pixel art; the characters stay as they are (the mixed-style joke).

## Beats
1. "way smaller": two blocks drop like game pieces: a huge LAMPORT block "8,192" then a small XMSS block "2,500"; the big one explodes into pixels; SCORE ticks up.
2. "that 1,232 byte transaction size limit": the playfield floor has a slot exactly 1,232 wide (labelled). The 2,500 block drops, does not fit, wedges; screen shake; red flashing GAME OVER; the engineer facepalms (use a hand-to-face pose if available, else freeze with head down tilt).
3. "five transactions": WORKAROUND LEVEL. The block is sawn into pieces; five little pixel mail trucks carry them one at a time to a TEMP ACCOUNT box, the fifth carrying EXECUTE; counter 1→5 slowly. Program box "BUNKER PROGRAM 003-A" with the see-the-code box (GitHub QR to program/src/lib.rs line 118) and proof box (Solscan QR to `CiZmcGsa…`). "That's not cool": a pixel thumbs-down stamp; lab coat poke.
4. "So we rebuilt it": INSERT COIN flashes; the engineer drops a Solana coin into the slot. A banner scrolls "SOLANA TRANSACTIONS V1" with a flashing NEW label above; the slot widens as "1,232" ticks up to "4,096"; the ">" between 2,500 and the limit grows, spins and settles as "<" (Liam's direction); "-A" flies off the program box and "-B" settles in; the five truck boxes shrink away one after another; a single new box pops in.
5. Last line = WIN SCREEN: high-score lines pop in: "1 TRANSACTION", "3,117 BYTES", "518,509 CU", then "SIGNATURE VERIFIED ON CHAIN" with a green pixel checkmark filling the screen. Joe hands up optional.
6. Tag (no speech, ~6 s): LEVEL COMPLETE text crawl in small pixel type with the rotation text box, the spent-leaf bitmap beside it (LED row from scene 5), a new tree installing as NEXT LEVEL; then the transaction table scrolls up like credits. Keep this readable but it need not be tiny-screen readable (Liam: the text box "doesn't need to be tiny screen readable").

Rules: 90% of the spoken beats readable at 426x240; render on dev-mac only, never ffmpeg on do-box; delete frame folders with literal paths; open your own stills at every beat; phone re-encode 960x540 crf 26. Branch: worktree `~/code/solana-bunker-s08`, branch `film/s08` from main with `film/floating-head` and `film/s07` merged in (reuse head pipeline, bodies, scene 7's last frame for the transition). Commit as the repo's configured identity, NO trailers. No push.

## Plan first
Write `docs/presentation/film-plan-s08.md` (beats, timings vs the cut audio, production method per visual including the CRT look and the pixel assets, risks + fallbacks) and ONE draft still of the cabinet look (playfield with the 1,232 slot, the wedged 2,500 block, GAME OVER, the engineer at the side). Report and STOP; build after the composer approves.
