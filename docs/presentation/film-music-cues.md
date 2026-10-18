# Solana Bunker, music cue sheet (Liam 16495: go on the music plan)

Five Suno cue families plus the arcade scored in-house with the chiptune tracker (pipeline/s08/score.py); the noir cue continues under scene 7 (the seminar) at -4 dB, then comes back up on the alley cut. Level: music about 20 dB under the voice during speech, up to 10 dB under in real gaps; duck fast attack / slow release; high-pass near 180 Hz; the brown-noise bed is muted while a cue plays; 20 ms edges; music changes only where the picture style changes. Keys: C major for news, workshop, arcade, sponsor; A minor for conspiracy and noir. Source: Suno on a paid plan (download while paid, keep the plan and date); CC0 fallback. Add a MUSIC credit line.

## Cue 1: Sponsor card + advisory

Where: Opening 0:00–0:18; reprised brighter in the infomercial (scene 9, colour half)

Suno style prompt: `1970s American TV advertising library music, 104 BPM, Rhodes electric piano, muted funk guitar, brushed drums, warm bass, absurdly reassuring, instrumental, sparse dialogue underscore, no vocals, no solos, no big builds, seamless loop, no intro, no outro`

Behaviour: Cuts dead at the WARNING card. Returns under the infomercial's colour half with the same chords, brighter synths, a synth sax lick allowed.

## Cue 2: News desk (open) + sign-off (close)

Where: Scene 2 and scene 10; the same cue both times is the bookend

Suno style prompt: `local cable news theme, 116 BPM, restrained synth brass, timpani hits, ticking hi-hat percussion, pulsing synth bass, officious urgency, instrumental, sparse dialogue underscore, no vocals, no solos, no big builds, 8-bar loop with a short stab ending`

Behaviour: Enters after the SPECIAL REPORT wipe sting, sits under the anchor, ducks hard under speech. The stab ending lands on the sign-off's last word, before the CNN ident.

## Cue 3: Conspiracy dossier

Where: Scene 3, corkboard, red string, the 1940s chart

Suno style prompt: `conspiracy documentary underscore, 76 BPM, muted analog synth pulse, bass clarinet, sparse vibraphone, ticking clock, low cello drone, exaggerated suspicion, instrumental, sparse dialogue underscore, no vocals, no melody, no big builds, seamless loop`

Behaviour: Starts on the first pin, swells only on the CENSORED stamp and the 'Trust me, bro' beat, out on the case file closing.

## Cue 4: Blueprint + whiteboard

Where: Scenes 4 and 5; thinned further under the Merkle tree

Suno style prompt: `educational cartoon workshop music, 96 BPM, pizzicato strings, marimba, woodblock, light glockenspiel, mechanical curiosity, playful, spacious arrangement, instrumental, sparse dialogue underscore, no vocals, no solos, no big builds, seamless loop`

Behaviour: One cue across both scenes so the blueprint-to-whiteboard cut reads as one lesson. Drop to pad and pizzicato only during the hash cascade and the Merkle tree. Silence on 'oh crap', back in under the shrug.

## Cue 5: Noir speakeasy

Where: Scene 6, black and white, rain

Suno style prompt: `1940s detective noir underscore, 68 BPM, upright bass, brushed snare, lonely muted trumpet, sparse piano chords, rainy night, deadpan disappointment, instrumental, sparse dialogue underscore, no vocals, no solos, 8-bar loop`

Behaviour: In under the rain, silence on the slot slam and REJECTED, nothing until the next scene.

## Cue 6: Arcade

Where: Scene 8 under play; the synthesized chiptune jingle and loop already in the tag stay

Suno style prompt: `1980s arcade puzzle game music, 124 BPM, chiptune, square wave lead, triangle wave bass, simple noise hat, playful tension, thin and quiet, instrumental, 8-bit, no vocals, seamless loop, short`

Behaviour: Under the cabinet play only; our own level-complete jingle and tag loop already exist, keep the same key.


## Suno takes received 2026-10-16

Analysis: librosa 1.0.0 + ffmpeg ebur128 on dev-mac; full data in `analysis.json` next to each wav under `~/audio-work/solana-bunker/music/suno/<cue>/`.

| Cue | File | Duration | BPM | Key | Intro | Natural end | Loudness (LUFS / TP) |
|---|---|---|---|---|---|---|---|
| 1-sponsor | suno-1-reassuring-groove-a.wav | 89.84 s | 103.4 | C major | 0.74 s (full from start) | 79.18 s | -16.3 / -5.4 dBTP |
| 2-news | suno-2-breaking-news-a.wav | 44.00 s | 117.5 | F minor | 4.23 s | 38.80 s | -15.7 / -3.1 dBTP |
| 3-conspiracy | suno-3-the-clock-ticks-twice-a.wav | 108.00 s | 152.0 | C minor | 6.43 s (builds to ~38 s) | 104.47 s | -16.8 / -3.6 dBTP |
| 4-workshop | suno-4-mechanical-curiosity-a.wav | 65.96 s | 95.7 (fit 97.0) | C major | 14.98 s | 64.46 s | -15.5 / -4.2 dBTP |
| 5-noir | suno-5-noir-a.wav | 126.40 s | 64.6 (drifts 66.3 to 63.0; fit 64.3) | C major / C minor ambiguous (0.765 vs 0.758) | 2.86 s | 114.64 s | -16.4 / -3.4 dBTP |
