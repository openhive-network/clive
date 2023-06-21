from __future__ import annotations

from collections.abc import Callable

from clive.__private.ui.widgets.select.select import Select
from clive.__private.ui.widgets.select.select_item import SelectItem
from clive.models import Asset


class CurrencySelector(Select[Callable[[float], Asset.ANY]]):
    """Base Currency Selector for operations, which require to choose type of Assets"""
    def __init__(self, *args) -> None:
        def _asset_factory(symbol: str) -> Callable[[float], Asset.ANY]:
            asset = Asset.resolve_symbol(symbol)
            return lambda value: asset(amount=Asset.float_to_nai_int(value, asset))

        super().__init__(
            items=[SelectItem(_asset_factory(symbol), symbol) for symbol in args],
            list_mount="ViewBag",
            placeholder="Select currency",
            selected=1,)
