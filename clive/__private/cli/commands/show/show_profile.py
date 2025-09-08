from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.show.show_accounts import ShowAccounts
from clive.__private.cli.print_cli import print_cli
from clive.__private.core.formatters.humanize import humanize_bool


@dataclass(kw_only=True)
class ShowProfile(ShowAccounts):
    async def _run(self) -> None:
        self._show_profile_info()
        self._show_accounts_info()

    def _show_profile_info(self) -> None:
        profile = self.profile
        print_cli(f"Profile name: {profile.name}")
        print_cli(f"Node address: {profile.node_address}")
        print_cli(f"Backup node addresses: {[str(url) for url in profile.backup_node_addresses]}")
        print_cli(f"Chain ID: {profile.chain_id}")
        print_cli(f"Known accounts enabled: {humanize_bool(profile.should_enable_known_accounts)}")
