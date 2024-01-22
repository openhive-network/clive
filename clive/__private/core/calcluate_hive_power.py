from __future__ import annotations

from math import ceil
from typing import TYPE_CHECKING, cast

from clive.__private.core.vests_to_hive import vests_to_hive

if TYPE_CHECKING:
    from clive.models import Asset
    from clive.models.aliased import DynamicGlobalProperties


def calculate_hive_power(gdpo: DynamicGlobalProperties, vests_value: Asset.Vests | int) -> int:
    return cast(
        int,
        ceil(
            int(vests_to_hive(vests_value, gdpo).amount)
            / (10 ** gdpo.total_reward_fund_hive.get_asset_information().precision)
        ),
    )
