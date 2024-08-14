from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.__private.cli.exceptions import CLIWorkingAccountIsNotSetError


@dataclass(kw_only=True)
class ShowKeys(ProfileBasedCommand):
    async def _run(self) -> None:
        profile_name = self.profile.name

        if not self.profile.accounts.has_working_account:
            raise CLIWorkingAccountIsNotSetError(self.profile)

        public_keys = list(self.profile.keys)
        typer.echo(f"{profile_name}, your keys are:\n{public_keys}")
