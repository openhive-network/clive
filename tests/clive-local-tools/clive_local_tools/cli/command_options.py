from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import TypeAlias

import test_tools as tt

from schemas.fields.basic import PublicKey

from .exceptions import UnsupportedOptionError

StringConvertibleOptionTypes: TypeAlias = str | int | tt.Asset.AnyT | PublicKey
CliOptionT: TypeAlias = bool | StringConvertibleOptionTypes | list[StringConvertibleOptionTypes] | None


def option_to_string(value: StringConvertibleOptionTypes) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    # mypy gives false positive here: https://github.com/python/mypy/issues/16707
    if isinstance(value, tt.Asset.AnyT):  # type: ignore[arg-type]
        return value.as_legacy()
    if isinstance(value, PublicKey):
        return str(value)
    raise UnsupportedOptionError(supported_type=StringConvertibleOptionTypes, actual_type=type(value))


def kwargs_to_cli_options(**cli_options: CliOptionT) -> list[str]:
    options: list[str] = []
    for key, value in cli_options.items():
        option_name = key.strip("_").replace("_", "-")
        if value is True:
            options.append(f"--{option_name}")
        elif value is False:
            options.append(f"--no-{option_name}")
        elif isinstance(value, list):
            options.extend([f"--{option_name}={option_to_string(entry)}" for entry in value])
        elif value is not None:
            options.append(f"--{option_name}={option_to_string(value)}")
    return options


def extract_params(params: dict[str, CliOptionT], *param_names_to_drop: str) -> dict[str, CliOptionT]:
    named_params = deepcopy(params)
    named_params.pop("self")
    for name in param_names_to_drop:
        named_params.pop(name)
    return named_params
