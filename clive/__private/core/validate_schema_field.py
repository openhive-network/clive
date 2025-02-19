from __future__ import annotations

from typing import Any

import msgspec


def validate_schema_field(schema_field: type[Any], value: Any) -> None:  # noqa: ANN401
    """
    Validate the given value against the given schema field e.g. one that inherits from pydantic.ConstrainedStr.

    For validating models use `pydantic.validate_model` instead.

    Raises
    ------
    pydantic.ValidationError: if the given value is invalid.
    """

    class Model(msgspec.Struct):
        value: schema_field  # type: ignore[valid-type]

    Model(value=value)


def is_schema_field_valid(schema_field: type[Any], value: Any) -> bool:  # noqa: ANN401
    try:
        validate_schema_field(schema_field, value)
    except Exception:
        return False
    else:
        return True
