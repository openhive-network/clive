from __future__ import annotations

from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class Lock(WorldBasedCommand):
    """Command to lock all wallets in the Clive environment."""

    @property
    def should_require_unlocked_wallet(self) -> bool:
        """
        Checking if unlocked wallet should be required.

        Returns:
            bool: False, because this command does not require an unlocked wallet.
        """
        return False

    async def _run(self) -> None:
        """
        Run the command to lock all wallets.

        This method locks all wallets in the Clive environment by calling the lock method on the world commands.

        Returns:
            None: This method does not return any value, it only locks the wallets.
        """
        await self.world.commands.lock()
        typer.echo("All wallets have been locked.")
