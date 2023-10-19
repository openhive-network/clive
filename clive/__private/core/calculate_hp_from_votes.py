from __future__ import annotations

from math import floor, log
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.models.asset import Asset


def calculate_hp_from_votes(votes: int, total_vesting_fund_hive: Asset.Hive, total_vesting_shares: Asset.Vests) -> str:
    if votes == 0:
        return "0 HP"

    total_vesting_fund = int(total_vesting_fund_hive.amount) / 10**total_vesting_fund_hive.precision
    total_shares = int(total_vesting_shares.amount) / 10**total_vesting_shares.precision

    votes_to_hp = (total_vesting_fund * (votes / total_shares)) // 1000

    units = ["", "HP", "K HP", "M HP"]
    k = 1000.0
    magnitude = int(floor(log(votes_to_hp, k)))
    return "{:.1f}{}".format(votes_to_hp / k**magnitude, units[magnitude])
