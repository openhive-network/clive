from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.print_cli import print_cli
from clive.__private.si.core.show import ShowProfiles as ShowProfilesSi


@dataclass(kw_only=True)
class ShowProfiles(ExternalCLICommand):
    async def _run(self) -> None:
        print_cli(f"Stored profiles are: {await ShowProfilesSi().run()}")
