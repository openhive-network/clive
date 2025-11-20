from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIChangeRecoveryAccountValidationError
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.models.schemas import ChangeRecoveryAccountOperation
from clive.__private.validators.change_recovery_account_validator import ChangeRecoveryAccountValidator

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
        new_recovery_account = self.new_recovery_account
        validation_result = ChangeRecoveryAccountValidator().validate(new_recovery_account)
        if not validation_result.is_valid:
            raise CLIChangeRecoveryAccountValidationError(
                new_recovery_account, humanize_validation_result(validation_result)
            )

        await super().validate()
