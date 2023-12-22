from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from schemas.operations import AccountWitnessProxyOperation


@dataclass(kw_only=True)
class ProcessProxyClear(OperationCommand):
    account_name: str

    async def _create_operation(self) -> AccountWitnessProxyOperation:
        return AccountWitnessProxyOperation(
            account=self.account_name,
            proxy="",
        )
