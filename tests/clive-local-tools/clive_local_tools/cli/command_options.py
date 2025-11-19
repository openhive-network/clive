from __future__ import annotations

from copy import copy, deepcopy
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

import test_tools as tt

from clive.__private.models.schemas import PublicKey

from .exceptions import UnsupportedOptionError

if TYPE_CHECKING:
    from collections.abc import Mapping

type CLIParameterValue = str | int | Decimal | tt.Asset.AnyT | PublicKey | Path
type CLIArgumentValue = CLIParameterValue
type CLIOptionValue = bool | CLIParameterValue | list[CLIParameterValue] | None


def stringify_parameter_value(value: CLIParameterValue) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, tt.Asset.AnyT):
        return value.as_legacy()
    if isinstance(value, PublicKey):
        return str(value)
    raise UnsupportedOptionError(supported_type=CLIParameterValue, actual_type=type(value))


def build_cli_options(cli_named_options: Mapping[str, CLIOptionValue]) -> list[str]:
    options: list[str] = []
    for key, value in cli_named_options.items():
        option_name = key.strip("_").replace("_", "-")
        if value is True:
            options.append(f"--{option_name}")
        elif value is False:
            options.append(f"--no-{option_name}")
        elif isinstance(value, list):
            options.extend([f"--{option_name}={stringify_parameter_value(entry)}" for entry in value])
        elif value is not None:
            options.append(f"--{option_name}={stringify_parameter_value(value)}")
    return options


def extract_params(params: dict[str, CLIOptionValue], *param_names_to_drop: str) -> dict[str, CLIOptionValue]:
    # TODO: this should be CLITester instancemethod, not global function
    # deepcopy on self is not possible as it causes CLITester to be copied but it can't be because of Beekeeper
    copied_params = copy(params)
    copied_params.pop("self")
    named_params = deepcopy(copied_params)
    for name in param_names_to_drop:
        named_params.pop(name)
    return named_params
