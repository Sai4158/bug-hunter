#!/usr/bin/env bash
set -euo pipefail
project_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
project_python="$project_root/.venv/bin/python"
if [[ ! -x "$project_python" ]]; then
    printf '%s\n' 'No project Python environment. No processes were stopped.'
    exit 0
fi
exec "$project_python" "$project_root/control.py" stop
