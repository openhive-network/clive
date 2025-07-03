from __future__ import annotations

from dataclasses import dataclass

from beekeepy.interfaces import HttpUrl

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class SetNode(WorldBasedCommand):
    """
    Class to set the node address in the profile.

    Args:
        node_address: The address of the node to set in the profile.
    """

    node_address: str

    async def _run(self) -> None:
        """
        Run the command to set the node address in the profile.

        This method converts the node address to an HttpUrl and sets it in the profile.

        Returns:
            None
        """
        url = HttpUrl(self.node_address)
        self.profile._set_node_address(url)
