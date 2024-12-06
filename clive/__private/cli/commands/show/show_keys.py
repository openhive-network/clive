from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIWorkingAccountIsNotSetError


@dataclass(kw_only=True)
class ShowKeys(WorldBasedCommand):
    async def _run(self) -> None:
        profile_name = self.profile.name

        if not self.profile.accounts.has_working_account:
            raise CLIWorkingAccountIsNotSetError(self.profile)

        public_keys = list(self.profile.keys)
        typer.echo(f"{profile_name}, your keys are:\n{public_keys}")
