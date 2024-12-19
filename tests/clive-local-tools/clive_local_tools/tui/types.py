from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypeAlias

if TYPE_CHECKING:
    from clive.__private.ui.app import Clive as CliveApp  # noqa: TC004
    from clive.__private.ui.clive_pilot import ClivePilot  # noqa: TC004

    __all__ = ["CliveApp", "ClivePilot", "LiquidAssetToken", "OperationProcessing"]
else:
    __all__ = ["LiquidAssetToken", "OperationProcessing"]

LiquidAssetToken: TypeAlias = Literal["HBD", "HIVE"]
OperationProcessing: TypeAlias = Literal["ADD_TO_CART", "FINALIZE_TRANSACTION"]
