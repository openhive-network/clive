from __future__ import annotations

from abc import abstractmethod

from textual.widgets import Select

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.models.asset import AssetAmount, AssetAmountInvalidFormatError, AssetFactory, AssetT


class CurrencySelectorBase(Select[AssetFactory[AssetT]], AbstractClassMessagePump):
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
    def _create_selectable() -> dict[str, AssetFactory[AssetT]]:
        """Should return dict of selectable items."""

    def create_asset(self, amount: AssetAmount) -> AssetT | None:
        asset = self.value
        assert asset is not None
        try:
            return asset(amount)
        except AssetAmountInvalidFormatError as error:
            self.notify(error.message, severity="error")
            return None
