from abc import ABC
from dataclasses import dataclass

from clive.__private.cli.commands.abc.contextual_cli_command import ContextualCLICommand
from clive.__private.core.profile_data import ProfileData


@dataclass(kw_only=True)
class ProfileBasedCommand(ContextualCLICommand[ProfileData], ABC):
    """A command that requires a profile to be loaded."""

    profile_name: str

    @property
    def profile_data(self) -> ProfileData:
        return self._context_manager_instance

    async def _create_context_manager_instance(self) -> ProfileData:
        return ProfileData.load(self.profile_name, auto_create=False)
