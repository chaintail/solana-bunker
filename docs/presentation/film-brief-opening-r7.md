# Film brief: opening, revision 7 (Liam 15977, 15986, 16018)

Scope is Liam's words, nothing wider. Three changes to the opening cut on `main` (v6, commit 3314b09). Everything else stays as rendered.

1. **Advisory card voice.** Voice is `en-US-Chirp3-HD-Enceladus` (Google Cloud TTS, v1beta1 `markup` input, service account `~/.secrets/gcp-tts-sa.json`). Per-phrase speaking rates, each phrase its own synth call, butt-joined with explicit silences, no time stretching:
   - "Warning." at 1.0, then 700 ms silence
   - "The following program contains math" at 1.08, then 300 ms silence
   - "conspiracy theories, and fear mongering based on hypothetical scenarios." at 1.15, then 400 ms silence
   - "Viewer discretion is advised." at 1.0
   Liam heard exactly this join (`ALT-advisory-Enceladus-1x-108-115-1x.wav`, 24 kHz mono, 300 ms lead and tail) and said it is the right voice. Reproduce it with the same calls, normalise to the card's loudness target, re-time the on-screen word reveals to the new audio, keep the `[WARNING]` label and the previous layout. Check "mongering" acoustically as in r5.
2. **PiP outline during the Justin zoom.** "The outline box around the picture-in-picture when we're zooming into Justin's head is flashing. Our image is on top of the outline. Fix the outline." The border must be its own layer above the thumbnail image for the whole zoom, so the image never covers it and it never flickers. Step through the zoom frames and confirm.
3. **Tweet highlights:** unchanged ("I'll leave the tweet alone").

Process: render on dev-mac only (never ffmpeg on do-box). Open your own stills at every change (advisory card at each phrase, PiP at zoom start, middle and end) before reporting. Output `out/opening-v7.mp4` plus a phone re-encode. Commit on `main` as Liam's identity with no Claude trailers. Report: outcome, the frames you looked at, anything not done as written.
