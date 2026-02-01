#!/usr/bin/env bash
# Summarize skills from a log file. Run from repo root: bash scripts/run_summarize.sh [log_path] [last_n]
#   log_path: path to log file (default: agent_log; any extension; relative to repo root)
#   last_n: optional; use only last N lines
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

LOG_PATH="${1:-agent_log}"
LAST_N="${2:-}"

if [ -n "$LAST_N" ]; then
  python -m skills_summarize_agent.run_summarize --project_root "$REPO_ROOT" --log_path "$LOG_PATH" --last "$LAST_N"
else
  python -m skills_summarize_agent.run_summarize --project_root "$REPO_ROOT" --log_path "$LOG_PATH"
fi
