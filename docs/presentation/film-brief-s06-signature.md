# Film brief: slide 6, a password is not a signature (Liam 16101/16112, composer vision 2026-10-15)

Liam: "Interesting vision. I love it, if Opus can pull it off. Make sure Opus clearly plans what it will do and you review his plan before starting… a really high quality attempt at this awesomely ambitious vision." So: PLAN FIRST, build only after the composer approves the plan.

Script (spoken, Liam's draft 3 beat 6, slide 6 only, every line kept): "Okay, this is where things" / [flash "*the math*" 500 ms] / "start to get cool." / "The problem with versions one and two is that a secret is just a password." / "Whoever shows the password first gets into the vault." / "But PASSWORD says nothing about where money should go. So if someone steals it on the way to the vault they can get in first!" / "What we actually want is a SIGNATURE." / "Something that says: this exact withdrawal, to this exact address, and nothing else."

Audio: Liam's take, cut per line, with the standard chain (afftdn nr=18 profile from the take's silent 0.10–0.70 s applied once before cutting, 20 ms cut fades, brown-noise bed under the whole scene, single loudnorm to -16 LUFS; see `apps/web/film/pipeline/build-conspiracy-v4.sh` and `data/conspiracy-audio.filter` on main). Never let the audio stop while lips move.

Characters: Liam's matted head on the generated bodies (`apps/web/film/assets/bodies/`, branch `film/floating-head`; head pipeline there). Stop-frame poses only, whole-figure moves, freeze when not speaking. Suit (arms-crossed) = bouncer. Lab coat (professor-point) = narrator, pokes in diagonally. Red devil = Liam's head tinted red, horns, bandit mask, no body. Stick man = the user, white marker lines, deliberately out of place.

## The style switch
Slide 5 ends on the cheap whiteboard. Slide 6 is film noir: black and white, film grain, one streetlight cone, rain streaks, a wet alley. The whiteboard is not faded; a passing car's headlight sweep wipes it away and leaves the alley. The only colour is the vault door: the high-quality vault render recast as a speakeasy door with a sliding slot at eye height, deep red, and later the sepia form and the red ink.

## Beats
1. "Okay, this is where things": on "things" the frame freezes and "*the math*" flashes for 500 ms in a cheap yellow font (Liam's note), then "start to get cool" resumes in the alley.
2. "a secret is just a password": suit bouncer stands in front of the door, arms crossed. The stick man walks up (whole-figure hop), a speech bubble reads "secret_42"; the slot slides open, the door swings open, he goes in.
3. "Whoever shows the password first": the devil head slides up behind, holding the same bubble, whispers it; the bouncer waves him in too.
4. "they can get in first!": the devil shoulders past the stick man in the doorway; the stick man is left outside with a "?" over his head.
5. "What we actually want is a SIGNATURE": the bouncer is yanked off sideways on a vaudeville hook (cheap). The lab coat narrator pokes in diagonally from the top right pointing down. A paper withdrawal form floats up and fills the left half in warm sepia: lines "TO:", "AMOUNT:", a signature line.
6. "this exact withdrawal": AMOUNT fills (e.g. 1.5 SOL). "to this exact address": TO fills with a Solana address (take a real devnet address from artifacts/public-deployment.json). "and nothing else": a quill signs with a flourish in red ink; the form slides through the slot; the door opens.
7. Tag (no spoken line, 1.5 s): the devil hands in a form of his own with a different TO address; the slot slams shut on his fingers. Freeze.

Program boxes: none (no new program version in this slide).

Rules: 90% readable at 426x240; render on dev-mac only, never ffmpeg on do-box, delete frame folders; open your own stills at every beat; phone re-encode 960x540 crf 26. Branch: worktree `~/code/solana-bunker-s06`, branch `film/s06` from main with `film/floating-head` merged in. Commit as the identity of commit 646d9bc, NO trailers of any kind. No push.

## Plan first
Before any rendering, write `docs/presentation/film-plan-s06.md` on the branch: for each beat, the exact on-screen elements, timings against the cut audio, how each visual is produced (CSS/SVG/canvas in the seekable scene, ffmpeg filters for grain/rain/headlight sweep, how the vault render becomes the door, how the bouncer/devil/narrator composites are placed), the noir look recipe (desaturation, grain, vignette, rain layer), the risks and the fallback for each risky element, and one draft still of the alley look (door, bouncer, rain, grain) rendered to a PNG. Report the plan and the still to the composer and STOP; build only after approval.
