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

Conspiracy x12 (Liam 16583, "1.2 on all"; 2026-10-16): the approved x11 cut (v4 choreography, lamp flicker removed) at 1.2x, no edit changes. apps/web/film/pipeline/capture-consp-x12.sh (capture.mjs --speed=1.2, title 210 -> 175 frames, scene 2044 -> 1704, hat 38 frames, 60-frame chunks) then build-conspiracy-x12.sh (Liam's take with v4's afftdn cleanup, atempo=1.2 pitch kept, two-pass loudnorm -16 LUFS, brown-noise bed at the new length; PiP frame k = v4 PiP frame round(1.2k); every overlay time / 1.2). Output conspiracy-x12.mp4: 1879 frames, 62.633 s, -16.0 LUFS. The black bar holds for 0.50 s (15 frames, 20.47-20.93 s) before CENSORED? slams. The scene has no generated voices or sound effects, so the whole mix is time-scaled.
