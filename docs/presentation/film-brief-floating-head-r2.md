# Floating head, revision 2: five bodies, one silent scene (Liam voice 15963, 2026-10-15 03:47Z)

Build `head-bodies-test.mp4`, about 12 s, 1280x720, silent, from the worktree on branch film/floating-head (commit f6ba76b built floating-head-test.mp4). Liam: "My head being used on a body is hilarious. Let's try to draw a better body."

## Fix the proportions first
- "I'm imagining the head being much smaller, almost a full body of the person." Each figure is a near full-body cartoon (head to knees or to shoes), the head about one sixth of the figure's height, so the head clip is scaled well down.
- "The head is sticking up way too high, so it would need to be much lower, and put the neck behind the body. We have a shirt collar, so it looks like I have a giraffe neck." Layer order: body in front of the neck. The head-and-neck clip sits BEHIND the collar layer so the collar covers the bottom of the neck; the chin sits just above the collar line. Draw each body with a separate collar/neckline layer for this.
- "This one looks like Donald Trump, just a fat guy in a blue suit." Slimmer, taller figures; narrow shoulders relative to height; no barrel torso.

## Five bodies, side by side in one scene
Five figures across the frame, each with the same silent head clip (use the existing head key from the r1 test, `dev-mac:~/video-work/head-test/head-key.mov`, re-scaled). A small label under each. Left to right:
1. **Suit.** Fitted dark suit, white shirt, tie.
2. **Man on the street.** Plain t-shirt, jeans, hands in pants pockets, sneakers.
3. **Detective.** Belted trench coat, holding a magnifying glass up in one hand.
4. **Bunker engineer** (the fourth, my pick): hard hat with a headlamp, grey coveralls, work gloves, holding a big vault key. (Alternative if it draws better: a 1940s physicist in a lab coat with a clipboard and pipe.)
5. **Blonde wig.** "Can we put a blonde wig on me as well, turning into a woman? It might be too ridiculous, but I would like to see it." A shoulder-length blonde wig layered over the head clip (hair in front of the forehead edge and behind the ears, so the face is untouched), on a figure in a blouse and skirt or a dress.

## Stop-frame poses, not fluid motion
"I don't necessarily think we want the bodies to have fluid movement. They can be sort of stop-frame positions… hands at the side, then the arm moves to point at something, then two hands in the air. Just give them a couple of different static positions." Each figure has three drawn poses: A arms at rest, B one arm pointing to the side, C both hands up. The scene cuts between poses (hold A 3 s, cut to B 3 s, cut to C 3 s, back to A), no tweening; a 2-frame hold-and-snap is fine. The head clip plays continuously on top, scaled and positioned per figure, with a tiny bob (2 px) at most.

## Draw it well: look at your own frames
"If the builder actually looks at their work, they can draw a much better body." Draw as SVG in an HTML scene with the same seekable contract as apps/web/film (window.__seek). After the first capture, extract a still of each figure in each pose (15 stills) and open every one with the Read tool. Judge proportions (head one sixth of height), neck hidden behind the collar, no giraffe neck, no barrel torso, hands readable, pointing arm clearly pointing. Redraw and re-capture until they pass. Put the final 15 stills and a full-frame still in the report.

## Rules
dev-mac only for ffmpeg and capture (ffmpeg in /opt/homebrew/bin; about 7 GB free, delete your frame folders after the encode; two other builders are rendering on dev-mac, so keep captures short). Worktree /home/claude/code/solana-bunker-head, branch film/floating-head; commit by pathspec with the identity of commit 0192493, no Co-Authored-By or any trailer; do not push or merge; do not touch /home/claude/code/solana-bunker or /home/claude/code/solana-bunker-conspiracy. Do not send anything to Telegram. Report: dev-mac path of head-bodies-test.mp4 (also copy it and the stills to /tmp/claude-1000/-home-claude--world-team-composer-workspace/a1d3bf88-bbef-40ad-bf7b-26a166b186fc/scratchpad/head2/), what you redrew after looking, and anything not followed as written.
