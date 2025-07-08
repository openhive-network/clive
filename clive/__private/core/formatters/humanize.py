from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Literal

import humanize
import inflection

from clive.__private.core.calculate_participation_count import calculate_participation_count_percent
from clive.__private.core.calculate_vests_to_hive_ratio import calculate_vests_to_hive_ratio
from clive.__private.core.constants.date import TIME_FORMAT_DAYS, TIME_FORMAT_WITH_SECONDS
from clive.__private.core.constants.node import NULL_ACCOUNT_KEY_VALUE
from clive.__private.core.constants.precision import (
    HIVE_PERCENT_PRECISION_DOT_PLACES,
    VESTS_TO_HIVE_RATIO_PRECISION_DOT_PLACES,
)
from clive.__private.core.date_utils import is_null_date, utc_now
from clive.__private.core.decimal_conventer import (
    DecimalConverter,
)
from clive.__private.core.formatters.case import underscore
from clive.__private.core.formatters.data_labels import (
    CURRENT_INFLATION_RATE_LABEL,
    HBD_EXCHANGE_RATE_LABEL,
    HBD_PRINT_RATE_LABEL,
    HBD_SAVINGS_APR_LABEL,
    HP_VEST_APR_LABEL,
    MEDIAN_HIVE_PRICE_LABEL,
    PARTICIPATION_COUNT_LABEL,
    VEST_HIVE_RATIO_LABEL,
)
from clive.__private.core.iwax import calculate_current_inflation_rate, calculate_hp_apr, calculate_witness_votes_hp
from clive.__private.models import Asset

if TYPE_CHECKING:
    from textual.validation import ValidationResult

    from clive.__private.core.iwax import (
        HpAPRProtocol,
        TotalVestingProtocol,
    )
    from clive.__private.models.schemas import HbdExchangeRate, OperationBase, PriceFeed


def _round_to_precision(data: Decimal, precision: int) -> Decimal:
    return DecimalConverter.round_to_precision(data, precision=precision)


type SignPrefixT = Literal["", "+", "-"]


def _maybe_labelize(label: str, text: str, *, add_label: bool = False) -> str:
    """Will conditionally labelize some text, when add_label param is set to True."""
    return f"{label + ':' if add_label else ''} {text}".lstrip()


def align_to_dot(*strings: str, center_to: int | str | None = None) -> list[str]:
    """Aligns values to dot. Optionally center the longest string to the center_to value."""
    strings_ = list(strings)

    if center_to is not None:
        if isinstance(center_to, str):
            center_to = len(center_to)

        longest_string = max(strings_, key=len)
        longest_string_index = strings_.index(longest_string)
        strings_.pop(longest_string_index)
        spaces_to_enter = center_to - len(longest_string)
        center_aligned_longest_string = " " * (spaces_to_enter // 2) + longest_string + " " * (spaces_to_enter // 2)
        strings_.insert(longest_string_index, center_aligned_longest_string)

    max_place_left_from_dot = max(string.find(".") for string in strings_)

    aligned_strings = []
    for string in strings_:
        aligned_string = string
        place_left_from_dot = string.find(".")
        if place_left_from_dot < max_place_left_from_dot:
            spaces_to_enter = max_place_left_from_dot - place_left_from_dot
            aligned_string = " " * spaces_to_enter + string
        aligned_strings.append(aligned_string)

    return aligned_strings


def humanize_validation_result(result: ValidationResult) -> str:
    """Return failure description from ValidationResult if any exists, otherwise returns 'No failures' message."""
    if result.is_valid:
        return "No failures"

    if len(result.failure_descriptions) > 1:
        return str(result.failure_descriptions)
    return result.failure_descriptions[0]


def humanize_natural_time(value: datetime | timedelta) -> str:
    """
    Return pretty formatted relative time from now.

    Args:
        value: A datetime or timedelta object representing the time to be humanized.

    Examples:
    now=datetime(1971, 1, 1, 0, 0), value=datetime(2000, 1, 1, 0, 0) -> "29 years ago"
    now=datetime(1999, 2, 1, 0, 0), value=datetime(2000, 1, 1, 0, 0) -> "10 months ago"
    now=datetime(1999, 12, 31, 0, 0), value=datetime(2000, 1, 1, 0, 0) -> "a day ago"
    now=datetime(2000, 1, 1, 1, 30), value=datetime(2000, 1, 1, 0, 0) -> "an hour from now"
    """
    if isinstance(value, datetime) and is_null_date(value):
        return "never"
    return humanize.naturaltime(value)


def humanize_datetime(value: datetime, *, with_time: bool = True, with_relative_time: bool = False) -> str:
    """
    Return pretty formatted datetime.

    Args:
        value: A datetime object to be formatted.
        with_time: Whether to include time in the output.
        with_relative_time: Whether to include relative time from now.

    Examples:
    datetime(1970, 1, 1, 0, 0) -> "1970-01-01T00:00:00"
    """
    if is_null_date(value):
        return "never"

    format_ = TIME_FORMAT_WITH_SECONDS if with_time else TIME_FORMAT_DAYS
    formatted = value.strftime(format_)
    if with_relative_time:
        return f"{formatted} ({humanize_natural_time(utc_now() - value.astimezone(UTC))})"
    return formatted


def humanize_class_name(cls: str | type[Any]) -> str:
    """
    Return pretty formatted class name.

    Args:
        cls: Class name or class itself.

    Examples:
    TransferToVestingOperation -> "Transfer to vesting operation"
    """
    class_name = cls if isinstance(cls, str) else cls.__name__
    return inflection.humanize(underscore(class_name))


def humanize_operation_name(operation: OperationBase) -> str:
    """
    Return pretty formatted operation name.

    Args:
        operation: An instance of OperationBase or its subclass.

    Examples:
    TransferToVestingOperation -> Transfer to vesting
    """
    return inflection.humanize(operation.get_name())


def humanize_operation_details(operation: OperationBase) -> str:
    """
    Return pretty formatted operation details (properties).

    Args:
        operation: An instance of OperationBase or its subclass.

    Examples:
    TransferToVestingOperation -> "from='alice', to='bob', amount='1.000 HIVE'"
    """
    out = ""

    operation_dict = dict(operation._iter(by_alias=True))
    for key, value in operation_dict.items():
        value_ = value

        # Display assets in legacy format.
        if isinstance(value, Asset.AnyT):
            value_ = Asset.to_legacy(value)

        out += f"{key}='{value_}', "

    return out[:-2]


def humanize_hive_power(value: Asset.Hive, *, use_short_form: bool = True, show_symbol: bool = True) -> str:
    """Return pretty formatted hive power."""
    symbol = "HP" if show_symbol else ""

    if not use_short_form:
        return f"{value.pretty_amount()} {symbol}".rstrip()

    formatted_string = humanize.naturalsize(value.pretty_amount(), binary=False)

    if "Byte" in formatted_string:
        return f"{value.pretty_amount()} {symbol}".rstrip()

    format_fix_regex = re.compile(r"(\d+\.\d*) (.)B")
    matched = format_fix_regex.match(formatted_string)
    assert matched is not None, "Given string does not match regex"
    new_value = matched[1]
    unit = matched[2]
    return f"{new_value}{unit} {symbol}".upper().rstrip()


def humanize_hive_power_with_comma(hive_power: Asset.Hive, *, show_symbol: bool = True) -> str:
    """Return pretty hive power."""
    symbol = "HP" if show_symbol else ""
    hp_value_with_commas = humanize.intcomma(hive_power.as_float(), ndigits=Asset.get_precision(Asset.Hive))
    return f"{hp_value_with_commas} {symbol}".rstrip()


def humanize_hbd_exchange_rate(hbd_exchange_rate: HbdExchangeRate, *, with_label: bool = False) -> str:
    """Return pretty formatted hdb exchange rate (price feed)."""
    return _maybe_labelize(HBD_EXCHANGE_RATE_LABEL, f"{hbd_exchange_rate.base.pretty_amount()} $", add_label=with_label)


def humanize_hbd_savings_apr(hbd_savings_apr: Decimal, *, with_label: bool = False) -> str:
    """Return pretty formatted hdb interese rate (APR)."""
    return _maybe_labelize(HBD_SAVINGS_APR_LABEL, humanize_percent(hbd_savings_apr), add_label=with_label)


def humanize_hbd_print_rate(hbd_print_rate: Decimal, *, with_label: bool = False) -> str:
    """Return pretty formatted hdb print rate."""
    return _maybe_labelize(HBD_PRINT_RATE_LABEL, humanize_percent(hbd_print_rate), add_label=with_label)


def humanize_apr(data: HpAPRProtocol | Decimal) -> str:
    """Return formatted APR value returned from wax."""
    calculated = data if isinstance(data, Decimal) else calculate_hp_apr(data)
    return humanize_percent(calculated)


def humanize_hp_vests_apr(data: HpAPRProtocol | Decimal, *, with_label: bool = False) -> str:
    """Return formatted text describing APR value returned from wax."""
    return _maybe_labelize(HP_VEST_APR_LABEL, humanize_apr(data), add_label=with_label)


def humanize_median_hive_price(current_price_feed: PriceFeed, *, with_label: bool = False) -> str:
    """Return formatted median hive price."""
    return _maybe_labelize(MEDIAN_HIVE_PRICE_LABEL, current_price_feed.base.pretty_amount(), add_label=with_label)


def humanize_current_inflation_rate(head_block_number: int, *, with_label: bool = False) -> str:
    """Return formatted inflation rate for head block returned from wax."""
    inflation = calculate_current_inflation_rate(head_block_number)
    return _maybe_labelize(CURRENT_INFLATION_RATE_LABEL, humanize_percent(inflation), add_label=with_label)


def humanize_participation_count(participation_count: int, *, with_label: bool = False) -> str:
    """Return pretty formatted participation rate."""
    participation_count_percent = calculate_participation_count_percent(participation_count)
    return _maybe_labelize(
        PARTICIPATION_COUNT_LABEL, humanize_percent(participation_count_percent), add_label=with_label
    )


def humanize_vest_to_hive_ratio(
    data: TotalVestingProtocol | Decimal, *, with_label: bool = False, show_symbol: bool = False
) -> str:
    """Return pretty formatted vest to hive ratio."""
    calculated = data if isinstance(data, Decimal) else calculate_vests_to_hive_ratio(data)
    symbol = f" {Asset.get_symbol(Asset.Vests)}" if show_symbol else ""
    return _maybe_labelize(
        VEST_HIVE_RATIO_LABEL,
        f"{_round_to_precision(calculated, precision=VESTS_TO_HIVE_RATIO_PRECISION_DOT_PLACES)}{symbol}",
        add_label=with_label,
    )


def humanize_bytes(value: int) -> str:
    """Return pretty formatted bytes."""
    return humanize.naturalsize(value, binary=True)


def humanize_witness_status(signing_key: str) -> str:
    """Return active/inactive string, witness is inactive if it has public key set to null account."""
    return "active" if signing_key != NULL_ACCOUNT_KEY_VALUE else "inactive"


def humanize_votes_with_suffix(votes: int, data: TotalVestingProtocol) -> str:
    """Return pretty formatted votes converted to hive power with K, M etc. suffix."""
    hive_power = calculate_witness_votes_hp(votes, data)
    return humanize_hive_power(hive_power)


def humanize_votes_with_comma(votes: int, data: TotalVestingProtocol) -> str:
    """Return pretty formatted votes converted to hive power."""
    hive_power = calculate_witness_votes_hp(votes, data)
    return f"{humanize.intcomma(hive_power.as_float(), ndigits=Asset.get_precision(Asset.Hive))} HP"


def humanize_asset(asset: Asset.AnyT, *, show_symbol: bool = True, sign_prefix: SignPrefixT = "") -> str:
    pretty_asset = Asset.pretty_amount(asset)
    asset_symbol = Asset.get_symbol(asset)
    if sign_prefix and int(asset.amount) != 0:
        # To not allow display + or - if balance is equal to zero.
        return f"{sign_prefix}{pretty_asset} {asset_symbol if show_symbol else ''}".rstrip()
    return f"{pretty_asset} {asset_symbol if show_symbol else ''}".rstrip()


def humanize_bool(value: bool) -> str:  # noqa: FBT001
    """Convert True/False to a more human-readable format."""
    if value:
        return "YES"
    return "NO"


def humanize_percent(hive_percent: Decimal) -> str:
    """Convert percent Decimal to percent string in human-readable format."""
    return f"{_round_to_precision(hive_percent, precision=HIVE_PERCENT_PRECISION_DOT_PLACES)} %"


def humanize_timedelta(value: timedelta) -> str:
    """
    Return pretty formatted timedelta.

    Args:
        value: A timedelta object to be formatted.

    Examples:
    timedelta(days=730) -> 2 years
    timedelta(days=2016) -> 5 years, 6 months and 8 days
    timedelta(days=6720) -> 18 years, 4 months and 28 days
    """
    return humanize.precisedelta(value)


def humanize_manabar_regeneration_time(regeneration_time: timedelta) -> str:
    """Return pretty information about regeneration time."""

    def is_full() -> bool:
        return regeneration_time == timedelta(seconds=0)

    if is_full():
        return "Full!"
    return humanize_natural_time(-regeneration_time)
