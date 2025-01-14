import sys
from dataclasses import dataclass
from getpass import getpass
from typing import Final

import typer

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand
from clive.__private.cli.exceptions import (
    CLIInvalidPasswordError,
    CLIInvalidSelectionError,
    CLIProfileDoesNotExistsError,
)
from clive.__private.core.commands.unlock import Unlock as CoreUnlockCommand
from clive.__private.core.commands.unlock import UnlockInvalidPasswordError
from clive.__private.core.constants.cli import UNLOCK_CREATE_PROFILE_HELP, UNLOCK_CREATE_PROFILE_SELECT
from clive.__private.core.profile import Profile

PASSWORD_SELECTION_ATTEMPTS: Final[int] = 3
PROFILE_SELECTION_ATTEMPTS: Final[int] = 3
ProfileSelectionOptions = dict[int, str]


@dataclass(kw_only=True)
class Unlock(BeekeeperBasedCommand):
    profile_name: str | None
    include_create_new_profile: bool

    async def validate(self) -> None:
        self._validate_profile_exists()
        await self.validate_beekeeper_remote_address_set()
        await self.validate_beekeeper_session_token_set()
        await super().validate()

    async def validate_inside_context_manager(self) -> None:
        await self.validate_session_is_locked()
        await super().validate_inside_context_manager()

    async def _run(self) -> None:
        profile_name = self._get_profile_name()
        if profile_name is None:
            typer.echo(UNLOCK_CREATE_PROFILE_HELP)
            return
        if sys.stdin.isatty():
            await self._unlock_in_tty_mode(profile_name)
        else:
            await self._unlock_in_non_tty_mode(profile_name)
        typer.echo(f"Profile `{profile_name}` is unlocked.")

    def _get_profile_name(self) -> str | None:
        return self.profile_name or self._prompt_for_profile_name()

    async def _unlock_profile(self, profile_name: str, password: str) -> None:
        try:
            await CoreUnlockCommand(
                beekeeper=self.beekeeper,
                wallet=profile_name,
                password=password,
            ).execute()
        except UnlockInvalidPasswordError as error:
            raise CLIInvalidPasswordError(profile_name) from error

    def _prompt_for_profile_name(self) -> str | None:
        options = self._generate_profile_options()
        self._display_profile_options(options)
        for i in range(PROFILE_SELECTION_ATTEMPTS):
            try:
                return self._get_selected_profile(options)
            except CLIInvalidSelectionError:  # noqa: PERF203
                attempts_left = PROFILE_SELECTION_ATTEMPTS - i - 1
                if attempts_left < 1:
                    raise
                message = f"Invalid selection. Try again. Attempts left: {attempts_left}"
                typer.secho(message, fg=typer.colors.RED)
                self._display_profile_options(options)
        raise AssertionError("Won't reach here")

    def _generate_profile_options(self) -> ProfileSelectionOptions:
        profiles = Profile.list_profiles()
        options: dict[int, str] = {}
        if self.include_create_new_profile:
            options[0] = UNLOCK_CREATE_PROFILE_SELECT
        options.update(ProfileSelectionOptions(enumerate(profiles, 1)))
        return options

    def _display_profile_options(self, options: ProfileSelectionOptions) -> None:
        typer.echo("Select profile to unlock:")
        for i, name in options.items():
            typer.echo(f"{i}. {name}")

    def _get_selected_profile(self, options: ProfileSelectionOptions) -> str | None:
        """Get selected profile name from prompt or None if profile creation is selected."""
        selection = typer.prompt("Enter the number")
        try:
            option_value = options[int(selection)]
        except (KeyError, ValueError) as error:
            raise CLIInvalidSelectionError from error
        if option_value == UNLOCK_CREATE_PROFILE_SELECT:
            return None
        return option_value

    def _validate_profile_exists(self) -> None:
        profile_name = self.profile_name
        if profile_name is None:
            return  # validation is not needed as profile will be selected interactively from list
        if profile_name not in Profile.list_profiles():
            raise CLIProfileDoesNotExistsError(profile_name)

    async def _unlock_in_tty_mode(self, profile_name: str) -> None:
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
        password = sys.stdin.readline().rstrip()
        await self._unlock_profile(profile_name, password)
