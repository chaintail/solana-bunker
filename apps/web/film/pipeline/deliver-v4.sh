#!/usr/bin/env bash
# Run ON dev-mac after stitch-v4.sh. All media processing stays on that VM.
# Usage: deliver-v4.sh [web hls measure] (default: all three).
# ROOT/W/MASTER may be overridden; the default delivery directory is master-v4.
set -euo pipefail
[[ $(uname -s) == Darwin ]] || { echo 'Run this script on dev-mac.' >&2; exit 1; }
export PATH=/opt/homebrew/bin:$PATH
ROOT=${ROOT:-$HOME/video-work/solana-bunker}
W=${W:-$ROOT/film/master-v4}
MASTER=${MASTER:-$W/solana-bunker-film-v4.mp4}
WEB=$W/solana-bunker-film-v4-web.mp4
steps=${*:-web hls measure}
mkdir -p "$W/rep"
[[ -f $MASTER ]] || { echo "Master is not ready: $MASTER" >&2; exit 1; }
ff() { ffmpeg -nostdin -hide_banner -v warning -y "$@"; }

if [[ $steps == *web* ]]; then
  # Uniform complexity allocation suppresses 1-second bursts that VBV's 8 Mbit
  # reservoir otherwise permits, while retaining CRF20/maxrate4M/bufsize8M.
  ff -i "$MASTER" -map 0:v:0 -map 0:a:0 \
    -vf 'scale=1280:720,setsar=1' -r 30 \
    -c:v libx264 -preset slow -profile:v high -level:v 3.1 \
    -crf 20 -maxrate 4000k -bufsize 8000k -g 60 -keyint_min 60 -sc_threshold 0 \
    -pix_fmt yuv420p -x264-params 'qcomp=0:ratetol=0.1' \
    -c:a aac -b:a 160k -movflags +faststart "$WEB"
fi

if [[ $steps == *hls* ]]; then
  mkdir -p "$W/hls/720p" "$W/hls/480p" "$W/hls/360p"
  # Encode from the master once; fixed GOPs put segment cuts at exact 4 s boundaries.
  ff -i "$MASTER" \
    -filter_complex '[0:v]split=3[v720a][v480a][v360a];[v720a]scale=1280:720,setsar=1[v720];[v480a]scale=854:480,setsar=1[v480];[v360a]scale=640:360,setsar=1[v360]' \
    -map '[v720]' -map 0:a:0 -r 30 -c:v libx264 -preset slow -profile:v high -level:v 3.1 -crf 20 \
    -maxrate 3500k -bufsize 7000k -g 60 -keyint_min 60 -sc_threshold 0 -pix_fmt yuv420p \
    -c:a aac -b:a 128k -f hls -hls_time 4 -hls_playlist_type vod -hls_segment_type fmp4 \
    -hls_flags independent_segments -hls_segment_options movflags=+cmaf -hls_fmp4_init_filename init.mp4 \
    -hls_segment_filename "$W/hls/720p/segment_%03d.m4s" "$W/hls/720p/index.m3u8" \
    -map '[v480]' -map 0:a:0 -r 30 -c:v libx264 -preset slow -profile:v high -level:v 3.1 -crf 22 \
    -maxrate 1600k -bufsize 3200k -g 60 -keyint_min 60 -sc_threshold 0 -pix_fmt yuv420p \
    -c:a aac -b:a 128k -f hls -hls_time 4 -hls_playlist_type vod -hls_segment_type fmp4 \
    -hls_flags independent_segments -hls_segment_options movflags=+cmaf -hls_fmp4_init_filename init.mp4 \
    -hls_segment_filename "$W/hls/480p/segment_%03d.m4s" "$W/hls/480p/index.m3u8" \
    -map '[v360]' -map 0:a:0 -r 30 -c:v libx264 -preset slow -profile:v high -level:v 3.0 -crf 23 \
    -maxrate 800k -bufsize 1600k -g 60 -keyint_min 60 -sc_threshold 0 -pix_fmt yuv420p \
    -c:a aac -b:a 128k -f hls -hls_time 4 -hls_playlist_type vod -hls_segment_type fmp4 \
    -hls_flags independent_segments -hls_segment_options movflags=+cmaf -hls_fmp4_init_filename init.mp4 \
    -hls_segment_filename "$W/hls/360p/segment_%03d.m4s" "$W/hls/360p/index.m3u8"
fi

if [[ $steps == *measure* ]]; then
  # ffprobe's packet PTS and sizes are the source of the per-second video peak.
  # The last partial second is not extrapolated; each bin sums floor(PTS).
  python3 - "$W" "$MASTER" <<'PY'
import collections
import decimal
import hashlib
import json
import pathlib
import re
import subprocess
import sys

work, master = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
expected = decimal.Decimal('420.700')

def probe(path, *args):
    return json.loads(subprocess.check_output(
        ['ffprobe', '-v', 'error', *args, '-of', 'json', str(path)], text=True))

def metadata(path):
    return probe(path, '-show_streams', '-show_format')

def packet_metrics(path, duration, check_gop=False):
    packets = probe(path, '-select_streams', 'v:0', '-show_packets',
                    '-show_entries', 'packet=pts_time,size,flags')['packets']
    seconds = collections.Counter()
    keyframes = []
    for packet in packets:
        pts = decimal.Decimal(packet['pts_time'])
        second = int(pts.to_integral_value(rounding=decimal.ROUND_FLOOR))
        seconds[second] += int(packet['size'])
        if 'K' in packet.get('flags', ''):
            keyframes.append(float(pts))
    if check_gop:
        assert abs(keyframes[0]) < 0.0001, keyframes[:1]
        assert all(abs(b-a-2.0) < 0.0001 for a,b in zip(keyframes, keyframes[1:])), keyframes
        assert len(keyframes) == 211, len(keyframes)
    return dict(video_average_bps=round(sum(seconds.values())*8/duration),
                video_peak_1s_bps=max(seconds.values())*8,
                peak_second=max(seconds, key=seconds.get),
                video_packets=len(packets), video_frame_count=len(packets), keyframe_count=len(keyframes),
                keyframe_interval_min_seconds=min((b-a for a,b in zip(keyframes,keyframes[1:])),default=0),
                keyframe_interval_max_seconds=max((b-a for a,b in zip(keyframes,keyframes[1:])),default=0),
                keyframe_interval_seconds=2.0 if check_gop else None)

master_meta = metadata(master)
mv = next(s for s in master_meta['streams'] if s['codec_type'] == 'video')
assert abs(decimal.Decimal(mv['duration'])-expected) < decimal.Decimal('.001'), mv
web = work/'solana-bunker-film-v4-web.mp4'
meta = metadata(web)
video = next(s for s in meta['streams'] if s['codec_type'] == 'video')
audio = next(s for s in meta['streams'] if s['codec_type'] == 'audio')
assert (video['width'],video['height'],video['profile'],video['pix_fmt']) == (1280,720,'High','yuv420p'), video
assert video['r_frame_rate'] == '30/1', video
assert int(video['nb_frames']) == 12621, video
assert abs(decimal.Decimal(video['duration'])-expected) < decimal.Decimal('.001'), video
assert audio['codec_name'] == 'aac', audio
metrics = packet_metrics(web, float(expected), check_gop=True)
assert metrics['video_peak_1s_bps'] <= 5_500_000, metrics
metrics.update(file_bytes=web.stat().st_size,
               container_average_bps=int(meta['format']['bit_rate']),
               video_duration_seconds=float(video['duration']),
               container_duration_seconds=float(meta['format']['duration']),
               sha256=hashlib.file_digest(web.open('rb'), 'sha256').hexdigest())

hls = []
master_lines = ['#EXTM3U', '#EXT-X-VERSION:7', '#EXT-X-INDEPENDENT-SEGMENTS']
for name, width, height, level in [('720p',1280,720,31),('480p',854,480,31),('360p',640,360,30)]:
    playlist = work/'hls'/name/'index.m3u8'
    lines = playlist.read_text().splitlines()
    assert '#EXT-X-PLAYLIST-TYPE:VOD' in lines and '#EXT-X-ENDLIST' in lines, name
    assert '#EXT-X-INDEPENDENT-SEGMENTS' in lines, name
    durations = [decimal.Decimal(line.split(':',1)[1].split(',')[0]) for line in lines if line.startswith('#EXTINF:')]
    references = [line for line in lines if line and not line.startswith('#')]
    init = [re.search(r'URI="([^"]+)"', line).group(1) for line in lines if line.startswith('#EXT-X-MAP:')]
    assert len(init) == 1 and len(references) == len(durations), name
    assert len(durations) == 106 and all(d == 4 for d in durations[:-1]), (name,durations)
    assert abs(sum(durations)-expected) <= decimal.Decimal('.001'), (name,sum(durations))
    for reference in references+init:
        assert (playlist.parent/reference).is_file(), (name,reference)
    init_meta = metadata(playlist.parent/init[0])
    assert 'cmfc' in init_meta['format']['tags']['compatible_brands'], init_meta
    variant = metadata(playlist)
    vs = next(s for s in variant['streams'] if s['codec_type']=='video')
    aus = next(s for s in variant['streams'] if s['codec_type']=='audio')
    assert (vs['width'],vs['height'],vs['profile'],vs['level']) == (width,height,'High',level), vs
    assert aus['codec_name'] == 'aac', aus
    # RFC 8216 peak segment rate: max contiguous segment sets covering
    # 0.5..1.5 times TARGETDURATION. Includes mux and audio bytes.
    sizes = [(playlist.parent/ref).stat().st_size for ref in references]
    target = decimal.Decimal(next(line.split(':',1)[1] for line in lines if line.startswith('#EXT-X-TARGETDURATION:')))
    peak = 0
    for start in range(len(durations)):
        total_duration, total_size = decimal.Decimal(0), 0
        for stop in range(start,len(durations)):
            total_duration += durations[stop]
            total_size += sizes[stop]
            if total_duration > target*decimal.Decimal('1.5'):
                break
            if total_duration >= target*decimal.Decimal('.5'):
                peak = max(peak, int(decimal.Decimal(total_size*8)/total_duration)+1)
    average = round(sum(sizes)*8/float(sum(durations)))
    # Conservative measured BANDWIDTH, rounded up to the next 1000 bit/s.
    bandwidth = ((peak+999)//1000)*1000
    codecs = f'avc1.6400{level:02x},mp4a.40.2'
    master_lines += [f'#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},AVERAGE-BANDWIDTH={average},RESOLUTION={width}x{height},FRAME-RATE=30.000,CODECS="{codecs}"', f'{name}/index.m3u8']
    hls.append(dict(variant=name,resolution=f'{width}x{height}',segments=len(references),
                    segment_duration_sum_seconds=str(sum(durations)),
                    final_segment_seconds=str(durations[-1]),average_bps=average,
                    peak_segment_bps=peak,declared_bandwidth=bandwidth,codecs=codecs,
                    file_bytes=sum(sizes)+(playlist.parent/init[0]).stat().st_size+playlist.stat().st_size))
(work/'hls/master.m3u8').write_text('\n'.join(master_lines)+'\n')
report = dict(master=str(master),master_video_duration_seconds=str(expected),
              master_sha256=hashlib.file_digest(master.open('rb'),'sha256').hexdigest(),
              environment=dict(host='dev-mac',platform=sys.platform,
                  ffmpeg=subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0],
                  ffprobe=subprocess.check_output(['ffprobe','-version'],text=True).splitlines()[0]),
              web=metrics,hls=hls,validation='PASS: web packet peak/GOP; HLS references, streams and duration sums')
(work/'rep/delivery-v4.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
PY
fi
echo "deliver-v4: done ($steps)"
