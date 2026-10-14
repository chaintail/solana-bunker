# Conspiracy section, first pass (Liam voice 15940, 2026-10-14 19:38Z: "take a first pass at animating the conspiracy section following your vision")

Build `conspiracy-v1.mp4`: the dossier title card (slide 1) and the conspiracy slide (slide 3) as one segment that plays right after the news desk. Script: docs/presentation/pitch-script-final.md, slides 1 and 3. Audio: Liam's recorded take, `audio.wav` with sentence timings in `bunker-transcript.json`, both in `/tmp/claude-1000/-home-claude--world-team-composer-workspace/a1d3bf88-bbef-40ad-bf7b-26a166b186fc/scratchpad/vid/` on do-box (copy to dev-mac `~/video-work/solana-bunker/audio/`). Slide 1 is "Who's excited for some mathematics… Nobody?… don't close the tab, I swear this gets good"; slide 3 runs from "But here's where the conspiracy starts" to "We will let you draw your own conclusions." Jump-cut his fumbles and dead air inside the section with your own judgement; keep every scripted sentence. Liam's matted 3:4 footage (`dev-mac:~/video-work/bunker/matte-full-alpha.mp4` + `matte-full-comp.mp4`, same timeline as audio.wav) is available for a small picture-in-picture of him; the dossier is the main picture.

World: dossier. Look: a desk seen from above, dark green blotter, warm lamp light from the top left, manila folders, photocopied paper with toner grain, red CLASSIFIED stamps, typewriter captions. Everything must read at 240p: big type, high contrast, one idea on screen at a time. Build as `apps/web/film/s01-title.html` and `apps/web/film/s03-conspiracy.html`, seekable with the same `window.__seek` contract as the other scenes (see apps/web/film/lib/film.js and s02-news.html), captured with apps/web/film/scripts/capture.mjs on dev-mac, encoded and muxed with the audio on dev-mac.

## Slide 1, title (dossier opens)
1. Empty desk. A thick manila folder drops in from above and lands with a dust puff, slightly askew.
2. The label types itself with typewriter clicks of motion (no sound effects): "SOLANA BUNKER". Then a red CLASSIFIED stamp slams at an angle.
3. On "Nobody?": a yellow sticky note slides in under a paperclip: "don't close the tab".
4. On "I swear this gets good": the cover lifts, revealing the first page, and we push in. Cut to slide 3.

## Slide 3, conspiracy (beats keyed to his sentences)
1. "But here's where the conspiracy starts": the open folder; the first page carries a typewriter header "CASE FILE 719 / THE MISSING PAPERS".
2. "OpenAI dropped over 700 math papers… overnight": a stack of paper sheets lands one after another, fast, with a counter in the corner ticking up to 719. The counter is big (it is the one number on the slide).
3. "covering seventeen disciplines": an index page slides in; seventeen discipline stamps appear in a grid, one per beat (Algebra, Analysis, Topology, Number Theory, Combinatorics, Geometry, Logic, Probability, Statistics, Optimization, PDE, Dynamical Systems, Graph Theory, Category Theory, Numerical Analysis, Game Theory, Information Theory).
4. "But one area was suspiciously missing. Cryptography.": the eighteenth slot stays empty, then a black redaction bar is drawn across it with the word CRYPTOGRAPHY showing through a torn gap for a moment before the bar covers it. Hold.
5. "Maybe that is because the math is sound": a pencilled note in the margin, "math checks out?".
6. "the US government may be leaning on OpenAI": corkboard inset. Two pinned items, an OpenAI card and a federal seal card, joined by red string. A third pin, "quantum?", dangles.
7. "there is precedent… this is what crypto Twitter was repeating": a printed tweet-shaped slip with a big UNVERIFIED stamp, pinned on top.
8. "Second World War… Manhattan Project… physicists stopped publishing": sepia shelf of journal spines labelled 1939 through 1947. The spines for 1942, 1943 and 1944 are missing: dust outlines where they stood. A slow pan along the shelf.
9. "rather than trust a bro, we checked": the UNVERIFIED stamp gets a second stamp over it: CHECKED. Then typewriter lines: "9,923 journal records, 1920–1947" and "719 papers, 2026". Optional: a small bar chart of papers per year with the 1942–44 dip, drawn as pencil on graph paper.
10. "The silence is real.": the lamp flickers once; the page holds still. Nothing else moves.
11. "We will let you draw your own conclusions.": the folder closes; a question-mark stamp lands on the cover. Hard cut to black for the next scene.

Optional, only if it is quick: Liam as a small PiP in the bottom right during beats 2 to 9 (matte footage over a paper-clipped Polaroid frame).

## Review your own frames
After every encode, extract stills on dev-mac (folder drop, CLASSIFIED stamp, counter at 719, redaction bar mid-draw, corkboard, shelf with the gaps, "silence is real" hold, closing stamp) and open each with the Read tool before reporting. Fix what looks wrong before reporting.

## Rules
dev-mac for every ffmpeg and capture run (the guard hook on do-box blocks them); frames under apps/web/render (gitignored); work on branch `film/conspiracy` in a worktree at /home/claude/code/solana-bunker-conspiracy so the opening builder on main is not disturbed; commit by pathspec with the identity of commit 0192493, no Co-Authored-By or Claude trailers, do not push, do not merge. Do not send anything to Telegram. Report: `dev-mac:~/video-work/solana-bunker/out/conspiracy-v1.mp4`, the stills (local paths), the cut list of his audio (in/out timestamps and what was cut), and anything not followed as written.
