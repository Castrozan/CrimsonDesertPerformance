#!/usr/bin/env bash
set -euo pipefail
repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_directory="$repository_root/build/native-tests"
mkdir -p "$output_directory"
nix shell nixpkgs#clang -c clang++ -std=c++20 -Wall -Wextra -Werror -I"$repository_root/src" \
  "$repository_root/tests/budget_policy_test.cpp" -o "$output_directory/budget_policy_test"
"$output_directory/budget_policy_test"
python3 -m unittest discover -s "$repository_root/tests" -p '*_test.py'
