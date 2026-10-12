#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Tool locations are overridable; no global Solana configuration is changed.
export PATH="${BUNKER_SOLANA_BIN:-/workspace/scratch/1a48031fefb9/toolchains/solana-release/bin}:${BUNKER_CARGO_BIN:-/root/.cargo/bin}:$PATH"
command -v cargo-build-sbf >/dev/null
cargo-build-sbf --manifest-path program/Cargo.toml --sbf-out-dir program/target/deploy
cargo-build-sbf --manifest-path crypto/svm-probe/Cargo.toml --sbf-out-dir target/deploy
python - <<'PY'
from pathlib import Path
import hashlib,json
for p in [Path('program/target/deploy/bunker_program.so'),Path('target/deploy/bunker_xmss_probe.so')]:
 print(json.dumps({'program':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
PY
