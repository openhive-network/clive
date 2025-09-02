from __future__ import annotations

import re
from abc import ABC, abstractmethod


class Matchable(ABC):
    @abstractmethod
    def is_matching_pattern(self, *patterns: str) -> bool:
        """
        Checks if the provided patterns match a certain condition.

        This method is meant to be implemented by subclasses and defines a
        custom logic to evaluate whether the supplied pattern(s) satisfy
        a specific criterion.

        Args:
            *patterns: The patterns to check against.

        Returns:
            True if the patterns match the condition, otherwise False.
        """


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
