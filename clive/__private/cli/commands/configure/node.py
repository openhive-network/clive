from dataclasses import dataclass

from helpy import HttpUrl

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand


@dataclass(kw_only=True)
class SetNode(ProfileBasedCommand):
    node_address: str

    async def _run(self) -> None:
        url = HttpUrl(self.node_address)
        self.profile_data._set_node_address(url)
