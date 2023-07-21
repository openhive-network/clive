from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import TypeVar

from textual.widgets import Select

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.widgets.notification import Notification
from clive.models.aliased import AssetBase
from clive.models.asset import AssetAmountInvalidFormatError, AssetAmountT

CurrencySelectorValueT = TypeVar("CurrencySelectorValueT", bound=AssetBase)

CurrencySelectorCallableT = Callable[[AssetAmountT], CurrencySelectorValueT]


class CurrencySelectorBase(Select[CurrencySelectorCallableT[CurrencySelectorValueT]], AbstractClassMessagePump):
    """Base Currency Selector for operations, which require to choose type of Assets."""

    def __init__(self) -> None:
        selectable = self._create_selectable()
        first_value = next(iter(selectable.values()))
        super().__init__(
            selectable.items(),
            prompt="Select currency",
            allow_blank=False,
            value=first_value,
        )

    @staticmethod
    @abstractmethod
    def _create_selectable() -> dict[str, CurrencySelectorCallableT[CurrencySelectorValueT]]:
        """Should return dict of selectable items."""

    def create_asset(self, amount: AssetAmountT) -> CurrencySelectorValueT | None:
        asset = self.value
        assert asset is not None
        try:
            return asset(amount)
        except AssetAmountInvalidFormatError as error:
            Notification(error.message, category="error").show()
            return None
