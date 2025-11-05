from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIChangingRecoveryAccountToWarningAccountError
from clive.__private.core.constants.alarms import WARNING_RECOVERY_ACCOUNTS
from clive.__private.models.schemas import ChangeRecoveryAccountOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction


@dataclass(kw_only=True)
class ProcessChangeRecoveryAccount(OperationCommand):
    account_to_recover: str
    new_recovery_account: str

    async def _create_operations(self) -> ComposeTransaction:
        yield ChangeRecoveryAccountOperation(
            account_to_recover=self.account_to_recover,
            new_recovery_account=self.new_recovery_account,
        )

    async def validate(self) -> None:
        if self.new_recovery_account in WARNING_RECOVERY_ACCOUNTS:
            raise CLIChangingRecoveryAccountToWarningAccountError(self.new_recovery_account)
        await super().validate()
