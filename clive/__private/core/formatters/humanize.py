from __future__ import annotations

from typing import Any

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
