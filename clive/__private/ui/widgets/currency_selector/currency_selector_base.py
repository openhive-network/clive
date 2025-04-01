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
from clive.__private.ui.widgets.clive_basic.clive_select import CliveSelect


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

    @staticmethod
    @abstractmethod
    def _create_selectable() -> dict[str, AssetFactoryHolder[AssetT]]:
        """Return dict of selectable items."""

    @property
    def default_asset_factory_holder(self) -> AssetFactoryHolder[AssetT]:
        return next(iter(self._selectable.values()))

    @property
    def default_asset_cls(self) -> type[AssetT]:
        return self.default_asset_factory_holder.asset_cls

    @property
    def asset_cls(self) -> type[AssetT]:
        """Returns selected asset type."""
        return self.selection_ensure.asset_cls

    @property
    def asset_factory(self) -> AssetFactory[AssetT]:
        """Return selected asset factory."""
        return self.selection_ensure.asset_factory

    def select_asset(self, asset_type: type[AssetT]) -> None:
        """
        Select asset by its type.

        Args:
        ----
            asset_type: Type of asset to select.
        """
        self.value = self._get_selectable(asset_type)

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

    def _get_selectable(self, asset_type: type[AssetT]) -> AssetFactoryHolder[AssetT]:
        for asset_factory_holder in self._selectable.values():
            if asset_factory_holder.asset_cls == asset_type:
                return asset_factory_holder
        raise AssertionError(f"Asset type {asset_type} is not selectable")
