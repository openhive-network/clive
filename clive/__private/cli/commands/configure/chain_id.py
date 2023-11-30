from dataclasses import dataclass

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand


@dataclass(kw_only=True)
class SetChainId(ProfileBasedCommand):
    chain_id: str

    async def _run(self) -> None:
        self.profile_data.set_chain_id(self.chain_id)


@dataclass(kw_only=True)
class UnsetChainId(ProfileBasedCommand):
    async def _run(self) -> None:
        self.profile_data.unset_chain_id()
