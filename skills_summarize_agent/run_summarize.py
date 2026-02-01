#!/usr/bin/env python3
"""
CLI entry point: summarize skills from an agent log (JSONL).

Usage (from repo root or any dir with the package on PYTHONPATH):
  python -m skills_summarize_agent.run_summarize --log_path agent_log
  python -m skills_summarize_agent.run_summarize --log_path /path/to/log.jsonl --last 100
  python -m skills_summarize_agent.run_summarize --project_root /path/to/project --output_dir /path/to/output
"""
import argparse
import os
import sys

from skills_summarize_agent import summarize_skills_from_log


def main():
    parser = argparse.ArgumentParser(
        description="Extract reusable SKILL.md from an agent log (JSONL).",
    )
    parser.add_argument(
        "--log_path",
        type=str,
        default="agent_log",
        help="Path to log file (relative to project_root or absolute; any extension, read as text).",
    )
    parser.add_argument(
        "--project_root",
        type=str,
        default=None,
        help="Root for reading logs; default: current working directory.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=None,
        help="Root for writing generated SKILLs; default: package default.",
    )
    parser.add_argument(
        "--last",
        type=int,
        default=None,
        help="Use only the last N lines of the log; default: all.",
    )
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root or os.getcwd())
    output_dir = os.path.abspath(args.output_dir) if args.output_dir else None

    print(f"[INFO] Project root: {project_root}")
    print(f"[INFO] Log path: {args.log_path}")
    if output_dir:
        print(f"[INFO] Output dir: {output_dir}")
    if args.last:
        print(f"[INFO] Last N lines: {args.last}")

    result = summarize_skills_from_log(
        log_path=args.log_path,
        project_root=project_root,
        output_root=output_dir,
        last_n=args.last,
    )

    if result["success"]:
        print("\n[OK] Skill summarizer finished.")
        if result.get("final_response"):
            print("\n--- Agent final response ---")
            text = result["final_response"]
            print(text[:2000] + ("..." if len(text) > 2000 else ""))
    else:
        print("\n[FAIL] Skill summarizer did not finish successfully.")
        if result.get("final_response"):
            print(result["final_response"])
    print(f"\nTool calls made: {len(result.get('tool_calls', []))}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
