import os
from pathlib import Path

# Root of the repository (two levels up from agents/shared/)
REPO_ROOT = Path(__file__).parent.parent.parent


def read_file(relative_path: str) -> str:
    """Read a file relative to the repository root."""
    full_path = REPO_ROOT / relative_path
    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {full_path}")
    return full_path.read_text(encoding="utf-8")


def write_file(relative_path: str, content: str) -> str:
    """Write content to a file relative to the repository root. Creates directories as needed."""
    full_path = REPO_ROOT / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return str(full_path)


def write_multiple_files(files: dict) -> list:
    """
    Write multiple files at once.
    files: dict mapping relative_path -> content
    Returns list of absolute paths written.
    """
    written = []
    for relative_path, content in files.items():
        written.append(write_file(relative_path, content))
    return written


def read_standards() -> dict:
    """Load project standards and template files referenced by all agents."""
    return {
        "ai_rules": read_file("docs/05-standards/ai-rules.md"),
        "tech_stack": read_file("docs/05-standards/technology-stack.md"),
        "module_template": read_file("docs/templates/module-template.md"),
    }
