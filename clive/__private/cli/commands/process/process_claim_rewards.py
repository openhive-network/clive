from __future__ import annotations

import errno
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, override

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.models.schemas import ClaimRewardBalanceOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction
    from clive.__private.models.schemas import Account


class CLIClaimRewardsZeroBalanceError(CLIPrettyError):
    def __init__(self, account_name: str) -> None:
        self.account_name = account_name
        message = f"Account `{account_name}` has no rewards to claim."
        super().__init__(message, errno.ENODATA)


@dataclass(kw_only=True)
class ProcessClaimRewards(OperationCommand):
    account_name: str
    _account: Account = field(init=False)

    @override
    async def fetch_data(self) -> None:
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        assert len(accounts) == 1, f"Expected exactly one account, got {len(accounts)}"
        self._account = accounts[0]

    @override
    async def validate_inside_context_manager(self) -> None:
        self._validate_has_rewards()
        await super().validate_inside_context_manager()

    def _validate_has_rewards(self) -> None:
        if self._has_zero_rewards():
            raise CLIClaimRewardsZeroBalanceError(self.account_name)

    async def _create_operations(self) -> ComposeTransaction:
        yield ClaimRewardBalanceOperation(
            account=self.account_name,
            reward_hive=self._account.reward_hive_balance,
            reward_hbd=self._account.reward_hbd_balance,
            reward_vests=self._account.reward_vesting_balance,
        )

    def _has_zero_rewards(self) -> bool:
        return (
            self._account.reward_hive_balance.amount == 0
            and self._account.reward_hbd_balance.amount == 0
            and self._account.reward_vesting_balance.amount == 0
        )
