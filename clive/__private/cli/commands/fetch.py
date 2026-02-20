from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli


@dataclass(kw_only=True)
class Fetch(WorldBasedCommand):
    async def _run(self) -> None:
        accounts = list(self.profile.accounts.tracked)
        wrapper = await self.world.commands.fetch_offline_data(accounts=accounts)
        if wrapper.error_occurred:
            raise wrapper.error  # type: ignore[misc]

        print_cli("Offline data fetched and cached successfully.")
        if self.profile.cached_tapos:
            print_cli(f"  TAPOS: ref_block_num={self.profile.cached_tapos.ref_block_num}")
        cached_count = sum(1 for a in accounts if a.has_cached_authority)
        print_cli(f"  Authorities cached for {cached_count}/{len(accounts)} tracked accounts.")

        await self.world.commands.save_profile()
