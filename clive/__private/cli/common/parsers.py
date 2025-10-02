from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, get_args

import typer

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import timedelta
    from decimal import Decimal

    from clive.__private.models.asset import Asset


def rename[R, **P](new_name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return func(*args, **kwargs)

        wrapper.__name__ = new_name
        return wrapper

    return decorator


def _parse_asset[ParsedAssetT: Asset.AnyT](raw: str, *allowed_assets: type[ParsedAssetT]) -> ParsedAssetT:
    """
    Parse the liquid asset amount.

    Also provides a nice error message if something is wrong with the asset input.
    E.g. when Asset.LiquidT is allowed:
    --amount "5.0 notexisting"
        "Invalid value for '--amount': Unknown asset type: 'NOTEXISTING'. Only ['HIVE', 'HBD'] are allowed."

    --amount "5.0 vests"
        "Invalid value for '--amount': Only ['HIVE', 'HBD'] are allowed."

    --amount "5.0000000 hive"
        "Invalid value for '--amount': Invalid asset amount format: '5.0000000'. Reason: ['Invalid precision for HIVE.
          Must be <=3.']"
    """
    from clive.__private.models.asset import (  # noqa: PLC0415
        Asset,
        AssetAmountInvalidFormatError,
        UnknownAssetTypeError,
    )

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
    from clive.__private.models.asset import Asset  # noqa: PLC0415

    return _parse_asset(raw, *get_args(Asset.LiquidT))  # type: ignore[no-any-return]


def voting_asset(raw: str) -> Asset.VotingT:
    from clive.__private.models.asset import Asset  # noqa: PLC0415

    raw = raw.upper().replace("HP", "HIVE")

    return _parse_asset(raw, *get_args(Asset.VotingT))  # type: ignore[no-any-return]


def hive_asset(raw: str) -> Asset.Hive:
    from clive.__private.models.asset import Asset  # noqa: PLC0415

    return _parse_asset(raw, Asset.Hive)


def decimal_percent(raw: str) -> Decimal:
    from clive.__private.cli.warnings import typer_echo_warnings  # noqa: PLC0415
    from clive.__private.core.constants.precision import HIVE_PERCENT_PRECISION_DOT_PLACES  # noqa: PLC0415
    from clive.__private.core.decimal_conventer import (  # noqa: PLC0415
        DecimalConversionNotANumberError,
        DecimalConverter,
    )

    try:
        with typer_echo_warnings():
            parsed = DecimalConverter.convert(raw, precision=HIVE_PERCENT_PRECISION_DOT_PLACES)
    except DecimalConversionNotANumberError as err:
        raise typer.BadParameter(f"`{raw}` can't be converted to number") from err
    if parsed < 0 or parsed > 100:  # noqa: PLR2004
        raise typer.BadParameter("Must be between 0 and 100")
    return parsed


@rename("text")
def scheduled_transfer_frequency_parser(raw: str) -> timedelta:
    """
    Frequency flag parser used in transfer-schedule.

    Args:
        raw: The raw input representing the frequency.

    Raises:
        typer.BadParameter: If the input is invalid or cannot be parsed.

    Returns:
        The parsed frequency.
    """
    from clive.__private.core.formatters.humanize import humanize_validation_result  # noqa: PLC0415
    from clive.__private.core.shorthand_timedelta import shorthand_timedelta_to_timedelta  # noqa: PLC0415
    from clive.__private.validators.scheduled_transfer_frequency_value_validator import (  # noqa: PLC0415
        ScheduledTransferFrequencyValidator,
    )

    status = ScheduledTransferFrequencyValidator().validate(raw)
    if status.is_valid:
        return shorthand_timedelta_to_timedelta(raw)
    raise typer.BadParameter(humanize_validation_result(status))
