from __future__ import annotations

from pathlib import Path
from typing import List


def load_repo_snippets(root: Path, glob_pattern: str) -> List[str]:
    snippets: List[str] = []
    for path in root.glob(glob_pattern):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        snippets.append(f"# File: {path.relative_to(root)}\n{content[:2000]}")
        if len(snippets) >= 10:
            break
    return snippets
