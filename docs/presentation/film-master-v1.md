# Solana Bunker film master v1

The ten scene masters joined into one film with hard cuts. The audio is mastered once over the whole film.

- Script: `apps/web/film/pipeline/stitch-v1.sh` (runs on dev-mac with ffmpeg-full 9.0.1; work dir `~/video-work/solana-bunker/film/master-v1/`)
- Outputs:
  - `solana-bunker-film-v1.mp4`: 1280x720, 30 fps, H.264 High crf 18 preset slow, yuv420p, faststart, AAC-LC mono 48 kHz 192k. Size 176,979,913 bytes, sha256 `dfe4703e4791ff3a4c568797ae369b916c0cb9d434a5afa6bf085c51e8850537`.
  - `solana-bunker-film-v1-phone.mp4`: 960x540, crf 26 preset medium, otherwise the same, with the same audio. Size 29,622,469 bytes, sha256 `7dcf8a2ddb13163a0b3e8a1eebe9d5a83dc17627286e89b6a00e34dbf699fdd8`.
- Runtime: **07:05.700** (425.700 s), **12,771 frames**, 20,433,600 audio samples.

## Scene masters

Every scene is 1280x720, 30/1 fps (r and avg), yuv420p, progressive H.264 High, with AAC-LC mono 48 kHz audio. Frame counts come from a full decode (`ffprobe -count_frames`). The SAR is N/A on scenes 1-4 and 1:1 on scenes 5-10. The concat sets every input to `setsar=1`, which changes no pixels. The audio fit is the decoded sample count minus frames x 1600.

| # | File | sha256 (first 16) | Frames | Duration | First film frame | Audio fit |
|---|---|---|---|---|---|---|
| 1 | out/opening-v11.mp4 | 5ad1e343576c691b | 1637 | 54.567 s | 0 | +2 samples (0.042 ms) trimmed |
| 2 | out/conspiracy-m1.mp4 | d5ba4dd2b524e851 | 1773 | 59.100 s | 1637 | exact |
| 3 | out/s04-m1.mp4 | 01e54c3f01a84df0 | 1395 | 46.500 s | 3410 | exact |
| 4 | out/s05-m1.mp4 | c5011524187d1c4a | 2287 | 76.233 s | 4805 | exact |
| 5 | s06/out/s06-m1.mp4 | d5a34d679b29b8bb | 663 | 22.100 s | 7092 | exact |
| 6 | s07/out/s07-m1.mp4 | fb12899cd4c7b08f | 1000 | 33.333 s | 7755 | exact |
| 7 | s08/out/s08-v8-x12.mp4 | 73c5b3aa73c3cc8b | 1059 | 35.300 s | 8755 | exact |
| 8 | s09/out/s09-m1.mp4 | 19d058f892f31a95 | 897 | 29.900 s | 9814 | exact |
| 9 | s10/out/s10-m1.mp4 | e6e6e0d751f658d1 | 835 | 27.833 s | 10711 | -2 samples (0.042 ms) padded |
| 10 | s11/out/s11-v8.mp4 | ca919d1146fb1f1d | 1225 | 40.833 s | 11546 | -2 samples (0.042 ms) padded |
| | **Total** | | **12,771** | **425.700 s** | | |

The dev-mac copies are byte-identical to the composer outbox copies (sha256 compared).

## Method

1. **Audio.** Each scene's AAC is decoded to 32-bit float PCM and fitted to exactly frames x 1600 samples (at most 2 samples changed). The ten files are then concatenated with the concat demuxer. The output sample count is checked against 12,771 x 1600.
2. **Mastering.** The whole film measures -16.15 LUFS integrated and -0.06 dBTP (loudnorm analysis). One linear gain of +0.15 dB is applied. Then a lookahead limiter runs at 4x oversampling (192 kHz, soxr): `alimiter`, ceiling -1.3 dB, attack 5 ms, release 50 ms, auto-level off, latency compensation on. The audio is resampled back to 48 kHz. Scenes are not normalised individually.
   - The ceiling is -1.3 rather than -1.0 because AAC encoding raises true peak. At a -1.0 ceiling the 192k master measured -0.88 dBTP, and a 128k phone track measured -0.86 dBTP on the Arcade square-wave score. The -1.3 ceiling and 192k on both files put both deliverables at -1.23 dBTP.
   - The limiter output is aligned with its input at lag 0 samples in every scene (cross-correlation, ±200 samples). It reduced gain in 1,639 of 42,570 10 ms blocks.
3. **Picture.** All ten scenes are decoded in one ffmpeg process and passed through `setsar=1` and the `concat` filter (hard cuts), then split. The master is libx264 crf 18 preset slow. The phone cut is `scale=960:540`, libx264 crf 26 preset medium, the settings the scene phone cuts used. Both are encoded once from the same decode, with no lossy intermediate, and muxed with the mastered PCM encoded to AAC 192k.

## Verification

### Frame count and alignment
- Both outputs decode to 12,771 frames at 30/1 fps, the sum of the scene frame counts. Video and audio durations are both 425.700 s, and the decoded audio is 20,433,600 samples.
- Every master frame was compared with every source frame (160x90 grey PSNR) at offsets -2 to +2 per scene. Offset 0 wins in all ten scenes by at least 10 dB of mean PSNR. At offset 0 the worst frame in the film is 46.5 dB and no frame is below 35 dB. No frame is dropped, duplicated or shifted.

### Picture joins
The contact sheet shows frames s-2, s-1, s and s+1 at each join (`solana-bunker-film-v1-joins.png` in the composer outbox).

| Join | Cut | Film frame | Time | Type | Result |
|---|---|---|---|---|---|
| 1 | Opening → Conspiracy | 1637 | 54.567 s | hard cut | SPECIAL REPORT card → dark green opening of Conspiracy (designed) |
| 2 | Conspiracy → Bunker | 3410 | 113.667 s | hard cut | CLASSIFIED folder → the same folder at the Bunker framing |
| 3 | Bunker → Whiteboard | 4805 | 160.167 s | continuous | crossfade baked into s05; same blueprint pose either side |
| 4 | Whiteboard → Speakeasy | 7092 | 236.400 s | continuous | s06 frame 0 equals s05's last frame (designed hold) |
| 5 | Speakeasy → Seminar | 7755 | 258.500 s | hard cut | REJECTED stamp → REJECTED stamp in the Seminar framing |
| 6 | Seminar → Arcade | 8755 | 291.833 s | hard cut | alley → Arcade's opening alley frame |
| 7 | Arcade → Infomercial | 9814 | 327.133 s | hard cut | arcade cabinet → dimmed cabinet at the head of the Infomercial |
| 8 | Infomercial → Sign-off | 10711 | 357.033 s | hard cut | Infomercial board → Sign-off's opening frame |
| 9 | Sign-off → Closing card | 11546 | 384.867 s | continuous | s11 frame 0 equals s10's last frame (designed) |

No join frame is black; the lowest mean luma at any join is 18.4 of 255, the dark alley at frame 8755. The only duplicate frames across a cut are the two designed ones (joins 4 and 9).

### Glitch scan
Scanner: `apps/web/film/scripts/glitch-scan.py` v2, the film/conspiracy copy. It was run over the master with the nine join frames as chunk starts.
- All nine chunk starts are clean.
- It flags 10 frames, all inside scenes. Nine reproduce on the source scene masters at the same scene frame with the same numbers: Conspiracy 64, 629, 1421 and 1758; Seminar 3, 605 and 679; Arcade 252; Infomercial 411. The tenth, Infomercial 456 (film 10270), has the same jumps in the source. It only passes the bar in the film scan, because the film's median difference (0.50) is lower than the Infomercial scene's (2.47).
- Looked at, the flags are designed motion: stamp and folder bumps, the CENSORED stamp landing, the Seminar lamp flicker behind the REJECTED stamp (film 7758, a full-frame bright frame between two dark ones), whiteboard jitter, an arcade bounce, and the dramatization and BIP-39 card bounces.
- The stitch introduced none of them.

### Audio joins
For each join: the sample step at the boundary, compared with the largest step within ±100 ms. Measured on the PCM master and again on the AAC decode of the delivered master, with the same result.

| Join | Boundary step | Neighbour max | Neighbour p99 |
|---|---|---|---|
| 1 Opening → Conspiracy | 0.0002 | 0.0018 | 0.0012 |
| 2 Conspiracy → Bunker | 0.0000 | 0.0014 | 0.0006 |
| 3 Bunker → Whiteboard (one music cue) | 0.0004 | 0.0054 | 0.0031 |
| 4 Whiteboard → Speakeasy | 0.0000 | 0.0000 | 0.0000 |
| 5 Speakeasy → Seminar | 0.0000 | 0.0000 | 0.0000 |
| 6 Seminar → Arcade | 0.0000 | 0.0022 | 0.0011 |
| 7 Arcade → Infomercial | 0.0000 | 0.0063 | 0.0015 |
| 8 Infomercial → Sign-off | 0.0000 | 0.0126 | 0.0044 |
| 9 Sign-off → Closing card | 0.0000 | 0.0054 | 0.0033 |

No boundary step exceeds its neighbourhood, so there is no click. Plotted ±100 ms around each join, every waveform crosses the cut without a step. The s04→s05 cue is continuous at sample level (±5 ms plot).

The stitch adds no samples. Joins 1, 2, 5, 6, 7 and 9 have low-level heads or tails (below -60 dBFS for 90-200 ms) that are part of the scene mixes themselves.

**Speech at the cuts.** faster-whisper small int8 was run on the master with word timestamps. No word straddles any of the nine cuts. The nearest words are:
- join 4: "All" starts 0.12 s after the cut
- join 5: "And" starts 0.26 s after
- join 9: "lab." ends 0.39 s before
- join 1: "Report" ends 0.51 s before
- join 2: "conclusions." ends 0.73 s before
- join 3: "last." ends 0.45 s before, and "So" starts 0.19 s after

Joins 6, 7 and 8 have no word within 1 s. The transcript is `solana-bunker-film-v1-transcript.txt` in the composer outbox.

### Loudness

| | Integrated | True peak | LRA |
|---|---|---|---|
| Film before mastering | -16.15 LUFS | -0.06 dBTP | 4.8 LU |
| Mastered PCM | -16.05 LUFS | -1.30 dBTP | 4.7 LU |
| `solana-bunker-film-v1.mp4` | **-16.05 LUFS** | **-1.23 dBTP** | 4.7 LU |
| `solana-bunker-film-v1-phone.mp4` | **-16.05 LUFS** | **-1.23 dBTP** | 4.7 LU |

Per scene, before → after mastering (ebur128 on each scene's samples). Short-term values are 3 s windows. The median ignores values below -70 LUFS.

| Scene | Integrated | Short-term max | Short-term median | True peak | Limiter max reduction |
|---|---|---|---|---|---|
| Opening | -16.0 → -15.8 | -15.1 → -15.0 | -16.8 → -16.6 | -1.4 → -1.3 | 0.06 dB |
| Conspiracy | -16.0 → -15.9 | -14.6 → -14.5 | -16.9 → -16.9 | -1.0 → -1.3 | 0.49 dB |
| Bunker | -16.0 → -15.9 | -14.4 → -14.4 | -16.9 → -16.8 | -0.8 → -1.3 | 0.68 dB |
| Whiteboard | -16.0 → -15.9 | -14.5 → -14.4 | -16.9 → -16.9 | -0.3 → -1.3 | 1.20 dB |
| Speakeasy | -16.0 → -15.9 | -14.6 → -14.4 | -16.7 → -16.6 | -1.8 → -1.7 | none |
| Seminar | -16.0 → -15.9 | -14.9 → -14.9 | -16.7 → -16.6 | -0.1 → -1.3 | 1.39 dB |
| Arcade | -16.2 → -16.2 | -15.1 → -15.1 | -16.6 → -16.6 | -0.9 → -1.3 | 0.53 dB |
| Infomercial | -16.0 → -15.9 | -14.6 → -14.5 | -16.5 → -16.3 | -1.8 → -1.7 | none |
| Sign-off | -16.0 → -15.9 | -14.9 → -14.8 | -16.2 → -16.1 | -1.9 → -1.7 | none |
| Closing card | -19.0 → -18.9 | -15.7 → -15.6 | -21.5 → -21.4 | -1.9 → -1.8 | none |

Every scene moves by the +0.15 dB gain, within the 0.1 LU rounding. Only Arcade stays put: its limiting offsets the gain. The closing card stays about 3 LU quieter, as designed.

### Closing card
All three QR codes decode from master frame 12300 (410.000 s) with zxing-cpp:
- `https://github.com/chaintail/solana-bunker`
- `https://t.me/chaintail`
- `https://x.com/ChaintailLabs`

The film's last frame is the "Product of Chaintail Labs" card at its fade.

## Chapters

| Start | Chapter |
|---|---|
| 00:00 | Opening |
| 00:54 | Conspiracy |
| 01:53 | Bunker |
| 02:40 | Whiteboard |
| 03:56 | Speakeasy |
| 04:18 | Seminar |
| 04:51 | Arcade |
| 05:27 | Infomercial |
| 05:57 | Sign-off |
| 06:24 | Closing card |

Total runtime 07:05.7.
