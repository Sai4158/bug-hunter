#!/usr/bin/env bash
set -euo pipefail
project_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
    printf '%s\n' 'Install Python 3.11+ before running setup.' >&2
    exit 1
fi
exec python3 "$project_root/setup_env.py" "$@"
