from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from typing_extensions import TypeIs

ValueT = TypeVar("ValueT")


def is_not_updated_yet(value: ValueT | NotUpdatedYet) -> TypeIs[NotUpdatedYet]:
    """Check whether the value is an instance of NotUpdatedYet."""
    return isinstance(value, NotUpdatedYet)


def is_updated(value: ValueT | NotUpdatedYet) -> TypeIs[ValueT]:
    """Check whether the value is not an instance of NotUpdatedYet."""
    return not is_not_updated_yet(value)


class NotUpdatedYet:
    """Used to check whether data is not updated yet or it is not present (created to avoid initialization via None)."""
