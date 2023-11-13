import typer

from clive.__private.cli.common.with_profile import WithProfile
from clive.__private.core._async import asyncio_run

show = typer.Typer(name="show", help="Show various data.")


@show.command(name="profiles")
def show_profiles() -> None:
    """Show all stored profiles."""
    from clive.__private.cli.commands.show.show_profiles import ShowProfiles

    asyncio_run(ShowProfiles().run())


@show.command(name="accounts")
@WithProfile.decorator
async def show_accounts(ctx: typer.Context) -> None:
    """Show all accounts stored in the profile."""
    from clive.__private.cli.commands.show.show_accounts import ShowAccounts

    common = WithProfile(**ctx.params)
    await ShowAccounts(profile_data=common.profile_data).run()


@show.command(name="keys")
@WithProfile.decorator
async def show_keys(ctx: typer.Context) -> None:
    """Show all the public keys stored in Clive."""
    from clive.__private.cli.commands.show.show_keys import ShowKeys

    common = WithProfile(**ctx.params)
    await ShowKeys(profile_data=common.profile_data).run()
