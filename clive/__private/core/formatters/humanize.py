from __future__ import annotations

import re
from typing import Any

import humanize
import inflection

from clive.__private.core.formatters.case import underscore
from clive.models import Asset, Operation


def humanize_class_name(cls: str | type[Any]) -> str:
    """
    Return pretty formatted class name.

    Args:
    ----
    cls: Class name or class itself.

    Examples:
    --------
    TransferToVestingOperation -> "Transfer to vesting operation"
    """
    class_name = cls if isinstance(cls, str) else cls.__name__
    return inflection.humanize(underscore(class_name))


def humanize_operation_name(operation: Operation) -> str:
    """
    Return pretty formatted operation name.

    Examples
    --------
    TransferToVestingOperation -> Transfer to vesting
    """
    return inflection.humanize(operation.get_name())


def humanize_operation_details(operation: Operation) -> str:
    """
    Return pretty formatted operation details (properties).

    Examples
    --------
    TransferToVestingOperation -> "from='alice', to='bob', amount='1.000 HIVE'"
    """
    out = ""

    operation_dict = dict(operation._iter(by_alias=True))
    for key, value in operation_dict.items():
        value_ = value

        # Display assets in legacy format.
        if isinstance(value, Asset.AnyT):  # type: ignore[arg-type]
            value_ = Asset.to_legacy(value)

        out += f"{key}='{value_}', "

    return out[:-2]


def humanize_hive_power(value: int) -> str:
    """Return pretty formatted hive power."""
    formatted_string = humanize.naturalsize(value, binary=False)
    if "Bytes" in formatted_string:
        return f"{value} HP"

    format_fix_regex = re.compile(r"(\d+\.\d*) (.)B")
    matched = format_fix_regex.match(formatted_string)
    assert matched is not None, "Given string does not match regex"
    return f"{matched[1]}{matched[2]} HP".upper()
