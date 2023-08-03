from __future__ import annotations

import inflection


def underscore(string: str) -> str:
    """Convert string from CamelCase to snake_case."""
    return inflection.underscore(string)
