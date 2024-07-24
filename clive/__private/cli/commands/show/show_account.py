from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class ShowAccount(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        pass
