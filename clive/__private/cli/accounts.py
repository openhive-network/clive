import typer

from clive.__private.cli.common.with_profile import WithProfile

accounts = typer.Typer(help="Manage your working/watched account(s).")


@accounts.command(name="list")
@WithProfile.decorator
async def list_(ctx: typer.Context) -> None:
    """List all accounts in the profile."""
    from clive.__private.cli.commands.accounts import AccountsList

    common = WithProfile(**ctx.params)
    await AccountsList(profile_data=common.profile_data).run()
