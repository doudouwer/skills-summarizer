"""
Skill Summarizer Agent: extracts reusable SKILL.md from other agents' execution logs.

Architecture:
- LLM: OpenAI-compatible API (strong reasoning, large context).
- Tools: read_file / write_file / list_dir (sandboxed).
- Skill context: summarizing-new-skills (SKILL.md) injected as system context.
"""
import json
import os
from typing import Any, Dict, List, Optional

from openai import OpenAI

from . import tools as file_tools
from .config import OPENAI_CONFIG


TOOL_DEFS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file. Allowed paths: under project root (e.g. agent log JSONL, configs) or under the skills output directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file (relative to project root or absolute)."},
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file. Only allowed under the designated skills output directory. Use for creating new SKILL.md or scripts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path for the new file (under output root)."},
                    "content": {"type": "string", "description": "Full content to write (e.g. SKILL.md body)."},
                },
                "required": ["file_path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List directory contents (names only). Use to check existing skills before creating a new one to avoid duplicates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dir_path": {"type": "string", "description": "Path to the directory to list."},
                },
                "required": ["dir_path"],
            },
        },
    },
]


def load_skill_context(skill_md_path: str) -> str:
    """Load the full SKILL.md (summarizing-new-skills) as context."""
    try:
        with open(skill_md_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"[Warning: Could not load skill file: {e}]\n"


def build_system_message(skill_content: str, output_root: str) -> str:
    """Build system prompt: role, capability, and execution rules."""
    return f"""# Role
You are a senior AI architect who extracts standardized workflows from messy execution logs and produces SKILL.md files that follow the Agent Skills spec (e.g. agentskills.io).

# Capability: summarizing-new-skills
When given a task to extract skills from agent logs, you must:
1. Use list_dir to inspect the existing skills directory ({output_root}) and avoid creating duplicates.
2. Use read_file to read the provided agent log (text file, often JSONL: one JSON per line with e.g. query, api_call_history, collected_info_sources).
3. Apply Pattern Extraction: Success Mining, Context Gap, Variable Abstraction, Hidden Requirements, Decision Logic, Failure Modes.
4. If you identify a reusable multi-step successful workflow, use write_file to produce a new SKILL.md under {output_root} (name: kebab-case only, no Unicode; description: third person with trigger phrases).
5. Put complex steps in a scripts/ subdir; keep the main SKILL concise (progressive disclosure).

# Rules
- Follow summarizing-new-skills metadata format (name, description, optional compatibility).
- name must be alphanumeric and hyphens only; no Unicode.
- Do not create skills for one-off or trivial instructions; avoid skill bloat.

# Full skill spec (follow strictly)
{skill_content}
"""


class SkillSummarizerAgent:
    """Agent that extracts reusable SKILL.md from agent execution logs."""

    def __init__(
        self,
        project_root: str,
        output_root: str,
        llm_client: Optional[OpenAI] = None,
        llm_model: Optional[str] = None,
        skill_md_path: Optional[str] = None,
        max_turns: int = 20,
    ):
        """
        Args:
            project_root: Root directory allowed for reads (logs, configs).
            output_root: Root directory allowed for writes (generated SKILLs).
            llm_client: OpenAI-compatible client; built from OPENAI_CONFIG if None.
            llm_model: Model name; defaults to OPENAI_CONFIG["model"].
            skill_md_path: Path to summarizing-new-skills SKILL.md; default: package SKILL.md.
            max_turns: Maximum tool-call rounds per run.
        """
        self.project_root = os.path.abspath(project_root)
        self.output_root = os.path.abspath(output_root)
        self.llm_model = llm_model or OPENAI_CONFIG.get("model", "gpt-5.2")
        self.max_turns = max_turns

        if llm_client is not None:
            self.llm_client = llm_client
        else:
            base_url = OPENAI_CONFIG.get("base_url")
            self.llm_client = OpenAI(
                api_key=OPENAI_CONFIG.get("api_key", ""),
                base_url=base_url if base_url else None,
            )

        pkg_dir = os.path.dirname(__file__)
        self.skill_md_path = skill_md_path or os.path.join(pkg_dir, "SKILL.md")
        self.skill_content = load_skill_context(self.skill_md_path)
        self.system_message = build_system_message(self.skill_content, self.output_root)

        self.allowed_read_roots = [self.project_root, self.output_root]
        os.makedirs(self.output_root, exist_ok=True)

    def _resolve_path(self, path: str) -> str:
        """Resolve path to absolute; relative paths are under project_root."""
        if os.path.isabs(path):
            return path
        return os.path.join(self.project_root, path)

    def _run_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single tool call."""
        if name == "read_file":
            file_path = self._resolve_path(arguments["file_path"])
            return file_tools.read_file(file_path, self.allowed_read_roots)
        if name == "write_file":
            file_path = arguments["file_path"]
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.output_root, file_path)
            return file_tools.write_file(file_path, arguments["content"], self.output_root)
        if name == "list_dir":
            dir_path = self._resolve_path(arguments["dir_path"])
            return file_tools.list_dir(dir_path, self.allowed_read_roots)
        return {"success": False, "error": f"Unknown tool: {name}"}

    def run(
        self,
        user_message: str,
        initial_messages: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Run one summarization task.

        Returns:
            {"success": bool, "message": str, "tool_calls": list, "final_response": str | None}
        """
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_message},
        ]
        if initial_messages:
            messages.extend(initial_messages)
        messages.append({"role": "user", "content": user_message})

        tool_calls_log: List[Dict] = []
        turn = 0

        while turn < self.max_turns:
            turn += 1
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                tools=TOOL_DEFS,
                tool_choice="auto",
                temperature=OPENAI_CONFIG.get("temperature", 0.3),
                max_completion_tokens=OPENAI_CONFIG.get("max_tokens", 4096),
            )
            choice = response.choices[0]
            msg = choice.message

            if not getattr(msg, "tool_calls", None) or len(msg.tool_calls) == 0:
                return {
                    "success": True,
                    "message": user_message,
                    "tool_calls": tool_calls_log,
                    "final_response": getattr(msg, "content", None) or "",
                }

            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in msg.tool_calls
                ],
            })

            for tc in msg.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                result = self._run_tool(name, args)
                tool_calls_log.append({"name": name, "arguments": args, "result": result})
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })

        return {
            "success": False,
            "message": user_message,
            "tool_calls": tool_calls_log,
            "final_response": None,
        }


def summarize_skills_from_log(
    log_path: str,
    project_root: Optional[str] = None,
    output_root: Optional[str] = None,
    last_n: Optional[int] = None,
) -> Dict[str, Any]:
    """
    SDK entry point: summarize skills from an agent log file.

    Log files are read as text (any filename/extension, e.g. .jsonl, .log, .txt, or none).
    Content is expected to be JSONL (one JSON object per line) so the LLM can infer workflows.

    Args:
        log_path: Path to the log file (relative to project_root or absolute; any extension).
        project_root: Root for reading; defaults to current working directory.
        output_root: Root for writing generated SKILLs; defaults to package default.
        last_n: Use only the last N lines of the log; None = use all.

    Returns:
        {"success": bool, "message": str, "tool_calls": list, "final_response": str | None}
    """
    from .config import DEFAULT_OUTPUT_DIR

    project_root = os.path.abspath(project_root or os.getcwd())
    output_root = os.path.abspath(output_root or DEFAULT_OUTPUT_DIR)

    abs_log = log_path if os.path.isabs(log_path) else os.path.join(project_root, log_path)
    if not os.path.isfile(abs_log):
        return {
            "success": False,
            "message": "",
            "tool_calls": [],
            "final_response": f"Log file not found: {abs_log}",
        }

    lines = []
    with open(abs_log, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(line)
    if last_n is not None and last_n > 0:
        lines = lines[-last_n:]

    log_preview = "\n".join(lines[:50])
    if len(lines) > 50:
        log_preview += f"\n... ({len(lines)} lines total; use read_file for more.)"

    user_message = f"""Extract reusable skills from the agent log below and write SKILL.md files following the summarizing-new-skills spec.

Log path: {log_path}
Total lines: {len(lines)}. First 50 lines:

---
{log_preview}
---

First list_dir on {output_root} to avoid duplicates, then analyze repeated successful patterns, then write_file new SKILL.md(s)."""

    agent = SkillSummarizerAgent(project_root=project_root, output_root=output_root)
    return agent.run(user_message)
