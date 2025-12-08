from __future__ import annotations

import errno
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.accounts.accounts import TrackedAccount
from clive.__private.models.schemas import ClaimRewardBalanceOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction
    from clive.__private.core.commands.data_retrieval.update_node_data.models import NodeData
    from clive.__private.models.asset import Asset


class NoRewardsToClaimError(CLIPrettyError):
    """Raised when there are no rewards to claim."""

    def __init__(self) -> None:
        super().__init__("No unclaimed rewards to claim.", errno.EPERM)


@dataclass(kw_only=True)
class ProcessClaimRewards(OperationCommand):
    """Claims all rewards in hive, hbd and hive power."""

    account_name: str
    _account_data: NodeData = field(init=False)

    @property
    def hbd_unclaimed(self) -> Asset.Hbd:
        return self._account_data.hbd_unclaimed

    @property
    def hive_unclaimed(self) -> Asset.Hive:
        return self._account_data.hive_unclaimed

    @property
    def vests_unclaimed(self) -> Asset.Vests:
        return self._account_data.unclaimed_hp_balance.vests_balance

    async def _create_operations(self) -> ComposeTransaction:
        yield ClaimRewardBalanceOperation(
            account=self.account_name,
            reward_hive=self.hive_unclaimed,
            reward_hbd=self.hbd_unclaimed,
            reward_vests=self.vests_unclaimed,
        )

    async def fetch_data(self) -> None:
        account = TrackedAccount(name=self.account_name)
        await self.world.commands.update_node_data(accounts=[account])
        self._account_data = account.data

    async def validate_inside_context_manager(self) -> None:
        self._validate_unclaimed_are_rewards_non_zero()
        await super().validate_inside_context_manager()

    def _validate_unclaimed_are_rewards_non_zero(self) -> None:
        if self.hbd_unclaimed == 0 and self.hive_unclaimed == 0 and self.vests_unclaimed == 0:
            raise NoRewardsToClaimError
