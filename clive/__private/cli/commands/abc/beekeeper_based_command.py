from abc import ABC
from dataclasses import dataclass

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.core.beekeeper import Beekeeper


@dataclass(kw_only=True)
class BeekeeperBasedCommand(ExternalCLICommand, ABC):
    """A command that requires beekeeper to be running."""

    beekeeper: Beekeeper
