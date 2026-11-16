#!/usr/bin/env bash
set -euo pipefail
lock_path="${CDMP_GAME_LOCK:-$HOME/.local/share/cdmp/game.lock}"
holder="${CDPERF_LOCK_HOLDER:-Lancelot}"
case "${1:-}" in
  take)
    if [ -e "$lock_path" ] && ! grep -q "^$holder " "$lock_path"; then
      echo "game held by: $(cat "$lock_path")" >&2
      exit 1
    fi
    [ -e "$lock_path" ] || (set -o noclobber; echo "$holder $(date +%H:%M:%S)" > "$lock_path")
    grep -q "^$holder " "$lock_path"
    ;;
  release)
    if [ -e "$lock_path" ] && grep -q "^$holder " "$lock_path"; then rm -f "$lock_path"; fi
    ;;
  *)
    echo "usage: $0 take|release" >&2
    exit 2
    ;;
esac
