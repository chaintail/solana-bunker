# Solana Bunker film master v2

The ten v2 scene masters (music treatment rollout, Conspiracy v13, credits v9) joined into one film with hard cuts. The audio is mastered once over the whole film. The method is unchanged from v1 (`film-master-v1.md`).

- Script: `apps/web/film/pipeline/stitch-v2.sh` (runs on dev-mac with ffmpeg-full; work dir `~/video-work/solana-bunker/film/master-v2/`)
- Outputs:
  - `solana-bunker-film-v2.mp4`: 1280x720, 30 fps, H.264 crf 18 preset slow, yuv420p, faststart, AAC-LC mono 48 kHz 192k. Size 176,574,854 bytes, sha256 `39864c18583b4207c41a22f17d6ccd74363e2b7129193a1dfc151004431ef684`.
  - `solana-bunker-film-v2-phone.mp4`: 960x540, crf 26 preset medium, same audio. Size 29,569,063 bytes, sha256 `079ec88a61135c9e6373e6f1b1828a8ce3b042bde199c5fb65ada0408fd5923e`.
- Runtime: **07:02.400** (422.400 s), **12,672 frames**, 20,275,200 audio samples (both outputs decode to exactly 12,672 x 1600).

## Scene masters

| # | File | sha256 (first 16) | Frames | Duration | First film frame | Audio fit |
|---|---|---|---|---|---|---|
| 1 | out/opening-m2.mp4 | ce0df0971a0f9378 | 1637 | 54.567 s | 0 | +2 samples trimmed |
| 2 | out/conspiracy-v13.mp4 | 46e4c1e25525a91a | 1660 | 55.333 s | 1637 | -2 samples padded |
| 3 | out/s04-m2.mp4 | 1077bf72d22ddef4 | 1395 | 46.500 s | 3297 | exact |
| 4 | out/s05-m2.mp4 | d2b471fa85af4951 | 2287 | 76.233 s | 4692 | exact |
| 5 | s06/out/s06-m2.mp4 | 4ebde4ab3aa3aa4e | 663 | 22.100 s | 6979 | exact |
| 6 | s07/out/s07-m2.mp4 | de86fdd4e775cdb4 | 1000 | 33.333 s | 7642 | exact |
| 7 | s08/out/s08-v8-x12.mp4 | 73c5b3aa73c3cc8b | 1059 | 35.300 s | 8642 | exact |
| 8 | s09/out/s09-m2.mp4 | 98960de3a5ac6999 | 897 | 29.900 s | 9701 | exact |
| 9 | s10/out/s10-m2.mp4 | 21fae5358d5a65c4 | 835 | 27.833 s | 10598 | exact |
| 10 | s11/out/s11-v9.mp4 | 18a5e7b1c1e1ce8b | 1239 | 41.300 s | 11433 | exact |
| | **Total** | | **12,672** | **422.400 s** | | |

Scene 7 (Arcade) is unchanged from v1. Against v1 the film is 99 frames (3.300 s) shorter: Conspiracy -113 frames, closing card +14 (s11-v9 is 1239 vs 1225).

## Method

Identical to v1: per-scene audio fitted to frames x 1600 samples and concatenated; one linear gain (+0.14 dB, from -16.14 LUFS) to -16.0 LUFS; 4x-oversampled `alimiter` at -1.3 dB; all ten pictures decoded once, hard cuts, master and phone encoded from the same decode with the mastered audio as AAC 192k. There are no crossfades in the pipeline; the joins are cuts.

## Verification

- Both outputs: 12,672 decoded frames at 30/1 fps, video and audio duration 422.400 s.
- Joins contact sheet (frames s-2 to s+1 at each of the nine joins): `solana-bunker-film-v2-joins.png` in the composer outbox. Joins at film frames 1637, 3297, 4692, 6979, 7642, 8642, 9701, 10598, 11433. No join frame is black. Only the contact sheet was inspected; the v1 glitch scan, frame-offset PSNR and audio-step checks were not rerun for v2.
- Transcript: `solana-bunker-film-v2-transcript.txt` (faster-whisper small int8, local).

### Loudness

| | Integrated | True peak | LRA |
|---|---|---|---|
| Film before mastering | -16.14 LUFS | -0.9 dBTP | 4.4 LU |
| Mastered PCM | -16.0 LUFS | -1.3 dBTP | n/a |
| `solana-bunker-film-v2.mp4` | **-16.01 LUFS** | **-1.24 dBTP** | 4.40 LU |
| `solana-bunker-film-v2-phone.mp4` | **-16.01 LUFS** | **-1.24 dBTP** | 4.40 LU |

Per scene, before to after mastering (ebur128; short-term is 3 s windows):

| Scene | Integrated | Short-term max | Short-term median | True peak |
|---|---|---|---|---|
| Opening | -16.0 to -15.9 | -14.7 to -14.6 | -16.4 to -16.2 | -1.6 to -1.4 |
| Conspiracy | -16.0 to -15.8 | -14.2 to -14.1 | -16.2 to -16.0 | -1.5 to -1.4 |
| Bunker | -16.0 to -15.9 | -14.0 to -13.9 | -16.3 to -16.1 | -1.5 to -1.4 |
| Whiteboard | -16.0 to -15.9 | -14.2 to -14.0 | -16.5 to -16.3 | -1.3 to -1.3 |
| Speakeasy | -16.0 to -15.9 | -14.3 to -14.1 | -16.2 to -16.0 | -1.5 to -1.4 |
| Seminar | -16.1 to -15.9 | -14.9 to -14.7 | -16.6 to -16.4 | -1.5 to -1.3 |
| Arcade | -16.2 to -16.2 | -15.1 to -15.1 | -16.6 to -16.6 | -0.9 to -1.3 |
| Infomercial | -16.0 to -15.9 | -14.4 to -14.2 | -16.0 to -15.8 | -1.5 to -1.4 |
| Sign-off | -16.0 to -15.9 | -14.7 to -14.5 | -15.9 to -15.7 | -1.5 to -1.4 |
| Closing card | -19.0 to -18.8 | -15.7 to -15.6 | -21.8 to -21.7 | -1.9 to -1.8 |

## Chapters

| Start | Chapter |
|---|---|
| 00:00 | Opening |
| 00:54 | Conspiracy |
| 01:49 | Bunker |
| 02:36 | Whiteboard |
| 03:52 | Speakeasy |
| 04:14 | Seminar |
| 04:48 | Arcade |
| 05:23 | Infomercial |
| 05:53 | Sign-off |
| 06:21 | Closing card |

Total runtime 07:02.4.
