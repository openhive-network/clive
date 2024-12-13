import errno
import sys
from dataclasses import dataclass
from getpass import getpass

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand
from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.exceptions import CLIPrettyError, CreatingProfileError
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.core.profile import Profile
from clive.__private.validators.profile_name_validator import ProfileNameValidator
from clive.__private.validators.set_password_validator import SetPasswordValidator
from clive.dev import is_in_dev_mode
from clive.exceptions import CommunicationError


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

        profile.save()

        try:
            await CreateWallet(beekeeper=self.beekeeper, wallet=profile.name, password=password).execute()
        except CommunicationError as e:
            profile.delete()
            if is_in_dev_mode():
                raise
            raise CreatingProfileError from e

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
        prompt = f"Enter password for profile `{self.profile_name}`: "
        return getpass(prompt)

    def _get_password_input_in_non_tty_mode(self) -> str:
        return sys.stdin.readline().rstrip()


@dataclass(kw_only=True)
class DeleteProfile(ExternalCLICommand):
    profile_name: str

    async def _run(self) -> None:
        Profile.delete_by_name(self.profile_name)
