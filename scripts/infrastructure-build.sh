#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Tool locations are overridable; no global Solana configuration is changed.
export PATH="${BUNKER_SOLANA_BIN:-$HOME/.local/share/solana/install/releases/4.3.0/solana-release/bin}:${BUNKER_CARGO_BIN:-$HOME/.cargo/bin}:$PATH"
command -v cargo-build-sbf >/dev/null
# Reject silent toolchain drift; release binaries report their own exact version.
solana --version | grep -q "solana-cli 4.3.0 "
cargo-build-sbf --version | grep -q "cargo-build-sbf 4.3.0"
cargo-build-sbf --tools-version v1.57 --manifest-path program/Cargo.toml --sbf-out-dir program/target/deploy -- --locked
cargo-build-sbf --tools-version v1.57 --manifest-path crypto/svm-probe/Cargo.toml --sbf-out-dir target/deploy -- --locked
${BUNKER_PYTHON:-python3} - <<'PY'
from pathlib import Path
import hashlib,json
for p in [Path('program/target/deploy/bunker_program.so'),Path('target/deploy/bunker_xmss_probe.so')]:
 print(json.dumps({'program':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
PY
