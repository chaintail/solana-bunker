# Solana Bunker film master v3

The ten v3 scene masters (music through every scene, news bed fades, credits groove, whiteboard handoff fix) joined into one film with hard cuts. The audio is mastered once over the whole film. The method is unchanged from v1 and v2 (`film-master-v1.md`, `film-master-v2.md`).

- Script: `apps/web/film/pipeline/stitch-v3.sh` (runs on dev-mac with ffmpeg-full; work dir `~/video-work/solana-bunker/film/master-v3/`)
- Outputs:
  - `solana-bunker-film-v3.mp4`: 1280x720, 30 fps, H.264 crf 18 preset slow, yuv420p, faststart, AAC-LC mono 48 kHz 192k. Size 176,577,842 bytes, sha256 `4608d9c4436ef7de34903e1a7256e674e8e7b22e4cf79265a4a881e62a4a2ccf`.
  - `solana-bunker-film-v3-phone.mp4`: 960x540, crf 26 preset medium, same audio. Size 29,605,574 bytes, sha256 `382f38964caf612e6a9694907a609c8700af02ec45eb812596fe64b4e7d57087`.
- Runtime: **07:02.400** (422.400 s), **12,672 frames**, 20,275,200 audio samples (both outputs decode to exactly 12,672 x 1600). Every scene has the same frame count as in v2, so the total and all chapter times are unchanged from v2.

## Scene masters

| # | File | sha256 (first 16) | Frames | Duration | First film frame | Audio fit |
|---|---|---|---|---|---|---|
| 1 | out/opening-m3.mp4 | 4272b97cd5ed918d | 1637 | 54.567 s | 0 | +2 samples trimmed |
| 2 | out/conspiracy-v13.mp4 | 46e4c1e25525a91a | 1660 | 55.333 s | 1637 | -2 samples padded |
| 3 | out/s04-m2.mp4 | 1077bf72d22ddef4 | 1395 | 46.500 s | 3297 | exact |
| 4 | out/s05-m3.mp4 | 35dad1ce3d2bac2f | 2287 | 76.233 s | 4692 | exact |
| 5 | s06/out/s06-m3.mp4 | e38174a637cdcf05 | 663 | 22.100 s | 6979 | exact |
| 6 | s07/out/s07-m3.mp4 | 6fdfeb523da0310c | 1000 | 33.333 s | 7642 | exact |
| 7 | s08/out/s08-v8-x12.mp4 | 73c5b3aa73c3cc8b | 1059 | 35.300 s | 8642 | exact |
| 8 | s09/out/s09-m2.mp4 | 98960de3a5ac6999 | 897 | 29.900 s | 9701 | exact |
| 9 | s10/out/s10-m3.mp4 | 92dbe5d4c0679e81 | 835 | 27.833 s | 10598 | exact |
| 10 | s11/out/s11-v11.mp4 | 6cdbbc90fb42b3aa | 1239 | 41.300 s | 11433 | exact |
| | **Total** | | **12,672** | **422.400 s** | | |

### Changes against v2

1. Opening: opening-m2 to opening-m3 (music through the scene); same 1637 frames.
2. Conspiracy: unchanged file (conspiracy-v13, same sha as v2).
3. Bunker: unchanged file (s04-m2, same sha as v2).
4. Whiteboard: s05-m2 to s05-m3 (whiteboard handoff fix); same 2287 frames.
5. Speakeasy: s06-m2 to s06-m3; same 663 frames.
6. Seminar: s07-m2 to s07-m3; same 1000 frames.
7. Arcade: unchanged file (s08-v8-x12, same sha as v1 and v2).
8. Infomercial: unchanged file (s09-m2, same sha as v2).
9. Sign-off: s10-m2 to s10-m3; same 835 frames.
10. Closing card: s11-v9 to s11-v11 (credits groove); same 1239 frames.

The per-scene one-liners record which file changed; the brief names the film-level changes (music through every scene, news bed fades, credits groove, whiteboard handoff fix) but the per-scene assignment of music and news bed changes beyond the whiteboard and credits scenes was not inspected here.

## Method

Identical to v2: per-scene audio fitted to frames x 1600 samples and concatenated; one linear gain (+0.30 dB, from -16.30 LUFS) to -16.0 LUFS; 4x-oversampled `alimiter` at -1.3 dB; all ten pictures decoded once, hard cuts, master and phone encoded from the same decode with the mastered audio as AAC 192k.

## Verification

- Both outputs: 12,672 decoded frames at 30/1 fps, video and audio duration 422.400 s, 20,275,200 decoded audio samples.
- Joins contact sheet (frames s-2 to s+1 at each of the nine joins, from the phone file): `solana-bunker-film-v3-joins.png` in the composer outbox. Joins at film frames 1637, 3297, 4692, 6979, 7642, 8642, 9701, 10598, 11433. No join frame is black. Only the contact sheet was inspected; the v1 glitch scan, frame-offset PSNR and audio-step checks were not rerun.
- Transcript: `solana-bunker-film-v3-transcript.txt` (faster-whisper small int8, local).

### Loudness

| | Integrated | True peak | LRA |
|---|---|---|---|
| Film before mastering | -16.30 LUFS | -0.9 dBTP | 4.2 LU |
| Mastered PCM | -16.0 LUFS | -1.3 dBTP | n/a |
| `solana-bunker-film-v3.mp4` | **-16.02 LUFS** | **-1.23 dBTP** | 4.30 LU |
| `solana-bunker-film-v3-phone.mp4` | **-16.02 LUFS** | **-1.23 dBTP** | 4.30 LU |

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
