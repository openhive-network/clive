from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class SetChainId(WorldBasedCommand):
    """
    Class that sets the chain ID.

    Args:
        chain_id: The chain ID to set.
    """

    chain_id: str

    async def _run(self) -> None:
        """
        Set the chain ID for the current profile.

        Returns:
            None
        """
        self.profile.set_chain_id(self.chain_id)


@dataclass(kw_only=True)
class UnsetChainId(WorldBasedCommand):
    """Class that unsets the chain ID."""

    async def _run(self) -> None:
        """
        Unset the chain ID for the current profile.

        Returns:
            None
        """
        self.profile.unset_chain_id()
