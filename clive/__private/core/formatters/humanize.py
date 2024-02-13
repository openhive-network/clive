from __future__ import annotations

import re
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

import humanize
import inflection

from clive.__private.core.calculate_hp_from_votes import calculate_hp_from_votes
from clive.__private.core.constants import NULL_ACCOUNT_KEY_VALUE
from clive.__private.core.formatters.case import underscore
from clive.models import Asset, Operation

if TYPE_CHECKING:
    from datetime import timedelta

    from schemas.fields.assets.hbd import AssetHbdHF26
    from schemas.fields.assets.hive import AssetHiveHF26
    from schemas.fields.compound import HbdExchangeRate


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


def humanize_hbd_exchange_rate(hbd_exchange_rate: HbdExchangeRate[AssetHiveHF26, AssetHbdHF26]) -> str:
    """Return pretty formatted hdb exchange rate (price feed)."""
    price_feed = int(hbd_exchange_rate.base.amount) / 10**3
    return f"{price_feed:.3f} $"


def humanize_hbd_interest_rate(hbd_interest_rate: int) -> str:
    """Return pretty formatted hdb interese rate (APR)."""
    percent = hbd_interest_rate / 100
    return f"{round(percent, 2)}%"


def humanize_witness_status(signing_key: str) -> str:
    """Return active/inactive string, witness is inactive if it has public key set to null account."""
    return "active" if signing_key != NULL_ACCOUNT_KEY_VALUE else "inactive"


def humanize_votes_with_suffix(
    votes: int, total_vesting_fund_hive: Asset.Hive, total_vesting_shares: Asset.Vests
) -> str:
    """Return pretty formatted votes converted to hive power with K, M etc. suffix."""
    hive_power = calculate_hp_from_votes(votes, total_vesting_fund_hive, total_vesting_shares)
    return humanize_hive_power(hive_power)


def humanize_votes_with_comma(
    votes: int, total_vesting_fund_hive: Asset.Hive, total_vesting_shares: Asset.Vests
) -> str:
    """Return pretty formatted votes converted to hive power."""
    hive_power = calculate_hp_from_votes(votes, total_vesting_fund_hive, total_vesting_shares)
    return f"{humanize.intcomma(hive_power, ndigits=0)} HP"


def humanize_asset(asset: Asset.AnyT, *, show_symbol: bool = True, sign_prefix: Literal["", "+", "-"] = "") -> str:
    pretty_asset = Asset.pretty_amount(asset)
    asset_symbol = asset.get_asset_information().symbol[0]
    if sign_prefix and int(asset.amount) != 0:
        # To not allow display + or - if balance is equal to zero.
        return f"{sign_prefix}{pretty_asset} {asset_symbol if show_symbol else ''}".rstrip()
    return f"{pretty_asset} {asset_symbol if show_symbol else ''}".rstrip()
