"""
Skill Summarizer Agent configuration.

Loads .env from repo root first, then from the current working directory.
Only includes settings required by this agent.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

_PKG_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _PKG_DIR.parent
load_dotenv(_REPO_ROOT / ".env")
load_dotenv()

# OpenAI-compatible API used by the agent
OPENAI_CONFIG = {
    "base_url": os.getenv("SKILL_SUMMARIZER_OPENAI_BASE_URL") or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    "api_key": os.getenv("SKILL_SUMMARIZER_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", ""),
    "model": os.getenv("SKILL_SUMMARIZER_OPENAI_MODEL") or os.getenv("OPENAI_MODEL", "gpt-5.2"),
    "temperature": float(os.getenv("SKILL_SUMMARIZER_TEMPERATURE", "0.3")),
    "max_tokens": int(os.getenv("SKILL_SUMMARIZER_MAX_TOKENS", "4096")),
}

DEFAULT_PROJECT_ROOT = os.getenv("SKILL_SUMMARIZER_PROJECT_ROOT", "")
DEFAULT_OUTPUT_DIR = str(_REPO_ROOT / "output")
