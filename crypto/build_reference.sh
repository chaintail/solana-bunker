#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 - <<'PYLOCK'
import hashlib,json
from pathlib import Path
lock=json.loads(Path('reference-lock.json').read_text())
assert lock['commit']=='171ccbd26f098542a67eb5d2b128281c80bd71a6'
for name,digest in lock['files'].items():
    assert hashlib.sha256((Path('reference')/name).read_bytes()).hexdigest()==digest,name
PYLOCK
mkdir -p build
# Fix upstream maximum-index zeroization ordering without altering hash/signature algorithms.
python3 - <<'PY'
from pathlib import Path
s=Path('reference/xmss_core.c').read_text()
needle='if (idx >= ((1ULL << params->full_height) - 1)) {'
assert s.count(needle)==1
Path('build/xmss_core_boundary.c').write_text(s.replace(needle,'if (idx >= (1ULL << params->full_height)) {'))
PY
sources=(params.c hash.c fips202.c hash_address.c randombytes.c wots.c xmss_commons.c utils.c)
args=();for s in "${sources[@]}";do args+=("reference/$s");done
gcc -O3 -fPIC -shared -Ireference reference_bridge.c "${args[@]}" reference/xmss_core.c -lcrypto -o build/libxmss_original.so
gcc -O3 -fPIC -shared -Ireference reference_bridge.c "${args[@]}" build/xmss_core_boundary.c -lcrypto -o build/libxmss_reference.so
