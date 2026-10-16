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

Conspiracy x12b (Liam, voice 2026-10-16: shave the end, close the folio on "we'll let you draw your own conclusions", cut the silence before it, end on his speaking): x12 with the end trimmed. apps/web/film/pipeline/conspiracy-x12b-edit.py rewrites the p13/p14 cut list: one splice in the cleaned take (take-dn.wav) at rising zero crossings, 126.863 s -> 128.100 s (1.237 s of take silence and the 0.5 s inserted gap removed), so "The silence is real." runs into "We'll let you draw your own conclusions" with a 0.305 s pause at 1.2x (was 1.56 s). The old p13/p14 word table was 1.2-1.6 s late against the audio; the measured times replace it ("We'll" 57.38 s, "conclusions." ends 58.68 s in the 1.2x file). s03: the close starts 57.69 s, the folder lands 58.57 s (frame 1757, as the line ends, with its shake), the ? slams over CLASSIFIED 58.73 s and is settled from 58.85 s; the corkboard fades 57.32-57.65 s; data-duration 68.13 -> 63.9. capture-consp-x12b.sh keeps the 28 x12 chunks before the first changed frame (s03 output frame 1545) and captures s03 c25 and c26; build-conspiracy-x12b.sh is the x12 method (v4 PiP rebuilt from the v4 cut list when out/consp4/pip.mov is absent). Output conspiracy-x12b.mp4: 1773 frames, 59.100 s (x12 62.633 s, 3.53 s shorter), -16.0 LUFS; the scene ends 0.42 s after the last word. The #cut layer at the scene end has never rendered a black frame (steps(1,end) completes only after the last sampled frame), in x12 and v4 as well.
