#!/bin/bash
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    echo "Error: this script must be sourced, not executed." >&2
    echo "Usage: source venv_activate.sh" >&2
    exit 1
fi
source "$(dirname "${BASH_SOURCE[0]}")/.venv/bin/activate"
