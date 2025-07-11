from __future__ import annotations

import inflection


def underscore(string: str) -> str:
    """
    Convert string from CamelCase to snake_case.

    Args:
        string: The input string in CamelCase format.

    Returns:
        The converted string in snake_case format.
    """
    return inflection.underscore(string)
