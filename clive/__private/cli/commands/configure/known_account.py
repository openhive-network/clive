from __future__ import annotations

import errno
from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.validators.set_known_account_validator import SetKnownAccountValidator


@dataclass(kw_only=True)
class AddKnownAccount(WorldBasedCommand):
    """
    Class to add a known account to the profile.

    Args:
        account_name: The name of the account to be added.
    """

    account_name: str

    async def validate_inside_context_manager(self) -> None:
        """
        Validate that the account can be added to the profile.

        Returns:
            None
        """
        self._validate_known_account()
        await super().validate_inside_context_manager()

    def _validate_known_account(self) -> None:
        """
        Validate that the account name is valid and can be added as a known account.

        Raises:
            CLIPrettyError: If the account name is invalid or cannot be added.

        Returns:
            None
        """
        result = SetKnownAccountValidator(self.profile).validate(self.account_name)
        if not result.is_valid:
            raise CLIPrettyError(f"Can't add this account: {humanize_validation_result(result)}", errno.EINVAL)

    async def _run(self) -> None:
        """
        Run the command to add the known account to the profile.

        Returns:
            None
        """
        self.profile.accounts.add_known_account(self.account_name)


@dataclass(kw_only=True)
class RemoveKnownAccount(WorldBasedCommand):
    """
    Class to remove a known account from the profile.

    Args:
        account_name: The name of the account to be removed.
    """

    account_name: str

    async def validate_inside_context_manager(self) -> None:
        """
        Validate that the account exists in the profile before attempting to remove it.

        Returns:
            None
        """
        self._validate_known_account_exists()
        await super().validate_inside_context_manager()

    def _validate_known_account_exists(self) -> None:
        """
        Validate that the account exists in the profile's known accounts.

        Raises:
            CLIPrettyError: If the account does not exist in the known accounts.

        Returns:
            None
        """
        if not self.profile.accounts.is_account_known(self.account_name):
            raise CLIPrettyError(f"Known account {self.account_name} not found.")

    async def _run(self) -> None:
        """
        Run the command to remove the known account from the profile.

        Returns:
            None
        """
        self.profile.accounts.remove_known_account(self.account_name)


@dataclass(kw_only=True)
class EnableKnownAccounts(WorldBasedCommand):
    """Class to enable known accounts in the profile."""

    async def _run(self) -> None:
        """
        Run the command to enable known accounts in the profile.

        Returns:
            None
        """
        self.profile.enable_known_accounts()


@dataclass(kw_only=True)
class DisableKnownAccounts(WorldBasedCommand):
    """Class to disable known accounts in the profile."""

    async def _run(self) -> None:
        """
        Run the command to disable known accounts in the profile.

        Returns:
            None
        """
        self.profile.disable_known_accounts()
