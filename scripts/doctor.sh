#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if ! command -v uv >/dev/null 2>&1; then
  printf 'uv is required for diagnostics\n' >&2
  exit 1
fi

exec uv run floating-agent --doctor "$@"
