from __future__ import annotations

from typing import TypeAlias

import test_tools as tt

from schemas.fields.basic import PublicKey

KwargsType: TypeAlias = None | str | bool | int | tt.Asset.AnyT | PublicKey


def option_to_string(value: KwargsType) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return str(value)
    if isinstance(value, tt.Asset.AnyT):  # type: ignore
        return value.as_legacy()
    if isinstance(value, PublicKey):
        return str(value)
    raise TypeError("Unsupported type")


def kwargs_to_cli_options(**kwargs: KwargsType) -> list[str]:
    options: list[str] = []
    for key, value in kwargs.items():
        option_name = key.strip("_").replace("_", "-")
        if value is True:
            options.append(f"--{option_name}")
        elif value is False:
            options.append(f"--no-{option_name}")
        elif value is not None:
            options.append(f"--{option_name}={option_to_string(value)}")
    return options
