from __future__ import annotations

import errno
from dataclasses import dataclass

import beekeepy.exceptions as bke

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
from clive.__private.storage.service.exceptions import MultipleProfileVersionsError
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
class CreateProfile(WorldBasedCommand):
    profile_name: str
    working_account_name: str | None = None

    @property
    def should_require_unlocked_wallet(self) -> bool:
        return False

    async def validate(self) -> None:
        profile_name_result = ProfileNameValidator().validate(self.profile_name)
        if not profile_name_result.is_valid:
            raise CLIPrettyError(
                f"Can't use this profile name: {humanize_validation_result(profile_name_result)}", errno.EINVAL
            )

    async def validate_inside_context_manager(self) -> None:
        await self._validate_session_is_locked()
        await super().validate_inside_context_manager()

    async def _run(self) -> None:
        password = self._get_validated_password()
        profile = Profile.create(self.profile_name, self.working_account_name)

        try:
            result = (
                await self.world.commands.create_profile_wallets(profile_name=profile.name, password=password)
            ).result_or_raise
        except bke.CommunicationError as error:
            if is_in_dev_mode():
                raise
            raise CLICreatingProfileCommunicationError from error

        wallet = result.unlocked_user_wallet
        encryption_wallet = result.unlocked_encryption_wallet
        await SaveProfile(
            unlocked_wallet=wallet, unlocked_encryption_wallet=encryption_wallet, profile=profile
        ).execute()

    def _get_validated_password(self) -> str:
        password = self._get_password_input_interactive() if self.is_interactive else self.read_piped()
        password_result = SetPasswordValidator().validate(password)
        if not password_result.is_valid:
            raise CLIPrettyError(
                f"Can't use this password: {humanize_validation_result(password_result)}", errno.EINVAL
            )
        return password

    def _get_password_input_interactive(self) -> str:
        password = self.read_interactive("Set a new password")
        password_repeat = self.read_interactive("Repeat password")
        if password != password_repeat:
            raise CLIInvalidPasswordRepeatError
        return password


@dataclass(kw_only=True)
class DeleteProfile(WorldBasedCommand, ForceableCLICommand):
    profile_name: str

    @property
    def should_validate_if_remote_address_required(self) -> bool:
        return False

    @property
    def should_validate_if_session_token_required(self) -> bool:
        return False

    @property
    def should_require_unlocked_wallet(self) -> bool:
        return False

    async def _run(self) -> None:
        try:
            await self.world.commands.delete_profile(profile_name_to_delete=self.profile_name, force=self.force)
        except MultipleProfileVersionsError as error:
            raise CLIMultipleProfileVersionsError(self.profile_name) from error
