#!/usr/bin/env bash
set -euo pipefail

patterns='(api[_-]?key|password|connection[_-]?string|accountkey|instrumentationkey)[[:space:]]*[:=][[:space:]]*["'\''][^"'\'']{16,}["'\'']|Bearer[[:space:]]+[A-Za-z0-9_/\+=.-]{20,}|https://[A-Za-z0-9.-]*webhook\.office\.com/[A-Za-z0-9_/\+=?.&%-]{20,}'
if grep -RInE "$patterns" . \
  --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.next --exclude-dir=__pycache__ \
  --exclude-dir=docs --exclude-dir=tests --exclude-dir=scripts/security \
  --exclude='*.env.example'; then
  echo "Potential secret-like value found. Review output above."
  exit 1
fi
echo "No likely hardcoded secrets found."
