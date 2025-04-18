from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from clive.__private.ui.app import Clive as CliveApp  # noqa: TC004
    from clive.__private.ui.clive_pilot import ClivePilot  # noqa: TC004

    __all__ = ["CliveApp", "ClivePilot", "LiquidAssetToken", "OperationProcessing"]
else:
    __all__ = ["LiquidAssetToken", "OperationProcessing"]

type LiquidAssetToken = Literal["HBD", "HIVE"]
type OperationProcessing = Literal["ADD_TO_CART", "FINALIZE_TRANSACTION"]
