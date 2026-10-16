# Solana Bunker, polished film plan (2026-10-13, after submission)

Liam: mix all four design worlds and more (he will bring further styles), one slide at a time, real motion graphics, 240p-legible. Script: docs/presentation/pitch-script-final.md (full, not the 3-minute cut). Footage: 3:4 matted selfie (dev-mac ~/video-work/bunker/, tone-mapped HLG to BT.709, RVM alpha).

| Slide | World | Choreography |
|---|---|---|
| 0 intro | broadcast | sponsor card "The following program is brought to you by Chaintail Labs", then advisory card: WARNING, contains math, conspiracy theories, fear mongering based on hypothetical scenarios, viewer discretion is advised (Liam 15771) |
| 1 title | dossier | PLAYS AFTER THE NEWS DESK (Liam 15775): opens the conspiracy section. desk, folder drops, label types, CLASSIFIED slams, warning note on paperclip, cover lifts out |
| 2 tweet | breaking news | lower third, Bankless thumbnail as footage, tweet document with magnifier, Liam as anchor |
| 3 conspiracy | dossier | photocopied index page with cryptography redacted, fission timeline from journal covers, proverb on telegram strip |
| 4 bunker | blueprint | vault door drafts itself, PDA as a point off a plotted curve |
| 5 v1, v2, robbery | terminal + comic cutaway | hashes and grid as terminal, stick-figure devil kept |
| 6 signature | dossier noir | door with slot, withdrawal form, quill |
| 7 hash sigs, one tx | blueprint then terminal | Lamport, Winternitz, Merkle drafted; byte counts and v1 rescue in terminal |
| 8 seed phrase | dossier | 24-word card, mostly redacted |
| 9 devnet | news ticker | confirmed transactions, QR grid |
| 10, 11 close | news sign-off, dossier | folder closes, lemur, contact QRs |

Pipeline: apps/web/film/<scene>.html, animations seekable (Web Animations API or window.__seek), apps/web/film/scripts/capture.mjs renders 30 fps PNG frames on do-box; encoding and compositing on dev-mac only.

## Opening v9 (Liam, voice 2026-10-16)

Four changes on the locked x11 cut (branch film/opening-v8, ff6c269). Everything else is x11's: the desk picture and the hold (`opening-x11/out/final`), Liam's desk voice at 1.1x with the denoise chain, the jump cut and the earlier end cut (`opening-x11/out/desk-final.wav`), "A special report." at +5 dB 0.75 s after the hold starts, the brown-noise bed and the limiter (0.80, no auto-level).

Scripts: `pipeline/render-vo-v9.py`, `pipeline/capture-v9.sh`, `pipeline/build-opening-v9.sh`, `pipeline/audio-v9.filter`, `pipeline/jingles-v9.py`, `pipeline/verify-v9.sh` (with `onsets-fine.py` and `contact-sheet.py`). Scenes: `s00b-advisory-v9.html` with `data/s00b-words-v9.js`, and `s00c-ident.html`. The x11 scripts and scenes are unchanged. Work tree on dev-mac: `~/video-work/solana-bunker/opening-v9`. Outputs: `out/opening-v9.mp4`, `out/opening-v9-phone.mp4`, `out/opening-v9-ident-compare.png` and `out/opening-v9-card-excerpt.mp3`.

1. **Sponsor and advisory reads at 1.2x.** Both use the existing renders sped up with atempo, which keeps the pitch. There is no re-synthesis.
   - Sponsor: `out/s00a-v5/vo-final.wav` at atempo 1.2, so 4.505 s becomes 3.766 s. The card has fixed animation times, so it is captured with `--speed=1.2`. It is 4.9 s before and 4.1 s after (147 to 123 frames), saving 0.8 s.
   - Advisory: the approved Chirp phrase files were synthesised at speaking rates 1.0, 1.08, 1.15 and 1.0. Each phrase is brought to an effective 1.2 from its own render with atempo 1.2, 1.111, 1.043 and 1.2. Stacking 1.2 on top would have given 1.30 and 1.38.
   - The lead-in, the three silences (700, 150 and 400 ms), the tail and every fixed time on the card are divided by 1.2. Word reveals are v7's word times mapped through each phrase's atempo.
   - The voice is 11.715 s before and 10.527 s after. The card is 13.0 s before and 11.567 s after (390 to 347 frames), saving 1.433 s.
2. **The Chaintail News Network ident replaces the BREAKING NEWS band.** `s00c-ident.html` is a port of s11's ident (`s11-cnn.html`, the bars and the ident).
   - Kept from s11: the same four broadcast bars, the swirl and its colours, and the lemur spin. The CNN / CHAINTAIL NEWS / NETWORK block and the red rule use the measured layout copied from s11, drawn at 1.6x above the centre.
   - BREAKING NEWS (Oswald 700, 118 px) slams in with CNN as one slam. The slam is s11's CNN slam: scale 2.4 to 1 over 0.25 s, the rule 0.1 s later, and a 2-frame shake on landing.
   - s11's beat lengths are kept and the gaps between beats are shortened: bars from 0, the lemur from 0.35, the lines from 0.85, the slam from 1.15 (it lands at 1.40), and the streak from 1.55.
   - The card ends on the old card's white flash, solid on the last frame, into the desk's entry flash. It is 2.2 s (66 frames), against the old 2.0 s, so the desk enters 0.2 s later relative to the card start.
3. **Jingle A (news-open-1-mini-jingle, mastered wav).**
   - Its first big hit (0.660 s into the file) is on the ident's landing frame (film 17.067 s), so it starts at 16.407 s.
   - The gain is -3.1 dB, which matches the event loudness of x11's horn as it was mixed (-27.7 LUFS).
   - It runs under the desk entry. At Liam's first word (18.147 s, 0.28 s into the desk voice) it is ducked -12 dB with a 100 ms attack and fades to silence over 1.0 s.
4. **Jingle C (news-open-3-da-da-da-daaa) replaces the horn stabs.**
   - Its last hit (the "daaa" attack, 0.467 s into the file) is on the SPECIAL REPORT slam frame: desk frame 1031, film frame 1567, 52.233 s, the first frame with the card at rest. Frame 1030 is less than 1 px off.
   - The gain is -2.6 dB, matched to the horn's event loudness.
   - It plays to the end of the scene (2.6 s of its 3.2 s) and fades with the bed over the last 0.6 s. Under "A special report." it is ducked 8 dB over the voiced span with 100 ms ramps. Unducked, the voice led C by 4.7 to 12.8 dB in the voiced 100 ms windows; ducked, it leads by 12.7 to 20.8 dB.

**Timeline (30 fps):**

| Part | Frames | Time (s) |
|---|---|---|
| Sponsor | 0–122 | 0–4.1 |
| Advisory | 123–469 | 4.1–15.667 (voice at 4.6) |
| Ident | 470–535 | 15.667–17.867 |
| Desk | 536–1567 | 17.867–52.267 |
| Hold | 1568–1630 | 52.267–54.367 |

The whole scene is 54.367 s (1631 frames), against x11's 56.4 s (1692 frames), so 2.033 s shorter.

**Checks:**
- Loudness is -16.4 LUFS integrated with a -1.9 dBFS peak (x11: -16.3 LUFS, -1.8 dBFS).
- glitch-scan v2 was run with the 16 chunk starts and stale-copy references at frames 0, 123, 470 and 536, on the master and the phone file.
  - There are no stale frame-0 copies.
  - One flag, the pair 535/536: the ident's last frame (solid white) and the desk's first frame (its entry flash at full opacity). This is the designed white hand-off.
- Onsets in the mix:
  - Jingle A's hit attack is at 17.071 to 17.073 s (17.064 to 17.068 s in the stem). The landing frame is at 17.067 s.
  - Jingle C's last-hit attack is at 52.240 to 52.243 s (52.235 s in the stem), 7 to 10 ms after the slam frame at 52.233 s.
  - The horn is gone. The mix's normalised correlation with the horn is -0.04, where x11 gave 0.40. Its correlation with C is 0.92.
- faster-whisper small (int8), run per section, finds the sponsor read, the advisory, the whole desk speech and "A special report." all intact.
