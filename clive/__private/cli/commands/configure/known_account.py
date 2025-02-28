from __future__ import annotations

import errno
from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.validators.set_known_account_validator import SetKnownAccountValidator


@dataclass(kw_only=True)
class AddKnownAccount(WorldBasedCommand):
    account_name: str

    async def validate_inside_context_manager(self) -> None:
        self._validate_known_account()
        await super().validate_inside_context_manager()

    def _validate_known_account(self) -> None:
        result = SetKnownAccountValidator(self.profile).validate(self.account_name)
        if not result.is_valid:
            raise CLIPrettyError(f"Can't add this account: {humanize_validation_result(result)}", errno.EINVAL)

    async def _run(self) -> None:
        self.profile.accounts.add_known_account(self.account_name)


@dataclass(kw_only=True)
class RemoveKnownAccount(WorldBasedCommand):
    account_name: str

    async def validate_inside_context_manager(self) -> None:
        self._validate_known_account_exists()
        await super().validate_inside_context_manager()

    def _validate_known_account_exists(self) -> None:
        if not self.profile.accounts.is_account_known(self.account_name):
            raise CLIPrettyError(f"Known account {self.account_name} not found.")

    async def _run(self) -> None:
        self.profile.accounts.remove_known_account(self.account_name)
