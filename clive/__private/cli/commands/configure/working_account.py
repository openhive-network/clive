from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError


@dataclass(kw_only=True)
class SwitchWorkingAccount(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        self.profile.accounts.switch_working_account(self.account_name)

    def _validate_already_working_account(self) -> None:
        if self.profile.accounts.is_account_working(self.account_name):
            raise CLIPrettyError(f"Account {self.account_name} is already a working account.") from None

    async def validate_inside_context_manager(self) -> None:
        self._validate_account_is_tracked(self.account_name)
        self._validate_already_working_account()
        await super().validate_inside_context_manager()
