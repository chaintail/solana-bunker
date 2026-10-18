# Solana Bunker film master v4

The ten scene masters joined into one film with hard cuts. Compared with v3, only the whiteboard source changes: `out/s05-m3.mp4` becomes `out/s05-v10.mp4`. The other nine source files retain their v3 SHA-256 hashes. The audio is mastered once over the whole film, using the unchanged v3 workflow.

- Script: `apps/web/film/pipeline/stitch-v4.sh` (runs on dev-mac with ffmpeg-full; work dir `~/video-work/solana-bunker/film/master-v4/`)
- Base: clean `film/master` at `634953f`.
- Outputs:
  - `solana-bunker-film-v4.mp4`: 1280x720, 30 fps, H.264 CRF 18 preset slow, yuv420p, faststart, AAC-LC mono 48 kHz 192k. Size 176,376,527 bytes, SHA-256 `ac58bee6f67adb2a3a004715337390e36f10ca59eb62025e47a0cd78e25c52a3`.
  - `solana-bunker-film-v4-phone.mp4`: 960x540, CRF 26 preset medium, same audio. Size 29,537,308 bytes, SHA-256 `575e881a1a69c7a8d07d72f5cb73b4ee670ec03f5776f33b503bb9502ee206c6`.
- Runtime: **07:00.700** (420.700 s), **12,621 frames**, 20,193,600 audio samples. Both encoded outputs decode to exactly 12,621 frames at 30/1 fps and 20,193,600 audio samples; video, audio, and container durations are 420.700 s.

## Scene masters

| # | File | sha256 (first 16) | Frames | Duration | First film frame | Audio fit |
|---|---|---|---|---|---|---|
| 1 | out/opening-m3.mp4 | 4272b97cd5ed918d | 1637 | 54.567 s | 0 | +2 samples trimmed |
| 2 | out/conspiracy-v13.mp4 | 46e4c1e25525a91a | 1660 | 55.333 s | 1637 | -2 samples padded |
| 3 | out/s04-m2.mp4 | 1077bf72d22ddef4 | 1395 | 46.500 s | 3297 | exact |
| 4 | out/s05-v10.mp4 | 17ac6e948e7cc112 | 2236 | 74.533 s | 4692 | exact |
| 5 | s06/out/s06-m3.mp4 | e38174a637cdcf05 | 663 | 22.100 s | 6928 | exact |
| 6 | s07/out/s07-m3.mp4 | 6fdfeb523da0310c | 1000 | 33.333 s | 7591 | exact |
| 7 | s08/out/s08-v8-x12.mp4 | 73c5b3aa73c3cc8b | 1059 | 35.300 s | 8591 | exact |
| 8 | s09/out/s09-m2.mp4 | 98960de3a5ac6999 | 897 | 29.900 s | 9650 | exact |
| 9 | s10/out/s10-m3.mp4 | 92dbe5d4c0679e81 | 835 | 27.833 s | 10547 | exact |
| 10 | s11/out/s11-v11.mp4 | 6cdbbc90fb42b3aa | 1239 | 41.300 s | 11382 | exact |
| | **Total** | | **12,621** | **420.700 s** | | |

### Changes against v3

Whiteboard changes from `s05-m3` (2,287 frames / 76.233 s) to `s05-v10` (2,236 frames / 74.533 s). The film is 51 frames (1.700 s) shorter. All chapter starts after Whiteboard move 1.700 s earlier; the first four chapter starts stay the same.

## Method

Identical to v3: per-scene audio fitted to frames x 1600 samples and concatenated; one linear gain (+0.30 dB, measured from -16.30 LUFS) to target -16.0 LUFS; 4x-oversampled `alimiter` at -1.3 dB; all ten pictures decoded once, hard cuts, master and phone encoded from the same decode with mastered audio as AAC 192k. Master uses H.264 CRF 18 preset slow at 1280x720. Phone uses CRF 26 preset medium at 960x540. Both use 30 fps, yuv420p, faststart, and mono 48 kHz AAC-LC.

## Verification

- All processing, frame counts, source probing, and loudness measurements ran on dev-mac. No ffmpeg or ffprobe ran on do-box.
- Both encoded outputs decode to exactly 12,621 frames at 30/1 fps and 20,193,600 audio samples; video, audio, and container durations are 420.700 s.
- Evidence: `~/video-work/solana-bunker/film/master-v4/rep/` on dev-mac. `source-metadata.json` records actual ffprobe video durations and full source SHA-256 hashes; `scenes.tsv` records decoded source frames and fitted audio sample counts; `out-*.txt` records encoded-output frame counts, duration, size, SHA-256, and loudness.
- The v3 contact sheet, transcript, glitch scan, frame-offset PSNR, and audio-step checks were not rerun for v4 by the stitch worker.

### Loudness

| | Integrated | True peak | LRA |
|---|---|---|---|
| Film before mastering | -16.30 LUFS | -0.92 dBTP | 4.10 LU |
| Mastered PCM | -16.02 LUFS | -1.30 dBTP | 4.10 LU |
| `solana-bunker-film-v4.mp4` | **-16.02 LUFS** | **-1.15 dBTP** | 4.10 LU |
| `solana-bunker-film-v4-phone.mp4` | **-16.02 LUFS** | **-1.15 dBTP** | 4.10 LU |

Per scene, before to after mastering (ebur128; short-term is 3 s windows):

| Scene | Integrated | Short-term max | Short-term median | True peak |
|---|---|---|---|---|
| Opening | -16.0 to -15.7 | -14.7 to -14.4 | -16.3 to -16.0 | -1.6 to -1.3 |
| Conspiracy | -16.0 to -15.7 | -14.2 to -13.9 | -16.2 to -15.9 | -1.5 to -1.3 |
| Bunker | -16.0 to -15.7 | -14.0 to -13.8 | -16.3 to -16.0 | -1.5 to -1.3 |
| Whiteboard | -16.0 to -15.7 | -14.1 to -13.8 | -16.3 to -16.0 | -1.3 to -1.3 |
| Speakeasy | -16.0 to -15.7 | -14.2 to -13.9 | -16.1 to -15.8 | -1.5 to -1.3 |
| Seminar | -16.0 to -15.7 | -14.8 to -14.5 | -16.4 to -16.1 | -1.5 to -1.3 |
| Arcade | -16.2 to -16.1 | -15.1 to -15.0 | -16.6 to -16.5 | -0.9 to -1.3 |
| Infomercial | -16.0 to -15.7 | -14.4 to -14.1 | -16.0 to -15.7 | -1.5 to -1.3 |
| Sign-off | -16.0 to -15.7 | -14.9 to -14.6 | -16.2 to -15.9 | -1.5 to -1.3 |
| Closing card | -19.2 to -18.9 | -15.5 to -15.2 | -20.9 to -20.6 | -1.9 to -1.6 |

## Chapters

Starts come from cumulative actual per-scene ffprobe video durations; mm:ss display is floored. Rounding of six-decimal stream durations can introduce a microsecond in the sum; exact frame-based runtime is 420.700 s.

| Start | Chapter |
|---|---|
| 00:00 | Opening |
| 00:54 | Conspiracy |
| 01:49 | Bunker |
| 02:36 | Whiteboard |
| 03:50 | Speakeasy |
| 04:13 | Seminar |
| 04:46 | Arcade |
| 05:21 | Infomercial |
| 05:51 | Sign-off |
| 06:19 | Closing card |

Total runtime 07:00.700. Full measured starts are also recorded in composer outbox `chapters-v4.md`.

## Delivery encodes

`apps/web/film/pipeline/deliver-v4.sh` runs on dev-mac after stitching. Final validation ran on dev-mac (Darwin), with ffmpeg and ffprobe 9.0.1. Both delivery encodes use the master SHA-256 recorded above.

### Web MP4

`solana-bunker-film-v4-web.mp4` is 1280x720, 30 fps, H.264 High Level 3.1, yuv420p, CRF 20 preset slow, VBV maxrate 4000k / bufsize 8000k, AAC 160k, and faststart. GOP is fixed at 60 frames with scene-cut keyframes disabled. The final file has 12,621 frames, runs 420.700 s, and contains 211 keyframes spaced exactly 2.000 s apart.

- Size: **90,215,123 bytes**; SHA-256 `c1bee5543e99350b1e92a85b9709c22a368fbc1924fb7be1d23ec78506c0a4b5`.
- Average video bitrate: **1,546,060 bit/s**; container average: **1,715,524 bit/s**.
- Peak video bitrate in a one-second PTS bin: **4,742,800 bit/s** at second 62, below the requested 5,500,000 bit/s ceiling. Bins sum video packet bytes by floor(PTS); the final partial second is not extrapolated.
- The first web encode with only the requested VBV settings measured 8,263,744 bit/s at second 94 and failed the ceiling. The final script retains CRF 20 / maxrate 4000k / bufsize 8000k and adds x264 `qcomp=0:ratetol=0.1`; the complete re-encode passed the measured ceiling. These results describe this file and measurement, without a claim about playback on every device or network.

### HLS ladder

The HLS VOD package uses CMAF-compatible fragmented MP4 (init compatible brands include `cmfc`), 4-second segments, fixed 60-frame GOPs, AAC 128k per rendition, relative references, and an independent-segments master playlist. Each rendition has 106 segments: 105 x 4.000 s plus one 0.700 s segment, totaling **420.700000 s**. All playlist references, stream profiles and dimensions, and duration sums passed validation.

| Rendition | H.264 level | CRF / maxrate / bufsize | Average muxed segment bit/s | Peak segment bit/s | Master BANDWIDTH |
|---|---|---|---|---|---|
| 1280x720 | High 3.1 | 20 / 3500k / 7000k | 1,911,529 | 4,195,151 | 4,196,000 |
| 854x480 | High 3.1 | 22 / 1600k / 3200k | 772,634 | 1,885,343 | 1,886,000 |
| 640x360 | High 3.0 | 23 / 800k / 1600k | 487,464 | 998,261 | 999,000 |

Master `BANDWIDTH` values round up the measured RFC 8216 peak segment rate, including mux and audio bytes, to the next 1000 bit/s. The 480p encode uses Level 3.1 because 854x480 at 30 fps exceeds Level 3.0's macroblock-rate limit. The complete package is **325 files / 166,803,895 bytes**: 318 `.m4s` segments, three init MP4s, three rendition playlists, and one master playlist.

## Publication

- Master: https://media.claude.do/solana-bunker/solana-bunker-film-v4.mp4
- Web MP4: https://media.claude.do/solana-bunker/solana-bunker-film-v4-web.mp4
- HLS master: https://media.claude.do/solana-bunker/v4/hls/master.m3u8
- YouTube (unlisted; `videos.list` confirmed): https://www.youtube.com/watch?v=TeB0ym4IPFk
- Private master: https://shared.claude.do/private/solana-bunker-film-v4-20261018-120045.mp4

Every public R2 object was checked with `curl -sI`: HTTP 200, `Accept-Ranges: bytes`, and one-year public cache headers. MP4s use `video/mp4`, `.m4s` segments use `video/iso.segment`, and playlists use `application/vnd.apple.mpegurl`.

YouTube accepted the master and confirmed unlisted privacy, then refused the supplied custom thumbnail. The uploader was not retried. Exact refusal:

```text
YouTube API HTTP 403: The authenticated user doesn't have permissions to upload and set custom video thumbnails.
Reasons: forbidden
```

The YouTube description uses the measured chapter list above, the repository URL, and the devnet program explorer URL. The supplied poster remains available locally; the API did not set it on the uploaded video.

Durable publication evidence is in the composer outbox under `solana-bunker-film-v4-publish/`: final delivery measurements, per-object R2 URL/header reports, YouTube response, private share response, and copied stitch measurements. The final publication report records the integrated commit and verified remote branch SHA. Original per-scene evidence remains on dev-mac under `~/video-work/solana-bunker/film/master-v4/rep/`.

**Tools.** Run from `apps/web`: `python3 film/scripts/glitch-scan-v2.py <video> [--chunk-starts N,M,...] [--chunk-size N] [--parts A,B,...] [--ref png|frame]... [--ref-db X] [--min-jump X] [--ignore F,F,...]` (NumPy, ffmpeg and ffprobe required; defaults: part `0`, reference threshold `30` dB, minimum jump `2.0`). For warm-up capture, use `node film/scripts/capture-v2.mjs <scene> [--layer=front|back] [--still=t,t,...] [--from=s] [--to=s] [--speed=f] [--out=dir]`; `--speed f` also works, defaults to `1`, and makes `--from`/`--to` output seconds. Set `CHROME` to the browser binary when needed. This helper discards two warm-up screenshots per page load and pins the final scaled frame to the scene's last frame; it lacks `--fresh`, so `capture.mjs` remains available alongside it. `glitch-scan.py` also remains as v1.
