from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.hive_vests_conversions import vests_to_hive

if TYPE_CHECKING:
    from clive.__private.models import Asset
    from clive.__private.models.aliased import DynamicGlobalProperties


@dataclass
class HpVestsBalance:
    """Class to store the balance of shares in HP and VESTS."""

    hp_balance: Asset.Hive
    vests_balance: Asset.Vests

    @classmethod
    def create(cls, vests: Asset.Vests, gdpo: DynamicGlobalProperties) -> HpVestsBalance:
        return cls(hp_balance=vests_to_hive(vests, gdpo), vests_balance=vests)
