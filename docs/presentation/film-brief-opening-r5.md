# Opening beats, revision 5 — lock the opening (Liam text 15937 + 15939, 2026-10-14 19:37Z)

Apply to the committed scenes in apps/web/film (commit bcc635b built opening-v4.mp4) and build `opening-v5.mp4`. Liam's words are quoted; everything else unchanged. His framing for this round: "I don't wanna nitpick this too much and we can't waste too much time making this video. Good enough. It's already way, way better, it's super cool." This is the last pass on the opening: do exactly these items, no extras.

## Voices: Google Cloud Text-to-Speech Studio voices replace kokoro on both cards
"I think we're far enough along here that we can use higher quality voices, not the cheap voices that we're using. I wanna either use Google Studio voices or 11 Labs." We have no ElevenLabs key; we do have the Google TTS service account that md-speak uses. Synthesize on do-box with curl (that is not video rendering, the guard hook allows it), request `audioEncoding: LINEAR16, sampleRateHertz: 24000`, base64-decode to WAV, scp to dev-mac. Script skeleton:

```
python3 - <<'PY'
import json,base64,subprocess
from google.oauth2 import service_account
import google.auth.transport.requests, urllib.request
c=service_account.Credentials.from_service_account_file('/home/claude/.secrets/gcp-tts-sa.json',scopes=['https://www.googleapis.com/auth/cloud-platform']); c.refresh(google.auth.transport.requests.Request())
body={"input":{"ssml":SSML},"voice":{"languageCode":"en-GB","name":"en-GB-Studio-C"},"audioConfig":{"audioEncoding":"LINEAR16","sampleRateHertz":24000}}
req=urllib.request.Request("https://texttospeech.googleapis.com/v1/text:synthesize",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+c.token,"Content-Type":"application/json"})
open(OUT,"wb").write(base64.b64decode(json.load(urllib.request.urlopen(req))["audioContent"]))
PY
```
Studio voices take SSML, so pauses are `<break time="..."/>` in one take; no per-phrase joining, no rubberband. Keep the kokoro pipeline files in the tree but out of the cut.

### Sponsor card (0a)
- Voice: `en-GB-Studio-C` (British female; "Isabella is better voice for opening but let's use a Google Studio voice instead for best quality"). Also render `en-GB-Chirp3-HD-Aoede` as an alternate file for Liam to compare; the cut uses Studio-C.
- Text: "The following program is brought to you <break time="550ms"/> by Chaintail Labs." ("Longer pause in opening before the word by": v4 had ~150 ms; make it about 550 ms.) Whole line at rate 1.0. No speed changes anywhere.
- Retime the logo reveal in `s00-intro.html` to land on the spoken "Chaintail Labs", as in v4.

### Advisory card (0b)
- "New voice for warning is way worse. Let's ditch the speed-up idea too. It sounds garbled." No speed ramp at all: the whole card at rate 1.0.
- Voice: `en-US-Studio-Q` (deep male announcer). Also render `en-GB-Studio-B` as an alternate file. Check "fear mongering" by ear in the output; if the voice says it wrong, use SSML `<phoneme alphabet="ipa" ph="ˈmʌŋɡərɪŋ">mongering</phoneme>` and verify again.
- Pauses as v4: after "Warning." 700 ms, after "math" 300 ms, before "Viewer discretion is advised." 400 ms, all as `<break>`.
- Layout: "I don't like the new layout of the warning screen. Let's just go back to how it was before. It was fine. We can leave the big WARNING label." Revert `s00b-advisory.html` to the v3 layout (`git show 514d9e5:apps/web/film/s00b-advisory.html`): no TV-MATH shrink-to-corner, no copy reflow. Keep only the big WARNING label if v4 added or enlarged it (diff v3 vs v4 and keep that one change). Re-time the on-screen reveal to the new audio.

## News desk (2)
- **End trim:** "Cut half a second sooner at the very end of me speaking the news report. Audio stops and my lips keep moving at the end." Trim the desk take's out-point 0.5 s earlier so the picture ends with the audio; the Q-DAY card and SPECIAL REPORT wipe follow from the new out-point.
- **Mid-take cut:** "Cut out the section between 'he said get ready for bunker mode' and 'what was his advice?'" (the public key cryptography part). Remove everything after the end of "…get ready for bunker mode" up to the start of "What was his advice?". Hard jump cut on the footage; cover the cut with a 6-frame cross-dissolve on the picture only if the jump looks bad on review. Keep the tweet highlight timeline in sync with the shortened audio (highlights were keyed to the words; re-key them).
- **CNN bug:** it is still slightly too high (Liam's screenshot, 15937). Vertically centre the CNN mark and the LIVE dot on the red headline bar's centre line. Measure on a captured frame: the red bar's top and bottom y, the logo's top and bottom y; the two centres must match within 2 px. Put the numbers in the report.

## Frame review is mandatory
"Make sure the agent is looking at frames of its own work. I think it would have noticed the CNN logo is slightly too high." After every encode, extract stills with ffmpeg on dev-mac (at least: sponsor card mid-line, WARNING card at the end of the reveal, news desk at the first highlight, news desk at the mid-take cut point ±2 frames, news desk at the last frame before the Q-DAY card) and open each still with the Read tool before reporting. Compare the WARNING still to a v3 still side by side. If a still shows a defect, fix and re-encode before reporting.

## Pipeline rules as before
dev-mac for every ffmpeg and capture run (guard hook on do-box blocks them); frames under apps/web/render (gitignored); only the changed segments re-encode; `pipeline/build-opening*.sh` stitches. Commit by pathspec in solana-bunker as Liam's identity, no Claude trailers, do not push. Report: `dev-mac:~/video-work/solana-bunker/out/opening-v5.mp4`, the stills listed above (local paths), the CNN alignment numbers, the mongering result, the alternate voice files, the mid-take cut in/out timestamps, and anything not followed as written.
