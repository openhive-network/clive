from abc import ABC, abstractmethod
from dataclasses import dataclass

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.core.profile_data import ProfileData


@dataclass(kw_only=True)
class ProfileBasedCommand(ExternalCLICommand, ABC):
    """A command that requires a profile to be loaded."""

    profile_name: str
    _profile_data: ProfileData | None = None

    @property
    def profile_data(self) -> ProfileData:
        assert self._profile_data is not None, "Profile data should be set before running the command."
        return self._profile_data

    async def run(self) -> None:
        profile_data_manager = ProfileData.load_with_auto_save(self.profile_name, auto_create=False)
        async with profile_data_manager as profile_data:
            self._profile_data = profile_data
            await self._run()

    @abstractmethod
    async def _run(self) -> None:
        """The actual implementation of the command."""
