from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import TypeVar

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.widgets.select.select import Select
from clive.__private.ui.widgets.select.select_item import SelectItem
from clive.models.aliased import AssetBase
from clive.models.asset import AssetAmountT

CurrencySelectorValueT = TypeVar("CurrencySelectorValueT", bound=AssetBase)

CurrencySelectorCallableT = Callable[[AssetAmountT], CurrencySelectorValueT]


class CurrencySelectorBase(Select[CurrencySelectorCallableT[CurrencySelectorValueT]], AbstractClassMessagePump):
    """Base Currency Selector for operations, which require to choose type of Assets."""

    def __init__(self) -> None:
        super().__init__(
            items=[SelectItem(function, symbol) for symbol, function in self._create_selectable().items()],
            list_mount="ViewBag",
            placeholder="Select currency",
            selected=0,
        )

    @staticmethod
    @abstractmethod
    def _create_selectable() -> dict[str, CurrencySelectorCallableT[CurrencySelectorValueT]]:
        """Should return dict of selectable items."""
