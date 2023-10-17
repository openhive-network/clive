from abc import ABC
from dataclasses import dataclass

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli_error import CLIError
from clive.__private.core.profile_data import ProfileData, ProfileDoesNotExistsError


@dataclass(kw_only=True)
class ProfileBasedCommand(ExternalCLICommand, ABC):
    """A command that requires a profile to be loaded."""

    profile_name: str

    def _load_profile(self) -> ProfileData:
        if not self.profile_name:
            raise CLIError("No profile specified.")

        try:
            return ProfileData.load(self.profile_name, auto_create=False)
        except ProfileDoesNotExistsError as error:
            raise CLIError(str(error)) from None
