from abc import ABC
from dataclasses import dataclass

from clive.__private.cli.commands.abc.contextual_cli_command import ContextualCLICommand
from clive.__private.core.profile import Profile


@dataclass(kw_only=True)
class ProfileBasedCommand(ContextualCLICommand[Profile], ABC):
    """A command that requires a profile to be loaded."""

    profile_name: str

    @property
    def profile(self) -> Profile:
        return self._context_manager_instance

    async def _create_context_manager_instance(self) -> Profile:
        return Profile.load(self.profile_name, auto_create=False)

    async def _hook_after_entering_context_manager(self) -> None:
        self._supply_with_correct_default_for_working_account(self.profile)
