from __future__ import annotations

from copy import copy, deepcopy
from pathlib import Path

import test_tools as tt

from clive.__private.models.schemas import PublicKey

from .exceptions import UnsupportedOptionError

type StringConvertibleOptionTypes = str | int | tt.Asset.AnyT | PublicKey | Path
type CliOptionT = (
    bool
    | StringConvertibleOptionTypes
    | list[StringConvertibleOptionTypes]
    | tuple[StringConvertibleOptionTypes, ...]
    | None
)


def option_to_string(value: StringConvertibleOptionTypes) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, tt.Asset.AnyT):
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
        elif isinstance(value, tuple):
            options.append(f"--{option_name}")
            options.extend([option_to_string(entry) for entry in value])
        elif value is not None:
            options.append(f"--{option_name}={option_to_string(value)}")
    return options


def extract_params(params: dict[str, CliOptionT], *param_names_to_drop: str) -> dict[str, CliOptionT]:
    # TODO: this should be CLITester instancemethod, not global function
    # deepcopy on self is not possible as it causes CLITester to be copied but it can't be because of Beekeeper
    copied_params = copy(params)
    copied_params.pop("self")
    named_params = deepcopy(copied_params)
    for name in param_names_to_drop:
        named_params.pop(name)
    return named_params
