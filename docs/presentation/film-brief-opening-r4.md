# Opening beats, revision 4 (Liam voice 15874 + 15876, 2026-10-14 12:08 ICT)

Apply to the committed scenes in apps/web/film (commit 514d9e5 built opening-v3.mp4) and build `opening-v4.mp4`. Liam's words are quoted; everything else unchanged.

## Voice-over technique (both cards)
"The speed compression stuff for the warning voice is really corrupting the audio." Drop the rubberband time-stretch. New technique: render each phrase as its own kokoro call at the phrase's native speed (kokoro's `speed` parameter), then concatenate the phrases with explicit silences. Native-speed synthesis has no stretch artifacts, and the pauses become real gaps. Crossfade nothing; butt-join with a 20 ms fade at each phrase edge to avoid clicks. Keep the one-take-plus-stretch pipeline files but do not use them in the cut.

### Sponsor card (0a), British female voice, bf_emma unless Liam picks Isabella
- "The following program is brought to you" at 1.15x.
- A very short pause (about 150 ms) before "by".
- "by Chaintail Labs" at 1.0x, "slower than the first sentence."
- Retime the logo reveal in `s00-intro.html` to land on the spoken "Chaintail Labs" (re-capture 0a; extend the card to fit with at most 1 s of air).

### Advisory card (0b), new male voice
- "Whichever voice we're using right now pronounces mongering wrong." Choose a different deep male kokoro voice (try am_adam, am_michael, am_fenrir, bm_george, bm_lewis); render "fear mongering" with each and pick the one that says MUN-ger-ing; if none does, spell it "fear-mongering" or "fear mungering" in the TTS input only.
- Pauses: a longer pause after "Warning." (about 700 ms); a short pause after "math" (about 300 ms); a short pause before "Viewer discretion is advised." (about 400 ms).
- Speed curve, per phrase, native: "Warning." 1.0x. "The following program contains math" 1.0x. Then accelerate phrase by phrase, "way more": "conspiracy theories" 1.3x, "and fear mongering" 1.6x, "based on hypothetical scenarios" 2.0x ("end around a 2x speed"). "Viewer discretion is advised." at 0.85x, "the slowest part".
- On-screen reveal follows the new phrase timings.
- TV-MATH box: starts at the current size, then shrinks and moves up into the top-left corner (classic rating bug), over about 1 s after the word "Warning". The copy re-flows to use the freed space.

## News desk (2)
- **Justin's face box:** "we are getting rid of Justin's face too early. Keep it there like way longer." Keep the zoomed face up until the tweet discussion ends ("hidden behind a hash"), then exit as now.
- **CNN bug:** move it up so its baseline aligns with the red headline bar ("in line with the red crypto Twitter in spiral"). Same mark, no redesign yet.
- **Top-left:** remove "CT NEWS". Move the blinking LIVE bug next to the CNN logo bottom right (test both; Liam's instinct is that LIVE beside CNN looks better and frees vertical height for the tweet). Leave the top-left empty.
- **Tweet component:** the fixed header was right in spirit but used the wrong crop ("you got the header of the tweet wrong"): use the real header from the screenshot (Justin's avatar, name, handle, X mark). ADD the fixed footer: the screenshot strip with likes and impressions, pinned at the bottom of the box; the body scrolls between the fixed header and the fixed footer. Use the extra vertical height from removing the top-left bug.
- **Highlights:** "highlight exact sentences, like an actual highlighter, one line at a time." The marker draws along the text from the sentence start to its end: it starts mid-line where the sentence starts and stops mid-line where it ends, never whole lines unless the sentence happens to fill them; multi-line sentences are drawn line by line in order. Highlights stay until the next sentence is highlighted (do not clear quickly). Needs word boxes: lay the body text out as real HTML text positioned over the screenshot (or re-typeset the body in the same font at the same size) so sentence spans are known. Sentences to highlight, in order of Liam's words, as before.
- **Ending:** cut Liam's final words "well, until quantum" (the take fumbles there). End the desk audio on "And maybe it never will be." At "maybe it never will be", bring the over-the-shoulder box back top right with a card reading "Q-DAY? (fake)" as a joke, then the SPECIAL REPORT wipe.

Pipeline rules as before (dev-mac for all media; commit by pathspec; no trailers; do not push). Report: v4 path, voice choice made for 0b and the mongering result, stills for the TV-MATH bug end position, the tweet with header+footer mid-scroll and a mid-sentence highlight, the Q-DAY card, and anything not followed as written.
