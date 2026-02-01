"""
skills_summarize_agent: extract reusable SKILL.md from agent execution logs.

SDK:
- summarize_skills_from_log: main entry; summarize from a log file (JSONL).
- SkillSummarizerAgent: low-level agent with read_file / write_file / list_dir tools.

Output follows the summarizing-new-skills spec (see SKILL.md).
"""
from .skill_summarizer_agent import (
    SkillSummarizerAgent,
    summarize_skills_from_log,
)

# Backward compatibility
extract_skills_from_agent_log = summarize_skills_from_log

__all__ = [
    "SkillSummarizerAgent",
    "summarize_skills_from_log",
    "extract_skills_from_agent_log",
]
