from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import timedelta
from getpass import getpass
from typing import Final

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import (
    CLIInvalidPasswordError,
    CLIInvalidSelectionError,
    CLIProfileDoesNotExistsError,
)
from clive.__private.core.constants.cli import UNLOCK_CREATE_PROFILE_HELP, UNLOCK_CREATE_PROFILE_SELECT
from clive.__private.core.error_handlers.abc.error_notificator import CannotNotifyError
from clive.__private.core.error_handlers.general_error_notificator import INVALID_PASSWORD_MESSAGE
from clive.__private.core.profile import Profile

PASSWORD_SELECTION_ATTEMPTS: Final[int] = 3
PROFILE_SELECTION_ATTEMPTS: Final[int] = 3
ProfileSelectionOptions = dict[int, str]


@dataclass(kw_only=True)
class Unlock(WorldBasedCommand):
    """
    Command to unlock a profile in the Clive environment.

    Args:
        profile_name: The name of the profile to unlock. If None, the user will be prompted to select a profile.
        unlock_time_mins: The duration in minutes for which the profile should be unlocked. None means permanent unlock.
        include_create_new_profile: If True, allows the user to create a new profile if no profiles exist.
    """

    profile_name: str | None
    unlock_time_mins: int | None = None
    include_create_new_profile: bool

    @property
    def should_require_unlocked_wallet(self) -> bool:
        """
        Checking if unlocked wallet should be required.

        Returns:
            bool: False, because this command does not require an unlocked wallet.
        """
        return False

    @property
    def _duration(self) -> timedelta | None:
        """
        Returns the duration for which the profile should be unlocked as a timedelta object.

        If `unlock_time_mins` is None, it means the profile should be permanently unlocked.

        Returns:
            timedelta | None: The duration for which the profile should be unlocked, or None for permanent unlock.
        """
        if self.unlock_time_mins is None:
            return None
        return timedelta(minutes=self.unlock_time_mins)

    @property
    def _is_unlock_permanent(self) -> bool:
        """
        Returns whether the profile should be permanently unlocked.

        If `unlock_time_mins` is None, it means the profile should be permanently unlocked.

        Returns:
            bool: True if the profile should be permanently unlocked, False otherwise.
        """
        return self.unlock_time_mins is None

    async def validate(self) -> None:
        """
        Validate the command before execution.

        Returns:
            None: This method does not return any value, it only performs validation.
        """
        self._validate_profile_exists()
        await super().validate()

    async def validate_inside_context_manager(self) -> None:
        """
        Validate the command inside a context manager.

        Returns:
            None: This method does not return any value, it only performs validation.
        """
        await self._validate_session_is_locked()
        await super().validate_inside_context_manager()

    async def _run(self) -> None:
        """
        Run the command to unlock a profile.

        This method checks if the profile creation help should be displayed, prompts for the profile name,
        and unlocks the profile either in TTY mode or non-TTY mode based on the input method.

        Returns:
            None: This method does not return any value, it only unlocks the profile.
        """
        if self._should_display_profile_creation_help():
            self._display_create_profile_help_info()
            return

        profile_name = self._get_profile_name()
        if profile_name is None:
            self._display_create_profile_help_info()
            return
        if sys.stdin.isatty():
            await self._unlock_in_tty_mode(profile_name)
        else:
            await self._unlock_in_non_tty_mode(profile_name)
        typer.echo(f"Profile `{profile_name}` is unlocked.")

    def _get_profile_name(self) -> str | None:
        """
        Get the profile name to unlock.

        Returns:
            str | None: The name of the profile to unlock. If None, the user will be prompted to select a profile.
            If no profiles exist and `include_create_new_profile` is True,
            the user will be prompted to create a new profile.
        """
        return self.profile_name or self._prompt_for_profile_name()

    async def _unlock_profile(self, profile_name: str, password: str) -> None:
        """
        Unlock the specified profile with the provided password.

        Args:
            profile_name: The name of the profile to unlock.
            password: The password to unlock the profile.

        Raises:
            CLIInvalidPasswordError: If the provided password is invalid.
            CannotNotifyError: If there is an error notifying about the unlock operation.

        Returns:
            None: This method does not return any value, it only unlocks the profile.
        """
        try:
            await self.world.commands.unlock(
                profile_name=profile_name,
                password=password,
                time=self._duration,
                permanent=self._is_unlock_permanent,
            )
        except CannotNotifyError as error:
            if INVALID_PASSWORD_MESSAGE in error.reason:
                raise CLIInvalidPasswordError(profile_name) from error
            raise

    def _prompt_for_profile_name(self) -> str | None:
        """
        Prompt the user to select a profile to unlock.

        If there are no profiles available and `include_create_new_profile` is True,
        the user will be given the option to create a new profile.

        Raises:
            AssertionError: If the user makes an invalid selection after multiple attempts.

        Returns:
            str | None: The name of the selected profile to unlock. If the user chooses to create a new profile,
            None is returned, indicating that the profile creation process should be initiated.
        """
        options = self._generate_profile_options()
        self._display_profile_options(options)
        for i in range(PROFILE_SELECTION_ATTEMPTS):
            try:
                return self._get_selected_profile(options)
            except CLIInvalidSelectionError:
                attempts_left = PROFILE_SELECTION_ATTEMPTS - i - 1
                if attempts_left < 1:
                    raise
                message = f"Invalid selection. Try again. Attempts left: {attempts_left}"
                typer.secho(message, fg=typer.colors.RED)
                self._display_profile_options(options)
        raise AssertionError("Won't reach here")

    def _generate_profile_options(self) -> ProfileSelectionOptions:
        """
        Generate a dictionary of profile selection options.

        If `include_create_new_profile` is True, the option to create a new profile is included.

        Returns:
            ProfileSelectionOptions: A dictionary where keys are integers representing the option number,
            and values are strings representing the profile names or the create new profile option.
        """
        profiles = Profile.list_profiles()
        options: dict[int, str] = {}
        if self.include_create_new_profile:
            options[0] = UNLOCK_CREATE_PROFILE_SELECT
        options.update(ProfileSelectionOptions(enumerate(profiles, 1)))
        return options

    def _display_profile_options(self, options: ProfileSelectionOptions) -> None:
        """
        Display the available profile options to the user.

        Args:
            options (ProfileSelectionOptions): A dictionary of profile selection options to display.

        Returns:
            None: This method does not return any value, it only prints the options to the console.
        """
        typer.echo("Select profile to unlock:")
        for i, name in options.items():
            typer.echo(f"{i}. {name}")

    def _get_selected_profile(self, options: ProfileSelectionOptions) -> str | None:
        """
        Get selected profile name from prompt or None if profile creation is selected.

        Args:
            options: A dictionary of profile selection options.

        Raises:
            CLIInvalidSelectionError: If the user makes an invalid selection that is not in the options.

        Returns:
            str | None: The name of the selected profile to unlock.If the user selects the option to create
            a new profile, None is returned, indicating that the profile creation process should be initiated.
        """
        selection = typer.prompt("Enter the number")
        try:
            option_value = options[int(selection)]
        except (KeyError, ValueError) as error:
            raise CLIInvalidSelectionError from error
        if option_value == UNLOCK_CREATE_PROFILE_SELECT:
            return None
        return option_value

    def _validate_profile_exists(self) -> None:
        """
        Validate that the specified profile exists.

        Raises:
            CLIProfileDoesNotExistsError: If the specified profile does not exist.

        Returns:
            None: This method does not return any value, it only performs validation.
        """
        profile_name = self.profile_name
        if profile_name is None:
            return  # validation is not needed as profile will be selected interactively from list
        if profile_name not in Profile.list_profiles():
            raise CLIProfileDoesNotExistsError(profile_name)

    async def _unlock_in_tty_mode(self, profile_name: str) -> None:
        """
        Unlock the profile in TTY mode by prompting the user for the password.

        Args:
            profile_name: The name of the profile to unlock.

        Raises:
            CLIInvalidPasswordError: If the provided password is invalid after multiple attempts.

        Returns:
            None: This method does not return any value, it only unlocks the profile.
        """
        prompt = f"Enter password for profile `{profile_name}`: "
        for i in range(PASSWORD_SELECTION_ATTEMPTS):
            password = getpass(prompt)
            try:
                await self._unlock_profile(profile_name, password)
            except CLIInvalidPasswordError:
                attempts_left = PASSWORD_SELECTION_ATTEMPTS - i - 1
                if attempts_left < 1:
                    raise
                message = f"Invalid password. Try again. Attempts left: {attempts_left}"
                typer.secho(message, fg=typer.colors.RED)
            else:
                return
        raise AssertionError("Won't reach here")

    async def _unlock_in_non_tty_mode(self, profile_name: str) -> None:
        """
        Unlock the profile in non-TTY mode by reading the password from standard input.

        Args:
            profile_name: The name of the profile to unlock.

        Returns:
            None: This method does not return any value, it only unlocks the profile.
        """
        password = sys.stdin.readline().rstrip()
        await self._unlock_profile(profile_name, password)

    def _should_display_profile_creation_help(self) -> bool:
        """
        Check if the profile creation help should be displayed.

        Returns:
            bool: True if no profiles are saved and `include_create_new_profile` is True, False otherwise.
        """
        return not Profile.is_any_profile_saved()

    def _display_create_profile_help_info(self) -> None:
        """
        Display help information for creating a new profile.

        This method prints the help information to the console, guiding the user on how to create a new profile

        Returns:
            None: This method does not return any value, it only prints the help information to the console.
        """
        typer.echo(UNLOCK_CREATE_PROFILE_HELP)
