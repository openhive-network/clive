from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class SetChainId(WorldBasedCommand):
    chain_id: str

    async def _run(self) -> None:
        self.profile.set_chain_id(self.chain_id)


@dataclass(kw_only=True)
class UnsetChainId(WorldBasedCommand):
    async def _run(self) -> None:
        self.profile.unset_chain_id()
