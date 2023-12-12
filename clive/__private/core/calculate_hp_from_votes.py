from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.models import Asset


def calculate_hp_from_votes(votes: int, total_vesting_fund_hive: Asset.Hive, total_vesting_shares: Asset.Vests) -> int:
    total_vesting_fund = int(total_vesting_fund_hive.amount) / 10**total_vesting_fund_hive.precision
    total_shares = int(total_vesting_shares.amount) / 10**total_vesting_shares.precision

    return (total_vesting_fund * (votes / total_shares)) // 1000000  # type: ignore[no-any-return]
