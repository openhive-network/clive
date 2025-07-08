from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ValidationError


def validate_schema_field(schema_field: type[Any], value: Any) -> None:  # noqa: ANN401
    """
    Validate the given value against the given schema field e.g. one that inherits from pydantic.ConstrainedStr.

    For validating models use `pydantic.validate_model` instead.

    Args:
        schema_field: The schema field type to validate against.
        value: The value to validate.

    Raises:
        pydantic.ValidationError: if the given value is invalid.
    """

    class Model(BaseModel):
        value: schema_field  # type: ignore[valid-type]

    Model.update_forward_refs(**locals())
    Model(value=value)


def is_schema_field_valid(schema_field: type[Any], value: Any) -> bool:  # noqa: ANN401
    try:
        validate_schema_field(schema_field, value)
    except ValidationError:
        return False
    else:
        return True
