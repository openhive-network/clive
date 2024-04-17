from __future__ import annotations

import re
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Literal

import humanize
import inflection

from clive.__private.core.calculate_hp_from_votes import calculate_hp_from_votes
from clive.__private.core.calculate_participation_count import calculate_participation_count_percent
from clive.__private.core.calculate_vests_to_hive_ratio import calulcate_vests_to_hive_ratio
from clive.__private.core.constants import (
    HIVE_PERCENT_PRECISION_DOT_PLACES,
    NULL_ACCOUNT_KEY_VALUE,
    VESTS_TO_HIVE_RATIO_PRECISION_DOT_PLACES,
)
from clive.__private.core.decimal_conventer import (
    DecimalConverter,
)
from clive.__private.core.formatters.case import underscore
from clive.__private.core.iwax import calculate_current_inflation_rate, calculate_hp_apr
from clive.__private.core.percent_conversions import hive_percent_to_percent
from clive.models import Asset, Operation

if TYPE_CHECKING:
    from datetime import timedelta

    from clive.__private.core.iwax import (
        HpAPRProtocol,
        VestsToHpProtocol,
    )
    from clive.models.aliased import CurrentPriceFeed, HbdExchangeRate


def _round_to_precision(data: Decimal, precision: int) -> Decimal:
    return DecimalConverter.round_to_precision(data, precision=precision)


def _is_null_date(value: datetime) -> bool:
    _value = value.replace(tzinfo=None)
    return _value == datetime(1970, 1, 1, 0, 0, 0) or _value == datetime(1969, 12, 31, 23, 59, 59)


def align_to_dot(*strings: str) -> list[str]:
    """Aligns values to dot."""
    max_place_left_from_dot = max(string.find(".") for string in strings)

    aligned_strings = []
    for string in strings:
        aligned_string = string
        place_left_from_dot = string.find(".")
        if place_left_from_dot < max_place_left_from_dot:
            spaces_to_enter = max_place_left_from_dot - place_left_from_dot
            aligned_string = " " * spaces_to_enter + string
        aligned_strings.append(aligned_string)

    return aligned_strings


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


def humanize_datetime(value: datetime, *, with_time: bool = True, with_relative_time: bool = False) -> str:
    """
    Return pretty formatted datetime.

    Examples
    --------
    datetime(1970, 1, 1, 0, 0) -> "1970-01-01T00:00:00"
    """
    if _is_null_date(value):
        return "never"

    format_ = "%Y-%m-%dT%H:%M:%S" if with_time else "%Y-%m-%d"
    formatted = value.strftime(format_)
    if with_relative_time:
        return f"{formatted} ({humanize_natural_time(datetime.now(timezone.utc) - value.astimezone(timezone.utc))})"
    return formatted


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


def humanize_hbd_exchange_rate(hbd_exchange_rate: HbdExchangeRate) -> str:
    """Return pretty formatted hdb exchange rate (price feed)."""
    return f"{hbd_exchange_rate.base.pretty_amount()} $"


def humanize_hbd_savings_apr(hbd_savings_apr: int | Decimal) -> str:
    """Return pretty formatted hdb interese rate (APR)."""
    value = hbd_savings_apr if isinstance(hbd_savings_apr, Decimal) else hive_percent_to_percent(hbd_savings_apr)
    return f"{_round_to_precision(value, precision=HIVE_PERCENT_PRECISION_DOT_PLACES)} %"


def humanize_hbd_print_rate(hbd_print_rate: int | Decimal) -> str:
    """Return pretty formatted hdb print rate."""
    value = hbd_print_rate if isinstance(hbd_print_rate, Decimal) else hive_percent_to_percent(hbd_print_rate)
    return f"{_round_to_precision(value, precision=HIVE_PERCENT_PRECISION_DOT_PLACES)} %"


def humanize_apr(data: HpAPRProtocol | Decimal) -> str:
    """Return formatted APR value returned from wax."""
    calculated = data if isinstance(data, Decimal) else calculate_hp_apr(data)
    return f"{_round_to_precision(calculated, precision=HIVE_PERCENT_PRECISION_DOT_PLACES)} %"


def humanize_median_hive_price(current_price_feed: CurrentPriceFeed) -> str:
    """Return formatted median hbd price."""
    return f"{current_price_feed.base.pretty_amount()} $"


def humanize_current_inflation_rate(head_block_number: int) -> str:
    """Return formatted inflation rate for head block returned from wax."""
    return f"{calculate_current_inflation_rate(head_block_number)} %"


def humanize_participation_count(participation_count: int) -> str:
    """Return pretty formatted participation rate."""
    return f"{calculate_participation_count_percent(participation_count)} %"


def humanize_vest_to_hive_ratio(data: VestsToHpProtocol | Decimal) -> str:
    """Return pretty formatted vest to hive ratio."""
    calculated = data if isinstance(data, Decimal) else calulcate_vests_to_hive_ratio(data)
    return f"{_round_to_precision(calculated, precision=VESTS_TO_HIVE_RATIO_PRECISION_DOT_PLACES)}"


def humanize_bytes(value: int) -> str:
    """Return pretty formatted bytes."""
    return humanize.naturalsize(value, binary=True)


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
    asset_symbol = Asset.get_symbol(asset)
    if sign_prefix and int(asset.amount) != 0:
        # To not allow display + or - if balance is equal to zero.
        return f"{sign_prefix}{pretty_asset} {asset_symbol if show_symbol else ''}".rstrip()
    return f"{pretty_asset} {asset_symbol if show_symbol else ''}".rstrip()


def humanize_bool(value: bool) -> str:
    """Convert True/False to a more human-readable format."""
    if value:
        return "YES"
    return "NO"
