from abc import ABC
from dataclasses import dataclass

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperCommon
from clive.__private.cli.commands.abc.contextual_cli_command import ContextualCLICommand
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.world import CLIWorld, World


@dataclass(kw_only=True)
class WorldBasedCommand(ContextualCLICommand[World], BeekeeperCommon, ABC):
    """A command that requires a world."""

    profile_name: str
    use_beekeeper: bool = True

    @property
    def world(self) -> World:
        return self._context_manager_instance

    @property
    def beekeeper(self) -> Beekeeper:
        return self.world.beekeeper

    async def _create_context_manager_instance(self) -> World:
        return CLIWorld(
            profile_name=self.profile_name,
            use_beekeeper=self.use_beekeeper,
            beekeeper_remote_endpoint=self.beekeeper_remote_url,
        )

    async def _hook_before_entering_context_manager(self) -> None:
        if self.use_beekeeper:
            self._print_launching_beekeeper()

    async def _hook_after_entering_context_manager(self) -> None:
        self._supply_with_correct_default_for_working_account(self.world.profile)
