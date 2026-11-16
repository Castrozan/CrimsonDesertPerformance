#!/usr/bin/env bash
set -euo pipefail
repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 -m unittest discover -s "$repository_root/tests" -p '*_test.py'
bash -n "$repository_root"/package/linux/cdperf-run "$repository_root"/package/linux/cdperf-free-memory "$repository_root"/tools/*.sh
