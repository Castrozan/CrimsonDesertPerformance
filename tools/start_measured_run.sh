#!/usr/bin/env bash
set -euo pipefail
run_label="$1"
sample_seconds="${2:-600}"
repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output="$repository_root/measurements/$(date +%Y-%m-%d)-$run_label.csv"
if pgrep -x CrimsonDesert.e >/dev/null; then
  pkill -x CrimsonDesert.e
  for _ in $(seq 60); do pgrep -x CrimsonDesert.e >/dev/null || break; sleep 1; done
  sleep 5
fi
systemctl --user stop ${CDPERF_PAUSE_USER_UNITS-hex.service} 2>/dev/null || true
"$repository_root/package/linux/cdperf-free-memory"
systemd-run --user --unit="cdperf-$run_label" --collect -p Nice=19 \
  python3 "$repository_root/tools/sample_metrics.py" "$output" --interval 2 --duration "$sample_seconds"
setsid -f steam steam://rungameid/3321460 >/dev/null 2>&1
echo "$output"
