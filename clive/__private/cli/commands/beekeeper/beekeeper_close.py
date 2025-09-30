from __future__ import annotations

from dataclasses import dataclass

from beekeepy.asynchronous import close_already_running_beekeeper
from beekeepy.exceptions import FailedToDetectRunningBeekeeperError

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.print_cli import print_cli
from clive.__private.settings import safe_settings


@dataclass(kw_only=True)
class BeekeeperClose(ExternalCLICommand):
    async def _run(self) -> None:
        print_cli("Closing beekeeper...")
        beekeeper_working_directory = safe_settings.beekeeper.working_directory
        try:
            close_already_running_beekeeper(cwd=beekeeper_working_directory)
        except FailedToDetectRunningBeekeeperError:
            print_cli("There was no running beekeeper.")
        else:
            print_cli("Beekeeper was closed.")
