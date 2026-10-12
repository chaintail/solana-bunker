#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Prerequisites: Python3.12+ requirements.txt; gcc/OpenSSL headers; Rust;
# Agave4.3.0 cargo-build-sbf/platform-tools1.57. No public network mutation.
bash scripts/infrastructure-build.sh
bash crypto/build_reference.sh
python -m crypto.generate_vectors
python tests/run_host.py
python tests/svm_harness.py --full --samples "${BUNKER_BENCHMARK_SAMPLES:-20}"
