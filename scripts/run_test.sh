#!/usr/bin/env bash
# Quick test using bundled sample log. Run from repo root: bash scripts/run_test.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

python -m skills_summarize_agent.run_summarize \
  --project_root "$REPO_ROOT" \
  --log_path data/example1 \
  --output_dir "$REPO_ROOT/output"
