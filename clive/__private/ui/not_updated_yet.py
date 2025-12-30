from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeIs


def is_not_updated_yet[T](value: T | NotUpdatedYet) -> TypeIs[NotUpdatedYet]:
    """
    Check whether the value is an instance of NotUpdatedYet.

    Args:
        value: The value to check.

    Returns:
        True if the value is an instance of NotUpdatedYet, False otherwise.
    """
    return isinstance(value, NotUpdatedYet)


def is_updated[T](value: T | NotUpdatedYet) -> TypeIs[T]:
    """
    Check whether the value is not an instance of NotUpdatedYet.

    Args:
        value: The value to check.

    Returns:
        True if the value is not an instance of NotUpdatedYet, False otherwise.
    """
    return not is_not_updated_yet(value)


class NotUpdatedYet:
    """Used to check whether data is not updated yet or it is not present (created to avoid initialization via None)."""
