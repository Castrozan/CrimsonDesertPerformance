#!/usr/bin/env bash
set -euo pipefail
run_label="$1"
sample_seconds="${2:-420}"
repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
coop_log="$HOME/.local/share/Steam/steamapps/common/Crimson Desert/bin64/cdmp.log"
pad_python="$repository_root/build/gcroots/python-evdev/bin/python3"
output="$repository_root/measurements/$(date +%Y-%m-%d)-$run_label.csv"
steam_skip_button=(965 592)

fresh_log_has() {
  [ -f "$coop_log" ] && [ "$(stat -c %Y "$coop_log")" -ge "$launch_time" ] && grep -q "$1" "$coop_log"
}

"$repository_root/tools/game_lock.sh" take
if pgrep -x CrimsonDesert.e >/dev/null; then
  pkill -x CrimsonDesert.e
  for _ in $(seq 60); do pgrep -x CrimsonDesert.e >/dev/null || break; sleep 1; done
  sleep 5
fi
systemctl --user stop ${CDPERF_PAUSE_USER_UNITS-hex.service} 2>/dev/null || true
"$repository_root/package/linux/cdperf-free-memory"
systemd-run --user --unit="cdperf-$run_label" --collect -p Nice=19 \
  python3 "$repository_root/tools/sample_metrics.py" "$output" --interval 2 --duration "$sample_seconds"
launch_time=$(date +%s)
setsid -f steam steam://rungameid/3321460 >/dev/null 2>&1

for _ in $(seq 40); do
  pgrep -x CrimsonDesert.e >/dev/null && break
  sleep 5
  pgrep -x CrimsonDesert.e >/dev/null || hypruse pointer click "${steam_skip_button[@]}" --then none >/dev/null || true
done
pgrep -x CrimsonDesert.e >/dev/null || { echo "game did not start" >&2; exit 1; }
echo "game process after $(( $(date +%s) - launch_time )) s"

play_time=""
for _ in $(seq 60); do
  fresh_log_has 'Local: pos' && break
  pgrep -x CrimsonDesert.e >/dev/null || { echo "game exited during load" >&2; exit 1; }
  if fresh_log_has 'Overlay: installed true'; then
    hyprctl dispatch focuswindow 'title:^Crimson Desert$' >/dev/null
    "$pad_python" "$repository_root/tools/press_pad.py" a
    play_time="${play_time:-$(date +%s)}"
  fi
  sleep 8
done
fresh_log_has 'Local: pos' || { echo "never reached the world" >&2; exit 1; }
echo "in world $(( $(date +%s) - launch_time )) s after launch, $(( $(date +%s) - ${play_time:-$launch_time} )) s after first Play press"
echo "$output"
