from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
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
from clive.__private.core.relative_path import get_relative_or_whole_path
from clive.__private.models import Asset

if TYPE_CHECKING:
    from textual.validation import ValidationResult

    from clive.__private.core.iwax import (
        HpAPRProtocol,
        TotalVestingProtocol,
    )
    from clive.__private.models.schemas import HbdExchangeRate, PriceFeed
    from clive.__private.models.operations import OperationBase


def _round_to_precision(data: Decimal, precision: int) -> Decimal:
    return DecimalConverter.round_to_precision(data, precision=precision)


type SignPrefixT = Literal["", "+", "-"]


def _maybe_labelize(label: str, text: str, *, add_label: bool = False) -> str:
    """
    Will conditionally labelize some text.

    Args:
        label: A label that can be added to the text.
        text: A text that can be labeled.
        add_label: Whether to labelize a given text or keep it unchanged.

    Example:
        >>> _maybe_labelize("Name", "alice")
        'alice'
        >>> _maybe_labelize("Name", "alice", add_label=True)
        'Name: alice'

    Returns:
        A labeled text or the original text.
    """
    return f"{label + ':' if add_label else ''} {text}".lstrip()


def align_to_dot(*strings: str, center_to: int | str | None = None) -> list[str]:
    """
    Aligns values to dot. Optionally center the longest string to the center_to value.

    Args:
        *strings: A variable number of strings to align.
        center_to: A value representing the length to center the longest string.

    Example:
        >>> align_to_dot("2.00 %", "6.00 %", "3.00 %", "12.00 %")
        [" 2.00 %", " 6.00 %", " 3.00 %", "12.00 %"]
        >>> align_to_dot("2.00 %", "6.00 %", "3.00 %", "12.00 %", "100.00%")
        ["  2.00 %", "  6.00 %", "  3.00 %", " 12.00 %", "100.00%"]
        >>> align_to_dot("2.00 %", "6.00 %", "3.00 %", "12.00 %", "100.00 %", center_to=8)
        ["  2.00 %", "  6.00 %", "  3.00 %", " 12.00 %", "100.00 %"]
        >>> align_to_dot("2.00 %", "6.00 %", "3.00 %", "12.00 %", "100.00 %", center_to="sometext")
        ["    2.00 %", "    6.00 %", "    3.00 %", "   12.00 %", "  100.00 %  "]


    Returns:
        Values aligned to the dot.
    """
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


def humanize_binding_id(id_: str) -> str:
    """
    Generates a human-readable description from a binding id.

    Args:
        id_: The binding id to be humanized.

    Example:
        >>> humanize_binding_id("lock_wallet")
        "Lock wallet"
        >>> humanize_binding_id("transfer_to_vesting")
        "Transfer to vesting"

    Returns:
        A human-readable description of the binding id.
    """
    return inflection.humanize(id_)


def humanize_validation_result(result: ValidationResult) -> str:
    """
    Return pretty formatted validation result.

    Args:
        result: An object containing the validation result.

    Example:
        >>> humanize_validation_result(ValidationResult(failures=[]))
        "No failures"
        >>> humanize_validation_result(ValidationResult(failures=[Failure(validator=BadAccountValidator, value='#',
           description='Invalid account name')]))
        "Invalid account name"
        >>> humanize_validation_result(ValidationResult(failures=[Failure(validator=PrivateKeyValidator,
            value='5KTNAYSHVzhnVPrwHpKhc5QqNQt6aW8JsrMT7T4hyrKydzYvYi', description='Invalid private key format.'),
            Failure(validator=PrivateKeyValidator, value='5KTNAYSHVzhnVPrwHpKhc5QqNQt6aW8JsrMT7T4hyrKydzYvYi',
            description='Does not match the expected public key.')]))
        ["Invalid private key format.", "Does not match the expected public key."]

    Returns:
        A human-readable data describing the validation result.
    """
    if result.is_valid:
        return "No failures"

    if len(result.failure_descriptions) > 1:
        return str(result.failure_descriptions)
    return result.failure_descriptions[0]


def humanize_natural_time(value: datetime | timedelta) -> str:
    """
    Return pretty formatted relative time from now.

    Args:
        value: An object representing the relative time.

    Example:
        Assuming that the current time is `datetime(2000, 1, 1, 0, 0)`:

        >>> humanize_natural_time(datetime(1971, 1, 1, 0, 0))
        "29 years ago"
        >>> humanize_natural_time(datetime(1999, 2, 1, 0, 0))
        "10 months ago"
        >>> humanize_natural_time(datetime(1999, 12, 31, 0, 0))
        "a day ago"
        >>> humanize_natural_time(datetime(2000, 1, 1, 1, 30))
        "an hour from now"

    Returns:
        A human-readable data representing the time difference.
    """
    if isinstance(value, datetime) and is_null_date(value):
        return "never"
    return humanize.naturaltime(value)


def humanize_datetime(value: datetime, *, with_time: bool = True, with_relative_time: bool = False) -> str:
    """
    Return pretty formatted datetime.

    Args:
        value: An object to be formatted.
        with_time: Whether to include time in the output.
        with_relative_time: Whether to include relative time from now.

    Example:
        >>> humanize_datetime(datetime(1970, 1, 1, 0, 0))
        'never'
        >>> humanize_datetime(datetime(2025, 1, 1, 0, 0))
        '2025-01-01T00:00:00'
        >>> humanize_datetime(datetime(2025, 1, 1, 0, 0), with_time=False)
        '2025-01-01'
        >>> humanize_datetime(datetime(2025, 1, 1, 0, 0), with_relative_time=True)
        '2025-01-01T00:00:00 (6 months ago)'
        >>> humanize_datetime(datetime(2050, 1, 1), with_relative_time=True)
        '2050-01-01T00:00:00 (24 years from now)'
        >>> humanize_datetime(datetime(2000, 1, 1), with_time=False, with_relative_time=True)
        '2000-01-01 (25 years ago)'

    Returns:
        A human-readable data representing the datetime.
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

    Example:
        >>> humanize_class_name(TransferToVestingOperation)
        "Transfer to vesting operation"

    Returns:
        A human-readable data representing the class name.
    """
    class_name = cls if isinstance(cls, str) else cls.__name__
    return inflection.humanize(underscore(class_name))


def humanize_operation_name(operation: OperationBase | type[OperationBase]) -> str:
    """
    Return pretty formatted operation name.

    Args:
        operation: Operation to be formatted.

    Example:
        >>> humanize_operation_name(TransferToVestingOperation)
        "Transfer to vesting"

    Returns:
        A human-readable data representing the operation name.
    """
    return inflection.humanize(operation.get_name())


def humanize_operation_details(operation: OperationBase) -> str:
    """
    Return pretty formatted operation details (properties).

    Args:
        operation: Operation to be formatted.

    Example:
        >>> operation = TransferToVestingOperation(from_='alice', to='bob', amount='1.000 HIVE')
        >>> humanize_operation_details(operation)
        "from='alice', to='bob', amount='1.000 HIVE'"

    Returns:
        Human-readable operation details.
    """
    out = ""

    operation_dict = operation.dict()

    for key, value in operation_dict.items():
        value_ = value

        # Display assets in legacy format.
        if isinstance(value, Asset.AnyT):
            value_ = Asset.to_legacy(value)

        out += f"{key}='{value_}', "

    return out[:-2]


def humanize_hive_power(value: Asset.Hive, *, use_short_form: bool = True, show_symbol: bool = True) -> str:
    """
    Return pretty formatted hive power.

    Args:
        value: An asset representing the hive power.
        use_short_form: Whether to use a short form.
        show_symbol: Whether to show the HP symbol.

    Example:
        >>> asset = Asset.hive(1035.401)
        >>> humanize_hive_power(asset)
        "1.0K HP"
        >>> humanize_hive_power(asset, use_short_form=False)
        "1035.401 HP"
        >>> humanize_hive_power(asset, show_symbol=False)
        "1.0K"

    Returns:
        A human-readable data representing the hive power.
    """
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
    """
    Return pretty formatted hive power including commas.

    Args:
        hive_power: A value representing the hive power.
        show_symbol: Whether to show the HP symbol.

    Example:
        >>> asset = Asset.hive(1035.401)
        >>> humanize_hive_power_with_comma(asset)
        "1,035.401 HP"
        >>> humanize_hive_power_with_comma(asset, show_symbol=False)
        "1,035.401"

    Returns:
        A human-readable data representing the hive power with commas.
    """
    symbol = "HP" if show_symbol else ""
    hp_value_with_commas = humanize.intcomma(hive_power.as_float(), ndigits=Asset.get_precision(Asset.Hive))
    return f"{hp_value_with_commas} {symbol}".rstrip()


def humanize_hbd_exchange_rate(hbd_exchange_rate: HbdExchangeRate, *, with_label: bool = False) -> str:
    """
    Return pretty formatted hdb exchange rate (price feed).

    Args:
        hbd_exchange_rate: An object containing the exchange rate.
        with_label: Whether to add a label to the output.

    Example:
        >>> exchange_rate = HbdExchangeRate(base=Asset.Hbd(0.242), quote=Asset.Hive(1))
        >>> humanize_hbd_exchange_rate(exchange_rate)
        "0.242 $"
        >>> humanize_hbd_exchange_rate(exchange_rate, with_label=True)
        "price feed: 0.242 $"

    Returns:
        A human-readable data representing the HBD exchange rate.
    """
    return _maybe_labelize(HBD_EXCHANGE_RATE_LABEL, f"{hbd_exchange_rate.base.pretty_amount()} $", add_label=with_label)


def humanize_hbd_savings_apr(hbd_savings_apr: Decimal, *, with_label: bool = False) -> str:
    """
    Return pretty formatted hdb interese rate (APR).

    Args:
        hbd_savings_apr: A value representing the HBD savings APR.
        with_label: Whether to add a label to the output.

    Example:
        >>> humanize_hbd_savings_apr(Decimal(15)))
        "15.00 %"
        >>> humanize_hbd_savings_apr(Decimal(15), with_label=True)
        "HBD savings APR: 15.00 %"

    Returns:
        A human-readable data representing the HBD savings APR.
    """
    return _maybe_labelize(HBD_SAVINGS_APR_LABEL, humanize_percent(hbd_savings_apr), add_label=with_label)


def humanize_hbd_print_rate(hbd_print_rate: Decimal, *, with_label: bool = False) -> str:
    """
    Return pretty formatted hdb print rate.

    Args:
        hbd_print_rate: A value representing the HBD print rate.
        with_label: Whether to add a label to the output.

    Example:
        >>> humanize_hbd_print_rate(Decimal(100)))
        "100.00 %"
        >>> humanize_hbd_savings_apr(Decimal(100), with_label=True)
        "HBD print rate: 100.00 %"

    Returns:
        A human-readable data representing the HBD print rate.
    """
    return _maybe_labelize(HBD_PRINT_RATE_LABEL, humanize_percent(hbd_print_rate), add_label=with_label)


def humanize_apr(data: HpAPRProtocol | Decimal) -> str:
    """
    Return formatted APR value returned from wax.

    Args:
        data: An instance representing the APR value.

    Example:
        >>> humanize_apr(Decimal(100)))
        "100.00 %"

    Returns:
        A human-readable data representing the APR value.
    """
    calculated = data if isinstance(data, Decimal) else calculate_hp_apr(data)
    return humanize_percent(calculated)


def humanize_hp_vests_apr(data: HpAPRProtocol | Decimal, *, with_label: bool = False) -> str:
    """
    Return formatted text describing APR value returned from wax.

    Args:
        data: An instance representing the APR value.
        with_label: Whether to add a label to the output.

    Example:
        >>> humanize_hp_vests_apr(Decimal("2.94"))
        "2.94 %"
        >>> humanize_hp_vests_apr(Decimal("2.94"), with_label=True))
        "HP/VESTS APR: 2.94 %"

    Returns:
        A human-readable data representing the APR value with an optional label.
    """
    return _maybe_labelize(HP_VEST_APR_LABEL, humanize_apr(data), add_label=with_label)


def humanize_median_hive_price(current_price_feed: PriceFeed, *, with_label: bool = False) -> str:
    """
    Return formatted median hive price.

    Args:
        current_price_feed: An instance containing the current price.
        with_label: Whether to add a label to the output.

    Example:
        >>> current_price_feed = PriceFeed(base=Asset.Hbd(0.239), quote=Asset.Hive(1))
        >>> humanize_median_hive_price(current_price_feed)
        "0.239"
        >>> humanize_median_hive_price(current_price_feed, with_label=True))
        "median Hive price: 0.239"

    Returns:
        A human-readable data representing the median hive price.
    """
    return _maybe_labelize(MEDIAN_HIVE_PRICE_LABEL, current_price_feed.base.pretty_amount(), add_label=with_label)


def humanize_current_inflation_rate(head_block_number: int, *, with_label: bool = False) -> str:
    """
    Return formatted inflation rate for head block returned from wax.

    Args:
        head_block_number: The head block number to calculate the inflation rate.
        with_label: Whether to add a label to the output.

    Example:
        >>> humanize_current_inflation_rate(98063585)
        "5.86 %"
        >>> humanize_current_inflation_rate(98063585, with_label=True))
        "current inflation rate: 5.86 %"

    Returns:
        A human-readable data representing the current inflation rate.
    """
    inflation = calculate_current_inflation_rate(head_block_number)
    return _maybe_labelize(CURRENT_INFLATION_RATE_LABEL, humanize_percent(inflation), add_label=with_label)


def humanize_participation_count(participation_count: int, *, with_label: bool = False) -> str:
    """
    Return pretty formatted participation rate.

    Args:
        participation_count: A value representing the participation count.
        with_label: Whether to add a label to the output.

    Example:
        >>> humanize_participation_count(128)
        "100.00 %"
        >>> humanize_participation_count(128, with_label=True)
        "participation: 100.00 %"

    Returns:
        A human-readable data representing the participation count percentage.
    """
    participation_count_percent = calculate_participation_count_percent(participation_count)
    return _maybe_labelize(
        PARTICIPATION_COUNT_LABEL, humanize_percent(participation_count_percent), add_label=with_label
    )


def humanize_vest_to_hive_ratio(
    data: TotalVestingProtocol | Decimal, *, with_label: bool = False, show_symbol: bool = False
) -> str:
    """
    Return pretty formatted vest to hive ratio.

    Args:
        data: An instance representing the vest to hive ratio.
        with_label: Whether to add a label to the output.
        show_symbol: Whether to show the VEST symbol.

    Example:
        >>> humanize_vest_to_hive_ratio(Decimal(1500))
        "1500.000"
        >>> humanize_vest_to_hive_ratio(Decimal(1500), show_symbol=True)
        "1500.000 VESTS"
        >>> humanize_vest_to_hive_ratio(Decimal(1500), with_label=True, show_symbol=True)
        ""VESTS/HIVE ratio: 1500.000 VESTS"

    Returns:
        A human-readable data representing the vest to hive ratio.
    """
    calculated = data if isinstance(data, Decimal) else calculate_vests_to_hive_ratio(data)
    symbol = f" {Asset.get_symbol(Asset.Vests)}" if show_symbol else ""
    return _maybe_labelize(
        VEST_HIVE_RATIO_LABEL,
        f"{_round_to_precision(calculated, precision=VESTS_TO_HIVE_RATIO_PRECISION_DOT_PLACES)}{symbol}",
        add_label=with_label,
    )


def humanize_bytes(value: int) -> str:
    """
    Return pretty formatted bytes.

    Args:
        value: A value representing the number of bytes.

    Example:
        >>> humanize_bytes(65536)
        "64.0 KiB"
    Returns:
        A human-readable data representing the size in bytes.
    """
    return humanize.naturalsize(value, binary=True)


def humanize_witness_status(signing_key: str) -> str:
    """
    Return active/inactive string, witness is inactive if it has public key set to null account.

    Args:
        signing_key: The signing key of the witness.

    Example:
        >>> humanize_witness_status("STM8PFEEhF9g3PMZu9mu9vso56bzP6i4aMYM73aWL8CkcKi4LEGLR")
        "active"

    Returns:
        A value indicating whether the witness is "active" or "inactive".
    """
    return "active" if signing_key != NULL_ACCOUNT_KEY_VALUE else "inactive"


def humanize_votes_with_suffix(votes: int, data: TotalVestingProtocol) -> str:
    """
    Return pretty formatted votes converted to hive power with K, M etc. suffix.

    Args:
        votes: A value representing the number of votes.
        data: An instance containing vesting data.

    Example:
        >>> @dataclasses.dataclass
        ... class ImplementsTotalVestingProtocol:
        ...     total_vesting_fund_hive: Asset.Hive
        ...     total_vesting_shares: Asset.Vests
        >>> humanize_votes_with_suffix(
        ...     1_234_567_890,
        ...     ImplementsTotalVestingProtocol(
        ...         Asset.hive(1_000_000_000),
        ...         Asset.vests(1_000_000_000),
        ...     )
        ... )
        "1.2K HP"

    Returns:
        A human-readable data representing the votes converted to hive power with suffix.
    """
    hive_power = calculate_witness_votes_hp(votes, data)
    return humanize_hive_power(hive_power)


def humanize_votes_with_comma(votes: int, data: TotalVestingProtocol) -> str:
    """
    Return pretty formatted votes converted to hive power.

    Args:
        votes: A value representing the number of votes.
        data: An instance containing vesting data.

    Example:
        >>> @dataclasses.dataclass
        ... class ImplementsTotalVestingProtocol:
        ...     total_vesting_fund_hive: Asset.Hive
        ...     total_vesting_shares: Asset.Vests
        >>> humanize_votes_with_comma(
        ...     1_234_567_890,
        ...     ImplementsTotalVestingProtocol(
        ...         Asset.hive(1_000_000_000),
        ...         Asset.vests(1_000_000_000),
        ...     )
        ... )
        "1,234.567 HP"

    Returns:
        A human-readable data representing the votes converted to hive power with commas.
    """
    hive_power = calculate_witness_votes_hp(votes, data)
    return f"{humanize.intcomma(hive_power.as_float(), ndigits=Asset.get_precision(Asset.Hive))} HP"


def humanize_asset(asset: Asset.AnyT, *, show_symbol: bool = True, sign_prefix: SignPrefixT = "") -> str:
    """
    Generate pretty formatted asset.

    Args:
        asset: An asset to be formatted.
        show_symbol: Whether to show the asset symbol.
        sign_prefix: A prefix to be added to the asset amount.

    Example:
        >>> asset = Asset.Hive(1035.401)
        >>> humanize_asset(asset)
        "1.0K HIVE"
        >>> humanize_asset(asset, show_symbol=False)
        "1.0K"
        >>> humanize_asset(asset, sign_prefix="+")
        "+1.0K HIVE"

    Returns:
        A human-readable data representing the asset amount with an optional symbol.
    """
    pretty_asset = Asset.pretty_amount(asset)
    asset_symbol = Asset.get_symbol(asset)
    if sign_prefix and int(asset.amount) != 0:
        # To not allow display + or - if balance is equal to zero.
        return f"{sign_prefix}{pretty_asset} {asset_symbol if show_symbol else ''}".rstrip()
    return f"{pretty_asset} {asset_symbol if show_symbol else ''}".rstrip()


def humanize_bool(value: bool) -> str:  # noqa: FBT001
    """
    Convert True/False to a more human-readable format.

    Args:
        value: A boolean value to be converted.

    Example:
        >>> humanize_bool(True)
        "YES"
        >>> humanize_bool(False)
        "NO"

    Returns:
        A string "YES" if value is True, otherwise "NO".
    """
    if value:
        return "YES"
    return "NO"


def humanize_percent(hive_percent: Decimal) -> str:
    """
    Convert percent Decimal to percent string in human-readable format.

    Args:
        hive_percent: A value representing the percentage value.

    Example:
        >>> humanize_percent(Decimal(100))
        "100.00 %"

    Returns:
        A data representing the percentage value rounded to the defined precision.
    """
    return f"{_round_to_precision(hive_percent, precision=HIVE_PERCENT_PRECISION_DOT_PLACES)} %"


def humanize_timedelta(value: timedelta) -> str:
    """
    Return pretty formatted timedelta.

    Args:
        value: An object to be formatted.

    Example:
        >>> humanize_timedelta(timedelta(days=730))
        2 years
        >>> humanize_timedelta(timedelta(days=2016))
        5 years, 6 months and 8 days
        >>> humanize_timedelta(timedelta(days=6720))
        18 years, 4 months and 28 days

    Returns:
        A human-readable data representing the timedelta.
    """
    return humanize.precisedelta(value)


def humanize_manabar_regeneration_time(regeneration_time: timedelta) -> str:
    """
    Return pretty information about regeneration time.

    Args:
        regeneration_time: An object representing the regeneration time.

    Example:
        >>> humanize_manabar_regeneration_time(timedelta(seconds=0))
        "Full!"
        >>> humanize_manabar_regeneration_time(timedelta(hours=1))
        "an hour from now"
        >>> humanize_manabar_regeneration_time(timedelta(hours=7, minutes=21))
        "7 hours from now"
        >>> humanize_manabar_regeneration_time(timedelta(days=1, hours=7, minutes=21))
        "a day from now"

    Returns:
        A human-readable data indicating the regeneration time or if it is full.
    """

    def is_full() -> bool:
        return regeneration_time == timedelta(seconds=0)

    if is_full():
        return "Full!"
    return humanize_natural_time(-regeneration_time)


def humanize_path(path: Path, *, add_leading_dot_slash: bool = False, add_trailing_slash: bool = False) -> str:
    """
    Humanize a path to a string.

    Path object shrink leading './' and trailing `/` so it is not possible to get it when converting to string.

    Args:
        path: A path to be humanized.
        add_leading_dot_slash: Whether to add a leading dot slash (only if path is not absolute).
        add_trailing_slash: Whether to add a trailing slash.

    Example:
        >>> humanize_path(Path('user/some/root/path'))
        'user/some/root/path'
        >>> humanize_path(Path('user/some/root/path'), add_leading_dot_slash=True)
        './user/some/root/path'
        >>> humanize_path(Path('user/some/root/path'), add_leading_dot_slash=True, add_trailing_slash=True)
        './user/some/root/path/'
        >>> humanize_path(Path(''))
        './'
        >>> humanize_path(Path(''), add_leading_dot_slash=True, add_trailing_slash=True)
        './'
        >>> humanize_path(Path('/user/some/root/path'))
        '/user/some/root/path'
        >>> humanize_path(Path('/user/some/root/path'), add_leading_dot_slash=True)
        '/user/some/root/path'

    Returns:
        Humanized string representation of the path, with optional leading dot slash and trailing slash.
    """
    if path == Path():
        return "./"

    prefix = "./" if add_leading_dot_slash and not path.is_absolute() else ""
    suffix = "/" if add_trailing_slash else ""
    return f"{prefix}{path}{suffix}"


def humanize_relative_or_whole_path(
    whole_path: Path,
    root_path: Path,
    *,
    add_leading_dot_slash: bool = False,
    add_trailing_slash: bool = False,
) -> str:
    """
    Humanize a path to a string, relative to the given root path if possible, otherwise the whole path.

    Args:
        whole_path: The full path.
        root_path: The root path to compute the relative path from.
        add_leading_dot_slash: Whether to add a leading dot slash (only if path is not absolute).
        add_trailing_slash: Whether to add a trailing slash.

    Example:
        >>> humanize_relative_or_whole_path(
        ...     Path('/user/some/root/path'),
        ...     Path('/user/some')
        ... )
        'some/root/path'
        >>> humanize_relative_or_whole_path(
        ...     Path('/user/some/root/path'),
        ...     Path('/user/some'),
        ...     add_leading_dot_slash=True
        ... )
        './some/root/path'
        >>> humanize_relative_or_whole_path(
        ...     Path('/user/some/root/path'),
        ...     Path('/user/some'),
        ...     add_trailing_slash=True
        ... )
        'some/root/path/'
        >>> humanize_relative_or_whole_path(
        ...     Path('/user/some/root/path'),
        ...     Path('/user/some'),
        ...     add_leading_dot_slash=True,
        ...     add_trailing_slash=True
        ... )
        './some/root/path/'
        >>> humanize_relative_or_whole_path(
        ...     Path('/etc/config'),
        ...     Path('/user/some'),
        ...     add_leading_dot_slash=True,
        ...     add_trailing_slash=True
        ... )
        '/etc/config/'
        >>> humanize_relative_or_whole_path(
        ...     Path('/etc/config'),
        ...     Path('/user/some'),
        ...     add_leading_dot_slash=True,
        ...     add_trailing_slash=False
        ... )
        '/etc/config'
            >>> humanize_relative_or_whole_path(
        ...     Path('/etc/config'),
        ...     Path('/user/some'),
        ...     add_leading_dot_slash=False,
        ...     add_trailing_slash=False
        ... )
        '/etc/config'

    Returns:
        Humanized string representation of the path, relative to the given root path if possible, otherwise
        the whole path, with optional leading dot slash and trailing slash.
    """
    path = get_relative_or_whole_path(whole_path=whole_path, root_path=root_path)
    return humanize_path(path, add_leading_dot_slash=add_leading_dot_slash, add_trailing_slash=add_trailing_slash)
