from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core import iwax

if TYPE_CHECKING:
    from clive.__private.models import Asset
    from clive.__private.models.schemas import DynamicGlobalProperties


@dataclass
class HpVestsBalance:
    """
    Class to store the balance of shares in HP and VESTS.

    Attributes:
        hp_balance: The balance in HP.
        vests_balance: The balance in VESTS.
    """

    hp_balance: Asset.Hive
    vests_balance: Asset.Vests

    @classmethod
    def create(cls, vests: Asset.Vests, gdpo: DynamicGlobalProperties) -> HpVestsBalance:
        return cls(hp_balance=iwax.calculate_vests_to_hp(vests, gdpo), vests_balance=vests)
