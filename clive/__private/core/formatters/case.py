from __future__ import annotations

import inflection


def underscore(string: str) -> str:
    """
    Convert string from CamelCase or kebab-case to snake_case.

    Args:
        string: The input string in CamelCase or kebab-case format.

    Returns:
        The converted string in snake_case format.
    """
    return inflection.underscore(string)


def dasherize(string: str) -> str:
    """
    Replace underscores with dashes in the string.

    Args:
        string: The input string in snake_case format.

    Example:
        >>> dasherize("some_text")
        'some-text'
        >>> dasherize("some-text")
        'some-text'

    Returns:
        The converted string.
    """
    return inflection.dasherize(string)


def camelize(string: str) -> str:
    """
    Convert strings to CamelCase.

    Args:
        string: The input string in snake_case format.

    Returns:
        The converted string in CamelCase format.
    """
    return inflection.camelize(string)
