from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import AccountWitnessProxyOperation


@dataclass(kw_only=True)
class ProcessProxyClear(OperationCommand):
    """
    Class to clear the proxy for a given account.

    Args:
        account_name: The name of the account for which to clear the proxy.
    """

    account_name: str

    async def _create_operation(self) -> AccountWitnessProxyOperation:
        """
        Create an operation to clear the proxy for the specified account.

        Returns:
            AccountWitnessProxyOperation: An operation with the account name and an empty proxy.
        """
        return AccountWitnessProxyOperation(
            account=self.account_name,
            proxy="",
        )
