from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core import iwax
from clive.models import Asset

if TYPE_CHECKING:
    from clive.models.aliased import DynamicGlobalProperties


def vests_to_hive(amount: int | Asset.Vests, gdpo: DynamicGlobalProperties) -> Asset.Hive:
    total_vesting_fund_hive = gdpo.total_vesting_fund_hive
    total_vesting_shares = gdpo.total_vesting_shares

    if isinstance(amount, int):
        amount = Asset.vests(amount)

    return iwax.calculate_vests_to_hp(amount, total_vesting_fund_hive, total_vesting_shares)


def hive_to_vests(amount: int | Asset.Hive, gdpo: DynamicGlobalProperties) -> Asset.Vests:
    if isinstance(amount, Asset.Hive):
        amount = int(amount.amount)

    return Asset.Vests(
        amount=int(amount * int(gdpo.total_vesting_shares.amount) / int(gdpo.total_vesting_fund_hive.amount))
    )
