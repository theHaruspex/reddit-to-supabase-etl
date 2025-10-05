#!/usr/bin/env bash
set -euo pipefail

MSG=${1:-"LLM execution complete"}

if command -v say >/dev/null 2>&1; then
  say "$MSG"
else
  echo "$MSG"
fi


