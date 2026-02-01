"""
Sandboxed file tools for the Skill Summarizer Agent.

- read_file: read-only; allowed under configured read roots (e.g. logs, configs).
- write_file: write allowed only under the designated output directory.
- list_dir: read-only; list contents under allowed roots.
"""
import os
from typing import Optional


def _resolve_allowed_base(path: str, allowed_bases: list) -> Optional[str]:
    """Return the allowed base that contains path, or None."""
    abs_path = os.path.abspath(path)
    for base in allowed_bases:
        abs_base = os.path.abspath(base)
        if abs_path == abs_base or abs_path.startswith(abs_base + os.sep):
            return abs_base
    return None


def read_file(
    file_path: str,
    allowed_read_roots: list,
    encoding: str = "utf-8",
) -> dict:
    """
    Read file contents. Allowed only when file_path is under one of allowed_read_roots.

    Returns:
        {"success": bool, "content": str | None, "error": str | None}
    """
    abs_path = os.path.abspath(file_path)
    base = _resolve_allowed_base(abs_path, allowed_read_roots)
    if base is None:
        return {
            "success": False,
            "content": None,
            "error": f"Path not allowed. Allowed roots: {allowed_read_roots}",
        }
    if not os.path.isfile(abs_path):
        return {"success": False, "content": None, "error": f"Not a file or not found: {abs_path}"}
    try:
        with open(abs_path, "r", encoding=encoding) as f:
            content = f.read()
        return {"success": True, "content": content, "error": None}
    except Exception as e:
        return {"success": False, "content": None, "error": str(e)}


def write_file(
    file_path: str,
    content: str,
    output_root: str,
    encoding: str = "utf-8",
) -> dict:
    """
    Write content to a file. Allowed only when file_path is under output_root.

    Returns:
        {"success": bool, "path": str | None, "error": str | None}
    """
    abs_path = os.path.abspath(file_path)
    abs_root = os.path.abspath(output_root)
    if abs_path != abs_root and not abs_path.startswith(abs_root + os.sep):
        return {
            "success": False,
            "path": None,
            "error": f"Write only allowed under output_root: {output_root}",
        }
    try:
        os.makedirs(os.path.dirname(abs_path) or ".", exist_ok=True)
        with open(abs_path, "w", encoding=encoding) as f:
            f.write(content)
        return {"success": True, "path": abs_path, "error": None}
    except Exception as e:
        return {"success": False, "path": None, "error": str(e)}


def list_dir(
    dir_path: str,
    allowed_list_roots: list,
) -> dict:
    """
    List directory contents (names only). Allowed only when dir_path is under allowed_list_roots.

    Returns:
        {"success": bool, "entries": list[str] | None, "error": str | None}
    """
    abs_path = os.path.abspath(dir_path)
    base = _resolve_allowed_base(abs_path, allowed_list_roots)
    if base is None:
        return {
            "success": False,
            "entries": None,
            "error": f"Path not allowed. Allowed roots: {allowed_list_roots}",
        }
    if not os.path.isdir(abs_path):
        return {"success": False, "entries": None, "error": f"Not a directory or not found: {abs_path}"}
    try:
        entries = sorted(os.listdir(abs_path))
        return {"success": True, "entries": entries, "error": None}
    except Exception as e:
        return {"success": False, "entries": None, "error": str(e)}
