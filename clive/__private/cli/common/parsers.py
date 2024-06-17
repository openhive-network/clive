from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Callable, Final, ParamSpec, TypeVar, get_args

import typer

from clive.__private.cli.warnings import typer_echo_warnings
from clive.__private.core.constants import (
    HIVE_PERCENT_PRECISION_DOT_PLACES,
    SCHEDULED_TRANSFER_MINIMUM_FREQUENCY_VALUE,
)
from clive.__private.core.decimal_conventer import DecimalConversionNotANumberError, DecimalConverter
from clive.__private.core.shorthand_timedelta import shorthand_timedelta_to_timedelta

if TYPE_CHECKING:
    from decimal import Decimal

    from clive.models import Asset

ParsedAssetT = TypeVar("ParsedAssetT", bound="Asset.AnyT")
P = ParamSpec("P")
R = TypeVar("R")

RenamedFuncT = Callable[P, R]


def rename(new_name: str) -> Callable[[RenamedFuncT], RenamedFuncT]:  # type: ignore[type-arg]
    def decorator(func: RenamedFuncT) -> RenamedFuncT:  # type: ignore[type-arg]
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:  # type: ignore[type-var]
            return func(*args, **kwargs)  # type: ignore[no-any-return]

        wrapper.__name__ = new_name
        return wrapper

    return decorator


def _parse_asset(raw: str, *allowed_assets: type[ParsedAssetT]) -> ParsedAssetT:
    """
    Parse the liquid asset amount.

    Also provides a nice error message if something is wrong with the asset input.
    E.g. when Asset.LiquidT is allowed:
    --amount "5.0 notexisting" -> Invalid value for '--amount': Unknown asset type: 'NOTEXISTING'. Only ['HIVE', 'HBD'] are allowed.
    --amount "5.0 vests" -> Invalid value for '--amount': Only ['HIVE', 'HBD'] are allowed.
    --amount "5.0000000 hive" -> Invalid value for '--amount': Invalid asset amount format: '5.0000000'. Reason: ['Invalid precision for HIVE. Must be <=3.']
    """
    from clive.models.asset import Asset, AssetAmountInvalidFormatError, UnknownAssetTypeError

    _allowed_assets: tuple[type[Asset.AnyT], ...] = allowed_assets  # type: ignore[assignment]
    allowed_symbols_message = f"Only {[Asset.get_symbol(allowed) for allowed in _allowed_assets]} are allowed."

    try:
        asset: ParsedAssetT = Asset.from_legacy(raw)  # type: ignore[assignment]
    except UnknownAssetTypeError as error:
        raise typer.BadParameter(f"{error} {allowed_symbols_message}") from None
    except AssetAmountInvalidFormatError as error:
        raise typer.BadParameter(f"{error}") from None

    if not isinstance(asset, _allowed_assets):
        raise typer.BadParameter(allowed_symbols_message)
    return asset


def liquid_asset(raw: str) -> Asset.LiquidT:
    from clive.models.asset import Asset

    return _parse_asset(raw, *get_args(Asset.LiquidT))  # type: ignore[no-any-return]


def voting_asset(raw: str) -> Asset.VotingT:
    from clive.models.asset import Asset

    raw = raw.upper().replace("HP", "HIVE")

    return _parse_asset(raw, *get_args(Asset.VotingT))  # type: ignore[no-any-return]


def hive_asset(raw: str) -> Asset.Hive:
    from clive.models.asset import Asset

    return _parse_asset(raw, Asset.Hive)


def decimal_percent(raw: str) -> Decimal:
    try:
        with typer_echo_warnings():
            parsed = DecimalConverter.convert(raw, precision=HIVE_PERCENT_PRECISION_DOT_PLACES)
    except DecimalConversionNotANumberError as err:
        raise typer.BadParameter(f"`{raw}` can't be converted to number") from err
    if parsed < 0 or parsed > 100:  # noqa: PLR2004
        raise typer.BadParameter("Must be between 0 and 100")
    return parsed


@rename("text")
def smart_frequency_parser(raw: str) -> int:
    """Parser function for frequency flag used in transfer-schedule."""
    try:
        td = shorthand_timedelta_to_timedelta(raw.lower())
    except ValueError as err:
        raise typer.BadParameter(
            'Incorrect frequency unit must be one of the following hH, dD, wW. (e.g. "24h" or "2d 2h")'
        ) from err

    hour_in_seconds: Final[int] = 3600
    frequency_period = int(td.total_seconds() / hour_in_seconds)
    if frequency_period < SCHEDULED_TRANSFER_MINIMUM_FREQUENCY_VALUE:
        raise typer.BadParameter(
            f"Value for 'frequency' must be greater than {SCHEDULED_TRANSFER_MINIMUM_FREQUENCY_VALUE}h."
        )
    return frequency_period
