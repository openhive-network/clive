import typer

from clive.__private.cli.common.with_profile import WithProfile
from clive.__private.core._async import asyncio_run

profile = typer.Typer(name="profile", help="Manage your profile.")


@profile.command()
@WithProfile.decorator
async def show(ctx: typer.Context) -> None:
    """Show profile information."""
    from clive.__private.cli.commands.profile import ProfileShow

    common = WithProfile(**ctx.params)
    await ProfileShow(profile_data=common.profile_data).run()


@profile.command()
def list_all() -> None:
    """List all stored profiles."""
    from clive.__private.cli.commands.profile import ProfileList

    asyncio_run(ProfileList().run())
