from __future__ import annotations

from typing import Any

from pydantic import BaseModel


def validate_schema_field(schema_field: type[Any], value: Any) -> None:
    """
    Validates the given value against the given schema field e.g. one that inherits from pydantic.ConstrainedStr.

    For validating models use `pydantic.validate_model` instead.

    Raises
    ------
    pydantic.ValidationError: if the given value is invalid.
    """

    class Model(BaseModel):
        value: schema_field  # type: ignore

    Model.update_forward_refs(**locals())
    Model(value=value)
