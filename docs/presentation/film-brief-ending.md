# Film brief: the ending (Liam 16296, 16325: scene 9 testimonial, back to the news desk, Chaintail News Network split-screen credits over the parchment outro)

Three pieces, in order. The take is `audio/bunker-take.wav` (dev-mac `~/video-work/solana-bunker/audio/`); transcript `s05/bunker-transcript.json`. Same audio chain as every scene (afftdn nr=18 once before cutting, 20 ms fades, brown-noise bed lowpass 220 volume 0.05, loudnorm −16 LUFS / TP −1.5, limiter ceiling as scene 9). Never let audio run while lips are still.

## A. Scene 9 extension: the testimonial (branch film/s09, appended to the infomercial's tag)
Spoken by the lab coat you, who pokes in at the end of scene 9 as the satisfied customer. Take 518.48–533.60 s:
"And this is not just a bunch of diagrams." / "All of this is live on DevNet right now." / "Three vaults for SOL, USDC." / "We demonstrate the robbery, the rejection, and rotation." / "Every number on the screen is a transaction you can open in the explorer."
Infomercial testimonial framing: the lab coat gets a lower third ("SATISFIED CUSTOMER" style name card, "Dr. L. C., cryptography nerd"), and as he names each claim a results card pops in with a Solscan QR, like before-and-after results: three vaults (program HssAePJfZrERFjEAhm89nY9Tc9BWAobxp2GqGhefNK6V, the array, Merkle and XMSS vault accounts), SOL and USDC withdrawals, the robbery (version two's front-run), the rejection (the XMSS program throwing out the swapped form), the rotation (new root). Every signature and account comes from `artifacts/public-deployment.json`; no number is invented. The QR codes are flat and decoder-checked at 720p and on the phone encode. The FREE tag and CALL NOW stay on screen. Scene 9 keeps its existing 29.83 s and grows by this beat; the last 2 s hold for the handoff.

## B. Scene 10: back at the news desk, the sign-off (branch film/s10)
The news desk from the opening (`apps/web/film/s02-news.html`: desk, bugs, lower third, over-the-shoulder box, chyron, the SPECIAL REPORT wipe) with Liam as the anchor from the matte footage (`matte-full-comp.mp4` + `matte-full-alpha.mp4` on dev-mac, see `pipeline/build-opening-v7.sh`; raw `~/video-work/bunker-raw.mov`). Transition in: the reverse of the opening's exit, the SPECIAL REPORT wipe opens onto the desk ("we now return to the studio").
Take 533.60–583.52 s, with the two false starts cut:
- 533.60–534.88 "Thanks for sticking around."
- 534.88–540.16 "If you made it this far and you didn't fall asleep, you must be a real crypto nerd like us."
- 540.16–542.24 "I told you the math would be worth it."
- 542.24–545.28 "And there's lots more in the white paper. Go check it out."
- CUT 545.28–563.36 (two false starts).
- 563.36–573.84 "The next cool piece of research is a stateless version of this. For this, we want to explore SLH-DSA. The signatures are bigger, but you never have to track which keys are spent."
- 573.84–581.76 "And my personal favorite idea, which we didn't get to yet, is using the vault to guard its own upgrade authority. It's a bunker protecting a bunker."
- 581.76–583.52 "Lots more to cook up in the lab."
On screen: chyron with the Crypto Twitter jokes continuing; on "crypto nerd" the lower third reads CRYPTO NERD and "graphy" squeezes itself in between to make CRYPTOGRAPHY NERD; on "white paper" the over-the-shoulder box shows the whitepaper QR (https://github.com/chaintail/solana-bunker/blob/main/research/whitepaper.md) with the title; on "stateless version" a COMING UP NEXT lower third: SLH-DSA, with "7,856 byte signatures, no state to track" (FIPS 205); on "bunker protecting a bunker" the over-the-shoulder box shows the vault inside a vault (the high-quality vault art from scene 4, nested); on "cook up in the lab" a beaker or lightbulb bug. The anchor video is cut at the sentence boundaries above; the picture cuts are hidden by the over-the-shoulder box swaps or a quick zoom, as the opening did.

## C. Scene 11: Chaintail News Network credits over the parchment outro (branch film/s11)
1. A full-screen Chaintail News Network ident: swirling abstract colours (the news desk's palette), the Chaintail lemur logo (`apps/web/film/assets/chaintail-logo.svg`, `-white.svg`, `-800.png`) spinning in with "CHAINTAIL NEWS NETWORK" and the letters CNN, flashy broadcast-style transition, about 3 s.
2. The ident splits the screen like a 1990s show's end credits: the LEFT third is the CNN panel (logo on top, credits scrolling up beneath it); the RIGHT two thirds is the parchment vault outro card: "Chaintail Labs R&D / Solana Vault", the GitHub QR (https://github.com/chaintail/solana-bunker) and the Telegram QR with their logos and links printed beneath, "Feel free to reach out with any questions!". Liam's last recorded line plays over it: take 583.52–586.08 "Feel free to reach out with any questions." (no face on screen; voice only, or the anchor in a small box if it reads better).
3. Credits text (Liam's final list, 16352/16357; scrolling, in this order; initials only for surnames; Mikail without an H; "Claude-Do", never "Claude D."; blocks are a heading line then names one per line):
   EXECUTIVE PRODUCERS: Liam C. / Claude-Do
   STORY INSPIRATION: Justin Drake
   CAST: NEWS ANCHOR Liam C. / SCIENTIST Liam C. / AVERAGE JOE Liam C. / BUNKER ENGINEER Liam C. / THE SUIT Liam C. / BANDIT DEVIL Liam C.
   VOICE ACTORS: THE ANNOUNCER Enceladus (Google Chirp 3 HD) / SPONSOR READ Studio C (Google, en-GB)
   WRITTEN BY: Liam C.
   DIRECTED BY: Claude-Do
   RESEARCH & DEVELOPMENT: Liam C. / Mikail R. / ChatGPT / Codex
   STORYBOARD: Claude Fable / Liam C.
   ART DIRECTION: Claude Fable / Liam C.
   SET DESIGN: Claude Fable / Claude Opus
   ANIMATION: Claude Opus
   COSTUME DESIGN: Codex GPT-6.1
   MATTE & COMPOSITING: ffmpeg / Chrome headless
   TRANSCRIPTION: NVIDIA Parakeet
   AUDIO ENGINEERS: Codex / Claude Fable / Grok (added in v3)
   MUSIC: Suno, prompts by Liam C. (added in v7)
   ARCADE SCORE: Original 8-bit score, Chaintail Labs (added in v7)
   NEWS STINGS: Freesound.org (CC0) / code_box: Mini News Jingle / xkeril: Minimalist news transition / Antwash: Da Da Da Daaa Opening (added in v7)
   SOUND EFFECTS: Freesound.org and Kenney.nl (CC0) (v7; v1-v6: freesound.org contributors (CC0) / Kenney)
   LOCATION: WorldOS v2 / do-box / Solana devnet
   ANIMATION STUDIO: dev-mac
   ASSOCIATE PRODUCER: Grok (added in v3)
   HOSTING & CATERING: GitHub
   ARCHIVAL SOURCES: Physical Review, 1920 to 1947 / 9,923 records checked
   STUNTS: Bunker Program HssAePJf…NK6V, Solana devnet / Every transaction in this film is real and open in the explorer.
   SPECIAL THANKS: Leslie Lamport / Robert Winternitz / Ralph Merkle / NIST
   Leslie Lamport portrait: photo by Leslie Lamport, via Wikimedia Commons (added in v7)
   No curves were harmed in the making of this film.
   No meme coins were harmed either. Yet.
   Based on a true story. / Events were dramatized. / Characters and names may have been changed to protect the identity of victims.
   Any resemblance to actual elliptic curves, living or broken, is purely coincidental.
   PRODUCT OF: Chaintail Labs (lemur logo)
   © 2026 Chaintail Labs
   The last full-screen card is "Based on a true story. Events were dramatized." style per section C.3 above, then PRODUCT OF Chaintail Labs with the logo, hold 3 s, fade to black.
4. The credits scroll must be readable at 426x240 for the role names; the names may be smaller.

Rules: render on dev-mac only, never ffmpeg on do-box; delete frame folders with literal paths; open your own stills at every beat; phone re-encode 960x540 crf 26. Worktrees `~/code/solana-bunker-s10` (branch film/s10) and `~/code/solana-bunker-s11` (film/s11), each from main with `film/floating-head` and `film/s09` merged in; the testimonial lands on film/s09 in `~/code/solana-bunker-s09`. Commit as the repo's configured identity, NO trailers. No push.

## Plan first
Write `docs/presentation/film-plan-ending.md` (cut lists for A, B and C vs the take, beat tables, production method per visual, the credits layout, risks and fallbacks) and THREE draft stills: the testimonial with a results card, the news desk at CRYPTOGRAPHY NERD, the split-screen credits over the parchment. Report and STOP; build after the composer approves.
