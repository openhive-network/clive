from __future__ import annotations

from collections.abc import Callable

from clive.__private.ui.widgets.select.select import Select
from clive.__private.ui.widgets.select.select_item import SelectItem
from clive.models import Asset


class CurrencySelector(Select[Callable[[float], Asset.AnyT]]):
    """
    Base Currency Selector for operations, which require to choose type of Assets.

    To use type symbols of assets in args e.g. super().__init__("HIVE").
    """

    def __init__(self, *args: str) -> None:
        def _asset_factory(symbol: str) -> Callable[[float], Asset.AnyT]:
            asset = Asset.resolve_symbol(symbol)
            return lambda value: asset(amount=Asset.convert_amount_to_internal_representation(value, asset))

        super().__init__(
            items=[SelectItem(_asset_factory(symbol), symbol) for symbol in args],
            list_mount="ViewBag",
            placeholder="Select currency",
            selected=1,
        )
