from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class ListKeys(WorldBasedCommand):
    def run(self) -> None:
        profile_name = self.world.profile_data.name
        public_keys = list(self.world.profile_data.working_account.keys)

        typer.echo(f"{profile_name}, your keys are:\n{public_keys}")


@dataclass(kw_only=True)
class ListNode(WorldBasedCommand):
    def run(self) -> None:
        typer.echo(self.world.node.address)
