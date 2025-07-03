from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import AccountWitnessProxyOperation


@dataclass(kw_only=True)
class ProcessProxySet(OperationCommand):
    """
    Class to set a witness proxy for an account.

    Args:
        account_name: The name of the account to set the proxy for.
        proxy: The witness proxy to set for the account.
    """

    account_name: str
    proxy: str

    async def _create_operation(self) -> AccountWitnessProxyOperation:
        """
        Create an operation to set the witness proxy for the account.

        Returns:
            AccountWitnessProxyOperation: The operation to set the witness proxy.
        """
        return AccountWitnessProxyOperation(
            account=self.account_name,
            proxy=self.proxy,
        )
