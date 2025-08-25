from __future__ import annotations

import re


def is_match(text: str, *patterns: str) -> bool:
    return any(re.search(re.escape(pattern), text) for pattern in patterns)
