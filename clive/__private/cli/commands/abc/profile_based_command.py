from abc import ABC
from dataclasses import dataclass

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.core.profile_data import ProfileData


@dataclass(kw_only=True)
class ProfileBasedCommand(ExternalCLICommand, ABC):
    """A command that requires a profile to be loaded."""

    profile_data: ProfileData
