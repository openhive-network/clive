from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from clive.__private.cli.completion import is_tab_completion_active

if not is_tab_completion_active():
    from helpy import wax as iwax

    from clive.__private.models import Asset

if TYPE_CHECKING:
    from decimal import Decimal


class TotalVestingProtocol(Protocol):
    """Simply pass gdpo, or object that provides required information."""

    total_vesting_fund_hive: Asset.Hive
    total_vesting_shares: Asset.Vests


def calculate_vests_to_hive_ratio(data: TotalVestingProtocol) -> Decimal:
    ratio = iwax.calculate_hp_to_vests(
        hive=Asset.hive(1),
        total_vesting_fund_hive=data.total_vesting_fund_hive,
        total_vesting_shares=data.total_vesting_shares,
    )
    return Asset.as_decimal(ratio)
