from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError


@dataclass(kw_only=True)
class SwitchWorkingAccount(WorldBasedCommand):
    """
    Class to switch the working account in the profile.

    Args:
        account_name: The name of the account to switch to as the working account.
    """

    account_name: str

    async def _run(self) -> None:
        """
        Run the command to switch the working account.

        Returns:
            None
        """
        self.profile.accounts.switch_working_account(self.account_name)

    def _validate_already_working_account(self) -> None:
        """
        Validate that the account is not already set as the working account.

        Raises:
            CLIPrettyError: If the account is already a working account.

        Returns:
            None
        """
        if self.profile.accounts.is_account_working(self.account_name):
            raise CLIPrettyError(f"Account {self.account_name} is already a working account.") from None

    async def validate_inside_context_manager(self) -> None:
        """
        Validate that the command can be run inside a context manager.

        Returns:
            None
        """
        self._validate_account_exists(self.account_name)
        self._validate_already_working_account()
        await super().validate_inside_context_manager()
