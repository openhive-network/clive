from __future__ import annotations

from typing import Any, TypeVar, overload

import msgspec

from clive.exceptions import CliveError

ExpectT = TypeVar("ExpectT")


class WrongTypeError(CliveError):
    """Raised when the type of the value is not the expected one."""


class NoMatchesError(CliveError):
    """Raised when no matches are found."""


@overload
def get_default_from_model(model: type[msgspec.Struct] | msgspec.Struct, field_name: str) -> Any: ...  # noqa: ANN401


@overload
def get_default_from_model(
    model: type[msgspec.Struct] | msgspec.Struct, field_name: str, expect_type: type[ExpectT]
) -> ExpectT: ...


def get_default_from_model(
    model: type[msgspec.Struct] | msgspec.Struct, field_name: str, expect_type: type[ExpectT] | None = None
) -> ExpectT | Any:
    """Get default value from pydantic model."""
    field = model.__fields__.get(field_name, None)

    if field is None:
        raise NoMatchesError(f"No matches for {field_name} in {model}")

    default_value = field.default

    if expect_type is not None and not isinstance(default_value, expect_type):
        raise WrongTypeError(f"{model}.{field_name} is wrong type; expected {expect_type}, got {type(default_value)}")

    return default_value
