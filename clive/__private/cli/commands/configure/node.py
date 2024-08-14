from dataclasses import dataclass

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.core.url import Url


@dataclass(kw_only=True)
class SetNode(ProfileBasedCommand):
    node_address: str

    async def _run(self) -> None:
        url = Url.parse(self.node_address)
        self.profile._set_node_address(url)
