# Solana Bunker, polished film plan (2026-10-13, after submission)

Liam: mix all four design worlds, one slide at a time, real motion graphics, 240p-legible. Script: docs/presentation/pitch-script-final.md (full, not the 3-minute cut). Footage: 3:4 matted selfie (dev-mac ~/video-work/bunker/, tone-mapped HLG to BT.709, RVM alpha).

| Slide | World | Choreography |
|---|---|---|
| 0 intro | broadcast | sponsor card "The following program is brought to you by Chaintail Labs", then advisory card: WARNING, contains math, conspiracy theories, fear mongering based on hypothetical scenarios, viewer discretion is advised (Liam 15771) |
| 1 title | dossier | desk, folder drops, label types, CLASSIFIED slams, warning note on paperclip, cover lifts out |
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
