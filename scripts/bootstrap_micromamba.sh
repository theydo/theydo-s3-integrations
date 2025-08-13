#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.mamba}"
BIN="$ROOT/bin/micromamba"

# Reuse if already present (idempotent)
if [[ -x "$BIN" ]]; then
  "$BIN" --version 2>/dev/null | head -n1 || true
  exit 0
fi

mkdir -p "$ROOT"

OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
  Linux)  platform="linux" ;;
  Darwin) platform="osx" ;;
  *) echo "Unsupported OS: $OS" >&2; exit 1 ;;
esac

case "$ARCH" in
  x86_64|amd64)   arch="64" ;;
  arm64|aarch64)  arch="arm64" ;;
  *) echo "Unsupported arch: $ARCH" >&2; exit 1 ;;
esac

URL="https://micro.mamba.pm/api/micromamba/${platform}-${arch}/latest"

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
curl -fsSL "$URL" -o "$tmp/mm.tar.bz2"
tar -xjf "$tmp/mm.tar.bz2" -C "$ROOT" bin/micromamba
chmod +x "$BIN"
