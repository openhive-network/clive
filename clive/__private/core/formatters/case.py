from __future__ import annotations

import inflection


def dasherize(string: str) -> str:
    """
    Convert string from snake_case to kebab-case.

    Args:
        string: The string that needs to be converted.

    Returns:
        String with underscores replaced by dashes.
    """
    return inflection.dasherize(string)


def underscore(string: str) -> str:
    """Convert string from CamelCase to snake_case."""
    return inflection.underscore(string)
