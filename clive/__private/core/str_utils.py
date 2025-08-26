from __future__ import annotations

import re


def is_text_matching_pattern(text: str, *patterns: str) -> bool:
    """
    Determines if the given text matches any of the provided patterns.

    Args:
        text: The text to be searched for matches.
        *patterns: The patterns to check against the provided text.

    Returns:
        True if any pattern matches the text, False otherwise.
    """
    return any(re.search(re.escape(pattern), text) for pattern in patterns)
