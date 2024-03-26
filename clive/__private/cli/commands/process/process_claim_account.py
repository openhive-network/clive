from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from schemas.operations import AccountWitnessProxyOperation


@dataclass(kw_only=True)
class ProcessClaimAccount(OperationCommand):
    creator: str
    fee: str

    async def _create_operation(self) -> AccountWitnessProxyOperation:
        return AccountWitnessProxyOperation(
            account=self.account_name,
            proxy=self.proxy,
        )
