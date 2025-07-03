from __future__ import annotations

import errno
import sys
from dataclasses import dataclass
from getpass import getpass

from beekeepy.exceptions import CommunicationError

from clive.__private.cli.commands.abc.forceable_cli_command import ForceableCLICommand
from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import (
    CLICreatingProfileCommunicationError,
    CLIInvalidPasswordRepeatError,
    CLIPrettyError,
)
from clive.__private.core.commands.save_profile import SaveProfile
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.core.profile import Profile
from clive.__private.storage.service import MultipleProfileVersionsError
from clive.__private.validators.profile_name_validator import ProfileNameValidator
from clive.__private.validators.set_password_validator import SetPasswordValidator
from clive.dev import is_in_dev_mode


class CLIMultipleProfileVersionsError(CLIPrettyError):
    """Class for errors related to multiple versions of a profile."""

    def __init__(self, profile_name: str) -> None:
        """
        Initialize the error with a message indicating multiple versions of a profile exist.

        Args:
            profile_name: The name of the profile with multiple versions.

        Returns:
            None
        """
        message = (
            f"Multiple versions or backups of profile `{profile_name}` exist."
            " If you want to remove all, please use the '--force' option."
        )
        super().__init__(message, errno.EEXIST)


@dataclass(kw_only=True)
class CreateProfile(WorldBasedCommand):
    """
    Class for creating a new profile.

    Args:
        profile_name: The name of the profile to create.
        working_account_name: the name of the working account for the profile.
    """

    profile_name: str
    working_account_name: str | None = None

    @property
    def should_require_unlocked_wallet(self) -> bool:
        """
        Indicate if an unlocked wallet is required for this command.

        Returns:
            False
        """
        return False

    async def validate(self) -> None:
        """
        Validate the profile name and password for creating a new profile.

        Raises:
            CLIPrettyError: If the profile name or password is invalid.

        Returns:
            None
        """
        profile_name_result = ProfileNameValidator().validate(self.profile_name)
        if not profile_name_result.is_valid:
            raise CLIPrettyError(
                f"Can't use this profile name: {humanize_validation_result(profile_name_result)}", errno.EINVAL
            )

    async def validate_inside_context_manager(self) -> None:
        """
        Validate that the session is locked before creating a profile.

        Returns:
            None
        """
        await self._validate_session_is_locked()
        await super().validate_inside_context_manager()

    async def _run(self) -> None:
        """
        Run the command to create a new profile with the specified name and working account.

        Raises:
            CLICreatingProfileCommunicationError: If there is a communication error while creating the profile.

        Returns:
            None
        """
        password = self._get_validated_password()
        profile = Profile.create(self.profile_name, self.working_account_name)

        try:
            result = (
                await self.world.commands.create_profile_wallets(profile_name=profile.name, password=password)
            ).result_or_raise
        except CommunicationError as error:
            if is_in_dev_mode():
                raise
            raise CLICreatingProfileCommunicationError from error

        wallet = result.unlocked_user_wallet
        encryption_wallet = result.unlocked_encryption_wallet
        await SaveProfile(
            unlocked_wallet=wallet, unlocked_encryption_wallet=encryption_wallet, profile=profile
        ).execute()

    def _get_validated_password(self) -> str:
        """
        Get a validated password from the user.

        Raises:
            CLIPrettyError: If the password is invalid or if the password repeat does not match.

        Returns:
            str: The validated password entered by the user.
        """
        if sys.stdin.isatty():
            password = self._get_password_input_in_tty_mode()
        else:
            password = self._get_password_input_in_non_tty_mode()
        password_result = SetPasswordValidator().validate(password)
        if not password_result.is_valid:
            raise CLIPrettyError(
                f"Can't use this password: {humanize_validation_result(password_result)}", errno.EINVAL
            )
        return password

    def _get_password_input_in_tty_mode(self) -> str:
        """
        Get a password from the user in a TTY environment.

        Raises:
            CLIInvalidPasswordRepeatError: If the password repeat does not match.

        Returns:
            str: The password entered by the user.
        """
        prompt = "Set a new password: "
        password = getpass(prompt)
        prompt_repeat = "Repeat password: "
        password_repeat = getpass(prompt_repeat)
        if password != password_repeat:
            raise CLIInvalidPasswordRepeatError
        return password

    def _get_password_input_in_non_tty_mode(self) -> str:
        """
        Get a password from the user in a non-TTY environment.

        Returns:
            str: The password entered by the user.
        """
        return sys.stdin.readline().rstrip()


@dataclass(kw_only=True)
class DeleteProfile(WorldBasedCommand, ForceableCLICommand):
    """
    Class for deleting a profile.

    Args:
        profile_name: The name of the profile to delete.
    """

    profile_name: str

    @property
    def should_validate_if_remote_address_required(self) -> bool:
        """
        Indicate if remote address validation is required for this command.

        Returns:
            False
        """
        return False

    @property
    def should_validate_if_session_token_required(self) -> bool:
        """
        Indicate if session token validation is required for this command.

        Returns:
            False
        """
        return False

    @property
    def should_require_unlocked_wallet(self) -> bool:
        """
        Indicate if an unlocked wallet is required for this command.

        Returns:
            False
        """
        return False

    async def _run(self) -> None:
        """
        Run the command to delete the specified profile.

        Raises:
            CLIMultipleProfileVersionsError: If multiple versions of the profile exist and force is not set.

        Returns:
            None
        """
        try:
            await self.world.commands.delete_profile(profile_name_to_delete=self.profile_name, force=self.force)
        except MultipleProfileVersionsError as error:
            raise CLIMultipleProfileVersionsError(self.profile_name) from error
