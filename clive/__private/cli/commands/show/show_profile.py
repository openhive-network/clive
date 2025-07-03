from __future__ import annotations

from dataclasses import dataclass

import typer

from clive.__private.cli.commands.show.show_accounts import ShowAccounts
from clive.__private.core.formatters.humanize import humanize_bool


@dataclass(kw_only=True)
class ShowProfile(ShowAccounts):
    """Show the profile information and accounts."""

    async def _run(self) -> None:
        """
        Show the profile information and accounts.

        Returns:
            None
        """
        self._show_profile_info()
        self._show_accounts_info()

    def _show_profile_info(self) -> None:
        """
        Show the profile information, and display it in a console.

        Profile info includes the profile name, node address, backup node addresses,
        chain ID, and whether known accounts are enabled.

        Returns:
            None
        """
        profile = self.profile
        typer.echo(f"Profile name: {profile.name}")
        typer.echo(f"Node address: {profile.node_address}")
        typer.echo(f"Backup node addresses: {[str(url) for url in profile.backup_node_addresses]}")
        typer.echo(f"Chain ID: {profile.chain_id}")
        typer.echo(f"Known accounts enabled: {humanize_bool(profile.should_enable_known_accounts)}")
