from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def check_for_pattern_in_file(file_path: Path, pattern: str) -> bool:
    with file_path.open() as log_file:
        for line in log_file:
            if re.search(pattern, line):
                return True
    return False
