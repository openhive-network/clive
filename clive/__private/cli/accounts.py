import typer

from clive.__private.cli.common import options
from clive.__private.core._async import asyncio_run

accounts = typer.Typer(help="Manage your working/watched account(s).")


@accounts.command(name="list")
def list_(
    profile: str = options.profile_option,
) -> None:
    """List all accounts in the profile."""
    from clive.__private.cli.commands.accounts import AccountsList

    asyncio_run(AccountsList(profile=profile).run())
