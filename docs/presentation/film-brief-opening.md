# Film brief: opening beats (sponsor card, advisory card, chime, news desk)

Liam's words (voice 15809, 15819): "wrap up this video, scene by scene or beat by beat." Beat zero is the parental-advisory TV joke with a deep announcer voice, then the breaking-news desk. Keep yesterday's recorded script unchanged; he has already recorded it.

Read first: `docs/presentation/film-plan.md` (style map, scene contract), `docs/presentation/pitch-script-final.md` (slides 0 and 2), `apps/web/film/lib/film.js` (scene helper, uncommitted), `apps/web/design-stills/out/news.png` and `dossier.png` (the looks to match), the skill `/home/claude/claudes-world/.claude/skills/animated-video/film-production.md`.

Scene contract (unchanged): each scene is `apps/web/film/<scene>.html`, `data-duration`/`data-fps`, every animation seekable by `window.__seek(t)` (Web Animations with fill both), seeded rng, `?t=` preview, `?capture` for frame mode, `window.__cues`. `apps/web/film/scripts/capture.mjs` (still to be written) drives headless Chrome, seeks each frame, writes PNG frames to `apps/web/render/<scene>/f%05d.png` (gitignored). Everything must stay legible at 240p: big type, few words on screen at once, high contrast.

## Beat 0a: sponsor card, about 4 s (`s00-intro.html`)
Black. Serif, centred, white: "The following program is brought to you by" then "Chaintail Labs" with the lemur logo `docs/presentation/assets/chaintail-logo-800.png`. Period TV feel: faint scanline/static flicker, a one-frame colour-bar flash at the very start. Audio: room tone only.

## Beat 0b: advisory card, about 12 s (same scene or `s00b-advisory.html`)
White on black. Rating box left (TV-PG style box, text "TV-MA" style letters replaced with "MATH"). Copy, revealed in step with the voice-over:

> Warning. The following program contains math, conspiracy theories, and fear mongering based on hypothetical scenarios. Viewer discretion is advised.

Voice-over: deep announcer. No ElevenLabs key exists on do-box yet; render with kokoro on dev-mac (deepest male voice available) so the beat is complete now, and keep the pipeline so an ElevenLabs render can be dropped in later. Render once at 1x, then time-stretch with the ffmpeg `rubberband` filter (pitch preserved) using `sendcmd` so the tempo ramps smoothly, no chunking: start at 1.1x on "Warning", ramp up through the disclaimer to about 2x, then drop back to 1.0x exactly on "Viewer discretion is advised." The on-screen text reveal follows the stretched audio timing (derive word times from the 1x render and map them through the tempo curve). Normalize to about -16 LUFS. Liam: "Everything at normal speed sounds too slow."

## Beat 0c: breaking-news chime, about 2 s
Liam supplies the chime file; leave a 2 s slot. Visual: red "BREAKING NEWS" slam with a white flash that covers the cut into the desk. Do NOT generate sound effects with ElevenLabs.

## Beat 2: news desk (`s02-news.html` plus composite)
Layout, 1280x720:
- Liam centre, matted footage (`dev-mac:~/video-work/bunker/matte-full-comp.mp4` + `matte-full-alpha.mp4`, 1080x1440), scaled so the full collar shows, behind a news desk; skyline backdrop in the `news.png` style.
- "LIVE" bug top-left. Lower third when he first appears: "Liam, Chaintail Labs, Senior Bunker Correspondent".
- Scrolling chyron at the bottom, made-up Crypto Twitter jokes about the tweet (handles shortened, e.g. "@sol_maxi_…: it's over" / "@quant_…: quantum is 30 years away, buy the dip"); 8 to 12 items, loop.
- Over-the-shoulder box top-right: the Bankless YouTube thumbnail with Justin's face (asset from the cheap deck, `apps/web/src/scenes/cheap/`). A red circle snaps onto his face and pulses twice, then the box zooms until his face fills it. When the tweet is discussed, the tweet card slides up on the other side; Liam stays on screen as anchor throughout.
- Exit: a "SPECIAL REPORT" wipe into the dossier at the conspiracy line (scene 1 title follows; not in this brief).

Audio: Liam's recorded take, `scratchpad/vid/audio.wav` with its transcript next to it (scratchpad path: `/tmp/claude-1000/-home-claude--world-team-composer-workspace/a1d3bf88-bbef-40ad-bf7b-26a166b186fc/scratchpad/vid/`). Cut his spoken opening ("warning, contains math, don't flip away") entirely; the desk audio starts where he begins talking about the tweet. Time the circle, zoom and tweet card to his words. Matted footage and audio must be offset by the same amount.

## Pipeline rules
- Frames (headless Chrome, PNG) render on do-box. ffmpeg, matting, audio, encoding ONLY on dev-mac (`ssh dev-mac`, ffmpeg-full at `/opt/homebrew/opt/ffmpeg-full/bin`, use `-nostdin` and `-/filter_complex <file>`). Never run ffmpeg on do-box.
- Working dir on dev-mac: `~/video-work/solana-bunker/out/<scene>/`. Disk is tight; ask before deleting anything under `~/video-work`.
- Commit in `~/code/solana-bunker` by pathspec only (`git add <files>`), using the repo's existing identity, no Claude trailers.

## Report wanted
Outcome format: one preview still per beat (0a, 0b, 0c, 2) pushed to dev-mac and the paths listed, a 720p mp4 of beats 0 to 2 at `dev-mac:~/video-work/solana-bunker/out/opening-v1.mp4`, the file list committed, and any point where the brief could not be followed as written.
