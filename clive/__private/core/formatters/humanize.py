from __future__ import annotations

import re
from datetime import datetime
from typing import TYPE_CHECKING, Any

import humanize
import inflection

from clive.__private.core.formatters.case import underscore
from clive.models import Asset, Operation

if TYPE_CHECKING:
    from datetime import timedelta


def _is_null_date(value: datetime) -> bool:
    return value == datetime(1970, 1, 1, 0, 0, 0)


def humanize_natural_time(value: datetime | timedelta) -> str:
    """
    Return pretty formatted relative time from now.

    Examples
    --------
    now=datetime(1971, 1, 1, 0, 0), value=datetime(2000, 1, 1, 0, 0) -> "29 years ago"
    now=datetime(1999, 2, 1, 0, 0), value=datetime(2000, 1, 1, 0, 0) -> "10 months ago"
    now=datetime(1999, 12, 31, 0, 0), value=datetime(2000, 1, 1, 0, 0) -> "a day ago"
    now=datetime(2000, 1, 1, 1, 30), value=datetime(2000, 1, 1, 0, 0) -> "an hour from now"
    """
    if isinstance(value, datetime) and _is_null_date(value):
        return "never"
    return humanize.naturaltime(value)


def humanize_datetime(value: datetime, *, with_time: bool = True) -> str:
    """
    Return pretty formatted datetime.

    Examples
    --------
    datetime(1970, 1, 1, 0, 0) -> "1970-01-01T00:00:00"
    """
    value = value.replace(tzinfo=None)
    if _is_null_date(value):
        return "never"

    format_ = "%Y-%m-%dT%H:%M:%S" if with_time else "%Y-%m-%d"
    return value.strftime(format_)


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
    if "Byte" in formatted_string:
        return f"{value} HP"

    format_fix_regex = re.compile(r"(\d+\.\d*) (.)B")
    matched = format_fix_regex.match(formatted_string)
    assert matched is not None, "Given string does not match regex"
    return f"{matched[1]}{matched[2]} HP".upper()
