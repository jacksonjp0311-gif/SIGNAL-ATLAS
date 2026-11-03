"""File boundary shared by release lineage, validation, and ZIP packaging."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator


_EXCLUDED_NAMES = {".git", "__pycache__"}


def iter_release_files(root: Path) -> Iterator[Path]:
    """Yield project files while pruning Git metadata and Python bytecode caches.

    A linked worktree's .git pointer file is excluded as well as .git directories.
    Other dot paths, including .github workflows, remain ordinary project content.
    """
    for directory, subdirectories, filenames in os.walk(root):
        subdirectories[:] = sorted(name for name in subdirectories if name not in _EXCLUDED_NAMES)
        for name in sorted(filenames):
            path = Path(directory) / name
            if name not in _EXCLUDED_NAMES and path.is_file():
                yield path
