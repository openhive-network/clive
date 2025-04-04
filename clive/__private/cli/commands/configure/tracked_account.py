from __future__ import annotations

import errno
from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.validators.set_tracked_account_validator import SetTrackedAccountValidator


@dataclass(kw_only=True)
class AddTrackedAccount(WorldBasedCommand):
    account_name: str

    def _validate_tracked_account(self) -> None:
        result = SetTrackedAccountValidator(self.profile).validate(self.account_name)
        if not result.is_valid:
            raise CLIPrettyError(f"Can't use this account name: {humanize_validation_result(result)}", errno.EINVAL)

    async def validate_inside_context_manager(self) -> None:
        self._validate_tracked_account()
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
