from __future__ import annotations

from abc import abstractmethod
from typing import Generic

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.models.asset import (
    AssetAmount,
    AssetFactory,
    AssetFactoryHolder,
    AssetT,
)
from clive.__private.ui.widgets.clive_select import CliveSelect


class CurrencySelectorBase(CliveSelect[AssetFactoryHolder[AssetT]], Generic[AssetT], AbstractClassMessagePump):
    """Base Currency Selector for operations, which require to choose type of Assets."""

    def __init__(self) -> None:
        self._selectable = self._create_selectable()
        super().__init__(
            self._selectable.items(),
            prompt="Select currency",
            allow_blank=False,
            value=self.default_asset_factory_holder,
        )

    @property
    def default_asset_factory_holder(self) -> AssetFactoryHolder[AssetT]:
        return next(iter(self._selectable.values()))

    @property
    def default_asset_cls(self) -> type[AssetT]:
        return self.default_asset_factory_holder.asset_cls

    @staticmethod
    @abstractmethod
    def _create_selectable() -> dict[str, AssetFactoryHolder[AssetT]]:
        """Return dict of selectable items."""

    def get_selectable(self, asset: str) -> AssetFactoryHolder[AssetT]:
        """Return selectable item for given asset."""
        return self._selectable[asset]

    @property
    def asset_cls(self) -> type[AssetT]:
        """Returns selected asset type."""
        return self.value_ensure.asset_cls

    @property
    def asset_factory(self) -> AssetFactory[AssetT]:
        """Return selected asset factory."""
        return self.value_ensure.asset_factory

    def create_asset(self, amount: AssetAmount) -> AssetT:
        """
        Create asset from amount.

        Args:
        ----
        amount: Amount of asset.

        Raises:
        ------
        AssetAmountInvalidFormatError: Raised when given amount is in invalid format.
        """
        asset_factory = self.asset_factory
        return asset_factory(amount)
