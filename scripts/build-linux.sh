#!/usr/bin/env bash
set -euo pipefail
repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export XWIN_DIR="${XWIN_DIR:-$HOME/.local/share/xwin/splat}"
llvm_packages="nixpkgs#llvmPackages_20"
export CLANG_RESOURCE_DIR="$(nix eval --raw "${llvm_packages}.clang-unwrapped.lib.outPath")/lib/clang/20"
mkdir -p "$repository_root/build/gcroots"
nix build -o "$repository_root/build/gcroots/clang-lib" "${llvm_packages}.clang-unwrapped.lib"
exec nix shell "${llvm_packages}.clang-unwrapped" "${llvm_packages}.lld" "${llvm_packages}.llvm" nixpkgs#cmake nixpkgs#ninja -c bash -c '
  cmake -S "$0" -B "$0/build/linux" -G Ninja -DCMAKE_TOOLCHAIN_FILE="$0/cmake/clang-cl-xwin.cmake" -DCMAKE_BUILD_TYPE=Release &&
  cmake --build "$0/build/linux"' "$repository_root"
