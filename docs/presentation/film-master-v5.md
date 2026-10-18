# Solana Bunker film master v5

V5 adds a 15-frame, 0.500-second poster with silence before the complete v4 film. The ten v4 scene masters, their order, and scene content are unchanged. The source repository starts at `41a909beb40a2a228c35aa2f8c80faa2e826aa0c` on `film/master`.

All media generation and validation runs on **dev-mac**. No ffmpeg or ffprobe runs on do-box. The output directory is `~/video-work/solana-bunker/film/master-v5/` on dev-mac.

## Master and phone outputs

- `solana-bunker-film-v5.mp4`: 176,647,168 bytes; SHA-256 `cea576b2c0250eb81ad3e012c734562b14c51efbd06fb0d31b0544a708eeb66c`.
- `solana-bunker-film-v5-phone.mp4`: 29,711,754 bytes; SHA-256 `1ff6c04caa66c10088b402c00298933644e251924024f1cc8ece2bfed167a139`.

The final video streams are limited-range `yuv420p` (`color_range=tv`). The poster encode explicitly converts its JPEG input to limited range before concatenation so the existing v4 picture keeps its intended range metadata.

## Reproduce

- `apps/web/film/pipeline/stitch-v5.sh` builds and validates the poster, master and phone outputs.
- `apps/web/film/pipeline/deliver-v5.sh` produces the web MP4 and HLS package and writes `rep/delivery-v5.json`. Its default steps are `web cover hls measure`; steps can also run individually.
- The chapter source is the measured v4 `rep/source-metadata.json`. Composer outbox `chapters-v5.md` records exact decimal starts and the publishable list.

The stitch script requires these exact completed v4 inputs under `film/master-v4/`, plus `rep/scenes.tsv` and the unchanged ten source scenes:

| Required file | SHA-256 |
|---|---|
| `solana-bunker-film-v4-nocover.mp4` | `ac58bee6f67adb2a3a004715337390e36f10ca59eb62025e47a0cd78e25c52a3` |
| `solana-bunker-film-v4-phone-nocover.mp4` | `575e881a1a69c7a8d07d72f5cb73b4ee670ec03f5776f33b503bb9502ee206c6` |
| `aud/film-master.wav` | `cea5acd6315c70b46e5d5dffb7bdd0712ab0a8dcb2473097c2836657316537d8` |

`stitch-v4.sh` originally writes unsuffixed master/phone names. The existing `-nocover.mp4` copies are the original no-artwork v4 files and match the v4 published SHA-256 values above; v5 expects those exact names and checks their hashes before processing. For a fresh v4 reproduction, retain copies under these names before adding artwork or replacing delivery files.

The master picture prepends the encoded poster to the existing completed v4 picture using stream copy. Audio prepends exactly 24,000 zero PCM samples to the unchanged v4 mastered PCM, then encodes AAC 192k once. There is no new per-scene mastering. The PCM prefix is exactly zero; decoded AAC master/phone prefixes have numerical leakage with a measured peak of -122.617319 dBFS (`stitch-evidence/aac-prefix.json`), so encoded AAC is not claimed to decode to literal zeros. Exact runtime is **07:01.200** (421.200 seconds), **12,636 frames** at 30 fps, and **20,217,600 audio samples** at 48 kHz.

The web encode retains v4 settings: 1280x720, 30 fps, H.264 High Level 3.1, yuv420p, CRF 20 preset slow, maxrate 4000k / bufsize 8000k, x264 `qcomp=0:ratetol=0.1`, AAC 160k, and faststart. Fixed GOP is 60 frames with scene-cut keyframes disabled. A copy remux adds `poster.jpg` as an MJPEG `attached_pic` stream; encoded picture and audio stream MD5 values must match before and after the remux. Container inspection verifies that `moov` precedes `mdat`.

The HLS ladder retains v4 settings and uses CMAF-compatible fragmented MP4, 4-second segments, fixed 60-frame GOPs, and mono AAC 128k at 48 kHz in each rendition. Each has 106 segments: 105 x 4.000 seconds and one 1.200-second segment, totaling 421.200 seconds. The 720p rendition uses CRF 20 / maxrate 3500k / bufsize 7000k; 480p uses CRF 22 / 1600k / 3200k; 360p uses CRF 23 / 800k / 1600k. H.264 levels are High 3.1, High 3.1 and High 3.0 respectively.

The delivery validator checks all master-playlist rendition references, all 318 media-segment references and three init references, rendition dimensions/profiles, CMAF brands, frame counts, 2-second keyframe spacing, and duration sums. It also decodes the complete AAC audio path for each rendition. Master `BANDWIDTH` rounds the measured RFC 8216 peak segment rate, including audio and mux bytes, up to the next 1000 bit/s.

## Chapters

Starts use cumulative measured v4 video-stream durations plus 0.500 seconds; mm:ss display is floored. Opening starts at 00:00 for YouTube and includes the poster. Source duration rounding produces a cumulative 421.199999 seconds; the exact frame-based runtime is 421.200 seconds.

| Start | Chapter | Scene starts at seconds |
|---|---|---|
| 00:00 | Opening | 0.500000 |
| 00:55 | Conspiracy | 55.066667 |
| 01:50 | Bunker | 110.400000 |
| 02:36 | Whiteboard | 156.900000 |
| 03:51 | Speakeasy | 231.433333 |
| 04:13 | Seminar | 253.533333 |
| 04:46 | Arcade | 286.866666 |
| 05:22 | Infomercial | 322.166666 |
| 05:52 | Sign-off | 352.066666 |
| 06:19 | Closing card | 379.899999 |

## Measured validation

Final validation ran on dev-mac (Darwin), with ffmpeg and ffprobe 9.0.1. The master and phone each contain 12,636 picture frames, 421.200-second video/audio/container durations, and exactly 20,217,600 decoded AAC samples. Both include the poster as an MJPEG `attached_pic` stream; adding artwork preserved encoded picture and audio MD5 values.

`rep/stitch-v5.json` records byte-identical v4 mastered PCM after the 24,000-sample zero prefix, and matching decoded hashes for all 12,621 existing v4 picture frames in each corresponding output. The first 15 frames are a repeated poster. Master frame-zero PSNR against the supplied poster is **48.086545 dB**, above 40 dB. Phone poster PSNR is **39.800462 dB** at the unchanged CRF 26 setting; the 40 dB acceptance threshold applies to the master.

| Output | Integrated loudness | True peak | LRA |
|---|---|---|---|
| Master | -16.02 LUFS | -1.15 dBTP | 4.10 LU |
| Phone | -16.02 LUFS | -1.15 dBTP | 4.10 LU |

### Web MP4

`solana-bunker-film-v5-web.mp4` is **90,900,778 bytes**, SHA-256 `f37e650079bb42346e7766557a6c302e48c4e92f08156b57a21513ff59e50e99`. It has 12,636 frames and a 421.200-second video/container duration. Its 211 keyframes start at zero and are exactly 2.000 seconds apart.

- Average video bitrate: **1,554,584 bit/s**; container average: **1,726,510 bit/s**.
- Peak video bitrate in a one-second PTS bin: **4,509,880 bit/s** at second 82, below 5,000,000 bit/s. Bins sum video packet bytes by floor(PTS); the final partial second is not extrapolated.
- Copy-remux A/V stream MD5 values match before and after artwork: video `f00e9294c10e1ff8d9b90d6dccbbae4e`, audio `a6a0358beb20448b6df5647424791b23`.
- Artwork is 1280x720 MJPEG with `attached_pic=1`; main video is limited-range yuv420p with `attached_pic=0`. Faststart box order passed.

### HLS ladder

| Rendition | Average muxed segment bit/s | Peak segment bit/s | Master BANDWIDTH |
|---|---|---|---|
| 1280x720 | 1,932,677 | 4,301,223 | 4,302,000 |
| 854x480 | 779,988 | 1,856,687 | 1,857,000 |
| 640x360 | 491,318 | 1,016,679 | 1,017,000 |

The complete package is **325 files / 168,705,624 bytes**: 318 `.m4s` segments, three init MP4s, three rendition playlists, and one master playlist. Every rendition has 12,636 frames and 2.000-second keyframe spacing. The first HLS keyframe PTS is 0.066667 seconds due to mux timestamp offset; segment-duration sums are 421.200000 seconds. All playlist references and complete AAC decode paths passed.

Evidence on dev-mac under `film/master-v5/rep/` includes `stitch-v5.json`, `delivery-v5.json`, `delivery-v5-final-measure.log`, `web-readiness-v5.json`, `web-av-before-cover.md5`, and `web-av-after-cover.md5`. Initial full-range poster outputs were rejected and replaced; their measurements are segregated under `rep/rejected-full-range/` and are not the final results above.

### Delivery script reproduction

Final `deliver-v5.sh` SHA-256 is `5ee57f7dd5c79f3ea6ac24895fa25164898bf5c0a09f62173e600f3f67be9b40`. The source tree was based on commit `41a909beb40a2a228c35aa2f8c80faa2e826aa0c`; the publication report records the final integrated commit.

The configured `~/video-work` path resolves to VM shared storage. Initial full-length web encodes returned success but immediate readers reported a missing `moov` atom; later readers accepted the same files. Short shared/local controls passed, so the underlying delayed-visibility cause was not established. The final script completes web encoding and artwork remuxing on local APFS under `/private/tmp`, validates the local MP4 streams and faststart order, then copies completed files with `fsync` and verifies source, staged-copy, and destination SHA-256 values. It waits for each foreground ffmpeg command to finish and uses no readiness retries.

The final script ran `web cover` successfully in `film/master-v5-repro-local/`, using the original v5 master and poster. Local and copied MP4 SHA-256 values both equal `3304945c2671572601b490eb7da0d4f0167d901836a2031b0c445d2d9395bfbf`; the reproduction has a 4,598,408 bit/s one-second peak, 12,636 frames, 421.200-second duration, 211 keyframes at 2.000-second intervals, and passing artwork/A/V MD5/faststart checks. The encoder reproduction is separately identified from the published MP4; no byte-identical re-encode claim is made. `rep/final-script-repro-v5.json` records the exact script hash, master hash, local/shared filesystems and copied output hashes. The same final script then ran `measure` against the unchanged published web and HLS files and passed every delivery check.

## Publication

- Master: https://media.claude.do/solana-bunker/solana-bunker-film-v5.mp4
- Web MP4: https://media.claude.do/solana-bunker/solana-bunker-film-v5-web.mp4
- HLS master: https://media.claude.do/solana-bunker/v5/hls/master.m3u8
- YouTube, unlisted: https://www.youtube.com/watch?v=74TAs5p3ls4
- Private master: https://shared.claude.do/private/solana-bunker-film-v5-20261018-125238.mp4

Direct observed HEAD requests to all three public master/web/HLS URLs returned HTTP 200, `Accept-Ranges: bytes`, and one-year public cache headers. Master and web report `video/mp4` with Content-Length 176647168 and 90900778 respectively. The HLS master reports `application/vnd.apple.mpegurl` with Content-Length 490. All 325 HLS objects were uploaded and individually verified. The YouTube upload is unlisted; no custom thumbnail was supplied. V4 publications remain unchanged.

Durable publication evidence is in composer outbox `solana-bunker-film-v5-publish/`, including `final-public-head.json`, `publication-report.json`, R2 object reports, YouTube verification, private-share response, delivery measurements and stitch evidence. The measured chapter list is also available separately as composer outbox `chapters-v5.md`.
