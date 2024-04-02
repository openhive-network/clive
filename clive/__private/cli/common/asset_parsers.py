from __future__ import annotations

from typing import TYPE_CHECKING

import typer

if TYPE_CHECKING:
    from clive.models import Asset


def liquid_asset(raw: str) -> Asset.LiquidT:
    """
    Parse the liquid asset amount.

    Also provides a nice error message if something is wrong with the asset input.
    E.g:
    --amount "5.0 notexisting" -> Invalid value for '--amount': Unknown asset type: 'NOTEXISTING'. Only ['HIVE', 'HBD'] are allowed.
    --amount "5.0 vests" -> Invalid value for '--amount': Only ['HIVE', 'HBD'] are allowed.
    --amount "5.0000000 hive" -> Invalid value for '--amount': Invalid asset amount format: '5.0000000'. Reason: ['Invalid precision for HIVE. Must be <=3.']
    """
    from clive.models.asset import Asset, AssetAmountInvalidFormatError, UnknownAssetTypeError

    allowed_assets: tuple[type[Asset.AnyT], ...] = (Asset.Hive, Asset.Hbd)
    allowed_symbols_message = f"Only {[Asset.get_symbol(allowed) for allowed in allowed_assets]} are allowed."

    try:
        asset = Asset.from_legacy(raw)
    except UnknownAssetTypeError as error:
        raise typer.BadParameter(f"{error} {allowed_symbols_message}") from None
    except AssetAmountInvalidFormatError as error:
        raise typer.BadParameter(f"{error}") from None

    if not isinstance(asset, (Asset.Hive, Asset.Hbd)):
        raise typer.BadParameter(allowed_symbols_message)
    return asset
