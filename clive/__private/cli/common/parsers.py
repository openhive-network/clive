from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, get_args

import typer

from clive.__private.cli.warnings import typer_echo_warnings
from clive.__private.core.constants import HIVE_PERCENT_PRECISION_DOT_PLACES
from clive.__private.core.decimal_conventer import DecimalConversionNotANumberError, DecimalConverter

if TYPE_CHECKING:
    from decimal import Decimal

    from clive.models import Asset

ParsedAssetT = TypeVar("ParsedAssetT", bound="Asset.AnyT")


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
