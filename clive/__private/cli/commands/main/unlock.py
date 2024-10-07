from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand
from clive.__private.core.commands.unlock import Unlock
from clive.__private.storage.service import PersistentStorageService


@dataclass(kw_only=True)
class CliveUnlock(BeekeeperBasedCommand):
    profile_name: str | None
    password: str

    async def _run(self) -> None:
        profile_name = self.profile_name or PersistentStorageService.get_default_profile_name()
        assert all(
            wallet.unlocked is False for wallet in (await self.beekeeper.api.list_wallets()).wallets
        ), "All wallets in session should be locked."
        await Unlock(
            app_state=None,
            beekeeper=self.beekeeper,
            wallet=profile_name,
            password=self.password,
        ).execute()
        typer.echo(f"Wallet of {profile_name} is unlocked.")
