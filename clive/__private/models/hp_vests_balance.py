from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.__private.models import Asset
    from clive.__private.models.schemas import DynamicGlobalProperties


@dataclass
class HpVestsBalance:
    """Class to store the balance of shares in HP and VESTS."""

    hp_balance: Asset.Hive
    vests_balance: Asset.Vests

    @classmethod
    def create(cls, vests: Asset.Vests, gdpo: DynamicGlobalProperties) -> HpVestsBalance:
        from clive.__private.core import iwax

        return cls(hp_balance=iwax.calculate_vests_to_hp(vests, gdpo), vests_balance=vests)
