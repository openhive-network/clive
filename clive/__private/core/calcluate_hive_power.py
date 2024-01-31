from __future__ import annotations

from math import ceil
from typing import TYPE_CHECKING

from clive.__private.core.hive_vests_conversions import vests_to_hive

if TYPE_CHECKING:
    from clive.models import Asset
    from clive.models.aliased import DynamicGlobalProperties


def calculate_hive_power(gdpo: DynamicGlobalProperties, vests_value: Asset.Vests | int) -> int:
    vests_to_hive_amount = int(vests_to_hive(vests_value, gdpo).amount)
    precision = gdpo.total_reward_fund_hive.get_asset_information().precision
    return int(ceil(vests_to_hive_amount / (10**precision)))
