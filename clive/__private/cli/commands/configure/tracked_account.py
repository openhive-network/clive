from __future__ import annotations

import errno
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.validators.set_tracked_account_validator import SetTrackedAccountValidator

if TYPE_CHECKING:
    from beekeepy.interfaces import HttpUrl


class CLIAddingNonExistingAccountToTrackedError(CLIPrettyError):
    """
    Raise when trying to add to tracked account non existing account.

    Args:
        account_name: Name of account usingr is trying to add.
        http_endpoint: Address of node that is providing account information.
    """

    def __init__(self, account_name: str, http_endpoint: HttpUrl) -> None:
        message = f"Account `{account_name}` doesn't exist on node `{http_endpoint}`."
        super().__init__(message, errno.EINVAL)


@dataclass(kw_only=True)
class AddTrackedAccount(WorldBasedCommand):
    account_name: str

    async def _validate_tracked_account(self) -> None:
        result = SetTrackedAccountValidator(self.profile).validate(self.account_name)
        if not result.is_valid:
            raise CLIPrettyError(f"Can't use this account name: {humanize_validation_result(result)}", errno.EINVAL)
        wrapper = await self.world.commands.does_account_exists_in_node(account_name=self.account_name)
        exists = wrapper.result_or_raise
        if not exists:
            raise CLIAddingNonExistingAccountToTrackedError(self.account_name, self.world.node.http_endpoint)

    async def validate_inside_context_manager(self) -> None:
        await self._validate_tracked_account()
        await super().validate_inside_context_manager()

    async def _run(self) -> None:
        self.profile.accounts.add_tracked_account(self.account_name)


@dataclass(kw_only=True)
class RemoveTrackedAccount(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        self.profile.accounts.remove_tracked_account(self.account_name)

    async def validate_inside_context_manager(self) -> None:
        self._validate_account_exists(self.account_name)
        await super().validate_inside_context_manager()
