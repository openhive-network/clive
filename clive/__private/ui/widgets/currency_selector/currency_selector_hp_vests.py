from __future__ import annotations

from typing import TypedDict

from clive.__private.models.asset import AssetFactoryHolderHbd, AssetFactoryHolderHive, AssetFactoryHolderVests
from clive.__private.ui.widgets.currency_selector.currency_selector_base import CurrencySelectorBase


class AssetFactoryDict(TypedDict):
    HP: AssetFactoryHolderHive
    VESTS: AssetFactoryHolderVests


class CurrencySelectorHpVests(CurrencySelectorBase):
    @staticmethod
    def _create_selectable() -> dict[str, AssetFactoryHolderHive | AssetFactoryHolderHbd | AssetFactoryHolderVests]:
        return {
            "HP": AssetFactoryHolderHive(),
            "VESTS": AssetFactoryHolderVests(),
        }
