from __future__ import annotations

from typing import TYPE_CHECKING

from clive.models import Asset

if TYPE_CHECKING:
    from clive.models.aliased import DynamicGlobalProperties


def hive_to_vests(amount: int | Asset.Hive, gdpo: DynamicGlobalProperties) -> Asset.Vests:
    if isinstance(amount, Asset.Hive):
        amount = int(amount.amount)

    return Asset.Vests(
        amount=int(amount * int(gdpo.total_vesting_shares.amount) / int(gdpo.total_vesting_fund_hive.amount))
    )
