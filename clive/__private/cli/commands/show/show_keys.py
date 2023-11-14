from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.__private.cli.exceptions import CLIWorkingAccountIsNotSetError


@dataclass(kw_only=True)
class ShowKeys(ProfileBasedCommand):
    async def _run(self) -> None:
        profile_name = self.profile_data.name

        if not self.profile_data.is_working_account_set():
            raise CLIWorkingAccountIsNotSetError(self.profile_data)

        public_keys = list(self.profile_data.working_account.keys)
        typer.echo(f"{profile_name}, your keys are:\n{public_keys}")
