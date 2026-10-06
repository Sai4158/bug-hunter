#!/usr/bin/env bash
set -euo pipefail
project_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
project_python="$project_root/.venv/bin/python"
if ! command -v python3 >/dev/null 2>&1; then
    printf '%s\n' 'Install Python 3.11+ first. See README.md.' >&2
    exit 1
fi
if [[ ! -x "$project_python" ]] || ! "$project_python" "$project_root/setup_env.py" --check; then
    python3 "$project_root/setup_env.py"
fi
exec "$project_python" "$project_root/control.py" start "$@"
