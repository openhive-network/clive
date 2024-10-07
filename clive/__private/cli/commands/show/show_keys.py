from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIWorkingAccountIsNotSetError


@dataclass(kw_only=True)
class ShowKeys(WorldBasedCommand):
    async def _run(self) -> None:
        profile_name = self.world.profile.name

        if not self.world.profile.accounts.has_working_account:
            raise CLIWorkingAccountIsNotSetError(self.world.profile)

        public_keys = list(self.world.profile.keys)
        typer.echo(f"{profile_name}, your keys are:\n{public_keys}")
