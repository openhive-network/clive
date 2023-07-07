from abc import ABC
from dataclasses import dataclass

from clive import World
from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand


@dataclass(kw_only=True)
class WorldBasedCommand(ExternalCLICommand, ABC):
    """A command that requires a world."""

    world: World
