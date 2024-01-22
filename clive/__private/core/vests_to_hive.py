from __future__ import annotations

from typing import TYPE_CHECKING

from clive.models import Asset

if TYPE_CHECKING:
    from clive.models.aliased import DynamicGlobalProperties


def vests_to_hive(amount: int | Asset.Vests, gdpo: DynamicGlobalProperties) -> Asset.Hive:
    if isinstance(amount, Asset.Vests):
        amount = int(amount.amount)
    return Asset.Hive(
        amount=int(amount * int(gdpo.total_vesting_fund_hive.amount) / int(gdpo.total_vesting_shares.amount))
    )
