from __future__ import annotations

import errno
import sys
from dataclasses import dataclass
from getpass import getpass

import typer
from beekeepy import AsyncBeekeeper
from beekeepy.exceptions import CommunicationError

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand
from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.exceptions import (
    CLICreatingProfileCommunicationError,
    CLIInvalidPasswordRepeatError,
    CLIPrettyError,
)
from clive.__private.core.commands.create_profile_wallets import CreateProfileWallets
from clive.__private.core.commands.get_wallet_names import GetWalletNames
from clive.__private.core.commands.lock import Lock
from clive.__private.core.commands.save_profile import SaveProfile
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.core.profile import Profile
from clive.__private.settings import safe_settings
from clive.__private.storage.service import MultipleProfileVersionsError
from clive.__private.validators.profile_name_validator import ProfileNameValidator
from clive.__private.validators.set_password_validator import SetPasswordValidator
from clive.dev import is_in_dev_mode


class CLIMultipleProfileVersionsError(CLIPrettyError):
    def __init__(self, profile_name: str) -> None:
        message = (
            f"Multiple versions or backups of profile `{profile_name}` exist."
            " If you want to remove all, please use the '--force' option."
        )
        super().__init__(message, errno.EEXIST)


@dataclass(kw_only=True)
class CreateProfile(BeekeeperBasedCommand):
    profile_name: str
    working_account_name: str | None = None

    async def validate(self) -> None:
        profile_name_result = ProfileNameValidator().validate(self.profile_name)
        if not profile_name_result.is_valid:
            raise CLIPrettyError(
                f"Can't use this profile name: {humanize_validation_result(profile_name_result)}", errno.EINVAL
            )

    async def validate_inside_context_manager(self) -> None:
        await self.validate_session_is_locked()
        await super().validate_inside_context_manager()

    async def _run(self) -> None:
        password = self._get_validated_password()
        profile = Profile.create(self.profile_name, self.working_account_name)

        try:
            result = await CreateProfileWallets(
                session=await self.beekeeper.session, profile_name=profile.name, password=password
            ).execute_with_result()
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
        prompt = "Set a new password: "
        password = getpass(prompt)
        prompt_repeat = "Repeat password: "
        password_repeat = getpass(prompt_repeat)
        if password != password_repeat:
            raise CLIInvalidPasswordRepeatError
        return password

    def _get_password_input_in_non_tty_mode(self) -> str:
        return sys.stdin.readline().rstrip()


@dataclass(kw_only=True)
class DeleteProfile(ExternalCLICommand):
    profile_name: str
    force: bool

    async def _run(self) -> None:
        try:
            Profile.delete_by_name(self.profile_name, force=self.force)
            await self._lock_remote_beekeeper()
        except MultipleProfileVersionsError as error:
            raise CLIMultipleProfileVersionsError(self.profile_name) from error

    async def _lock_remote_beekeeper(self) -> None:
        if safe_settings.beekeeper.is_remote_address_set:
            async with await AsyncBeekeeper.remote_factory(
                url_or_settings=safe_settings.beekeeper.settings_remote_factory()
            ) as beekeeper:
                session = await beekeeper.session
                unlocked_wallets = await GetWalletNames(
                    session=session, filter_by_status="unlocked"
                ).execute_with_result()
                if self.profile_name in unlocked_wallets:
                    await Lock(session=session).execute()
                    typer.echo("Locked beekeeper session.")
