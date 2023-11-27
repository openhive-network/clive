from __future__ import annotations

from abc import abstractmethod
from typing import Generic

from textual.widgets import Select
from textual.widgets._select import NoSelection

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.models.asset import (
    AssetAmount,
    AssetAmountInvalidFormatError,
    AssetFactory,
    AssetFactoryHolder,
    AssetT,
)


class CurrencySelectorBase(Select[AssetFactoryHolder[AssetT]], Generic[AssetT], AbstractClassMessagePump):
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
    def _create_selectable() -> dict[str, AssetFactoryHolder[AssetT]]:
        """Should return dict of selectable items."""

    @property
    def value_ensure(self) -> AssetFactoryHolder[AssetT]:
        """Returns selected asset factory."""
        value = self.value
        assert not isinstance(value, NoSelection), "Value should be set."
        return value

    @property
    def asset_cls(self) -> type[AssetT]:
        """Returns selected asset type."""
        return self.value_ensure.asset_cls

    @property
    def asset_factory(self) -> AssetFactory[AssetT]:
        """Returns selected asset factory."""
        return self.value_ensure.asset_factory

    def create_asset(self, amount: AssetAmount) -> AssetT | None:
        asset_factory = self.asset_factory
        try:
            return asset_factory(amount)
        except AssetAmountInvalidFormatError as error:
            self.notify(error.message, severity="error")
            return None
