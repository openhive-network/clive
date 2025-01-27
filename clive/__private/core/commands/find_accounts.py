from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import CommandError
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.models.schemas import Account
from clive.__private.models.schemas import FindAccounts as SchemasFindAccounts

if TYPE_CHECKING:
    from clive.__private.core.node import Node


class FindAccountsCommandError(CommandError):
    pass


class AccountNotFoundError(FindAccountsCommandError):
    pass


class UnrequestedAccountsReceivedError(FindAccountsCommandError):
    pass


@dataclass(kw_only=True)
class FindAccounts(CommandWithResult[list[Account]]):
    node: Node
    accounts: list[str]

    async def _execute(self) -> None:
        response: SchemasFindAccounts = await self.node.api.database_api.find_accounts(accounts=self.accounts)
        self._check_if_all_accounts_received(response)
        self._check_received_list_length(response)
        self._result = response.accounts

    def _check_if_all_accounts_received(self, response: SchemasFindAccounts) -> None:
        for account in self.accounts:
            if not any(response_account.name == account for response_account in response.accounts):
                raise AccountNotFoundError(self, f"Account {account} not found on node {self.node.http_endpoint}")

    def _check_received_list_length(self, response: SchemasFindAccounts) -> None:
        if len(self.accounts) != len(response.accounts):
            received = [response_account.owner for response_account in response.accounts]
            raise UnrequestedAccountsReceivedError(
                self, f"Requested list {self.accounts} and received {received} on node {self.node.http_endpoint}"
            )
