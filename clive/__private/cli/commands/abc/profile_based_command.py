from abc import ABC
from dataclasses import dataclass

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli_error import CLIError
from clive.__private.core.profile_data import ProfileData, ProfileDoesNotExistsError


@dataclass(kw_only=True)
class ProfileBasedCommand(ExternalCLICommand, ABC):
    """A command that requires a profile to be loaded."""

    profile: str

    def _load_profile(self) -> ProfileData:
        try:
            return ProfileData.load(self.profile, auto_create=False)
        except ProfileDoesNotExistsError:
            raise CLIError(f"Profile `{self.profile}` does not exists.") from None
