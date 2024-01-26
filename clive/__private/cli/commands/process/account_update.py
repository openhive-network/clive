from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from schemas.operations import AccountUpdate2Operation

if TYPE_CHECKING:
    from clive.__private.cli.common.update_authority import AccountUpdateFunction


@dataclass(kw_only=True)
class AccountUpdate(OperationCommand):
    account_name: str
    callbacks: list[AccountUpdateFunction]
    offline: bool

    async def _create_operation(self) -> AccountUpdate2Operation:
        full_operation = AccountUpdate2Operation(
            account=self.account_name,
            owner=None,
            active=None,
            posting=None,
            memo_key=None,
            json_metadata="",
            posting_json_metadata="",
            extensions=[],
        )

        if self.offline is False:
            response = await self.world.node.api.database_api.find_accounts(accounts=[self.account_name])
            if len(response.accounts) == 0:
                raise CLIPrettyError(f"Account {self.account_name} not found on node {self.world.node.address}")

            account = response.accounts[0]
            assert (
                account.name == self.account_name
            ), f"find_accounts query should return {self.account_name} account, not {account.name}"

            full_operation = AccountUpdate2Operation(
                account=account.name,
                owner=account.owner,
                active=account.active,
                posting=account.posting,
                memo_key=account.memo_key,
                json_metadata="",
                posting_json_metadata="",
                extensions=[],
            )

        operation = deepcopy(full_operation)

        for callback in self.callbacks:
            operation = callback(operation)

        return self.__skip_untouched_fields(full_operation, operation)

    def __skip_untouched_fields(
        self, full_operation: AccountUpdate2Operation, operation: AccountUpdate2Operation
    ) -> AccountUpdate2Operation:
        return AccountUpdate2Operation(
            account=full_operation.account,
            owner=operation.owner if operation.owner != full_operation.owner else None,
            active=operation.active if operation.active != full_operation.active else None,
            posting=operation.posting if operation.posting != full_operation.posting else None,
            memo_key=operation.memo_key if operation.memo_key != full_operation.memo_key else None,
            json_metadata="",
            posting_json_metadata="",
            extensions=[],
        )
